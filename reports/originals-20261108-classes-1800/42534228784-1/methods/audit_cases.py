import os
from pathlib import Path
import json, tarfile, hashlib, sys, collections
sys.path.insert(0, os.environ['ZOO_CODE'])
from zoo import catalogue
cache = Path(os.environ.get('ZOO_CACHE', 'cache'))
root = Path(os.environ.get('ZOO_ANALYSIS', 'analysis'))
selection = json.loads((root / 'case-selection.json').read_text())
cat = catalogue.catalogue()
seeds = cat['suites']['classes-1800']['seeds']
features = {r['cell']: r for p in root.glob('cells-*.jsonl') for r in map(json.loads, p.read_text().splitlines())}
case_root = root / 'cases'
case_root.mkdir(exist_ok=True)
manifest = []
for cell in sorted({s['cell'] for s in selection['selections']}):
    f = features[cell]
    arm = f['specimen']
    shard = seeds.index(f['seed']) % (60 if arm.startswith('angband') else 180)
    raw = cache / f'raw-{arm}-{shard}'
    target = case_root / f"{arm}-{f['seed']}"
    target.mkdir(exist_ok=True)
    with tarfile.open(next(raw.glob('*.tgz'))) as tar:
        for member in tar:
            name = member.name.removeprefix('./')
            if not member.isfile() or not name.startswith(cell + '/'):
                continue
            rel = name[len(cell) + 1:]
            out = target / rel
            assert out.resolve().is_relative_to(target.resolve())
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(tar.extractfile(member).read())
    raw_manifest = json.loads((target / 'evidence.json').read_text())
    for name, p in raw_manifest['files'].items():
        assert hashlib.sha256((target / name).read_bytes()).hexdigest() == p['sha256'], (cell, name)
    receipt = json.loads((raw / 'download-receipt.json').read_text())
    roles = [s for s in selection['selections'] if s['cell'] == cell]
    details = {'cell': cell, 'roles': roles, 'raw_artifact': raw.name, 'artifact_id': receipt['artifact']['id'], 'artifact_url': f"https://github.com/diegoami/borg-zoo/actions/runs/42534228784/artifacts/{receipt['artifact']['id']}", 'case_path': str(target), 'feature': f, 'raw_files_verified': len(raw_manifest['files'])}
    manifest.append(details)
    if arm.startswith('angband'):
        result = json.loads((target / 'result.json').read_text())
        details['native_environment_keys'] = list(result.get('environment') or {})
    print(json.dumps({'cell': cell, 'roles': [s['role'] for s in roles], 'outcome': f['outcome'], 'cause': f['cause'], 'turn': (f['final'] or {}).get('turn'), 'birth_hp': f['birth_hp'], 'birth_stats': f['birth_stats'], 'final': f['final'], 'cmds': f['command_counts'], 'messages': f['message_counts'], 'confirmed_buys': f['confirmed_retail_buys'], 'inventory': f['final_inventory'], 'first_commands': f.get('first_commands', [])[:3], 'last_commands': f.get('last_commands', [])[-5:], 'last_messages': f['last_messages'][-12:], 'native_environment_keys': details.get('native_environment_keys')}, indent=2))
(root / 'case-manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
