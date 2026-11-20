#!/usr/bin/env python3
"""List recent zoo runs with their deaths, to pick one for /death-report.

    runs.py [FILTER] [--n 15]

Reads the results branch: each experiment's runs (results/EXPERIMENT/RUNID-ATTEMPT),
newest first, with games, deaths and deaths per class. FILTER keeps experiments whose
name contains it (e.g. "fde8", "full", "leash"). The site's run page address has the same
EXPERIMENT/RUNID-ATTEMPT, e.g. .../runs/reborn-main-fde8-full/44681930409-1/index.html.
"""
import argparse
import collections
import json
import subprocess


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('filter', nargs='?', default='')
    ap.add_argument('--n', type=int, default=15)
    a = ap.parse_args()
    g = lambda *x: subprocess.run(['git', *x], capture_output=True, text=True).stdout
    g('fetch', '-q', 'origin', 'results')
    runs = []
    for line in g('ls-tree', '-d', '--name-only', 'origin/results:results/').split():
        if a.filter in line:
            for d in g('ls-tree', '--name-only', f'origin/results:results/{line}/').split():
                if d.split('-')[0].isdigit():
                    runs.append((int(d.split('-')[0]), line, d))
    runs.sort(reverse=True)
    print('| run | experiment | games | deaths | deaths per class |')
    print('|---|---|---:|---:|---|')
    for rid, exp, d in runs[:a.n]:
        cells = [json.loads(l) for l in g('show', f'origin/results:results/{exp}/{d}/cells.jsonl').splitlines() if l.strip()]
        dead = [c for c in cells if c.get('outcome') == 'death']
        per = collections.Counter(c.get('class') for c in dead)
        print(f"| {d} | {exp} | {len(cells)} | {len(dead)} | {', '.join(f'{k} {v}' for k, v in per.most_common())} |")


if __name__ == '__main__':
    main()
