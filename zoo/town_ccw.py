"""First-CCW opportunities from pinned Track P planner receipts."""
from bisect import bisect_left, bisect_right
from collections import Counter
from itertools import groupby
import json
from pathlib import Path
import re

from . import town
from .catalogue import cell_key

SOURCE = '137b6c44f666626d66fccd7a32259dea12ee0ee2'
PLAN_SCHEMAS = {
    '11214501638b3d172113d41c10a304932c925f51': 20,
    SOURCE: 25,
}
SETTINGS = {
    'town_csw_reserve_percent': 100, 'town_prepared_ccw': 2, 'town_prepared_ccw_percent': 112,
    'town_prepared_neutralize': 2, 'town_prepared_neutralize_percent': 40,
    'town_prepared_dear_after_recall': 1, 'town_recall_reserve': 2, 'buy_recall_from_gold': 200,
}
# Engine item kinds and planner capability indices at the supported pins.
CCW = 233
ALCHEMIST = 4
LIGHT, FOOD, PHASE, PHASE_RESERVE, PREP_CCW = 0, 1, 4, 61, 82
RECALL_TRAIT = 38
ITEMS = {'ccw': (CCW,), 'csw': (232,), 'clw': (231,), 'recall': (208,), 'phase_door': (185,),
         'neutralize_poison': (237,), 'food': range(7, 16), 'spare_lights': (4, 5), 'oil': (6,)}
STATE = re.compile(r'^(\d+) \S+ d(\d+)/(\d+) .*?\bau(-?\d+) .*?\bp([0-9a-f]+) e([0-9a-f]+)\b')
CONFIRMATION = re.compile(
    r'^# Buying (?:(\d+) x )?(?:Potions? of (Cure Critical Wounds|Neutralize Poison)'
    r'|Scrolls? of (Word of Recall))( \{unseen\})?\.$')
PURCHASE_KINDS = {'Cure Critical Wounds': 'ccw', 'Neutralize Poison': 'neutralize_poison',
                  'Word of Recall': 'recall'}
STREAMS = ('town-plan.jsonl', 'town-departure-fuel.jsonl', 'state.log', 'messages.log',
           'town-transactions.jsonl', 'settings-resolved.json')


def json_lines(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def pack(plan):
    kinds = Counter()
    for place, _, kind, qty, *_ in plan['kit']:
        if place == 0:
            kinds[kind] += qty
    return {name: sum(kinds[kind] for kind in ids) for name, ids in ITEMS.items()}


def purchases(directory):
    """Pair post-purchase Borg names to the immediately preceding native receipt."""
    receipts = iter(json_lines(directory / 'town-transactions.jsonl'))
    pending = None
    events = []
    for line in (directory / 'messages.log').read_text().splitlines():
        message = town.MESSAGE.match(line)
        if not message:
            continue
        key, turn, text = int(message[1]), int(message[2]), message[4]
        if town.BUY.match(text):
            pending = next(receipts, None)
            if pending and (pending['key_index'] != key or pending['native_receipt'] != text):
                raise ValueError(f'town transaction differs from message at key {key}')
        elif text.startswith('# Town plan executing action '):
            pending = None
        elif text.startswith('# Buying '):
            match = CONFIRMATION.fullmatch(text)
            if match:
                quantity = int(match[1] or 1)
                kind = PURCHASE_KINDS[match[2] or match[3]]
                verified = bool(pending and pending['wallet_verified'] and pending['quantity'] == quantity)
                events.append({'turn': pending['game_turn'] if pending else turn,
                               'confirmation_turn': turn, 'key': key, 'kind': kind, 'quantity': quantity,
                               'unseen': bool(match[4]), 'verified': verified, 'transaction': pending})
            pending = None
    return events


def opportunity(plan, held):
    shop_stock = {(shop, slot): (tval, sval, qty, price)
                  for shop, stock in plan['shops'] for slot, tval, sval, qty, price, _ in stock}
    offers = {slot: (qty, price) for (shop, slot), (tval, sval, qty, price) in shop_stock.items()
              if shop == ALCHEMIST and (tval, sval) == (26, 10) and qty > 0}
    available = {(shop, slot): qty for shop, slot, qty in plan['available']}
    curves = {row[0]: row for row in plan['capability_curves']}
    gold, slots, _, weight = plan['limits']
    urgent_gold = sum(shop_stock[shop, slot][3] for shop, slot, _ in plan['urgent'] if shop != 7)
    # The negative food demand carries the exact floor. A positive demand can
    # include a larger trip forecast. Between the two shipped floor values,
    # a positive demand alone cannot establish whether food covers the floor.
    food_demand, food_on_hand = curves[FOOD][2:4]
    if food_demand < 0:
        food_covered = food_on_hand >= -food_demand
    elif food_on_hand >= min(food_demand, 225_000):
        food_covered = True
    elif food_on_hand < 150_000:
        food_covered = False
    else:
        food_covered = None
    staples = {
        'light': curves[LIGHT][1] == 0 or curves[LIGHT][3] >= abs(curves[LIGHT][2]),
        'food': food_covered,
        'phase_door': curves[PHASE][3] >= max(1000, -curves[PHASE_RESERVE][2]),
    }
    fitting = [slot for shop, slot, kind, _, slots_cost, item_weight, *_ in plan['wares']
               if shop == ALCHEMIST and kind == CCW and slot in offers and available.get((shop, slot), 0) > 0
               and 0 < offers[slot][1] <= gold and slots_cost <= slots and item_weight <= weight]
    post_urgent_gold = plan['gold'] - urgent_gold
    recall_trait = dict(plan['traits']).get(RECALL_TRAIT, 0)
    return {'turn': plan['gturn'], 'step': plan['step'],
            'offers': [{'slot': slot, 'stock': qty, 'price': price,
                        'available': available.get((ALCHEMIST, slot), 0), 'fits': slot in fitting}
                       for slot, (qty, price) in offers.items()],
            'recall': held['recall'], 'recall_trait': recall_trait,
            'post_urgent_gold': post_urgent_gold, 'spendable_gold': gold,
            'staples_covered': staples, 'ccw_row_present': PREP_CCW in curves,
            'gate_open': post_urgent_gold >= SETTINGS['buy_recall_from_gold']
                         and recall_trait >= SETTINGS['town_recall_reserve'],
            'ccw_row_active': PREP_CCW in curves and curves[PREP_CCW][1] > 0,
            'action': [plan['paction'], *plan['act']]}


def departure_pack(last, departure, states):
    """Qualify pack and equipment using their unchanged native state hashes."""
    if departure is None:
        return None, 'no departure recorded'
    if (not states or states[0][0] != last['gturn'] or states[-1][0] != departure['game_turn']
            or not any(depth == 0 and gold == last['gold'] and turn == last['gturn']
                       for turn, depth, _, gold, *_ in states)
            or not any(state[1] > 0 for state in states)):
        return None, 'no matching town-to-dungeon state window'
    first_dungeon = next(i for i, state in enumerate(states) if state[1] > 0)
    transition = states[first_dungeon]
    if transition[0] != departure['game_turn'] or transition[1] != departure['depth']:
        return None, 'ambiguous town-to-dungeon state window'
    if len({tuple(state[4:]) for state in states[:first_dungeon + 1]}) != 1:
        return None, 'pack or equipment fingerprint changed before departure'
    counts = pack(last)
    counts.update({'equipped_light': departure['equipped'], 'light_radius': departure['radius'],
                   'unlight': departure['unlight']})
    return counts, None


def collect(directory, source):
    directory = Path(directory)
    missing = [name for name in STREAMS if not (directory / name).is_file()]
    result = {'schema': 'borg-zoo/ccw-census@1', 'visits': [], 'missing': missing}
    plan_schema = PLAN_SCHEMAS.get(source)
    if plan_schema is None or missing:
        return {**result, 'status': 'unavailable',
                'error': 'unexpected source pin' if plan_schema is None else 'missing required receipts'}
    try:
        settings = json.loads((directory / 'settings-resolved.json').read_text())['effective_settings']
        differences = {name: settings.get(name) for name, want in SETTINGS.items() if settings.get(name) != want}
        if differences:
            return {**result, 'status': 'unavailable', 'error': 'settings mismatch', 'differences': differences}
        return {**result, **visit_rows(directory, plan_schema)}
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        # Preserve the game outcome and surface measurement failures separately.
        return {**result, 'status': 'unavailable', 'error': str(exc)}


def visit_rows(directory, plan_schema):
    plans = json_lines(directory / 'town-plan.jsonl')
    if any(plan['v'] != plan_schema or plan['mode'] != 1 for plan in plans):
        raise ValueError(f'expected live v{plan_schema} planner receipts')
    visits = [list(rows) for _, rows in groupby(plans, key=lambda row: row['visit'])]
    if [rows[0]['visit'] for rows in visits] != sorted({row['visit'] for row in plans}):
        raise ValueError('planner visits are out of order')
    states = [tuple(int(v) for v in match.groups()[:4]) + match.groups()[4:]
              for line in (directory / 'state.log').read_text().splitlines() if (match := STATE.match(line))]
    if not states:
        raise ValueError('no native state fingerprints')
    turns = [s[0] for s in states]
    departures = json_lines(directory / 'town-departure-fuel.jsonl')
    departure_turns = [d['game_turn'] for d in departures]
    events = purchases(directory)
    purchase_turns = [event['turn'] for event in events]
    rows = []
    joined = 0
    for i, visit in enumerate(visits):
        first, last = visit[0], visit[-1]
        start, end = first['gturn'], last['gturn']
        next_start = visits[i + 1][0]['gturn'] if i + 1 < len(visits) else turns[-1] + 1
        # A previous visit can leave and return at the new visit's first
        # turn. Start with the last plan row, which still observes town.
        departure_i = bisect_left(departure_turns, end)
        departure = departures[departure_i] if departure_i < len(departures) else None
        if departure and not end <= departure['game_turn'] < next_start:
            departure = None
        stop = min(next_start, departure['game_turn'] + 1) if departure else next_start
        bought = events[bisect_left(purchase_turns, start):bisect_left(purchase_turns, stop)]
        joined += len(bought)
        descent = departure['game_turn'] if departure else None
        window = states[bisect_left(turns, end):bisect_right(turns, descent)] if departure else []
        inventory, gap = departure_pack(last, departure, window)
        first_state_i = bisect_left(turns, start)
        max_depth = states[first_state_i][2] if first_state_i < len(states) else None
        row = {'visit': first['visit'], 'first_turn': start, 'last_plan_turn': end, 'max_depth': max_depth,
               'opening_pack': pack(first), 'last_town_pack': pack(last),
               'departure_turn': descent, 'departure_pack': inventory,
               'departure_gap': gap, 'purchases': bought}
        for plan in visit:
            held = pack(plan)
            if held['ccw']:
                continue
            at = opportunity(plan, held)
            row.setdefault('first_without_ccw', at)
            if at['ccw_row_active']:
                row.setdefault('first_active_ccw_row', at)
            if at['offers']:
                row.setdefault('first_stocked', at)
            if any(offer['fits'] for offer in at['offers']):
                row.setdefault('first_affordable', at)
                if all(at['staples_covered'].values()):
                    row.setdefault('first_after_staples', at)
                    if at['ccw_row_present'] and not at['gate_open']:
                        row.setdefault('first_recall_gated', at)
                    if not at['ccw_row_present']:
                        row.setdefault('first_before_prepared_row', at)
                    if at['gate_open'] and at['ccw_row_active']:
                        row.setdefault('first_gate_open', at)
        ccw_purchases = [event for event in bought if event['kind'] == 'ccw']
        row['bought_ccw'] = any(event['verified'] for event in ccw_purchases)
        row['ccw_purchase_uncertain'] = any(not event['verified'] for event in ccw_purchases)
        row['ccw_purchase_not_seen'] = not ccw_purchases
        rows.append(row)
    return {'status': 'ok', 'visits': rows, 'unjoined_purchases': len(events) - joined}


def summary(rows):
    conditions = {
        'planner_visits': lambda row: True,
        'without_ccw': lambda row: 'first_without_ccw' in row,
        'stocked': lambda row: 'first_stocked' in row,
        'affordable': lambda row: 'first_affordable' in row,
        'after_staples': lambda row: 'first_after_staples' in row,
        'gate_open': lambda row: 'first_gate_open' in row,
        'gate_stayed_closed': lambda row: ('first_recall_gated' in row and 'first_active_ccw_row' not in row),
        'before_prepared_row': lambda row: 'first_before_prepared_row' in row,
        'bought_ccw': lambda row: row['bought_ccw'],
        'ccw_purchase_uncertain': lambda row: row['ccw_purchase_uncertain'],
        'departed_with_ccw': lambda row: (row['departure_pack'] or {}).get('ccw', 0) > 0,
        'departure_unknown': lambda row: row['departure_pack'] is None,
        'gate_open_departed_with_ccw': lambda row: ('first_gate_open' in row
                                                    and (row['departure_pack'] or {}).get('ccw', 0) > 0),
        'gate_open_departure_unknown': lambda row: ('first_gate_open' in row and row['departure_pack'] is None),
        'gate_open_miss': lambda row: ('first_gate_open' in row and row['ccw_purchase_not_seen']
                                       and (row['departure_pack'] or {}).get('ccw') == 0),
        'gate_closed_miss': lambda row: ('first_recall_gated' in row and 'first_active_ccw_row' not in row
                                         and row['ccw_purchase_not_seen']
                                         and (row['departure_pack'] or {}).get('ccw') == 0),
    }
    counts = {}
    for name, check in conditions.items():
        matched = [row for row in rows if check(row)]
        counts[name] = {'visits': len(matched), 'starts': len({row['cell'] for row in matched})}
    return counts


def publish(target, records):
    records = sorted(records, key=cell_key)
    sources = {record['specimen_ref'] for record in records if record.get('specimen_ref')}
    source = next(iter(sources or {SOURCE})) if len(sources) <= 1 else None
    rows, cells = [], []
    for record in records:
        census = record.get('ccw_census', {'status': 'unavailable', 'error': 'no census collected'})
        identity = {'cell': cell_key(record), 'seed': record['seed'], 'outcome': record['outcome'],
                    'source': record.get('specimen_ref') or source,
                    'world': (record.get('world') or {}).get('name', 'normal'),
                    'race': record.get('played_race'), 'class': record.get('played_class')}
        rows.extend({**identity, **row} for row in census.get('visits', []))
        cells.append({**identity, **{k: v for k, v in census.items() if k != 'visits'}})
    with (target / 'ccw-visits.jsonl').open('w') as stream:
        for row in rows:
            stream.write(json.dumps(row, sort_keys=True) + '\n')
    (target / 'ccw-census.json').write_text(json.dumps({
        'schema': 'borg-zoo/ccw-census-summary@1', 'source': source, 'cells': cells,
        'all_visits': summary(rows),
        'max_dl_at_least_2': summary([row for row in rows if (row['max_depth'] or 0) >= 2]),
    }, sort_keys=True, indent=2) + '\n')
