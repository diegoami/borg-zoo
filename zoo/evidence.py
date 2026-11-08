"""Hash retained raw attempt files and build an observed death index.

This is an evidence inventory, not a causal diagnosis or replay-verification claim.
"""
import csv
import hashlib
import json
from pathlib import Path

from .catalogue import cell_key


def attach(record, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    files = {}
    for path in sorted(directory.rglob('*')):
        if path.is_file() and path.name != 'evidence.json':
            files[str(path.relative_to(directory))] = {
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'bytes': path.stat().st_size,
            }
    missing = []
    if record.get('outcome') in ('death', 'turn_cap', 'completion'):
        if record.get('harness_kind', 'better-borg-c') == 'better-borg-c':
            missing.extend(name for name in ('trace.txt', 'result.json') if name not in files)
            if record['outcome'] == 'death' and not any(name.endswith('.map') for name in files):
                missing.append('native final .map')
        else:
            for required in ('run.json', 'states.jsonl', 'commands.jsonl', 'messages.jsonl'):
                if not any(name.endswith('/' + required) or name == required for name in files):
                    missing.append('raw ' + required)
    manifest = {'schema': 'borg-zoo/evidence@1', 'cell': cell_key(record), 'files': files,
                'missing_required': missing, 'complete': not missing and bool(files)}
    (directory / 'evidence.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    record['evidence'] = manifest


def write_indexes(target, records):
    target = Path(target)
    problems = {cell_key(record): ((record.get('evidence') or {}).get('missing_required') or ['no raw evidence inventory'])
                for record in records if not (record.get('evidence') or {}).get('complete')}
    (target / 'evidence-status.json').write_text(json.dumps({
        'schema': 'borg-zoo/evidence-status@1', 'planned_records': len(records),
        'inventoried_records': sum(bool(record.get('evidence')) for record in records),
        'complete': not problems, 'problems': problems,
        'qualification': 'Per-file inventories are generated before upload. Raw archives have independent SHA-256 files; retrieve and verify them before claiming durable local recovery.'
    }, indent=2, sort_keys=True) + '\n')
    rows = []
    for record in sorted(records, key=cell_key):
        if record['outcome'] != 'death' and not record.get('died_after_cap'):
            continue
        rows.append({
            'cell': cell_key(record), 'specimen': record['specimen'], 'seed': record['seed'],
            'race': record.get('played_race'), 'class': record.get('played_class'),
            'outcome': record['outcome'], 'cause': record.get('cause'),
            'died_after_cap': record.get('died_after_cap'), 'final': record.get('final'),
            'evidence': record.get('evidence'),
            'diagnosis': 'unassessed',
            'qualification': 'Recorded outcome only; no causal diagnosis or replay fidelity claimed.',
        })
    (target / 'deaths.json').write_text(json.dumps(rows, indent=2, sort_keys=True) + '\n')
    with (target / 'deaths.csv').open('w', newline='') as stream:
        fields = ['cell', 'specimen', 'seed', 'race', 'class', 'outcome', 'cause', 'turn', 'depth', 'level']
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({**{k: row.get(k) for k in fields if k not in ('turn', 'depth', 'level')},
                             **{k: (row.get('final') or {}).get(k) for k in ('turn', 'depth', 'level')}})
