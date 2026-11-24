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
  a stall. The cell also checks the core's copy of the loaded plan in the
  output directory, and records a frozen-turn loop (borg-rs#90) as a stall.
- a specimen with "scary_lists": {NAME: sha256} ships those named scary
  monster lists (borg-reborn-rs harness/NAME, #518, borg-zoo#228) the same
  way: the build copies each, hash-checked, into the build's scary_lists/;
  a profile setting borg_scary_list = NAME gets it as the cell's user/NAME
  and the cell records {name, sha256}. A missing or invalid list stops the
  binary with exit 2 before play, a config_error.
- a specimen with "worlds": {NAME: sha256} ships those world configs
  (borg-reborn-rs harness/worlds/NAME.txt, #704, borg-zoo#482): the build
  copies each, hash-checked, with scripts/make-world.py into the build. A
  profile setting borg_world = NAME gets, per cell, the game data that tool
  makes from the build's lib/ in the cell's world/, passed with -dgamedata,
  -dpref, -dhelp and -dscreens as harness/run.sh does. The borg_world line
  never reaches the Borg; the cell records {name, sha256, data_sha256}, and
  world/ is removed after play (the pinned config and tool remake it).
- a specimen with "loop_checks": true (and every plan specimen) gets the
  frozen-turn stall and the key-outlier flag without carrying plans.
- every inherited BORG_* environment variable is cleared before a cell.
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
from . import settings_receipt, stall

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
    r'^(?P<turn>\d+) \S+ d(?P<depth>\d+)/(?P<max_depth>\d+) hp(?P<hp>-?\d+)/(?P<max_hp>\d+) sp\S+ f\S+ '
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


# Character levels to report first_turn_at_level for: every level to 20 (borg-zoo#718).
LEVEL_MARKS = tuple(range(2, 21))
# Max HP marks for first_turn_at_max_hp (borg-zoo#718; borg-reborn-rs#1061's 25 HP stair-scum threshold).
MAX_HP_MARKS = (15, 20, 25, 30, 40, 60)


def first_turns_at_level(states, marks=LEVEL_MARKS):
    """The first game turn with character level at or above each mark."""
    out = {}
    for s in states:
        for m in marks:
            if s['level'] >= m and str(m) not in out:
                out[str(m)] = s['turn']
    return out


def first_turns_at_max_hp(states, marks=MAX_HP_MARKS):
    """The first game turn with max HP at or above each mark."""
    out = {}
    for s in states:
        for m in marks:
            if s['max_hp'] >= m and str(m) not in out:
                out[str(m)] = s['turn']
    return out


def turns_at_level_depth(states, end_turn=None):
    """Game turns spent at each (character level, current depth) pair, as
    {"<level>,<depth>": turns}: each interval between consecutive state lines
    is charged to the earlier line's pair, and the last line's pair is charged
    up to end_turn (the cell's final turn) when that is later. The exposure
    for a deaths-per-turn rate at a level and depth (borg-zoo#718); a death's
    own (level, depth) is in the cell's final."""
    out = {}
    for i, s in enumerate(states):
        if i + 1 < len(states):
            nxt = states[i + 1]['turn']
        else:
            nxt = end_turn if end_turn is not None else s['turn']
        span = nxt - s['turn']
        if span > 0:
            key = f"{s['level']},{s['depth']}"
            out[key] = out.get(key, 0) + span
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


# The native core reads dozens of BORG_* environment variables and prefers
# them to the run's borg.txt (BORG_CORE, BORG_ERRAND, BORG_ERRANDS_PLAN,
# BORG_STOPSCARED, BORG_PARAM_*, ...; borg-reborn-rs docs/ZOO-INTERFACE.md);
# BORG_RUN_DIR also turns on core traces. A cell measures its files only, so
# every inherited BORG_* variable is cleared; the adapter sets its own record
# paths afterwards.
AMBIENT_PREFIX = 'BORG_'


# The core's copy of the plan it loaded, in the output directory (the parent
# of -summary when BORG_RUN_DIR is unset): the evidence a plan was in force,
# since its "# Plan:" notes are only written with -msglog.
LOADED_PLAN = 'errands_plan.txt'

# Keys at one game turn that mark a frozen-turn loop: borg-rs#90's oil
# store/take cycle at the Home spends 4,315-5,141 keys at single turns, while
# normal play, shops included, peaked at 383 in 54 shopping cells
# (borg-zoo#123). The loop ends and play resumes, so the cell reaches its
# cap; it is a stall all the same.
LOOP_KEYS = 1000

# A burst is shopping, not a loop, when gold falls at least once per this many
# keys at the burst turn (borg-zoo#205): shop transactions take no game time,
# so a Ranger buying 120 Arrows one at a time spent 1,083 keys at one turn
# with 120 gold drops (one per ~9 keys), while borg-rs#90's oil store/take
# cycle gains nothing and leaves gold unchanged.
PURCHASE_KEYS = 25


def loop_checks(spec):
    """Whether cells of this specimen get the frozen-turn and key-outlier
    checks: plan specimens always, others when they ask ("loop_checks":
    true, borg-zoo#129)."""
    return bool(spec.get('plans') or spec.get('loop_checks'))


def frozen_turn_loop(keys_text):
    """Keys per game turn in a borgh keys.log: the busiest turn, and how
    many turns reach LOOP_KEYS and with how many keys in all."""
    counts = {}
    for line in keys_text.splitlines():
        turn = line.split(' ', 1)[0]
        counts[turn] = counts.get(turn, 0) + 1
    if not counts:
        return {'turn': None, 'max_keys': 0, 'bursts': 0, 'burst_keys': 0}
    turn = max(counts, key=counts.get)
    bursts = [n for n in counts.values() if n >= LOOP_KEYS]
    out = {'turn': int(turn) if turn.isdigit() else turn, 'max_keys': counts[turn],
           'bursts': len(bursts), 'burst_keys': sum(bursts)}
    if bursts:
        out['burst_turns'] = [[int(t) if t.isdigit() else t, n] for t, n in counts.items() if n >= LOOP_KEYS]
    return out


def burst_purchases(state_text, turns):
    """{turn: times gold fell} over the -statelog lines of each burst turn."""
    wanted, drops, last = set(turns), {t: 0 for t in turns}, {}
    for s in parse_state_log(state_text):
        t = s['turn']
        if t in wanted:
            if t in last and s['gold'] < last[t]:
                drops[t] += 1
            last[t] = s['gold']
    return drops


def classify_bursts(loop, state_text):
    """(loop turns, purchase-burst turns) of a frozen_turn_loop result. Without
    a state log every burst counts as a loop, as before."""
    turns = loop.get('burst_turns') or []
    if state_text is None:
        return turns, []
    drops = burst_purchases(state_text, [t for t, _ in turns])
    shopping = [[t, n, drops[t]] for t, n in turns if drops[t] * PURCHASE_KEYS >= n]
    loops = [[t, n] for t, n in turns if drops[t] * PURCHASE_KEYS < n]
    return loops, shopping


# A cell with more keys than this many times its arm's median (over the
# arm's full-length, turn-cap cells) is flagged at collection. It catches a
# store/take cycle across visits, which costs game time and so escapes the
# per-turn check above; borg-rs#90's cell had 6.4 times its arm's median,
# normal shopping cells at most 1.7 times (borg-zoo#123). A flag, not an
# outcome: the cell is listed and the endpoints are reported with and
# without flagged cells.
KEY_OUTLIER_FACTOR = 3
KEY_OUTLIER_MIN_CELLS = 5


def flag_key_outliers(records):
    """Mark records whose final keys exceed KEY_OUTLIER_FACTOR times the
    median of their arm (suite, specimen, profile); the number flagged."""
    arms = {}
    for r in records:
        arms.setdefault((r.get('suite'), r.get('specimen'), r.get('profile')), []).append(r)
    flagged = 0
    for cells in arms.values():
        full = sorted(r['final']['keys'] for r in cells
                      if (r.get('observed_outcome') or r.get('outcome')) == 'turn_cap'
                      and isinstance((r.get('final') or {}).get('keys'), int))
        if len(full) < KEY_OUTLIER_MIN_CELLS:
            continue
        mid = len(full) // 2
        median = full[mid] if len(full) % 2 else (full[mid - 1] + full[mid]) / 2
        for r in cells:
            keys = (r.get('final') or {}).get('keys')
            if isinstance(keys, int) and median and keys > KEY_OUTLIER_FACTOR * median:
                r['key_outlier'] = {'keys': keys, 'arm_median': median, 'ratio': round(keys / median, 2)}
                flagged += 1
    return flagged


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


def copy_scary_lists(spec, source, out):
    """Copy the specimen's pinned scary lists (harness/NAME) into the build; {name: sha256}."""
    lists = {}
    for name, digest in sorted((spec.get('scary_lists') or {}).items()):
        src = Path(source) / 'harness' / plan_name(name)
        if not src.is_file():
            raise ValueError(f'specimen scary list {name} is not in harness/ at {spec["ref"]}')
        if sha256(src) != digest:
            raise ValueError(f'specimen scary list {name} has sha256 {sha256(src)}, catalogue pins {digest}')
        (out / 'scary_lists').mkdir(exist_ok=True)
        shutil.copy(src, out / 'scary_lists' / name)
        lists[name] = digest
    return lists


def ship_scary_list(spec, manifest, build_dir, out, name, lines=None):
    """Write the build's scary list NAME as the cell's user/NAME, with the arm's LINES
    appended (borg-zoo#228: the list is an overlay, a later line for a monster
    replaces an earlier one and `monster | none` removes it); the sha256 of the
    file written."""
    name = plan_name(name)
    digest = (spec.get('scary_lists') or {}).get(name)
    if digest is None:
        raise ValueError(f'specimen ships no scary list {name}')
    src = Path(build_dir) / 'scary_lists' / name
    if (manifest.get('scary_lists') or {}).get(name) != digest or not src.is_file() or sha256(src) != digest:
        raise ValueError(f'build {build_dir} does not carry scary list {name} at sha256 {digest}')
    data = src.read_bytes()
    if lines:
        data = data + (b'' if data.endswith(b'\n') or not data else b'\n') + \
            ''.join(f'{line}\n' for line in lines).encode()
    (out / 'user' / name).write_bytes(data)
    return hashlib.sha256(data).hexdigest()


SCARY_NONE = 'none'
SCARY_LINE = re.compile(r'^[ \t]*borg_scary_list[ \t]*=[ \t]*(\S*)[ \t]*$', re.M)


def scary_name(profile, borg_txt):
    """(the scary list a cell reads, where it came from): the profile's
    borg_scary_list, else the written borg.txt's own line (a specimen that
    ships the list on, borg-zoo#228); (None, None) for the compiled C list,
    which an arm asks for with borg_scary_list: none."""
    name = profile['settings'].get('borg_scary_list')
    source = 'profile'
    if name is None:
        m = SCARY_LINE.findall(borg_txt)
        name, source = (m[-1] if m else None), 'shipped borg.txt'
    if not name or name == SCARY_NONE:
        return None, None
    return name, source


def scary_lines(profile):
    """An arm's scary list lines, checked: strings, one line each."""
    lines = profile['settings'].get('borg_scary_list_lines')
    if lines is None:
        return None
    if not isinstance(lines, list) or not all(isinstance(l, str) and l.strip() and '\n' not in l for l in lines):
        raise ValueError('borg_scary_list_lines must be a list of one-line strings')
    return lines


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
    shipped = SCARY_LINE.findall((out / 'borg.txt').read_text())
    if shipped and shipped[-1] not in ('', SCARY_NONE) and shipped[-1] not in (spec.get('scary_lists') or {}):
        raise ValueError(f"harness/borg.txt at {spec['ref']} sets borg_scary_list = {shipped[-1]}, which the specimen "
                         'does not pin ("scary_lists": {name: sha256}, borg-zoo#228)')
    if (out / 'plans').exists():
        shutil.rmtree(out / 'plans')
    plans = copy_plans(spec, source, out)
    if (out / 'scary_lists').exists():
        shutil.rmtree(out / 'scary_lists')
    scary = copy_scary_lists(spec, source, out)
    if (out / 'worlds').exists():
        shutil.rmtree(out / 'worlds')
    worlds, world_tool = copy_worlds(spec, source, out)
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
    if scary:
        manifest['scary_lists'] = scary
    if worlds:
        manifest['worlds'] = worlds
        manifest['world_tool_sha256'] = world_tool
    if build_id.get('binary_sha256') != manifest['binary_sha256']:
        raise ValueError('copied binary does not match BUILD_ID')
    (out / 'build.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    return manifest


# Profile settings the adapter consumes itself instead of writing to borg.txt:
# an arm's lines appended to its scary list (borg-zoo#228).
ADAPTER_SETTINGS = ('borg_scary_list_lines', 'borg_world')
WORLD_LINE = re.compile(r'^[ \t]*borg_world[ \t]*=[ \t]*(\S*)[ \t]*\n?', re.M)
WORLD_TOOL = 'make-world.py'


def borg_txt_settings(profile):
    """The profile settings that go into the run's borg.txt."""
    return {k: v for k, v in profile['settings'].items() if k not in ADAPTER_SETTINGS}


def config_text(build_dir, profile, race=0, cls=0):
    base = (Path(build_dir) / 'borg.txt').read_text()
    text = cat_mod._override(base, 'borg_respawn_race', str(race))
    text = cat_mod._override(text, 'borg_respawn_class', str(cls))
    text = cat_mod._override(text, 'borg_cheat_death', 'FALSE')
    text = cat_mod._override(text, 'borg_respawn_winners', 'FALSE')
    for name, value in sorted(borg_txt_settings(profile).items()):
        text = cat_mod._override(text, name, cat_mod.setting_value(value))
    # harness/run.sh (#704) removes the world key before the core reads borg.txt.
    return WORLD_LINE.sub('', text)


def copy_worlds(spec, source, out):
    """Copy the specimen's pinned world configs (harness/worlds/NAME.txt) and
    scripts/make-world.py into the build; ({name: sha256}, tool sha256)."""
    worlds = {}
    pins = spec.get('worlds') or {}
    if not pins:
        return worlds, None
    for name, digest in sorted(pins.items()):
        src = Path(source) / 'harness/worlds' / f'{plan_name(name)}.txt'
        if not src.is_file():
            raise ValueError(f'specimen world {name} is not in harness/worlds at {spec["ref"]}')
        if sha256(src) != digest:
            raise ValueError(f'specimen world {name} has sha256 {sha256(src)}, catalogue pins {digest}')
        (out / 'worlds').mkdir(exist_ok=True)
        shutil.copy(src, out / 'worlds' / f'{name}.txt')
        worlds[name] = digest
    tool = Path(source) / 'scripts' / WORLD_TOOL
    if not tool.is_file():
        raise ValueError(f'specimen pins worlds but scripts/{WORLD_TOOL} is not at {spec["ref"]}')
    (out / 'tools').mkdir(exist_ok=True)
    shutil.copy(tool, out / 'tools' / WORLD_TOOL)
    return worlds, sha256(tool)


def world_name(profile, base_text):
    """The world a cell plays: the profile's borg_world, else the shipped
    borg.txt's line; None for upstream's data ('none' or no key)."""
    name = profile['settings'].get('borg_world')
    if name is None:
        m = WORLD_LINE.findall(base_text)
        name = m[-1] if m else None
    return None if not name or name == 'none' else plan_name(name)


def make_world(spec, manifest, build_dir, out, name):
    """Make world NAME's game data in the cell's world/; its record and the
    data root to pass to the game."""
    digest = (spec.get('worlds') or {}).get(name)
    if digest is None:
        raise ValueError(f'specimen ships no world {name}')
    config = Path(build_dir) / 'worlds' / f'{name}.txt'
    tool = Path(build_dir) / 'tools' / WORLD_TOOL
    if ((manifest.get('worlds') or {}).get(name) != digest or not config.is_file() or sha256(config) != digest
            or not tool.is_file() or sha256(tool) != manifest.get('world_tool_sha256')):
        raise ValueError(f'build {build_dir} does not carry world {name} at sha256 {digest}')
    root = out / 'world'
    if root.exists():
        shutil.rmtree(root)
    done = subprocess.run(['python3', str(tool), '--config', str(config), '--lib', str(Path(build_dir) / 'game/lib'),
                           '--out', str(root)], capture_output=True, text=True)
    data_sha = done.stdout.strip().splitlines()[-1] if done.returncode == 0 and done.stdout.strip() else None
    if not data_sha or not re.fullmatch(r'[0-9a-f]{64}', data_sha):
        raise ValueError(f'world {name}: {WORLD_TOOL} failed: {(done.stderr or done.stdout).strip()[-300:]}')
    return {'name': name, 'sha256': digest, 'data_sha256': data_sha}, root


def check_config(text, profile):
    wrong = []
    for name, value in borg_txt_settings(profile).items():
        if f'\n{name} = {cat_mod.setting_value(value)}\n' not in '\n' + text:
            wrong.append(name)
    return ('settings not written: ' + ', '.join(sorted(wrong))) if wrong else None


def check_effective(summary, profile):
    """For opted-in modern specimens, verify what the Borg actually used."""
    actual = summary.get('effective_settings')
    if not isinstance(actual, dict):
        return 'native summary has no effective_settings'
    wrong = [name for name, value in borg_txt_settings(profile).items()
             if name not in actual or actual[name] != value]
    return ('settings not effective: ' + ', '.join(sorted(wrong))) if wrong else None


def command(game_bin, out, cell, race_i, cls_i, suite, spec, keep=False, data_root=None):
    data = ([f'-dgamedata={data_root / "gamedata"}', f'-dpref={data_root / "customize"}',
             f'-dhelp={data_root / "help"}', f'-dscreens={data_root / "screens"}'] if data_root else [])
    argv = [str(game_bin), '-mborgh', '-n', '-uBorg'] + \
        [f'-d{d}={out / d}' for d in ('user', 'save', 'archive', 'panic', 'scores')] + data + \
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
    scary, scary_source = scary_name(profile, text)
    lines = scary_lines(profile)
    if lines and scary is None:
        raise ValueError('borg_scary_list_lines with no scary list (the compiled C list takes no lines)')
    scary_sha = ship_scary_list(spec, manifest, build_dir, out, scary, lines) if scary is not None else None
    world = world_name(profile, (build_dir / 'borg.txt').read_text())
    world_record, data_root = make_world(spec, manifest, build_dir, out, world) if world else (None, None)
    game = build_dir / 'game'
    argv = command(game / 'angband', out, cell, race_i, cls_i, suite, spec, keep=keep, data_root=data_root)
    env = dict(os.environ, TZ='UTC', LANG='C.UTF-8', LC_ALL='C.UTF-8')
    # This also keeps parallel cells from writing to an inherited
    # process-global record path (BORG_TOWN_PLAN_RECORD, BORG_TRIP_RECORD).
    for name in [n for n in env if n.startswith(AMBIENT_PREFIX)]:
        del env[name]
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
    if data_root is not None:
        shutil.rmtree(data_root, ignore_errors=True)
    summary = {}
    if (out / 'summary.json').exists():
        try:
            summary = json.loads((out / 'summary.json').read_text())
        except ValueError as exc:
            error = f'unreadable summary: {exc}'
    if outcome is None:
        if rc == 2 and not summary and (spec.get('plans') or spec.get('scary_lists')):
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
    loaded_plan = out / LOADED_PLAN
    loaded_sha = sha256(loaded_plan) if loaded_plan.is_file() else None
    if summary and spec.get('plans') and loaded_sha != plan_sha:
        # The core copies the plan it loaded into the output directory.
        mismatch = (mismatch + '; ' if mismatch else '') + (
            f'plan {plan} not loaded: output copy sha256 {loaded_sha}' if plan is not None
            else f'no plan requested, but the core loaded one (sha256 {loaded_sha})')
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
    loop = None
    purchase_burst = None
    if loop_checks(spec) and keys.exists():
        loop = frozen_turn_loop(keys.read_text(errors='replace'))
        has_state = (out / 'state.log').exists()
        if loop['bursts']:
            loops, shopping = classify_bursts(
                loop, (out / 'state.log').read_text(errors='replace') if has_state else None)
            loop.update(loop_turns=loops, purchase_turns=shopping, bursts=len(loops))
            if shopping:
                # Shopping is progress, not a stall (borg-zoo#205): flagged, outcome kept.
                purchase_burst = {'turns': shopping, 'keys': sum(n for _, n, _ in shopping),
                                  'purchases': sum(p for _, _, p in shopping)}
        if loop['bursts'] and outcome in ('death', 'turn_cap', 'borg_stopped'):
            observed_outcome, outcome = outcome, 'stalled'
            turn, keys_at = max(loop['loop_turns'], key=lambda tn: tn[1])
            why = 'and gold unchanged (no purchases)' if has_state else '(no state log to rule out shopping)'
            error = (f"frozen-turn loop: {loop['bursts']} game turns with {LOOP_KEYS}+ keys {why}, "
                     f"{keys_at} at turn {turn}")
    if outcome not in ('death', 'turn_cap', 'completion'):
        stall_info = stall.borgh(keys.read_text(errors='replace') if keys.exists() else '', summary)
        if loop and loop['bursts']:
            stall_info = {**stall_info, 'kind': 'frozen_turn_loop', 'frozen_turn_loop': loop}
    state_log = out / 'state.log'
    states = parse_state_log(state_log.read_text(errors='replace')) if state_log.exists() else []
    native_settings = summary.get('effective_settings')
    native_settings = native_settings if isinstance(native_settings, dict) else {}
    record = {
        'schema': 'borg-zoo/cell@1', **cell, 'harness_kind': 'borg-rs', 'profile_applied': applied,
        'specimen_ref': spec['ref'], 'impl': spec['impl'],
        'profile_sha256': cat_mod.profile_sha256(profile),
        'config_sha256': hashlib.sha256(text.encode()).hexdigest(),
        'plan': {'name': plan, 'sha256': plan_sha, 'loaded_sha256': loaded_sha} if plan is not None else None,
        'world': world_record,
        'scary_list': ({'name': scary, 'source': scary_source,
                        'base_sha256': (spec.get('scary_lists') or {}).get(scary),
                        'lines': lines or [], 'sha256': scary_sha} if scary is not None else None),
        'cap': suite['cap'], 'birth': suite['birth'],
        'boundary': 'exact' if spec.get('exact_turns') else 'after-key',
        'outcome': outcome, 'runner_outcome': summary.get('stop_reason'),
        'config_error': mismatch,
        'config_checked': 'native effective_settings and written file' if spec.get('verify_effective_settings') else 'written file (effective settings not required for this specimen)',
        'native_reported_settings': native_settings or None,
        'settings_resolved': settings_receipt.collect(out, summary.get('class'), profile['settings']),
        'effective_settings': {name: native_settings.get(name)
                               for name in profile['settings']} if spec.get('verify_effective_settings') else None,
        'cause': summary.get('death_cause') or ('(alive and well)' if summary and not summary.get('dead') else None),
        'character': ' '.join(x for x in (summary.get('race'), summary.get('class')) if x) or None,
        'played_race': summary.get('race'), 'played_class': summary.get('class'),
        'final': {'kind': summary.get('stop_reason'), 'turn': summary.get('game_turns'),
                  'depth': summary.get('depth'), 'max_depth': summary.get('max_depth'),
                  'level': summary.get('clevel'),
                  'max_level': summary.get('max_clevel', summary.get('clevel')),
                  'max_level_verified': summary.get('max_clevel') is not None,
                  'hp': None, 'decisions': None, 'keys': summary.get('keys')},
        'first_turn_at_depth': first_turns_at_depth(states) if states else {},
        # borg-zoo#718: time at a level and depth, for a death rate per turn of exposure; {} without a state log.
        'first_turn_at_level': first_turns_at_level(states) if states else {},
        'turns_at_level_depth': turns_at_level_depth(states, summary.get('game_turns')) if states else {},
        'first_turn_at_max_hp': first_turns_at_max_hp(states) if states else {},
        'milestones': milestones(states, suite['cap']) if states else None,
        'wall_seconds': wall,
        'trace_sha256': keys_sha, 'play_sha256': keys_sha,
        'error': error,
        'stall': stall_info,
        'source_sha256': (manifest.get('build_id') or {}).get('source_sha256'),
        # The upstream Angband commit the build compiled (borg-zoo#473: borg-reborn-rs #730 moved it).
        'engine_upstream': (manifest.get('build_id') or {}).get('engine_upstream'),
        # How the compiler orders the arguments of a call (borg-reborn-rs #855, 22224640): an `ltr` build plays other
        # games from the same seed. Absent in builds before that commit (they were built `rtl` on the GCC runners).
        'arg_order': (manifest.get('build_id') or {}).get('arg_order'),
        'binary_sha256': manifest.get('binary_sha256'), 'compiler': manifest.get('compiler'),
        'rustc': manifest.get('rustc'), 'platform': manifest.get('platform'),
    }
    if loop_checks(spec):
        record['frozen_turn_loop'] = loop
        if purchase_burst:
            record['purchase_burst'] = purchase_burst
        record['observed_outcome'] = observed_outcome if observed_outcome != outcome else None
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
