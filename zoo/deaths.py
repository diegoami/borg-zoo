"""Death bundles for borg-cemetery (borg-zoo#176).

A cell that ends in a natural death is replayed once, after its record is
written, with the logs a cemetery dossier needs: -msglog, -statelog and
BORG_RUN_DIR (the core's decision trace and parameters). The replay must
play the same keys as the cell: its keys.log sha256 is checked against the
record's play_sha256, and a bundle that differs is kept but marked
`not_reproduced`. The replay never changes the cell record.

A bundle directory is the run directory borg-cemetery's
scripts/native/export-death.py reads, so the cemetery imports it with
scripts/import_zoo_deaths.py:

  summary.json keys.log messages.log state.log
  trace-core.jsonl (last TRACE_KEEP lines) trace-core.lines (full count)
  params-core.json user/borg.txt user/<plan> config.txt BUILD_ID
  zoo-death.json   the cell record, the run, and the reproduction status

config.txt holds what the cemetery's rerun-death.py needs to rebuild the
cell's borg.txt (seed, race and class indices, cap, borg_txt_sha256, the
profile's settings, zoo_* provenance), in the format of the zoo dossiers
already in the cemetery.

Only borg-rs cells (borg-rs and borg-reborn-rs) are bundled. A death of
another harness kind is listed in the index as `unsupported`, never
dropped. An experiment opts out with "cemetery_deaths": false.
"""
import hashlib
import json
import os
import shutil
import subprocess
from collections import deque
from pathlib import Path

from . import catalogue as cat_mod

SCHEMA = 'borg-zoo/death-bundle@1'
INDEX = 'index.jsonl'

# The core trace of a 100k-turn game is tens of MB; a dossier keeps its
# last 200 thinks, so the bundle keeps those TRACE_KEEP lines and writes the
# full count to trace-core.lines, which the cemetery reports as the total.
TRACE_KEEP = 200


def trim_trace(path, keep=TRACE_KEEP):
    """Keep the last KEEP lines of a JSONL trace; (total lines, sha256 of the full file)."""
    path = Path(path)
    if not path.is_file():
        return None
    digest, tail, total = hashlib.sha256(), deque(maxlen=keep), 0
    with path.open('rb') as f:
        for line in f:
            digest.update(line)
            total += 1
            tail.append(line)
    path.write_bytes(b''.join(tail))
    path.with_suffix('.lines').write_text(f'{total}\n')
    return {'lines': total, 'kept': len(tail), 'sha256': digest.hexdigest()}


def enabled(exp):
    return exp.get('cemetery_deaths', True) is not False


def wanted(record):
    """Whether a cell record is a death the cemetery should receive."""
    return record.get('outcome') == 'death'


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def config_text(record, cell, spec, profile, race_i, cls_i, borg_txt, plan_sha, provenance, streams=()):
    """config.txt in the zoo-dossier format (borg-cemetery rerun-death.py)."""
    lines = [f"seed={cell['seed']}", f'race_idx={race_i}', f'class_idx={cls_i}',
             f"turns={record['cap']}", f"exact_turns={1 if spec.get('exact_turns') else 0}",
             f'borg_txt_sha256={hashlib.sha256(borg_txt.encode()).hexdigest()}',
             f"zoo_experiment={provenance.get('experiment') or ''}",
             f"zoo_run={provenance.get('run_id') or ''}",
             f"zoo_profile={cell['profile']}", f"zoo_specimen={cell['specimen']}",
             f"zoo_suite={cell['suite']}"]
    if streams:
        # Observation-only record paths the cell set (a retained-evidence or
        # town-shadow cell); a rerun sets them too, to be the cell exactly.
        lines.append('zoo_record_streams=' + ','.join(streams))
    for name, value in sorted(profile['settings'].items()):
        if name == 'borg_plan':
            # The format of the zoo dossiers already in the cemetery. Its
            # rerun-death.py (borg-cemetery#59, zoo_plan) maps this back to
            # borg_plan = NAME and checks the dossier's errands_plan.txt
            # against errands_plan_sha256; the older harness path of that
            # tool reads borg_errands_plan_sha256 and cannot rerun zoo cells.
            lines += [f'borg_errands_plan=user/{value}', f'errands_plan_sha256={plan_sha}']
        else:
            lines.append(f'{name}={cat_mod.setting_value(value)}')
    return '\n'.join(lines) + '\n'


def record_streams(spec, profile, keep):
    """The record variables borgrs.run_cell set for a cell: {VARIABLE: file}."""
    if not (keep or spec.get('town_shadow_records')):
        return {}
    return {name: filename for setting, name, filename in (
        ('borg_town_plan', 'BORG_TOWN_PLAN_RECORD', 'town-plan.jsonl'),
        ('borg_trip_policy', 'BORG_TRIP_RECORD', 'trip.jsonl'))
        if profile['settings'].get(setting) == 1 or (setting == 'borg_town_plan' and spec.get('town_shadow_records'))}


def replay_borgrs(record, cell, build_dir, cat, out, provenance, keep=False):
    """Replay a borg-rs death cell into OUT with full logs; the bundle status."""
    from . import borgrs
    applied, profile = cat_mod.resolve_profile(cat, cell)
    suite = cat['suites'][cell['suite']]
    spec = cat['specimens']['specimens'][cell['specimen']]
    build_dir = Path(build_dir).resolve()
    manifest = json.loads((build_dir / 'build.json').read_text())
    if manifest['source_commit'] != spec['ref'] or manifest['impl'] != spec['impl']:
        raise ValueError(f'build {build_dir} does not match specimen {cell["specimen"]}')
    if out.exists():
        raise ValueError(f'refusing to overwrite death bundle: {out}')
    for d in ('user', 'save', 'archive', 'panic', 'scores'):
        (out / d).mkdir(parents=True)
    race, cls = cat_mod.character(suite, cell['seed']) or ('Human', 'Warrior')
    race_i, cls_i = cat_mod.RACES.index(race), cat_mod.CLASSES.index(cls)
    text = borgrs.config_text(build_dir, profile, race_i, cls_i)
    if hashlib.sha256(text.encode()).hexdigest() != record.get('config_sha256'):
        raise ValueError('borg.txt differs from the one the cell played')
    (out / 'user/borg.txt').write_text(text)
    plan = profile['settings'].get('borg_plan')
    plan_sha = borgrs.ship_plan(spec, manifest, build_dir, out, plan) if plan is not None else None
    game = build_dir / 'game'
    argv = borgrs.command(game / 'angband', out, cell, race_i, cls_i, suite, spec, keep=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith(borgrs.AMBIENT_PREFIX)}
    env.update(TZ='UTC', LANG='C.UTF-8', LC_ALL='C.UTF-8', BORG_RUN_DIR=str(out))
    # The cell's own record streams, if it had any: the replay is the cell's
    # configuration plus logs, not a different process configuration.
    streams = record_streams(spec, profile, keep)
    for name, filename in streams.items():
        env[name] = str(out / filename)
        (out / filename).touch()
    try:
        with (out / 'stderr.log').open('w') as err:
            rc = subprocess.run(argv, cwd=game, env=env, stdout=subprocess.DEVNULL, stderr=err,
                                timeout=suite['wall_seconds']).returncode
    except subprocess.TimeoutExpired:
        rc = 'timeout'
    if plan is not None and plan != 'errands_plan.txt':
        # export-death.py keeps user/errands_plan.txt as the dossier's plan;
        # copied after play, so the replay's user/ is the cell's.
        shutil.copy(out / 'user' / plan, out / 'user/errands_plan.txt')
    keys = out / 'keys.log'
    keys_sha = sha256(keys) if keys.exists() else None
    summary = json.loads((out / 'summary.json').read_text()) if (out / 'summary.json').exists() else {}
    if keys_sha and keys_sha == record.get('play_sha256') and summary.get('dead'):
        status, why = 'reproduced', None
    else:
        status = 'not_reproduced'
        why = (f'replay keys {str(keys_sha)[:12]}, cell played {str(record.get("play_sha256"))[:12]}'
               f'; exit {rc}; dead {summary.get("dead")}')
    (out / 'config.txt').write_text(config_text(record, cell, spec, profile, race_i, cls_i, text, plan_sha, provenance, sorted(streams)))
    (out / 'BUILD_ID').write_text(''.join(f'{k}={v}\n' for k, v in sorted((manifest.get('build_id') or {}).items())))
    for d in ('save', 'archive', 'panic', 'scores'):
        shutil.rmtree(out / d, ignore_errors=True)
    trace = trim_trace(out / 'trace-core.jsonl')
    return status, why, {'impl': spec['impl'], 'repository': spec.get('repository'), 'ref': spec['ref'],
                         'source_sha256': (manifest.get('build_id') or {}).get('source_sha256'),
                         'binary_sha256': manifest.get('binary_sha256'), 'replay_keys_sha256': keys_sha,
                         'trace_core': trace}


def bundle(record, cell, build_dir, cat, root, provenance, keep=False):
    """Write a death bundle under ROOT for a death record; its index entry."""
    key = cat_mod.cell_key(cell)
    spec = cat['specimens']['specimens'][cell['specimen']]
    kind = spec.get('kind', 'better-borg-c')
    entry = {'schema': SCHEMA, 'cell': key, 'seed': cell['seed'], 'suite': cell['suite'],
             'specimen': cell['specimen'], 'profile': cell['profile'], 'harness_kind': kind,
             'character': record.get('character'), 'cause': record.get('cause'),
             'final': record.get('final'), 'play_sha256': record.get('play_sha256'), **provenance}
    if kind != 'borg-rs':
        return {**entry, 'status': 'unsupported', 'error': f'no death bundle for harness kind {kind}'}
    # Absolute: the game runs with the game directory as its working directory
    # (compare.yml passes a relative --deaths; run 44098927907 lost all 11 bundles).
    out = Path(root).resolve() / key
    try:
        status, why, build = replay_borgrs(record, cell, build_dir, cat, out, provenance, keep=keep)
    except Exception as exc:  # reported per death, never dropped
        return {**entry, 'status': 'error', 'error': f'{type(exc).__name__}: {exc}'}
    entry = {**entry, 'status': status, 'error': why, 'build': build, 'bundle': key}
    (out / 'zoo-death.json').write_text(json.dumps({**entry, 'record': record}, indent=2, sort_keys=True) + '\n')
    return entry


def provenance_from_env(exp):
    """The run this bundle came from, from the GitHub Actions environment."""
    run_id = os.environ.get('GITHUB_RUN_ID')
    server, repo = os.environ.get('GITHUB_SERVER_URL'), os.environ.get('GITHUB_REPOSITORY')
    return {'experiment': exp['name'], 'run_id': run_id,
            'run_attempt': os.environ.get('GITHUB_RUN_ATTEMPT'),
            'run_url': f'{server}/{repo}/actions/runs/{run_id}' if run_id and server and repo else None,
            'zoo_commit': os.environ.get('GITHUB_SHA')}
