import os
from pathlib import Path
from collections import Counter
import tarfile, json, re
cache = Path(os.environ.get('ZOO_CACHE', 'cache'))
out = Path(os.environ.get('ZOO_ANALYSIS', 'analysis'))
features = {r['cell']: r for p in out.glob('cells-*.jsonl') for r in map(json.loads, p.read_text().splitlines())}
own_names = {}
for arm in ['angband-e473-original', 'neo-5a9-original']:
    with tarfile.open(next((cache / ('build-' + arm)).glob('*.tgz'))) as tar:
        members = {m.name: m for m in tar if m.isfile()}
        if arm.startswith('neo'):
            classes = json.loads(tar.extractfile(members[arm + '/pack/class.json']).read())['records']
            own_names[arm] = {r['name']: [b['name'] for b in r.get('book') or []] for r in classes}
        else:
            name = next((n for n in members if n.endswith('/lib/gamedata/class.txt')))
            text = tar.extractfile(members[name]).read().decode()
            classes = {}
            current = None
            for line in text.splitlines():
                if line.startswith('name:'):
                    current = line[5:]
                    classes[current] = []
                elif line.startswith('book:') and current:
                    parts = line.split(':')
                    if len(parts) >= 4:
                        classes[current].append(parts[3])
            own_names[arm] = classes
rows = []
for folder in sorted(cache.glob('raw-*')):
    if not (folder / 'download-receipt.json').exists():
        continue
    payload = {}
    with tarfile.open(next(folder.glob('*.tgz')), mode='r|gz') as tar:
        for member in tar:
            if not member.isfile():
                continue
            name = member.name.removeprefix('./')
            parts = name.split('/')
            key = '/'.join(parts[:4])
            rel = '/'.join(parts[4:])
            if key not in features:
                continue
            if rel in ('trace.txt', 'run/messages.jsonl', 'run/commands.jsonl'):
                payload.setdefault(key, {})[rel] = tar.extractfile(member).read().decode(errors='replace')
    for key, p in payload.items():
        f = features[key]
        titles = own_names[f['specimen']].get(f['class'], [])
        r = {'cell': key, 'class': f['class'], 'outcome': f['outcome'], 'own_book_titles': titles, 'own_book_throw_notes': [], 'own_book_projectile_messages': [], 'starting_book_handle_throw_intents': []}
        if f['specimen'].startswith('angband'):
            for line in p.get('trace.txt', '').splitlines():
                if 'Throwing painful object' in line and any((title in line for title in titles)):
                    r['own_book_throw_notes'].append(line)
        else:
            book_handles = {item['handle']: item for item in f.get('birth_inventory') or [] if item.get('tval') in (30, 31, 32, 33, 34)}
            for line in p.get('run/commands.jsonl', '').splitlines():
                e = json.loads(line)
                cmd = (e.get('intent') or {}).get('command') or {}
                if cmd.get('code') == 'throw' and (cmd.get('args') or {}).get('handle') in book_handles:
                    r['starting_book_handle_throw_intents'].append(e)
            for line in p.get('run/messages.jsonl', '').splitlines():
                e = json.loads(line)
                text = e.get('text', '')
                if text.startswith('Your ') and re.search('\\b(?:hits|misses)\\b', text) and any((title in text for title in titles)):
                    r['own_book_projectile_messages'].append(e)
        rows.append(r)
assert len(rows) == 3600
(out / 'book-throw-audit.jsonl').write_text(''.join((json.dumps(r, sort_keys=True) + '\n' for r in rows)))
for prefix in ['angband', 'neo']:
    rr = [r for r in rows if '/' + ('angband-e473-original' if prefix == 'angband' else 'neo-5a9-original') + '/' in r['cell']]
    hit = [r for r in rr if r['own_book_throw_notes'] or r['own_book_projectile_messages']]
    print(json.dumps({'arm': prefix, 'lives_with_own_realm_book_throw_evidence': len(hit), 'by_class': dict(Counter((r['class'] for r in hit))), 'outcomes': dict(Counter((r['outcome'] for r in hit))), 'starting_book_handle_intent_lives': sum((bool(r['starting_book_handle_throw_intents']) for r in rr))}, indent=2))
