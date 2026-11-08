"""Adapter over borg-rs's deterministic harness (the borgh frontend).

A borg-rs specimen is a borg-rs commit built with harness/build.sh, either
with the Rust Borg (impl "rust") or with the C Borg compiled in the same tree
(impl "c"). Runs mirror harness/run.sh: the run's user/borg.txt is the
checkout's harness/borg.txt with the profile's settings applied, and the
borgh frontend writes summary.json and keys.log.

Limits compared with the better-borg-c observer, recorded per cell:
- borgh prints no effective-settings line, so the settings are checked in
  the borg.txt the zoo writes, not in what the Borg parsed;
- there is no per-turn state stream, so depth marks and survival by turn
  are not available;
- borgh picks race and class from indices (with -menu-letters, in
  p_race.txt and class.txt order); fixed and assigned birth are supported,
  random birth is not.
- borgh stops after the first key at or past the turn cap, so a run can
  end past the cap.
"""
import hashlib
import json
import os
import platform
import shutil
import subprocess
import time
from pathlib import Path

from . import catalogue as cat_mod
from . import stall

STOP = {'turns': 'turn_cap', 'death': 'death', 'clev': 'turn_cap', 'depth': 'turn_cap',
        'borg_stopped': 'stalled', 'blocked': 'stalled'}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(spec, source, out):
    """Build a borg-rs checkout (at spec['ref']) and keep the game dir."""
    source = Path(source).resolve()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip()
    if head != spec['ref']:
        raise ValueError(f"borg-rs checkout is at {head}, specimen wants {spec['ref']}")
    impl = spec['impl']
    env = os.environ.copy()
    env['BORG_IMPL'] = impl
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    with (out / 'build.log').open('w') as log:
        subprocess.run(['harness/build.sh'], cwd=source, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    game = source / 'build' / impl / 'game'
    if (out / 'game').exists():
        shutil.rmtree(out / 'game')
    shutil.copytree(game, out / 'game', symlinks=False)
    shutil.copy(source / 'harness/borg.txt', out / 'borg.txt')
    build_id = dict(line.split('=', 1) for line in (source / 'build' / impl / 'BUILD_ID').read_text().splitlines()
                    if '=' in line)
    manifest = {'kind': 'borg-rs', 'impl': impl, 'source_commit': head,
                'binary_sha256': sha256(out / 'game/angband'),
                'build_id': build_id,
                'compiler': subprocess.check_output(['cc', '--version'], text=True).splitlines()[0],
                'rustc': build_id.get('rustc'),
                'platform': f'{platform.system()} {platform.machine()}', 'complete': True}
    if build_id.get('binary_sha256') != manifest['binary_sha256']:
        raise ValueError('copied binary does not match BUILD_ID')
    (out / 'build.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    return manifest


def config_text(build_dir, profile, race=0, cls=0):
    base = (Path(build_dir) / 'borg.txt').read_text()
    text = cat_mod._override(base, 'borg_respawn_race', str(race))
    text = cat_mod._override(text, 'borg_respawn_class', str(cls))
    text = cat_mod._override(text, 'borg_cheat_death', 'FALSE')
    text = cat_mod._override(text, 'borg_respawn_winners', 'FALSE')
    for name, value in sorted(profile['settings'].items()):
        text = cat_mod._override(text, name, cat_mod.setting_value(value))
    return text


def check_config(text, profile):
    wrong = []
    for name, value in profile['settings'].items():
        if f'\n{name} = {cat_mod.setting_value(value)}\n' not in '\n' + text:
            wrong.append(name)
    return ('settings not written: ' + ', '.join(sorted(wrong))) if wrong else None


def run_cell(cell, build_dir, work, cat):
    applied, profile = cat_mod.resolve_profile(cat, cell)
    suite = cat['suites'][cell['suite']]
    spec = cat['specimens']['specimens'][cell['specimen']]
    build_dir = Path(build_dir).resolve()
    manifest = json.loads((build_dir / 'build.json').read_text())
    if manifest['source_commit'] != spec['ref'] or manifest['impl'] != spec['impl']:
        raise ValueError(f'build {build_dir} does not match specimen {cell["specimen"]}')
    out = Path(work).resolve() / cat_mod.cell_key(cell)
    if out.exists():
        shutil.rmtree(out)
    for d in ('user', 'save', 'archive', 'panic', 'scores'):
        (out / d).mkdir(parents=True)
    race, cls = cat_mod.character(suite, cell['seed']) or ('Human', 'Warrior')
    race_i, cls_i = cat_mod.RACES.index(race), cat_mod.CLASSES.index(cls)
    text = config_text(build_dir, profile, race_i, cls_i)
    (out / 'user/borg.txt').write_text(text)
    mismatch = check_config(text, profile)
    game = build_dir / 'game'
    command = [str(game / 'angband'), '-mborgh', '-n', '-uBorg'] + \
        [f'-d{d}={out / d}' for d in ('user', 'save', 'archive', 'panic', 'scores')] + \
        ['--', '-seed', str(cell['seed']), '-race', str(race_i), '-class', str(cls_i), '-turns', str(suite['cap']),
         '-keylog', str(out / 'keys.log'), '-summary', str(out / 'summary.json'), '-menu-letters']
    env = dict(os.environ, TZ='UTC', LANG='C.UTF-8', LC_ALL='C.UTF-8')
    start = time.monotonic()
    outcome, error, rc = None, None, None
    try:
        with (out / 'stderr.log').open('w') as err:
            rc = subprocess.run(command, cwd=game, env=env, stdout=subprocess.DEVNULL, stderr=err,
                                timeout=suite['wall_seconds']).returncode
    except subprocess.TimeoutExpired:
        outcome, error = 'wall_timeout', f"no stop within {suite['wall_seconds']} s"
    wall = time.monotonic() - start
    summary = {}
    if (out / 'summary.json').exists():
        try:
            summary = json.loads((out / 'summary.json').read_text())
        except ValueError as exc:
            error = f'unreadable summary: {exc}'
    if outcome is None:
        if rc not in (0, None) and not summary:
            outcome, error = ('crash' if rc < 0 else 'harness_failure'), f'exit code {rc}'
        elif not summary:
            outcome, error = 'harness_failure', error or 'no summary.json'
        else:
            outcome = 'death' if summary.get('dead') else STOP.get(summary.get('stop_reason'), 'harness_failure')
            if outcome == 'stalled':
                error = f"borgh stop_reason {summary.get('stop_reason')}"
    if summary and (summary.get('race'), summary.get('class')) != (race, cls):
        mismatch = (mismatch + '; ' if mismatch else '') + \
            f"character {summary.get('race')} {summary.get('class')}, expected {race} {cls}"
    if mismatch and outcome in ('death', 'turn_cap', 'completion'):
        outcome = 'config_error'
    keys = out / 'keys.log'
    keys_sha = sha256(keys) if keys.exists() else None
    stall_info = None
    if outcome not in ('death', 'turn_cap', 'completion'):
        stall_info = stall.borgh(keys.read_text(errors='replace') if keys.exists() else '', summary)
    record = {
        'schema': 'borg-zoo/cell@1', **cell, 'harness_kind': 'borg-rs', 'profile_applied': applied,
        'specimen_ref': spec['ref'], 'impl': spec['impl'],
        'profile_sha256': cat_mod.profile_sha256(profile),
        'config_sha256': hashlib.sha256(text.encode()).hexdigest(),
        'cap': suite['cap'], 'birth': suite['birth'],
        'outcome': outcome, 'runner_outcome': summary.get('stop_reason'),
        'config_error': mismatch, 'config_checked': 'written file (borgh reports no effective settings)',
        'cause': summary.get('death_cause') or ('(alive and well)' if summary and not summary.get('dead') else None),
        'character': ' '.join(x for x in (summary.get('race'), summary.get('class')) if x) or None,
        'played_race': summary.get('race'), 'played_class': summary.get('class'),
        'final': {'kind': summary.get('stop_reason'), 'turn': summary.get('game_turns'),
                  'depth': summary.get('depth'), 'max_depth': summary.get('max_depth'),
                  'level': summary.get('clevel'), 'max_level': summary.get('clevel'),
                  'hp': None, 'decisions': None, 'keys': summary.get('keys')},
        'first_turn_at_depth': {},
        'wall_seconds': wall,
        'trace_sha256': keys_sha, 'play_sha256': keys_sha,
        'error': error,
        'stall': stall_info,
        'binary_sha256': manifest.get('binary_sha256'), 'compiler': manifest.get('compiler'),
        'rustc': manifest.get('rustc'), 'platform': manifest.get('platform'),
    }
    keys.unlink(missing_ok=True)
    return record
