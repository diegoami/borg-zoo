"""Call a separately pinned tracker toolkit over original Neo source trees.

No Neo engine, host or Borg decision implementation lives in the zoo. The
runtime bundle is produced by the tracker proposal's tools-only driver.
"""
import hashlib
import json
import platform
import os
import subprocess
import time
from pathlib import Path

from . import catalogue as cat_mod

OUTCOMES = {'death', 'turn_cap', 'stalled', 'borg_stopped', 'decision_cap', 'harness_failure'}


def check_checkout(directory, expected):
    directory = Path(directory).resolve()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=directory, text=True).strip()
    dirty = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'],
                                    cwd=directory, text=True)
    if head != expected or dirty:
        raise ValueError(f'checkout {directory} must be clean at {expected}; HEAD={head}, dirty={bool(dirty)}')
    return directory


def toolkit_script(toolkit, spec, name):
    root = check_checkout(toolkit, spec['toolkit_ref'])
    path = root / spec['toolkit_path'] / name
    if not path.is_file():
        raise ValueError(f'missing pinned toolkit script {path}')
    return path


def build(spec, source, engine, toolkit, out):
    source = check_checkout(source, spec['ref'])
    engine = check_checkout(engine, spec['engine_ref'])
    script = toolkit_script(toolkit, spec, 'build.mjs')
    out = Path(out).resolve()
    if out.exists():
        raise ValueError(f'build output exists: {out}')
    out.parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, CI='1', COREPACK_ENABLE_DOWNLOAD_PROMPT='0')
    subprocess.run(['pnpm', 'install', '--frozen-lockfile'], cwd=engine, env=env, check=True)
    subprocess.run(['pnpm', 'exec', 'tsc', '-b', 'packages/core', 'packages/content', 'packages/mod-sdk'],
                   cwd=engine, env=env, check=True)
    subprocess.run(['node', str(script), '--engine-dir', str(engine), '--borg-dir', str(source),
                    '--out', str(out)], check=True)
    manifest = json.loads((out / 'build.json').read_text())
    bundle = out / 'bundle.mjs'
    manifest.update({'kind': 'neo-original', 'source_commit': spec['ref'],
                     'engine_commit': spec['engine_ref'], 'toolkit_commit': spec['toolkit_ref'],
                     'binary_sha256': hashlib.sha256(bundle.read_bytes()).hexdigest(),
                     'compiler': 'node ' + subprocess.check_output(['node', '--version'], text=True).strip(),
                     'platform': platform.platform()})
    (out / 'zoo-build.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    return manifest


def summarise(cell, spec, suite, record, error, wall):
    record = record or {}
    outcome = record.get('outcome')
    if record.get('schema') != 'neo-original/run@1' or outcome not in OUTCOMES:
        outcome, error = 'harness_failure', error or 'missing or invalid original-Neo record'
    identity = record.get('provenance') or {}
    if outcome != 'harness_failure' and record and ((identity.get('engine') or {}).get('commit') != spec['engine_ref'] or (identity.get('borg') or {}).get('commit') != spec['ref']):
        outcome, error = 'harness_failure', 'original Neo engine/Borg identity mismatch'
    birth = record.get('birth') or {}
    if outcome != 'harness_failure' and record and (birth.get('race'), birth.get('class')) != (cell['race'], cell['class']):
        outcome, error = 'config_error', 'assigned race/class differs from played birth'
    died_after_cap = None
    if outcome == 'death' and record.get('turn', 0) > suite['cap']:
        died_after_cap = {'turn': record['turn'], 'cause': record.get('causeOfDeath')}
        outcome = 'turn_cap'
    return {'schema': 'borg-zoo/cell@1', **cell, 'harness_kind': 'neo-original',
            'specimen_ref': spec['ref'], 'engine_ref': spec['engine_ref'],
            'toolkit_ref': spec['toolkit_ref'], 'profile_sha256': cat_mod.profile_sha256({'settings': {}}),
            'cap': suite['cap'], 'birth': suite['birth'], 'outcome': outcome,
            'runner_outcome': record.get('outcome'), 'cause': record.get('causeOfDeath'),
            'died_after_cap': died_after_cap, 'played_race': birth.get('race'),
            'played_class': birth.get('class'), 'birth_record': birth,
            'settings_effective': record.get('settings'), 'turn_cap': record.get('turnCap'),
            'final': {'turn': record.get('turn'), 'depth': record.get('depth'),
                      'max_depth': record.get('maxDepth'), 'level': record.get('level'),
                      'max_level': record.get('maxLevel'), 'hp': record.get('hp'),
                      'max_hp': record.get('maxHp'), 'energy': record.get('energy'),
                      'decisions': record.get('decisions')},
            'first_turn_at_depth': {str(k): v for k, v in (record.get('firstDepthTurns') or {}).items()},
            'play_sha256': record.get('playSha256'), 'trace_sha256': record.get('playSha256'),
            'provenance': identity, 'wall_seconds': wall, 'error': error or record.get('error'),
            'last_messages': record.get('messages'), 'stall': record.get('stall'),
            'platform': platform.platform()}


def run_cell(cell, build_dir, work, cat, toolkit):
    spec = cat['specimens']['specimens'][cell['specimen']]
    suite = cat['suites'][cell['suite']]
    script = toolkit_script(toolkit, spec, 'run.mjs')
    build_dir = Path(build_dir).resolve()
    manifest = json.loads((build_dir / 'zoo-build.json').read_text())
    bundle = build_dir / 'bundle.mjs'
    if (manifest['source_commit'], manifest['engine_commit'], manifest['toolkit_commit']) != (
            spec['ref'], spec['engine_ref'], spec['toolkit_ref']):
        raise ValueError('Neo build/source/toolkit identity mismatch')
    if hashlib.sha256(bundle.read_bytes()).hexdigest() != manifest['binary_sha256']:
        raise ValueError('Neo bundle changed after build')
    out = Path(work).resolve() / cat_mod.cell_key(cell)
    out.mkdir(parents=True, exist_ok=False)
    run_dir = out / 'run'
    cmd = ['node', str(script), '--bundle', str(bundle), '--seed', str(cell['seed']),
           '--race', cell['race'], '--class', cell['class'], '--turns', str(suite['cap']),
           '--out', str(run_dir)]
    start = time.monotonic()
    error, record, rc = None, None, None
    limit = suite['wall_seconds'] * spec.get('wall_factor', 1)
    timed_out = False
    with (out / 'stdout.log').open('w') as stdout, (out / 'stderr.log').open('w') as stderr:
        try:
            rc = subprocess.run(cmd, stdout=stdout, stderr=stderr, timeout=limit).returncode
        except subprocess.TimeoutExpired:
            timed_out, error = True, f'no stop within {limit}s'
    if (run_dir / 'run.json').exists():
        try:
            record = json.loads((run_dir / 'run.json').read_text())
        except ValueError as exc:
            error = str(exc)
    result = summarise(cell, spec, suite, record, error, time.monotonic() - start)
    if timed_out:
        result['outcome'] = 'wall_timeout'
    elif rc and result['outcome'] not in ('harness_failure', 'config_error'):
        result['outcome'], result['error'] = 'harness_failure', f'driver exited {rc}'
    command_path = run_dir / 'commands.jsonl'
    if result.get('play_sha256') and command_path.exists():
        if hashlib.sha256(command_path.read_bytes()).hexdigest() != result['play_sha256']:
            result['outcome'], result['error'] = 'harness_failure', 'command stream hash mismatch'
    result['binary_sha256'] = manifest['binary_sha256']
    result['compiler'] = manifest['compiler']
    return result
