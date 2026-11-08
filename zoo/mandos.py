"""Adapter over Mandos's headless measurement entry point (tools/zoo-run.mjs).

A Mandos specimen is a diegoami/mandos commit that has the entry point
(docs/ZOO-HARNESS.md, record schema mandos/zoo-run@1). It plays the Neo
Angband engine from the pinned npm packages, not the C game: a Mandos seed is
a different game from a C seed, so Mandos runs are never paired with C or
borg-rs runs (stats pairs only within one harness kind).

Build: `pnpm install --frozen-lockfile` and `node tools/zoo-build.mjs` in an
exact checkout, once per specimen; the bundle is kept. Run: the same exact
checkout, installed the same way, plays one character per process with that
bundle. zoo-run checks that source, bundle and content match before play.

Counters and caps, as Mandos defines them:
- `turn` is Core game ticks from birth, ten per normal-speed action;
- the turn cap stops at the first Core loop boundary at or after the cap, so
  a run can overshoot it (one rest can run a thousand ticks). The record keeps
  the requested and actual ticks. A death after the requested cap means the
  character was alive at the cap, so the zoo counts it as a turn-cap run and
  keeps the death in `died_after_cap`;
- `decisions` counts issued commands, `loopCalls` Core loop calls (what the
  safety cap bounds), `attempts` armed replies.
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

# borg.txt setting -> Mandos controller flag. Only these nine are controller
# settings in Mandos; any other profile setting cannot be applied.
FLAGS = {
    'borg_plays_risky': 'borg.playsRisky',
    'borg_worships_damage': 'borg.worshipsDamage',
    'borg_worships_speed': 'borg.worshipsSpeed',
    'borg_worships_hp': 'borg.worshipsHp',
    'borg_worships_mana': 'borg.worshipsMana',
    'borg_worships_ac': 'borg.worshipsAc',
    'borg_worships_gold': 'borg.worshipsGold',
    'borg_self_scum': 'borg.selfScum',
    'borg_munchkin_start': 'borg.munchkinStart',
}
# Mandos outcome -> zoo outcome. borg_stopped and decision_cap are kept as
# their own outcomes: neither is a death, and neither reached the endpoint.
OUTCOME = {'death': 'death', 'turn_cap': 'turn_cap', 'stalled': 'stalled',
           'borg_stopped': 'borg_stopped', 'decision_cap': 'decision_cap',
           'harness_failure': 'harness_failure'}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def unsupported_settings(profile):
    """Profile settings Mandos cannot apply (a list; empty when all apply)."""
    bad = [name for name, value in profile['settings'].items()
           if name not in FLAGS or not isinstance(value, bool)]
    if profile.get('base') == 'shipped':
        bad.append('base: shipped')
    return sorted(bad)


def flags(profile):
    return {FLAGS[name]: value for name, value in sorted(profile['settings'].items())}


def install(source):
    env = dict(os.environ, COREPACK_ENABLE_DOWNLOAD_PROMPT='0', CI='1')
    pnpm = ['pnpm'] if shutil.which('pnpm') else ['corepack', 'pnpm']
    subprocess.run(pnpm + ['install', '--frozen-lockfile'], cwd=source, env=env, check=True,
                   stdout=subprocess.DEVNULL)


def check_checkout(source, ref):
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip()
    if head != ref:
        raise ValueError(f'Mandos checkout is at {head}, specimen wants {ref}')


def build(spec, source, out):
    source = Path(source).resolve()
    check_checkout(source, spec['ref'])
    out = Path(out).resolve()
    if (out / 'bundle').exists():
        shutil.rmtree(out / 'bundle')
    out.mkdir(parents=True, exist_ok=True)
    install(source)
    printed = subprocess.check_output(['node', 'tools/zoo-build.mjs', '--out', str(out / 'bundle')],
                                      cwd=source, text=True)
    built = json.loads(printed.strip().splitlines()[-1])
    node = subprocess.check_output(['node', '--version'], text=True).strip()
    manifest = {'kind': 'mandos', 'source_commit': spec['ref'],
                'binary_sha256': built['bundleSha256'], 'bundle_sha256': built['bundleSha256'],
                'source_sha256': built['sourceSha256'], 'compiler': f'node {node}',
                'platform': f'{platform.system()} {platform.machine()}', 'complete': True}
    (out / 'build.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    return manifest


def command(source, bundle, cell, race, cls, cap, out, settings_file=None):
    cmd = ['node', str(Path(source) / 'tools/zoo-run.mjs'), '--bundle', str(bundle),
           '--seed', str(cell['seed']), '--turns', str(cap), '--race', race, '--class', cls,
           '--out', str(out / 'run.json'), '--states', str(out / 'states.jsonl'),
           '--commands', str(out / 'commands.jsonl')]
    if settings_file:
        cmd += ['--settings', str(settings_file)]
    return cmd


def read_states(path):
    states = []
    if path.exists():
        for line in path.read_text(errors='replace').splitlines():
            try:
                states.append(json.loads(line))
            except ValueError:
                break  # a truncated last line after an interrupted run
    return states


def stall_info(record, states, outcome):
    last = states[-1] if states else {}
    frozen = last.get('turn')
    at_frozen = [s for s in states if s.get('turn') == frozen]
    first = at_frozen[0] if at_frozen else {}
    depths = [s.get('depth') for s in at_frozen]
    watch = (record or {}).get('stall') or {}
    return {
        'source': 'mandos',
        'kind': watch.get('kind') or {'borg_stopped': 'borg_stopped', 'decision_cap': 'decision_cap'}.get(
            outcome, 'no_record' if not record else 'unclassified'),
        'stop_reason': (record or {}).get('stopped'),
        'watch': watch or None,
        'last_turn': frozen,
        'decisions_delta': (last.get('decisions') or 0) - (first.get('decisions') or 0) if states else None,
        'energy_delta': (last.get('energy') or 0) - (first.get('energy') or 0) if states else None,
        'depth_changes': sum(1 for a, b in zip(depths, depths[1:]) if a != b),
        'top_notes_at_last_turn': ([[f"{watch.get('kind')}: {json.dumps(watch.get('command'), sort_keys=True)[:80]}",
                                     1]] if watch else []),
        'position': None,
        'position_note': 'the Mandos record has no player position',
    }


def summarise(cell, spec, profile, suite, record, states, requested, error, wall):
    """One zoo cell from a Mandos run record (or its absence)."""
    race, cls = requested
    cap = suite['cap']
    if record is None:
        outcome = 'harness_failure'
    elif record.get('schema') != 'mandos/zoo-run@1':
        outcome, error = 'harness_failure', f"unexpected schema {record.get('schema')!r}"
    else:
        outcome = OUTCOME.get(record.get('outcome'), 'harness_failure')
        if outcome == 'harness_failure' and not error:
            error = json.dumps(record.get('error') or record.get('outcome'))[:500]
    record = record or {}
    died_after_cap = None
    if outcome == 'death' and (record.get('turn') or 0) > cap:
        died_after_cap = {'turn': record.get('turn'), 'cause': record.get('causeOfDeath')}
        outcome = 'turn_cap'
    mismatch = []
    birth = record.get('birth') or {}
    if record and (birth.get('race'), birth.get('class')) != (race, cls):
        mismatch.append(f"character {birth.get('race')} {birth.get('class')}, expected {race} {cls}")
    effective = record.get('settings') or {}
    for name, value in flags(profile).items():
        if record and effective.get(name) is not value:
            mismatch.append(f'{name} is {effective.get(name)!r}, profile wants {value!r}')
    config_error = '; '.join(mismatch) or None
    if config_error and outcome in ('death', 'turn_cap'):
        outcome = 'config_error'
    first = {str(k): v for k, v in (record.get('firstDepthTurns') or {}).items()}
    turn_cap = record.get('turnCap') or {}
    return {
        'schema': 'borg-zoo/cell@1', **cell, 'harness_kind': 'mandos',
        'specimen_ref': spec['ref'], 'engine': spec.get('engine'),
        'profile_sha256': cat_mod.profile_sha256(profile),
        'config_sha256': hashlib.sha256(json.dumps(flags(profile), sort_keys=True).encode()).hexdigest(),
        'cap': cap, 'birth': suite['birth'],
        'outcome': outcome, 'runner_outcome': record.get('outcome'),
        'config_error': config_error,
        'config_checked': 'effective controller settings in the Mandos record' if record else None,
        'cause': record.get('causeOfDeath') if outcome == 'death' else (
            '(alive and well)' if outcome == 'turn_cap' else None),
        'died_after_cap': died_after_cap,
        'character': f"{birth.get('race')} {birth.get('class')}" if birth else None,
        'played_race': birth.get('race'), 'played_class': birth.get('class'),
        'birth_record': birth or None,
        'settings_effective': effective or None,
        'cfg': record.get('cfg'),
        'final': {'kind': record.get('outcome'), 'turn': record.get('turn'),
                  'depth': record.get('depth'), 'max_depth': record.get('maxDepth'),
                  'level': record.get('level'), 'max_level': record.get('maxLevel'),
                  'hp': record.get('hp'), 'max_hp': record.get('maxHp'), 'energy': record.get('energy'),
                  'decisions': record.get('decisions'), 'attempts': record.get('attempts'),
                  'loop_calls': record.get('loopCalls'), 'no_command_replies': record.get('noCommandReplies')},
        'turn_cap': {'requested': turn_cap.get('requested', cap), 'actual': turn_cap.get('actual'),
                     'overshoot': turn_cap.get('overshoot'), 'exact': turn_cap.get('exact'),
                     'unit': turn_cap.get('unit', 'core_game_tick')},
        'first_turn_at_depth': first,
        'commands_census': record.get('commands'),
        'wall_seconds': wall,
        'mandos_wall_ms': (record.get('metadata') or {}).get('wallTimeMs'),
        'trace_sha256': record.get('playSha256'), 'play_sha256': record.get('playSha256'),
        'error': error,
        'stall': stall_info(record, states, outcome) if outcome not in ('death', 'turn_cap', 'completion') else None,
        'provenance': record.get('provenance'),
        'binary_sha256': (record.get('provenance') or {}).get('bundleSha256'),
        'compiler': ('node ' + ((record.get('provenance') or {}).get('runtime') or {}).get('node', '?')),
        'platform': platform.platform(),
    }


def run_cell(cell, build_dir, work, cat, source):
    applied, profile = cat_mod.resolve_profile(cat, cell)
    suite = cat['suites'][cell['suite']]
    spec = cat['specimens']['specimens'][cell['specimen']]
    if source is None:
        raise ValueError('a Mandos run needs --source: the installed Mandos checkout at the specimen ref')
    build_dir, source = Path(build_dir).resolve(), Path(source).resolve()
    manifest = json.loads((build_dir / 'build.json').read_text())
    if manifest['source_commit'] != spec['ref']:
        raise ValueError(f'build {build_dir} does not match specimen {cell["specimen"]}')
    bad = unsupported_settings(profile)
    if bad:
        raise ValueError(f'profile {cell["profile"]} has settings Mandos cannot apply: {", ".join(bad)}')
    out = Path(work).resolve() / cat_mod.cell_key(cell)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    race, cls = cat_mod.character(suite, cell['seed']) or ('Human', 'Warrior')
    settings_file = None
    if profile['settings']:
        settings_file = out / 'settings.json'
        settings_file.write_text(json.dumps(flags(profile), sort_keys=True))
    run_dir = out / 'run'  # zoo-run creates it; its outputs must not exist yet
    cmd = command(source, build_dir / 'bundle', cell, race, cls, suite['cap'], run_dir, settings_file)
    wall_limit = suite['wall_seconds'] * spec.get('wall_factor', 1)
    start = time.monotonic()
    error, rc = None, None
    try:
        with (out / 'stderr.log').open('w') as err:
            rc = subprocess.run(cmd, cwd=source, stdout=subprocess.DEVNULL, stderr=err,
                                timeout=wall_limit).returncode
    except subprocess.TimeoutExpired:
        error = f'no stop within {wall_limit} s'
    wall = time.monotonic() - start
    record = None
    if (run_dir / 'run.json').exists():
        try:
            record = json.loads((run_dir / 'run.json').read_text())
        except ValueError as exc:
            error = error or f'unreadable run.json: {exc}'
    elif error is None:
        tail = (out / 'stderr.log').read_text(errors='replace')[-400:]
        error = f'no run.json (exit code {rc}): {tail}'
    states = read_states(run_dir / 'states.jsonl')
    cell_record = summarise(cell, spec, profile, suite, record, states, (race, cls), error, wall)
    cell_record['profile_applied'] = applied
    if error and error.startswith('no stop within'):
        cell_record['outcome'] = 'wall_timeout'
        cell_record['stall'] = stall_info(record, states, 'wall_timeout')
    elif rc not in (0, None) and record and record.get('outcome') != 'harness_failure':
        cell_record['outcome'], cell_record['error'] = 'harness_failure', f'exit code {rc} with a non-failure record'
    if cell_record['play_sha256'] and (run_dir / 'commands.jsonl').exists():
        if sha256(run_dir / 'commands.jsonl') != cell_record['play_sha256']:
            cell_record['outcome'] = 'harness_failure'
            cell_record['error'] = 'commands.jsonl does not hash to playSha256'
    if cell_record['outcome'] in ('death', 'turn_cap'):
        # The hash is kept; the stream itself is kept (and uploaded by the
        # workflow) only for runs that did not reach an endpoint.
        (run_dir / 'commands.jsonl').unlink(missing_ok=True)
    return cell_record
