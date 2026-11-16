"""Adapter over borg-rs's deterministic harness (the borgh frontend).

A borg-rs specimen is a borg-rs commit built with harness/build.sh, either
with the Rust Borg (impl "rust") or with the C Borg compiled in the same tree
(impl "c"). Runs mirror harness/run.sh: the run's user/borg.txt is the
checkout's harness/borg.txt with the profile's settings applied, and the
borgh frontend writes summary.json and keys.log.

Limits compared with the better-borg-c observer, recorded per cell:
- borgh prints no effective-settings line, so the settings are checked in
  the borg.txt the zoo writes, not in what the Borg parsed;
- borgh picks race and class from indices (with -menu-letters, in
  p_race.txt and class.txt order); fixed and assigned birth are supported,
  random birth is not.
- borgh stops after the first key at or past the turn cap ("boundary":
  "after-key" on the cell), unless the specimen declares "exact_turns":
  true, which passes -exact-turns and stops the run at the cap itself
  ("boundary": "exact"). Existing specimens keep "after-key": the flag is
  opt-in per specimen, not a change to how they already run.
- a specimen with "depth_stream": true additionally passes -statelog, and
  the cell's first_turn_at_depth and milestones (level, max depth, gold on
  hand at turn fractions of the cap) come from it; without the flag there
  is no per-turn state stream, so neither is available. The log carries no
  item values, only gear hashes, so it gives gold on hand, not a full net
  worth (inventory and equipment value).
- a specimen with "plans": {NAME: sha256} ships those errands plans
  (borg-reborn-rs harness/plans/NAME, borg-zoo#123). The build copies each
  one, checked against its pinned hash, into the build's plans/; a profile
  setting borg_plan = NAME gets it as the cell's user/NAME, next to the
  borg.txt that names it, and the cell records the plan's sha256. Such a
  binary exits with status 2 instead of ignoring a missing or invalid plan,
  so exit 2 without a summary is a config_error, and its borg_stopped (the
  level-50 handover or a plan's handback) is the borg_stopped outcome, not
  a stall.
"""
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import time
from pathlib import Path

from . import catalogue as cat_mod
from . import stall

# borgh writes `clevel` for a level stop; older builds wrote `clev` (borg-zoo#48).
STOP = {'turns': 'turn_cap', 'death': 'death', 'clevel': 'turn_cap', 'clev': 'turn_cap',
        'depth': 'turn_cap', 'borg_stopped': 'stalled', 'blocked': 'stalled'}

# Depth marks to report first_turn_at_depth for, matching harness.py's (the
# better-borg-c observer adapter) so the two are comparable.
DEPTH_MARKS = (1, 2, 3, 4, 5, 6, 8, 10, 15, 20)

# borgh -statelog line: "<turn> <x>,<y> d<depth>/<max depth> hp../.. sp../..
# f.. au<gold> xp<xp> lv<level> t...| o...| p... e... r...". A line with no
# player state yet (before birth) is "<turn> -" and is skipped.
STATE_LINE = re.compile(
    r'^(?P<turn>\d+) \S+ d(?P<depth>\d+)/(?P<max_depth>\d+) hp\S+ sp\S+ f\S+ '
    r'au(?P<gold>-?\d+) xp(?P<xp>\d+) lv(?P<level>\d+)\b')


def parse_state_log(text):
    """The per-key states a -statelog file records, as a list of dicts."""
    out = []
    for line in text.splitlines():
        m = STATE_LINE.match(line)
        if m:
            out.append({k: int(v) for k, v in m.groupdict().items()})
    return out


def first_turns_at_depth(states, marks=DEPTH_MARKS):
    out = {}
    for s in states:
        for m in marks:
            if s['max_depth'] >= m and str(m) not in out:
                out[str(m)] = s['turn']
    return out


def milestones(states, cap, fractions=(0.25, 0.5, 0.75, 1.0)):
    """Level, max depth and gold on hand at turn fractions of the cap: the
    last state -statelog logged at or before that turn. Not a net worth:
    the state log hashes gear, it does not value it."""
    rows = []
    for f in fractions:
        t = int(cap * f)
        at_or_before = [s for s in states if s['turn'] <= t]
        last = at_or_before[-1] if at_or_before else None
        rows.append({'turn': t, 'level': last['level'] if last else None,
                     'max_depth': last['max_depth'] if last else None,
                     'gold': last['gold'] if last else None})
    return rows


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# Environment overrides the native core prefers to the run's borg.txt
# (borg-reborn-rs docs/ZOO-INTERFACE.md); a cell measures its file only.
# BORG_RUN_DIR also turns on core traces.
AMBIENT = ('BORG_RUN_DIR', 'BORG_CORE', 'BORG_ERRAND', 'BORG_ERRAND_BUDGET', 'BORG_PROFILE', 'BORG_PLAN')


def plan_name(name):
    """A borg_plan value the adapter can ship: a bare file name."""
    if (not isinstance(name, str) or not name or Path(name).name != name or name.startswith('.')
            or name == 'borg.txt'):
        raise ValueError(f'borg_plan must be a bare file name, not {name!r}')
    return name


def copy_plans(spec, source, out):
    """Copy the specimen's pinned plans into the build; {name: sha256}."""
    plans = {}
    for name, digest in sorted((spec.get('plans') or {}).items()):
        src = Path(source) / 'harness/plans' / plan_name(name)
        if not src.is_file():
            raise ValueError(f'specimen plan {name} is not in harness/plans at {spec["ref"]}')
        if sha256(src) != digest:
            raise ValueError(f'specimen plan {name} has sha256 {sha256(src)}, catalogue pins {digest}')
        (out / 'plans').mkdir(exist_ok=True)
        shutil.copy(src, out / 'plans' / name)
        plans[name] = digest
    return plans


def ship_plan(spec, manifest, build_dir, out, name):
    """Write the build's plan NAME as the cell's user/NAME; its sha256."""
    name = plan_name(name)
    digest = (spec.get('plans') or {}).get(name)
    if digest is None:
        raise ValueError(f'specimen ships no plan {name}')
    src = Path(build_dir) / 'plans' / name
    if (manifest.get('plans') or {}).get(name) != digest or not src.is_file() or sha256(src) != digest:
        raise ValueError(f'build {build_dir} does not carry plan {name} at sha256 {digest}')
    shutil.copy(src, out / 'user' / name)
    return digest


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
    if (out / 'plans').exists():
        shutil.rmtree(out / 'plans')
    plans = copy_plans(spec, source, out)
    build_id = dict(line.split('=', 1) for line in (source / 'build' / impl / 'BUILD_ID').read_text().splitlines()
                    if '=' in line)
    manifest = {'kind': 'borg-rs', 'impl': impl, 'source_commit': head,
                'binary_sha256': sha256(out / 'game/angband'),
                'build_id': build_id,
                'compiler': subprocess.check_output(['cc', '--version'], text=True).splitlines()[0],
                'rustc': build_id.get('rustc'),
                'platform': f'{platform.system()} {platform.machine()}', 'complete': True}
    if plans:
        manifest['plans'] = plans
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


def check_effective(summary, profile):
    """For opted-in modern specimens, verify what the Borg actually used."""
    actual = summary.get('effective_settings')
    if not isinstance(actual, dict):
        return 'native summary has no effective_settings'
    wrong = [name for name, value in profile['settings'].items()
             if name not in actual or actual[name] != value]
    return ('settings not effective: ' + ', '.join(sorted(wrong))) if wrong else None


def command(game_bin, out, cell, race_i, cls_i, suite, spec, keep=False):
    argv = [str(game_bin), '-mborgh', '-n', '-uBorg'] + \
        [f'-d{d}={out / d}' for d in ('user', 'save', 'archive', 'panic', 'scores')] + \
        ['--', '-seed', str(cell['seed']), '-race', str(race_i), '-class', str(cls_i), '-turns', str(suite['cap']),
         '-keylog', str(out / 'keys.log'), '-summary', str(out / 'summary.json'), '-menu-letters']
    if spec.get('exact_turns'):
        argv.append('-exact-turns')
    if spec.get('depth_stream') or keep:
        argv += ['-statelog', str(out / 'state.log')]
    if keep:
        argv += ['-msglog', str(out / 'messages.log')]
    return argv


def run_cell(cell, build_dir, work, cat, keep=False):
    applied, profile = cat_mod.resolve_profile(cat, cell)
    suite = cat['suites'][cell['suite']]
    spec = cat['specimens']['specimens'][cell['specimen']]
    keep = keep or bool(spec.get('town_shadow_records'))
    build_dir = Path(build_dir).resolve()
    manifest = json.loads((build_dir / 'build.json').read_text())
    if manifest['source_commit'] != spec['ref'] or manifest['impl'] != spec['impl']:
        raise ValueError(f'build {build_dir} does not match specimen {cell["specimen"]}')
    out = Path(work).resolve() / cat_mod.cell_key(cell)
    if out.exists():
        if keep:
            raise ValueError(f'refusing to overwrite retained attempt: {out}')
        shutil.rmtree(out)
    for d in ('user', 'save', 'archive', 'panic', 'scores'):
        (out / d).mkdir(parents=True)
    race, cls = cat_mod.character(suite, cell['seed']) or ('Human', 'Warrior')
    race_i, cls_i = cat_mod.RACES.index(race), cat_mod.CLASSES.index(cls)
    text = config_text(build_dir, profile, race_i, cls_i)
    (out / 'user/borg.txt').write_text(text)
    mismatch = check_config(text, profile)
    plan = profile['settings'].get('borg_plan')
    plan_sha = ship_plan(spec, manifest, build_dir, out, plan) if plan is not None else None
    game = build_dir / 'game'
    argv = command(game / 'angband', out, cell, race_i, cls_i, suite, spec, keep=keep)
    env = dict(os.environ, TZ='UTC', LANG='C.UTF-8', LC_ALL='C.UTF-8')
    for name in [n for n in env if n in AMBIENT or n.startswith('BORG_PARAM_')]:
        del env[name]
    # Never let parallel cells write to an inherited process-global path.
    for name in ('BORG_TOWN_PLAN_RECORD', 'BORG_TRIP_RECORD'):
        env.pop(name, None)
    if keep:
        streams = {}
        for setting, name, filename in (
                ('borg_town_plan', 'BORG_TOWN_PLAN_RECORD', 'town-plan.jsonl'),
                ('borg_trip_policy', 'BORG_TRIP_RECORD', 'trip.jsonl')):
            if profile['settings'].get(setting) == 1 or (setting == 'borg_town_plan' and spec.get('town_shadow_records')):
                env[name] = str(out / filename)
                (out / filename).touch()  # Empty means no recorded consultation.
                streams[name] = filename
        (out / 'town-recording.json').write_text(json.dumps({
            'schema': 'borg-zoo/town-recording@1', 'argv': argv,
            'source_commit': spec['ref'], 'profile_applied': applied,
            'config_sha256': hashlib.sha256(text.encode()).hexdigest(),
            'streams': streams,
        }, indent=2) + '\n')
    start = time.monotonic()
    outcome, error, rc = None, None, None
    try:
        with (out / 'stderr.log').open('w') as err:
            rc = subprocess.run(argv, cwd=game, env=env, stdout=subprocess.DEVNULL, stderr=err,
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
        if rc == 2 and not summary and spec.get('plans'):
            # The binary refused its configuration (a plan it could not load,
            # a conflicting errand, an invalid setting) before playing.
            outcome, error = 'config_error', 'exit code 2: the binary rejected its configuration'
            mismatch = (mismatch + '; ' if mismatch else '') + error
        elif rc not in (0, None) and not summary:
            outcome, error = ('crash' if rc < 0 else 'harness_failure'), f'exit code {rc}'
        elif not summary:
            outcome, error = 'harness_failure', error or 'no summary.json'
        else:
            outcome = 'death' if summary.get('dead') else STOP.get(summary.get('stop_reason'), 'harness_failure')
            if summary.get('stop_reason') == 'borg_stopped' and spec.get('plans') and not summary.get('dead'):
                outcome = 'borg_stopped'
            elif outcome == 'stalled':
                error = f"borgh stop_reason {summary.get('stop_reason')}"
    if summary and (summary.get('race'), summary.get('class')) != (race, cls):
        mismatch = (mismatch + '; ' if mismatch else '') + \
            f"character {summary.get('race')} {summary.get('class')}, expected {race} {cls}"
    if summary and spec.get('verify_effective_settings'):
        effective_error = check_effective(summary, profile)
        if effective_error:
            mismatch = (mismatch + '; ' if mismatch else '') + effective_error
    shadow = None
    if spec.get('town_shadow_records'):
        from . import town_shadow
        shadow = town_shadow.collect(out / 'town-plan.jsonl', summary.get('effective_settings'))
        if shadow.get('error'):
            mismatch = (mismatch + '; ' if mismatch else '') + shadow['error']
    observed_outcome = outcome
    if mismatch and (spec.get('town_shadow_records') or outcome in ('death', 'turn_cap', 'completion', 'borg_stopped')):
        outcome = 'config_error'
    keys = out / 'keys.log'
    keys_sha = sha256(keys) if keys.exists() else None
    stall_info = None
    if outcome not in ('death', 'turn_cap', 'completion'):
        stall_info = stall.borgh(keys.read_text(errors='replace') if keys.exists() else '', summary)
    state_log = out / 'state.log'
    states = parse_state_log(state_log.read_text(errors='replace')) if state_log.exists() else []
    native_settings = summary.get('effective_settings')
    native_settings = native_settings if isinstance(native_settings, dict) else {}
    record = {
        'schema': 'borg-zoo/cell@1', **cell, 'harness_kind': 'borg-rs', 'profile_applied': applied,
        'specimen_ref': spec['ref'], 'impl': spec['impl'],
        'profile_sha256': cat_mod.profile_sha256(profile),
        'config_sha256': hashlib.sha256(text.encode()).hexdigest(),
        'plan': {'name': plan, 'sha256': plan_sha} if plan is not None else None,
        'cap': suite['cap'], 'birth': suite['birth'],
        'boundary': 'exact' if spec.get('exact_turns') else 'after-key',
        'outcome': outcome, 'runner_outcome': summary.get('stop_reason'),
        'config_error': mismatch,
        'config_checked': 'native effective_settings and written file' if spec.get('verify_effective_settings') else 'written file (effective settings not required for this specimen)',
        'native_reported_settings': native_settings or None,
        'effective_settings': {name: native_settings.get(name)
                               for name in profile['settings']} if spec.get('verify_effective_settings') else None,
        'cause': summary.get('death_cause') or ('(alive and well)' if summary and not summary.get('dead') else None),
        'character': ' '.join(x for x in (summary.get('race'), summary.get('class')) if x) or None,
        'played_race': summary.get('race'), 'played_class': summary.get('class'),
        'final': {'kind': summary.get('stop_reason'), 'turn': summary.get('game_turns'),
                  'depth': summary.get('depth'), 'max_depth': summary.get('max_depth'),
                  'level': summary.get('clevel'), 'max_level': summary.get('clevel'),
                  'hp': None, 'decisions': None, 'keys': summary.get('keys')},
        'first_turn_at_depth': first_turns_at_depth(states) if states else {},
        'milestones': milestones(states, suite['cap']) if states else None,
        'wall_seconds': wall,
        'trace_sha256': keys_sha, 'play_sha256': keys_sha,
        'error': error,
        'stall': stall_info,
        'binary_sha256': manifest.get('binary_sha256'), 'compiler': manifest.get('compiler'),
        'rustc': manifest.get('rustc'), 'platform': manifest.get('platform'),
    }
    if shadow is not None:
        record['town_shadow'] = shadow
        record['observed_outcome'] = observed_outcome
        (out / 'town-shadow-summary.json').write_text(json.dumps(shadow, indent=2) + '\n')
    # Death evidence: a natural death's keys are kept (not the stop-reason
    # stall path above, which already read them) so the measured repository
    # can verify them against play_sha256; every other outcome's keys are
    # discarded as before.
    if keep:
        from . import town, returns
        record['town_activity'] = town.collect(out)
        record['return_activity'] = returns.collect(out)
    if not keep and outcome != 'death':
        keys.unlink(missing_ok=True)
    if not keep:
        state_log.unlink(missing_ok=True)
    return record
