import os
from pathlib import Path
import json, re
root = Path(os.environ.get('ZOO_ANALYSIS', 'analysis'))
fs = [json.loads(line) for p in root.glob('cells-*.jsonl') for line in p.read_text().splitlines() if line.strip()]
assert len(fs) == 3600
meta = json.loads((Path(os.environ.get('ZOO_ANALYSIS', 'analysis')) / 'monster-metadata.json').read_text())['arms']

def norm(s):
    return re.sub('^(?:a|an|the)\\s+', '', (s or '').strip().lower())
lookup = {a: {norm(name): v for name, v in data.items()} for a, data in meta.items()}

def group(r):
    if r['outcome'] != 'death':
        return None
    if (lookup[r['specimen']].get(norm(r['cause'])) or {}).get('never_move'):
        return 'declared_immobile_killer'
    if 'Farmer Maggot' in (r['cause'] or ''):
        return 'maggot_dogs'
    if norm(r['cause']) == 'poison':
        return 'poison'
    return 'other'

def median_death(rows):
    return sorted(rows, key=lambda r: (r['final']['turn'], r['seed']))[(len(rows) - 1) // 2]

def control(death, arm):
    candidates = [r for r in fs if r['specimen'] == arm and r['outcome'] == 'turn_cap' and (r['class'] == death['class']) and (r['race'] == death['race'])]
    matching = 'same class and race'
    if not candidates:
        candidates = [r for r in fs if r['specimen'] == arm and r['outcome'] == 'turn_cap' and (r['class'] == death['class'])]
        matching = 'same class only; no same-race cap exists'

    def rank(r):
        hp = abs(r['birth_hp'] - death['birth_hp'])
        a, b = (r.get('birth_stats'), death.get('birth_stats'))
        stats = sum((abs(x - y) for x, y in zip(a, b))) if a and b else 0
        return (hp, stats, r['seed'])
    chosen = min(candidates, key=rank)
    return (chosen, {'matching': matching, 'ranking': 'absolute initial-HP difference, then L1 distance of Neo birth-stat vectors when both exist, then numeric seed', 'candidate_caps': len(candidates), 'rank': rank(chosen)})
selected = []
rules = []
for tag in ['declared_immobile_killer', 'maggot_dogs', 'poison']:
    dead = [r for r in fs if r['specimen'] == 'neo-5a9-original' and group(r) == tag]
    death = median_death(dead)
    selected.append({'role': 'Neo representative death', 'group': tag, 'cell': death['cell']})
    rule = {'group': tag, 'eligible_neo_deaths': len(dead), 'death_rule': 'lower median death tick, numeric seed breaks ties', 'death': death['cell'], 'controls': []}
    for arm in ['neo-5a9-original', 'angband-e473-original']:
        cap, how = control(death, arm)
        selected.append({'role': 'Neo surviving comparison' if arm.startswith('neo') else 'C surviving reference', 'group': tag, 'cell': cap['cell']})
        rule['controls'].append({'cell': cap['cell'], **how})
    rules.append(rule)
cdead = [r for r in fs if r['specimen'] == 'angband-e473-original' and group(r) == 'declared_immobile_killer']
ref = median_death(cdead)
selected.append({'role': 'C failure reference', 'group': 'declared_immobile_killer', 'cell': ref['cell']})
result = {'schema': 'borg-zoo/systematic-cases@1', 'all_records_audited_before_selection': 3600, 'rules': rules, 'additional_c_failure_rule': 'lower median death tick among all C deaths to declared NEVER_MOVE races; seed breaks ties', 'selections': selected, 'unique_cases': len({s['cell'] for s in selected}), 'qualification': 'Reference examples are not paired worlds or causal controls. C has no separately recorded birth-stat vector. Fallback matching and reused controls remain explicit.'}
(root / 'case-selection.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
for s in selected:
    r = next((r for r in fs if r['cell'] == s['cell']))
    print(json.dumps({**s, 'race': r['race'], 'class': r['class'], 'cause': r['cause'], 'turn': (r['final'] or {}).get('turn'), 'birth_hp': r['birth_hp'], 'birth_stats': r['birth_stats']}))
print('unique cases', result['unique_cases'])
