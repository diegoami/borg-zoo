"""Verify the two frozen inputs and reproduce the class-pairing receipt."""
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from zoo import catalogue, stats

if len(sys.argv) != 3:
    raise SystemExit('usage: recompute.py CONTROL.jsonl RESERVE.jsonl')
receipt = json.loads(Path(__file__).with_name('verification.json').read_text())
cells = []
for path, expected in zip(map(Path, sys.argv[1:]), receipt['inputs']):
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected['sha256']:
        raise SystemExit(f'input hash mismatch: {path}')
    cells.extend(json.loads(line) for line in path.read_text().splitlines())
cat = catalogue.catalogue()
exp = catalogue.experiment(catalogue.ROOT / 'experiments/rs-family-buying-classes-1800.json', cat)
rows = [r for r in stats.paired_by_class(exp, cells, cat['specimens']['specimens'])['classes-1800']
        if r['profile'] == receipt['arm_profile']]
if rows != receipt['per_class']:
    raise SystemExit('class-pairing receipt differs')
print('Verified input hashes and all nine class-pairing rows (3,600 cells).')
