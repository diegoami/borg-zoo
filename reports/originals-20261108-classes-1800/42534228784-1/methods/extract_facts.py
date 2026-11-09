import os
'Bounded, read-only extraction of recorded facts. No game is run.'
from pathlib import Path
from collections import Counter, deque
import json, tarfile, re, io, sys, hashlib, datetime, importlib.util
ROOT = Path(os.environ.get('ZOO_CACHE', 'cache'))
OUT = Path(os.environ.get('ZOO_ANALYSIS', 'analysis'))
OUT.mkdir(exist_ok=True)
VIEW = Path(os.environ['VIEWER_PRESENTATION'])
spec = importlib.util.spec_from_file_location('record_presentation', VIEW)
presentation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(presentation)
LOC = re.compile('^# Loc:(\\d+),(\\d+) Dep:(\\d+) Lev:(\\d+) HP:(-?\\d+)/(\\d+) SP:(-?\\d+)/(\\d+)')
BORG = re.compile('^BORG (\\d+) (.*)$')

def feature(row):
    return {'feature_version': 3, 'cell': '/'.join((str(row[k]) for k in ('suite', 'specimen', 'profile', 'seed'))), 'specimen': row['specimen'], 'seed': row['seed'], 'race': row['race'], 'class': row['class'], 'outcome': row['outcome'], 'cause': row.get('cause'), 'final': row.get('final'), 'died_after_cap': row.get('died_after_cap'), 'wall_seconds': row.get('wall_seconds'), 'birth_hp': None, 'birth_max_hp': None, 'birth_stats': None, 'birth_gold': None, 'birth_inventory': None, 'birth_options': {}, 'first_dungeon_tick': None, 'first_dungeon_source': None, 'c_plan_buy': 0, 'c_issued_buy': 0, 'c_retail_issued_buy': 0, 'c_home_issued_buy': 0, 'c_shop_entries': 0, 'native_messages_bounded': row['specimen'].startswith('angband'), 'native_energy_semantics': 'cumulative_spent' if row['specimen'].startswith('angband') else None, 'neo_energy_semantics': 'current_balance' if row['specimen'].startswith('neo') else None, 'command_counts': {}, 'refused_counts': {}, 'message_counts': {}, 'message_count': 0, 'confirmed_retail_buys': 0, 'confirmed_retail_sells': 0, 'final_inventory': [], 'has_final_map': False, 'final_map_player': None, 'last_state': None, 'last_commands': [], 'last_messages': [], 'raw_files': []}

def messages(lines, f, neo):
    counts = Counter()
    tail = deque(maxlen=100)
    buys = []
    sells = []
    for line in lines:
        if not line.strip():
            continue
        if neo:
            r = json.loads(line)
            text = r.get('text', '')
            t = r.get('turn')
        else:
            text = line.removeprefix('MESSAGE ')
            t = None
        tail.append({'turn': t, 'text': text})
        f['message_count'] += 1
        for token, label in [('There is a wall in the way!', 'wall_in_way'), ('You see nothing there to tunnel.', 'nothing_to_tunnel'), ('You cannot see!', 'cannot_see'), ('*** LOW HITPOINT WARNING! ***', 'low_hp_warning'), ('You are paralyzed', 'paralysis'), ('You are no longer poisoned', 'poison_cleared'), ('You are poisoned', 'poisoned')]:
            if token in text:
                counts[label] += 1
        if text.startswith('You bought '):
            f['confirmed_retail_buys'] += 1
            buys.append({'turn': t, 'text': text})
        if text.startswith('You sold '):
            f['confirmed_retail_sells'] += 1
            sells.append({'turn': t, 'text': text})
    f['message_counts'] = dict(counts)
    f['last_messages'] = list(tail)
    f['buy_messages'] = buys
    f['sell_messages'] = sells

def native_trace(data, f):
    locs = deque(maxlen=100)
    retained = []
    plans = []
    issued = []
    retail_issued = []
    store = None
    for order, line in enumerate(data.splitlines()):
        if line.startswith('ACTIVE_OPTIONS '):
            f['birth_options'] = {k: int(v) for k, v in (pair.split('=', 1) for pair in line.split()[1:]) if k.startswith('birth_')}
        if line.startswith('MESSAGE '):
            retained.append(line)
            continue
        b = BORG.match(line)
        if not b:
            continue
        t = int(b[1])
        note = b[2]
        m = LOC.match(note)
        if m:
            y, x, depth, level, hp, mhp, sp, msp = map(int, m.groups())
            locs.append({'turn': t, 'x': x, 'y': y, 'depth': depth, 'level': level, 'hp': hp, 'maxHp': mhp, 'sp': sp, 'maxSp': msp})
            if depth > 0 and f['first_dungeon_tick'] is None:
                f['first_dungeon_tick'] = t
                f['first_dungeon_source'] = 'first positive-depth Borg location note; earlier brief visits can be missed'
                f['native_first_dungeon_note_order'] = order
        entered = re.match("# Entering a '(\\d+)' shop", note)
        if entered:
            store = int(entered[1])
            f['c_shop_entries'] += 1
        if note.startswith("# Buying '") and ' at ' in note:
            f['c_plan_buy'] += 1
            plans.append((t, order))
        elif re.match('^# Buying .+\\.$', note):
            f['c_issued_buy'] += 1
            issued.append((t, order))
            if store == 7:
                f['c_home_issued_buy'] += 1
            elif store is not None:
                f['c_retail_issued_buy'] += 1
                retail_issued.append(t)
    f['native_last_locations'] = list(locs)
    f['c_first_retail_buy_note_tick'] = min(retail_issued, default=None)
    f['c_retail_buy_notes_by_tick'] = {str(limit): sum((t <= limit for t in retail_issued)) for limit in (1000, 2500, 5000, 10000)}
    f['c_buy_plan_before_first_dungeon'] = sum((order < f['native_first_dungeon_note_order'] for t, order in plans)) if f['first_dungeon_tick'] is not None else len(plans)
    f['c_buy_issued_before_first_dungeon'] = sum((order < f['native_first_dungeon_note_order'] for t, order in issued)) if f['first_dungeon_tick'] is not None else len(issued)
    messages(retained, f, False)

def neo_commands(lines, f):
    counts = Counter()
    refused = Counter()
    tail = deque(maxlen=100)
    first = []
    buys = []
    before_descend = Counter()
    saw_descend = False
    for line in lines:
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get('type') != 'intent':
            continue
        intent = r.get('intent') or {}
        cmd = intent.get('command') or {}
        code = cmd.get('code') if intent.get('kind') == 'command' else intent.get('kind')
        counts[code] += 1
        if not saw_descend:
            if code == 'descend':
                saw_descend = True
            else:
                before_descend[code] += 1
        if r.get('accepted') is False:
            refused[code] += 1
        tail.append(r)
        if len(first) < 30:
            first.append(r)
        if code == 'descend' and f.get('first_descend_intent_tick') is None:
            f['first_descend_intent_tick'] = r.get('turn')
        if code == 'shop-buy':
            buys.append(r.get('turn'))
    f['commands_before_first_descend_intent'] = dict(before_descend)
    f['neo_buy_intents_before_first_descend_intent'] = before_descend.get('shop-buy', 0)
    f['command_counts'] = dict(counts)
    f['refused_counts'] = dict(refused)
    f['last_commands'] = list(tail)
    f['first_commands'] = first
    f['neo_first_shop_buy_intent_tick'] = min((t for t in buys if isinstance(t, int)), default=None)
    f['neo_shop_buy_intents_by_tick'] = {str(limit): sum((isinstance(t, int) and t <= limit for t in buys)) for limit in (1000, 2500, 5000, 10000)}
    f['neo_buy_intents_before_first_dungeon'] = sum((t <= f['first_dungeon_tick'] for t in buys if isinstance(t, int))) if f['first_dungeon_tick'] is not None else len(buys)
for folder in sorted(ROOT.glob('cells-*')):
    if not (folder / 'download-receipt.json').exists():
        continue
    compact = next(folder.glob('*.jsonl'))
    rows = [json.loads(line) for line in compact.read_text().splitlines() if line.strip()]
    raw = ROOT / ('raw-' + folder.name.removeprefix('cells-'))
    if not (raw / 'download-receipt.json').exists():
        continue
    target = OUT / (folder.name + '.jsonl')
    if target.exists():
        continue
    fs = {feature(row)['cell']: feature(row) for row in rows}
    rowmap = {'/'.join((str(row[k]) for k in ('suite', 'specimen', 'profile', 'seed'))): row for row in rows}
    payload = {key: {} for key in fs}
    with tarfile.open(next(raw.glob('*.tgz')), mode='r|gz') as tar:
        for member in tar:
            if not member.isfile():
                continue
            name = member.name.removeprefix('./')
            parts = name.split('/')
            if len(parts) < 5:
                continue
            key = '/'.join(parts[:4])
            if key not in fs:
                continue
            rel = '/'.join(parts[4:])
            f = fs[key]
            f['raw_files'].append(rel)
            if rel in ('result.json', 'trace.txt', 'run/run.json', 'run/commands.jsonl', 'run/messages.jsonl', 'run/states.jsonl') or rel.endswith('.map'):
                payload[key][rel] = tar.extractfile(member).read().decode(errors='replace')
    for key, f in fs.items():
        p = payload[key]
        row = rowmap[key]
        if 'result.json' in p:
            r = json.loads(p['result.json'])
            states = r.get('states') or []
            start = next((v for v in states if v.get('kind') == 'start'), states[0] if states else {})
            f['birth_hp'] = start.get('hp')
            f['last_state'] = states[-1] if states else None
            native_trace(p.get('trace.txt', ''), f)
            maps = [v for name, v in p.items() if name.endswith('.map')]
            f['raw_map_present'] = bool(maps)
            if maps:
                projection = presentation.parse_native_map(row, maps[0])
                f['final_inventory'] = [v['description'] for group in projection['groups'] for v in group['rows']]
                f['has_final_map'] = bool(projection['map'])
                f['final_map_player'] = (projection['map'] or {}).get('player')
        else:
            r = json.loads(p['run/run.json']) if 'run/run.json' in p else {}
            birth = r.get('birth') or {}
            f.update({'birth_hp': birth.get('hp'), 'birth_max_hp': birth.get('maxHp'), 'birth_stats': birth.get('stats'), 'birth_gold': birth.get('gold'), 'birth_inventory': birth.get('inventory'), 'birth_options': birth.get('options') or {}, 'first_dungeon_tick': (r.get('firstDepthTurns') or {}).get('1'), 'first_dungeon_source': 'Core loop depth-change snapshots', 'stop_reason': (r.get('stall') or {}).get('reason') or r.get('stopped'), 'settings': r.get('settings'), 'cfg': r.get('cfg')})
            world = r.get('finalKnownWorld') or {}
            f['final_inventory'] = [v.get('description') for v in r.get('finalInventory') or []]
            f['has_final_map'] = bool(world.get('level'))
            f['final_map_player'] = (world.get('player') or {}).get('grid')
            f['final_player'] = world.get('player')
            f['store_record_shapes'] = [list(s) for s in (world.get('stores') or [])[:1]]
            f['known_stores'] = world.get('stores')
            states = [json.loads(v) for v in p.get('run/states.jsonl', '').splitlines() if v.strip()]
            f['last_state'] = states[-1] if states else None
            if f['first_dungeon_tick'] is None:
                entry = next((v for v in states if v.get('depth', 0) > 0), None)
                if entry:
                    f['first_dungeon_tick'] = entry['turn']
                    f['first_dungeon_source'] = 'retained depth-change state' if entry.get('kind') == 'depth' else 'periodic-state upper bound'
            if f['birth_hp'] is None and states:
                f['birth_hp'] = states[0].get('hp')
                f['birth_max_hp'] = states[0].get('maxHp')
            neo_commands(p.get('run/commands.jsonl', '').splitlines(), f)
            messages(p.get('run/messages.jsonl', '').splitlines(), f, True)
    with target.open('x') as stream:
        for key in sorted(fs):
            stream.write(json.dumps(fs[key], sort_keys=True) + '\n')
    print(folder.name, len(fs), flush=True)
meta = {'feature_version': 3, 'viewer_projection_commit': 'e1ad87d738118ef1565b8134f07115d44575e9df', 'viewer_projection_file_sha256': hashlib.sha256(VIEW.read_bytes()).hexdigest(), 'extraction_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'shards': len(list(OUT.glob('cells-*.jsonl'))), 'qualification': 'Recorded-fact extraction only; no game/replay executed, no causal classification or representative case selected.'}
(OUT / 'extraction-meta.json').write_text(json.dumps(meta, indent=2) + '\n')
print(json.dumps(meta), flush=True)
