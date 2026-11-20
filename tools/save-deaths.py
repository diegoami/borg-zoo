#!/usr/bin/env python3
"""Save the deaths of one arm of a zoo run in a borg-cemetery checkout.

The zoo's results branch keeps no key logs, so a death is first replayed
locally (the game is deterministic) with the logs kept:

  python3 -m zoo run --experiment experiments/NAME.json --specimen SPEC \
      --arm SPEC:PROFILE --build build --work work --out out --jobs 4 --keep

Then, for each death of that arm in the run's cells.jsonl, this tool
  1. checks the replayed keys.log against the recorded play_sha256 and the
     written borg.txt against the recorded config_sha256 (a death that does not
     reproduce is reported and skipped, never exported),
  2. writes config.txt into the run directory (the zoo identity and every
     setting the arm asked for; the cemetery exporter reads it and derives the
     encounter family from it),
  3. calls the cemetery's scripts/native/export-death.py, which writes the
     D-<sha256> dossier and registers it (catalogue, statistics, canonical ids),
     then runs scripts/death_ids.py --check.

It writes only into the cemetery checkout you name. Use a fresh clone on a
branch, not another session's worktree, and open a pull request there.

  python3 tools/save-deaths.py --cells RUN/cells.jsonl --work WORK --profile PROFILE \
      --experiment NAME --run-id RUN_ID --cemetery CEMETERY_CLONE --source SOURCE_AT_PIN \
      [--seed S ...] [--dry-run]
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_config(cell, run_dir, experiment, run_id):
    summ = json.loads((run_dir / 'summary.json').read_text())
    s = dict(cell.get('requested_profile_settings') or {})
    lines = [f"seed={cell['seed']}", f"race_idx={summ['race_idx']}", f"class_idx={summ['class_idx']}",
             f"turns={cell['cap']}", f"exact_turns={1 if cell.get('boundary') == 'exact' else 0}",
             f"borg_txt_sha256={cell['config_sha256']}", f"zoo_experiment={experiment}", f"zoo_run={run_id}",
             f"zoo_profile={cell['profile']}", f"zoo_specimen={cell['specimen']}"]
    plan = cell.get('plan')
    for k, v in s.items():
        if k == 'borg_plan':
            lines += ['borg_errands_plan=user/errands_plan.txt', f"errands_plan_sha256={plan['sha256']}"]
        else:
            lines.append(f'{k}={v}')
    (run_dir / 'config.txt').write_text('\n'.join(lines) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--cells', required=True, help="the run's cells.jsonl")
    ap.add_argument('--work', required=True, help='the zoo run --work directory of the --keep replay')
    ap.add_argument('--profile', required=True)
    ap.add_argument('--experiment', required=True)
    ap.add_argument('--run-id', required=True, help='the Actions run the deaths were recorded in')
    ap.add_argument('--cemetery', required=True, help='a borg-cemetery checkout (a fresh clone on a branch)')
    ap.add_argument('--source', required=True, help='the specimen source checkout at its pin (has build/rust/BUILD_ID)')
    ap.add_argument('--seed', type=int, action='append', help='only these starts')
    ap.add_argument('--dry-run', action='store_true', help='verify the replays, write nothing')
    a = ap.parse_args()
    cem, source, work = Path(a.cemetery).resolve(), Path(a.source).resolve(), Path(a.work)
    cells = [json.loads(l) for l in Path(a.cells).read_text().splitlines() if l.strip()]
    deaths = [c for c in cells if c['profile'] == a.profile and c['outcome'] == 'death'
              and (not a.seed or c['seed'] in a.seed)]
    env = dict(os.environ, BORG_DEATH_RECORDS_DIR=str(cem / 'deaths'), BORG_DEATH_SOURCE_ROOT=str(source))
    exported, bad = 0, 0
    for c in deaths:
        d = work / c['suite'] / c['specimen'] / a.profile / str(c['seed'])
        why = None
        if not (d / 'keys.log').exists():
            why = 'no replayed keys.log (run zoo run with --keep first)'
        elif sha256(d / 'keys.log') != c['play_sha256']:
            why = 'replayed keys do not match the recorded play_sha256'
        elif sha256(d / 'user/borg.txt') != c['config_sha256']:
            why = 'written borg.txt does not match the recorded config_sha256'
        if why:
            bad += 1
            print(f"seed {c['seed']}: SKIPPED, {why}", file=sys.stderr)
            continue
        print(f"seed {c['seed']}: {c['class']} {c['race']}, {c['cause']}: replay verified")
        if a.dry_run:
            continue
        write_config(c, d, a.experiment, a.run_id)
        subprocess.run([sys.executable, str(cem / 'scripts/native/export-death.py'), str(d), '--impl', 'rust',
                        '--build-id', str(source / 'build/rust/BUILD_ID')], env=env, check=True, cwd=cem)
        exported += 1
    if exported:
        subprocess.run([sys.executable, str(cem / 'scripts/death_ids.py'), '--check'], env=env, check=True, cwd=cem)
    print(f'{len(deaths)} deaths, {exported} exported, {bad} skipped')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
