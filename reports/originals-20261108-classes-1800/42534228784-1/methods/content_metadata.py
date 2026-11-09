import os
from pathlib import Path
import json, tarfile, re, hashlib
root = Path(os.environ.get('ZOO_CACHE', 'cache'))
out = Path(os.environ.get('ZOO_ANALYSIS', 'analysis'))
out.mkdir(exist_ok=True)

def tokens(values):
    return {v.strip() for text in values or [] for v in text.split('|') if v.strip()}

def parse_native(text):
    records = []
    current = None
    for line in text.splitlines():
        if not line or line.startswith('#') or ':' not in line:
            continue
        key, _, value = line.partition(':')
        value = value.strip()
        if key == 'name':
            current = {'name': value, 'flags': [], 'flags-off': []}
            records.append(current)
        elif current is not None:
            if key in ('flags', 'flags-off'):
                current.setdefault(key, []).append(value)
            elif key == 'base':
                current['base'] = value
    return records

def compile_records(races, bases):
    bases = {r['name']: r for r in bases}
    result = {}
    for race in races:
        flags = tokens((bases.get(race.get('base')) or {}).get('flags')) | tokens(race.get('flags'))
        flags -= tokens(race.get('flags-off'))
        result[race['name']] = {'base': race.get('base'), 'flags': sorted(flags), 'never_move': 'NEVER_MOVE' in flags}
    return result
allmeta = {}
for arm in ['angband-e473-original', 'neo-5a9-original']:
    archive = next((root / ('build-' + arm)).glob('*.tgz'))
    with tarfile.open(archive) as tar:
        members = {m.name: m for m in tar if m.isfile()}
        if arm.startswith('neo'):
            races = json.loads(tar.extractfile(members[arm + '/pack/monster.json']).read())['records']
            bases = json.loads(tar.extractfile(members[arm + '/pack/monster_base.json']).read())['records']
        else:
            names = {file: next((name for name in members if name.endswith('/lib/gamedata/' + file))) for file in ['monster.txt', 'monster_base.txt']}
            races = parse_native(tar.extractfile(members[names['monster.txt']]).read().decode())
            bases = parse_native(tar.extractfile(members[names['monster_base.txt']]).read().decode())
        allmeta[arm] = compile_records(races, bases)
(out / 'monster-metadata.json').write_text(json.dumps({'qualification': 'Flags are declared in the pinned content, including inherited base flags; no game was run and no current movement or avoidability is inferred.', 'arms': allmeta}, indent=2, sort_keys=True) + '\n')
print(json.dumps({arm: {'races': len(rows), 'declared_never_move': sum((r['never_move'] for r in rows.values()))} for arm, rows in allmeta.items()}))
