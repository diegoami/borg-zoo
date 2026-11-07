"""borg-zoo command line: plan, build, run, collect, site."""
import argparse
import datetime
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import catalogue as cat_mod
from . import harness, site


def cmd_plan(args):
    exp = cat_mod.experiment(args.experiment)
    plan = cat_mod.plan(exp, args.shards)
    if args.github_output:
        with open(os.environ['GITHUB_OUTPUT'], 'a') as out:
            out.write(f"specimens={json.dumps(plan['specimens'])}\n")
            out.write(f"runs={json.dumps(plan['runs'])}\n")
            out.write(f"name={exp['name']}\n")
    print(json.dumps({'experiment': exp['name'], 'cells': plan['cells'],
                      'builds': len(plan['specimens']), 'run_jobs': len(plan['runs'])}))


def cmd_build(args):
    manifest = harness.build(args.specimen, args.harness, args.out)
    print(json.dumps({'specimen': args.specimen, 'binary_sha256': manifest['binary_sha256'],
                      'compiler': manifest['compiler']}))


def cmd_run(args):
    cat = cat_mod.catalogue()
    exp = cat_mod.experiment(args.experiment, cat)
    mine = cat_mod.shard(cat_mod.cells(exp, cat), args.specimen, args.shard, args.shards)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    def one(cell):
        record = harness.run_cell(cell, args.build, args.harness, args.work, cat, keep=args.keep)
        print(json.dumps({k: record[k] for k in ('specimen', 'profile', 'seed', 'outcome', 'wall_seconds')}),
              flush=True)
        return record

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        records = list(pool.map(one, mine))
    with out.open('w') as f:
        for r in records:
            f.write(json.dumps(r, sort_keys=True) + '\n')
    print(f'{len(records)} cells -> {out}')


def cmd_collect(args):
    cat = cat_mod.catalogue()
    exp = cat_mod.experiment(args.experiment, cat)
    expected = {cat_mod.cell_key(c) for c in cat_mod.cells(exp, cat)}
    records = {}
    for path in sorted(Path(args.cells).rglob('*.jsonl')):
        for line in path.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                records[cat_mod.cell_key(r)] = r
    missing = sorted(expected - set(records))
    for key in missing:
        suite, specimen, profile, seed = key.split('/')
        records[key] = {'schema': 'borg-zoo/cell@1', 'suite': suite, 'specimen': specimen,
                        'profile': profile, 'seed': int(seed), 'outcome': 'harness_failure',
                        'error': 'no record collected (job failed or was cancelled)',
                        'final': {}, 'first_turn_at_depth': {}, 'cap': cat['suites'][suite]['cap']}
    target = Path(args.results) / exp['name'] / args.run_id
    target.mkdir(parents=True, exist_ok=False)
    with (target / 'cells.jsonl').open('w') as f:
        for key in sorted(records, key=lambda k: (k.split('/')[0], exp['specimens'].index(k.split('/')[1]),
                                                   exp['profiles'].index(k.split('/')[2]), int(k.split('/')[3]))):
            f.write(json.dumps(records[key], sort_keys=True) + '\n')
    used = {
        'harness': cat['specimens']['harness'],
        'specimens': {k: cat['specimens']['specimens'][k] for k in exp['specimens']},
        'profiles': {k: {**cat['profiles'][k], 'sha256': cat_mod.profile_sha256(cat['profiles'][k])}
                     for k in exp['profiles']},
        'suites': {k: cat['suites'][k] for k in exp['suites']},
    }
    env = {'compilers': sorted({r.get('compiler') for r in records.values() if r.get('compiler')}),
           'platforms': sorted({r.get('platform') for r in records.values() if r.get('platform')})}
    meta = {'schema': 'borg-zoo/run@1', 'run_id': args.run_id, 'run_url': args.run_url,
            'completed': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
            'zoo_commit': args.zoo_commit, 'experiment': exp, 'catalogue': used,
            'environment': env, 'missing_cells': len(missing)}
    (target / 'meta.json').write_text(json.dumps(meta, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'run': str(target), 'cells': len(records), 'missing': len(missing)}))


def cmd_site(args):
    n = site.build_site(args.results, args.out)
    print(f'{n} runs -> {args.out}')


def main(argv=None):
    p = argparse.ArgumentParser(prog='python -m zoo', description=__doc__)
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('plan')
    s.add_argument('--experiment', required=True)
    s.add_argument('--shards', type=int, default=4)
    s.add_argument('--github-output', action='store_true')
    s = sub.add_parser('build')
    s.add_argument('--specimen', required=True)
    s.add_argument('--harness', required=True)
    s.add_argument('--out', required=True)
    s = sub.add_parser('run')
    s.add_argument('--experiment', required=True)
    s.add_argument('--specimen', required=True)
    s.add_argument('--shard', type=int, default=0)
    s.add_argument('--shards', type=int, default=1)
    s.add_argument('--build', required=True)
    s.add_argument('--harness', required=True)
    s.add_argument('--work', required=True)
    s.add_argument('--out', required=True)
    s.add_argument('--jobs', type=int, default=os.cpu_count() or 1)
    s.add_argument('--keep', action='store_true', help='keep traces and terminal logs')
    s = sub.add_parser('collect')
    s.add_argument('--experiment', required=True)
    s.add_argument('--cells', required=True)
    s.add_argument('--results', required=True)
    s.add_argument('--run-id', required=True)
    s.add_argument('--run-url', default='')
    s.add_argument('--zoo-commit', default='')
    s = sub.add_parser('site')
    s.add_argument('--results', required=True)
    s.add_argument('--out', required=True)
    args = p.parse_args(argv)
    {'plan': cmd_plan, 'build': cmd_build, 'run': cmd_run, 'collect': cmd_collect, 'site': cmd_site}[args.cmd](args)


if __name__ == '__main__':
    sys.exit(main())
