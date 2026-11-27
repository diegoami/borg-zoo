"""Stage the Track R4.5 parity arms (borg-zoo#792) into harness/suite.sh layout.

Each shard job ran borg-reborn-rs's own ``harness/suite.sh`` on a slice of the
pinned suite and uploaded its partial output tree. This module merges one
arm's shards into a single tree that ``harness/check-r45-suite.py`` (pin
610aabe) accepts: the union of the cell directories, a manifest rewritten to
the canonical suite name and sha with the union of the ``run_config.*`` lines,
and the ``DONE`` marker. The pinned constants mirror the checker's own; both
pins' ``harness/borg.txt`` hashes to SHIPPED (verified 2026-11-25).
"""
import argparse
import hashlib
import json
import shutil
import time
from pathlib import Path

SUITES = {
    'smoke': 'ee385771607f85e06257062def13fdf0bfe60773772a547280c5c0d9ec24339e',
    'full': '7c81c28c03be3e6c188cb555fa8c917402bae0819d0791a1a810e031214d2eed',
}
ARMS = ('native', 'check', 'switch')
ARM_REF = {
    'native': '24be98732748230062882fe2b7d9601dba5e2cc0',
    'check': '83e28cd4c3fb9a3a0eb4cb75e0ff8d635f25a9d2',
    'switch': '83e28cd4c3fb9a3a0eb4cb75e0ff8d635f25a9d2',
}
SHADOW_FILES = ('shadow.jsonl', 'shadow-stats.jsonl')


def manifest_of(path):
    values = {}
    for line in path.read_text().splitlines():
        key, sep, value = line.partition('=')
        if sep:
            values[key] = value
    return values


def manifest_text(values):
    order = ['implementation', 'suite', 'suite_sha256', 'borg_txt_sha256',
             'build_id_git_rev', 'build_id_git_dirty', 'build_id_inputs_dirty',
             'binary_sha256', 'build_id_source_sha256', 'checkout_source_sha256',
             'binary_sha256_end', 'overrides']
    out = []
    seen = set()
    for key in order + [k for k in values if not (k in order or k.startswith('run_config.')
                                                  or k in seen or k == 'finished_utc')]:
        if key in values and key not in seen:
            out.append(f'{key}={values[key]}')
            seen.add(key)
    for key in sorted(k for k in values if k.startswith('run_config.')):
        out.append(f'{key}={values[key]}')
    out.append(f"finished_utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    return '\n'.join(out) + '\n'


def stage_suite(suite, shards_dir, out, checker_suite, expect_names=None):
    canonical = Path(checker_suite)
    digest = hashlib.sha256(canonical.read_bytes()).hexdigest()
    if digest != SUITES[suite]:
        raise SystemExit(f'{canonical}: sha256 {digest} does not match the pinned {suite} suite')
    names = [line.split()[0] for line in canonical.read_text().splitlines()
             if line.strip() and not line.lstrip().startswith('#')]
    if expect_names is not None and sorted(names) != sorted(expect_names):
        raise SystemExit(f'suite rows differ from the expected names')
    report = {}
    for arm in ARMS:
        shard_globs = sorted(shards_dir.glob(f'parity-{arm}-*'), key=lambda p: int(p.name.rsplit('-', 1)[1]))
        if not shard_globs:
            raise SystemExit(f'no shards downloaded for arm {arm}')
        arm_out = out / arm
        arm_out.mkdir(parents=True)
        run_config = {}
        identity = None
        seconds = 0
        placed = set()
        for shard in shard_globs:
            partial = shard / 'partial'
            mpath = partial / 'manifest'
            if not mpath.exists():
                raise SystemExit(f'{shard}: no partial/manifest (the shard failed before writing one)')
            man = manifest_of(mpath)
            if identity is None:
                identity = {k: v for k, v in man.items() if not k.startswith('run_config.')
                            and k not in ('suite', 'suite_sha256', 'finished_utc')}
            for k, v in man.items():
                if k.startswith('run_config.'):
                    run_config[k] = v
            if (shard / 'shard_seconds.txt').exists():
                seconds += int((shard / 'shard_seconds.txt').read_text().strip().split('=')[-1])
            for cell in sorted(p for p in partial.iterdir() if p.is_dir()):
                name = cell.name
                if name in placed:
                    raise SystemExit(f'{arm}: cell {name} appears in two shards')
                exit_file = cell / 'run_exit'
                if not exit_file.exists() or exit_file.read_text().strip() != '0':
                    raise SystemExit(f'{arm}/{name}: unsuccessful cell (run_exit missing or nonzero)')
                shutil.copytree(cell, arm_out / name)
                placed.add(name)
        if placed != set(names):
            raise SystemExit(f'{arm}: cells {sorted(set(names) - placed)} never ran')
        for filename in SHADOW_FILES:
            got = set(arm_out.rglob(filename))
            want = {arm_out / n / filename for n in names} if arm != 'native' else set()
            if got != want:
                raise SystemExit(f'{arm}: {filename} files wrong: missing {sorted(str(p.relative_to(arm_out)) for p in want - got)}, '
                                 f'extra {sorted(str(p.relative_to(arm_out)) for p in got - want)}')
        merged = dict(identity)
        merged['suite'] = suite
        merged['suite_sha256'] = SUITES[suite]
        merged['build_id_git_rev'] = ARM_REF[arm]
        merged.update(run_config)
        (arm_out / 'manifest').write_text(manifest_text(merged))
        (arm_out / 'DONE').write_text(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + '\n')
        report[arm] = {'cells': len(placed), 'shards': len(shard_globs), 'shard_seconds': seconds}
    print(json.dumps({'suite': suite, 'arms': report}, indent=1))
    for arm, r in report.items():
        print(f"{arm}: {r['cells']} cells over {r['shards']} shards, ~{r['shard_seconds'] // 60} min wall per arm (sum of shard seconds)")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='command', required=True)
    st = sub.add_parser('stage', help='merge shard partials into the retained layout')
    st.add_argument('--suite', required=True, choices=sorted(SUITES))
    st.add_argument('--shards-dir', required=True, type=Path)
    st.add_argument('--out', required=True, type=Path)
    st.add_argument('--checker-suite', required=True, type=Path,
                    help='the pinned suite file inside the checker checkout (its hash is verified)')
    st.add_argument('--native-ref', default=ARM_REF['native'])
    st.add_argument('--candidate-ref', default=ARM_REF['check'])
    args = ap.parse_args()
    stage_suite(args.suite, args.shards_dir, args.out, args.checker_suite)


if __name__ == '__main__':
    main()
