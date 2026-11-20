#!/usr/bin/env python3
"""Download a zoo run's death bundles and keep the ones asked for.

    fetch_bundles.py RUN_ID|EXPERIMENT --out DIR [--class Ranger] [--seeds 1,2,3] [--profile NAME]

RUN may be the experiment's name (e.g. reborn-main-fde8-full): the latest run on the
results branch is used, and its id printed. scripts/runs.py lists recent runs.

Writes DIR/all (the run's deaths-* artifacts as downloaded) and DIR/selected (a copy
with each shard's index.jsonl cut to the selected deaths and only their bundle
directories), which is what borg-cemetery's import_zoo_deaths.py --bundles reads.
Prints one line per selected death. Bundles that are not "reproduced" are skipped:
their key stream did not match the zoo cell's, so nothing built from them is the game.
"""
import argparse
import json
import shutil
import subprocess
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run')
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--class', dest='cls')
    ap.add_argument('--seeds')
    ap.add_argument('--profile')
    ap.add_argument('--repo', default='diegoami/borg-zoo')
    a = ap.parse_args()
    if not a.run.isdigit():
        root = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True, check=True).stdout.strip()
        subprocess.run(['git', '-C', root, 'fetch', '-q', 'origin', 'results'], check=True)
        dirs = subprocess.run(['git', '-C', root, 'ls-tree', '--name-only', f'origin/results:results/{a.run}/'], capture_output=True, text=True).stdout.split()
        if not dirs:
            raise SystemExit(f'no runs of {a.run} on the results branch (scripts/runs.py lists them)')
        latest = max(dirs, key=lambda d: int(d.split('-')[0]))
        print(f'{a.run}: latest run {latest} (of {len(dirs)})')
        a.run = latest.split('-')[0]
    seeds = {int(s) for s in a.seeds.split(',')} if a.seeds else None
    raw, sel = a.out / 'all', a.out / 'selected'
    if not raw.exists():
        raw.mkdir(parents=True)
        subprocess.run(['gh', 'run', 'download', a.run, '-R', a.repo, '-p', 'deaths-*', '-D', str(raw)], check=True)
    shutil.rmtree(sel, ignore_errors=True)
    n = 0
    for idx in sorted(raw.rglob('index.jsonl')):
        keep = []
        for line in idx.read_text().splitlines():
            if not line.strip():
                continue
            e = json.loads(line)
            ch = e.get('character') or ''
            if e.get('status') != 'reproduced' or not e.get('bundle'):
                continue
            if seeds is not None and e.get('seed') not in seeds:
                continue
            if a.cls and not ch.endswith(' ' + a.cls):
                continue
            if a.profile and e.get('profile') != a.profile:
                continue
            keep.append(e)
        if not keep:
            continue
        out = sel / idx.relative_to(raw).parent
        out.mkdir(parents=True, exist_ok=True)
        (out / 'index.jsonl').write_text(''.join(json.dumps(e) + '\n' for e in keep))
        for e in keep:
            shutil.copytree(idx.parent / e['bundle'], out / e['bundle'])
            f = e.get('final') or {}
            print(f"{e['seed']}\t{e['character']}\t{e['cause']}\tCL{f.get('level')}\tDL{f.get('depth')}\tturn {f.get('turn')}\t{e['specimen']}")
            n += 1
    print(f'{n} bundles in {sel}')


if __name__ == '__main__':
    main()
