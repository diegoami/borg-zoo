import os
from pathlib import Path
from collections import Counter, defaultdict
import json, statistics, re
root = Path(os.environ.get('ZOO_ANALYSIS', 'analysis'))
fs = [json.loads(line) for p in root.glob('cells-*.jsonl') for line in p.read_text().splitlines() if line.strip()]
assert len(fs) == len({r['cell'] for r in fs}) == 3600
metadata = json.loads((Path(os.environ.get('ZOO_ANALYSIS', 'analysis')) / 'monster-metadata.json').read_text())['arms']

def norm(s):
    return re.sub('^(?:a|an|the)\\s+', '', (s or '').lower().strip())
lookups = {arm: {norm(name): data for name, data in races.items()} for arm, races in metadata.items()}

def median(v):
    v = [x for x in v if isinstance(x, (int, float))]
    return statistics.median(v) if v else None

def dist(v):
    return dict(Counter((str(x) for x in v)))

def bucket(t):
    for a, b in [(0, 1000), (1000, 2500), (2500, 5000), (5000, 10000), (10000, 25000), (25000, 50000), (50000, 100001)]:
        if a <= t < b:
            return f'{a}-{b - 1}'
    return 'outside'
summary = {'schema': 'borg-zoo/recorded-facts-analysis@1', 'records': len(fs), 'arms': {}, 'coverage': {}}
for arm in ['angband-e473-original', 'neo-5a9-original']:
    rows = [r for r in fs if r['specimen'] == arm]
    dead = [r for r in rows if r['outcome'] == 'death']
    caps = [r for r in rows if r['outcome'] == 'turn_cap']
    never = [r for r in dead if (lookups[arm].get(norm(r['cause'])) or {}).get('never_move')]
    byclass = {cls: {'starts': len(rr), 'outcomes': dict(Counter((r['outcome'] for r in rr))), 'birth_hp_median': median([r['birth_hp'] for r in rr]), 'birth_hp_min': min((r['birth_hp'] for r in rr)), 'birth_hp_max': max((r['birth_hp'] for r in rr))} for cls, rr in ((cls, [r for r in rows if r['class'] == cls]) for cls in sorted({r['class'] for r in rows}))}
    byrace = {race: {'starts': len(rr), 'outcomes': dict(Counter((r['outcome'] for r in rr)))} for race, rr in ((race, [r for r in rows if r['race'] == race]) for race in sorted({r['race'] for r in rows}))}
    observed_entry = [r['first_dungeon_tick'] for r in rows if r['first_dungeon_tick'] is not None]
    shops = {'c_lives_with_purchase_plan': sum((r['c_plan_buy'] > 0 for r in rows)), 'c_lives_with_buy_note': sum((r['c_issued_buy'] > 0 for r in rows)), 'c_lives_with_retail_buy_note': sum((r['c_retail_issued_buy'] > 0 for r in rows)), 'c_lives_with_store_entry': sum((r['c_shop_entries'] > 0 for r in rows)), 'c_buy_plan_notes': sum((r['c_plan_buy'] for r in rows)), 'c_retail_buy_notes': sum((r['c_retail_issued_buy'] for r in rows)), 'lives_with_retained_confirmed_buy_message': sum((r['confirmed_retail_buys'] > 0 for r in rows)), 'retained_confirmed_buy_messages': sum((r['confirmed_retail_buys'] for r in rows)), 'lives_with_retained_confirmed_sell_message': sum((r['confirmed_retail_sells'] > 0 for r in rows)), 'retained_confirmed_sell_messages': sum((r['confirmed_retail_sells'] for r in rows))}
    if arm.startswith('neo'):
        shops.update({'lives_issuing_shop_buy': sum((r['command_counts'].get('shop-buy', 0) > 0 for r in rows)), 'shop_buy_intents': sum((r['command_counts'].get('shop-buy', 0) for r in rows)), 'shop_sell_intents': sum((r['command_counts'].get('shop-sell', 0) for r in rows)), 'shop_exit_intents': sum((r['command_counts'].get('shop-exit', 0) for r in rows)), 'lives_with_shop_buy_intent_by_tick': {str(limit): sum((r['neo_shop_buy_intents_by_tick'][str(limit)] > 0 for r in rows)) for limit in (1000, 2500, 5000, 10000)}, 'first_shop_buy_intent_median': median([r['neo_first_shop_buy_intent_tick'] for r in rows]), 'lives_buying_before_first_descend_intent': sum((r.get('neo_buy_intents_before_first_descend_intent', 0) > 0 for r in rows)), 'first_intent_codes': dict(Counter((((r.get('first_commands') or [{}])[0].get('intent') or {}).get('command', {}).get('code') for r in rows))), 'terminal_records_with_any_nonempty_known_store': sum((any((s.get('stock') for s in r.get('known_stores') or [])) for r in rows)), 'terminal_records_with_empty_known_stores': sum((r.get('known_stores') is not None and (not any((s.get('stock') for s in r.get('known_stores') or []))) for r in rows))})
    else:
        shops.update({'lives_with_retail_buy_note_by_tick': {str(limit): sum((r['c_retail_buy_notes_by_tick'][str(limit)] > 0 for r in rows)) for limit in (1000, 2500, 5000, 10000)}, 'first_retail_buy_note_median': median([r['c_first_retail_buy_note_tick'] for r in rows]), 'lives_with_buy_plan_before_positive_depth_note_not_first_entry': sum((r['c_buy_plan_before_first_dungeon'] > 0 for r in rows)), 'lives_with_buy_note_before_positive_depth_note_not_first_entry': sum((r['c_buy_issued_before_first_dungeon'] > 0 for r in rows))})
    summary['arms'][arm] = {'starts': len(rows), 'outcomes': dict(Counter((r['outcome'] for r in rows))), 'class': byclass, 'race': byrace, 'death_ticks': dict(Counter((bucket(r['final']['turn']) for r in dead))), 'death_depth': dist((r['final']['depth'] for r in dead)), 'death_level': dist((r['final']['level'] for r in dead)), 'never_move_deaths': len(never), 'never_move_causes': dict(Counter((r['cause'] for r in never))), 'cause_metadata_unmatched': dict(Counter((r['cause'] for r in dead if norm(r['cause']) not in lookups[arm]))), 'town_dog_deaths': sum(('Farmer Maggot' in (r['cause'] or '') for r in dead)), 'poison_deaths': sum((norm(r['cause']) == 'poison' for r in dead)), 'first_positive_depth_observation_median_not_native_entry_time': median(observed_entry), 'first_positive_depth_observation_le_30': sum((t <= 30 for t in observed_entry)), 'first_positive_depth_observation_coverage': len(observed_entry), 'birth_hp_median': median([r['birth_hp'] for r in rows]), 'birth_hp_by_outcome': {out: median([r['birth_hp'] for r in rows if r['outcome'] == out]) for out in sorted({r['outcome'] for r in rows})}, 'shopping': shops, 'neo_stall_reasons': dict(Counter((r.get('stop_reason') for r in rows if r['outcome'] == 'stalled'))), 'coverage': {'birth_stats': sum((r['birth_stats'] is not None for r in rows)), 'birth_gold': sum((r['birth_gold'] is not None for r in rows)), 'final_map_parsed': sum((r['has_final_map'] for r in rows)), 'birth_no_selling': dist((r['birth_options'].get('birth_no_selling') for r in rows))}}
c = [r for r in fs if r['specimen'] == 'angband-e473-original']
n = [r for r in fs if r['specimen'] == 'neo-5a9-original']
cmedian = {(race, cls): median([r['birth_hp'] for r in c if (r['race'], r['class']) == (race, cls)]) for race, cls in {(r['race'], r['class']) for r in c}}
summary['neo_initial_hp_vs_native_same_class_race_median'] = dict(Counter(('lower' if r['birth_hp'] < cmedian[r['race'], r['class']] else 'higher' if r['birth_hp'] > cmedian[r['race'], r['class']] else 'equal' for r in n)))
summary['hp_match_outcomes'] = {group: dict(Counter((r['outcome'] for r in n if ('lower' if r['birth_hp'] < cmedian[r['race'], r['class']] else 'higher' if r['birth_hp'] > cmedian[r['race'], r['class']] else 'equal') == group))) for group in ('lower', 'equal', 'higher')}
summary['qualifications'] = ['All records audited before representative case selection.', 'C and Neo seeds generate different games; no paired causal inference.', 'C default point buy and Neo ordinary Core roller differ. Native birth stats/gold/gear were not separately captured.', 'Native messages are bounded retained history; Neo messages.jsonl is complete to stop or timeout.', 'C buying notes are plans or issued actions, not transaction confirmations. Neo gate acceptance is not Core effect success.', 'Native energy is cumulative spent energy; Neo energy is the current balance.', 'Native first positive-depth location notes can miss brief earlier visits; neither they nor the sampled maxDepth bounds provide exact first-entry times. Do not compare their medians as time spent preparing in town.', 'Never-move categories use inherited flags declared in the respective pinned content, not assumed avoidability.', 'Empty known store stock does not prove no store visit.']
(root / 'aggregate.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
for arm, d in summary['arms'].items():
    print(arm, json.dumps({k: d[k] for k in ['outcomes', 'death_ticks', 'death_depth', 'death_level', 'never_move_deaths', 'town_dog_deaths', 'poison_deaths', 'first_positive_depth_observation_median_not_native_entry_time', 'first_positive_depth_observation_le_30', 'first_positive_depth_observation_coverage', 'birth_hp_median', 'shopping', 'neo_stall_reasons', 'coverage']}, indent=2))
print('HP versus native matched class/race median', summary['neo_initial_hp_vs_native_same_class_race_median'])
