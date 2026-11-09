"""Adapter over better-borg-c's native runner (tools/measure-native.py).

The zoo does not re-implement building or running. It loads the runner from a
checkout of the pinned harness commit and calls its prepare() and run().

The observer stops a run at engine turn T itself (the suite's cap), so every
cell's "boundary" is "exact" (docs/DESIGN.md; borg-reborn-rs's requested
field, borg-zoo#30).
"""
import hashlib
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

from . import catalogue as cat_mod
from . import stall

VALID = ('death', 'turn_cap', 'completion')
DEPTH_MARKS = (1, 2, 3, 4, 5, 6, 8, 10, 15, 20)


def load_runner(harness):
    harness = Path(harness).resolve()
    path = harness / 'tools/measure-native.py'
    spec = importlib.util.spec_from_file_location('measure_native', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_harness(harness, expected_commit):
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=harness, text=True).strip()
    if head != expected_commit:
        raise ValueError(f'harness checkout is at {head}, catalogue pins {expected_commit}')
    return head


def build(specimen_name, harness, out, cat=None, source=None, engine=None, toolkit=None):
    cat = cat or cat_mod.catalogue()
    specimens = cat['specimens']
    spec = specimens['specimens'][specimen_name]
    if spec.get('kind') == 'neo-original':
        from . import neo_original
        return neo_original.build(spec, source, engine, toolkit, out)
    if spec.get('kind') == 'borg-rs':
        from . import borgrs
        return borgrs.build(spec, source, out)
    if spec.get('kind') == 'mandos':
        from . import mandos
        return mandos.build(spec, source, out)
    check_harness(harness, specimens['harness']['commit'])
    runner = load_runner(harness)
    runner.prepare(SimpleNamespace(ref=spec['ref'], output=Path(out), observe=True,
                                   recording=False, retry=False))
    manifest = json.loads((Path(out) / 'build.json').read_text())
    if manifest['source_commit'] != spec['ref']:
        raise ValueError(f"built {manifest['source_commit']}, expected {spec['ref']}")
    return manifest


LETTERS = 'abcdefgimnopqrstuvwxyz'  # all_letters_nohjkl, the birth menus' tags
DEFAULT_BIRTH = 'key a\nkey a\nkey a\n'


def birth_input(runner, race, cls):
    """The runner's birth input with race and class chosen in the menus.

    The birth menus select on a double tap: pressing an item's letter moves
    the cursor to it and pressing it again selects it, while the letter of
    the already highlighted first item selects at once. The runner's own
    input is "a a a" (Human, Warrior, point-based) followed by its other keys.
    """
    base = runner.birth_keys(False)
    if base.count(DEFAULT_BIRTH) != 1:
        raise ValueError('unexpected runner birth input; cannot choose race and class')

    def tap(index):
        return 'key a\n' if index == 0 else f'key {LETTERS[index]}\nkey {LETTERS[index]}\n'
    keys = tap(cat_mod.RACES.index(race)) + tap(cat_mod.CLASSES.index(cls)) + 'key a\n'
    return base.replace(DEFAULT_BIRTH, keys)


def parse_character(trace_text):
    for line in trace_text.splitlines():
        if line.startswith('CHARACTER '):
            parts = line.split()
            if len(parts) >= 4:
                return parts[-2], parts[-1]
    return None


def parse_options(trace_text):
    for line in trace_text.splitlines():
        if line.startswith('BORG_OPTIONS '):
            return {k: int(v) for k, v in (p.split('=', 1) for p in line.split()[1:])}
    return None


CONFIG_LINES = ('BORG_OPTIONS ', 'ACTIVE_OPTIONS ')


def play_sha256(trace_text):
    """Hash of the trace without the configuration lines, so two profiles
    that play the same game hash the same."""
    kept = [line for line in trace_text.splitlines(keepends=True) if not line.startswith(CONFIG_LINES)]
    return hashlib.sha256(''.join(kept).encode()).hexdigest() if kept else None


def first_turns_at_depth(states):
    marks = {}
    for state in states:
        depth = state.get('max_depth')
        if not isinstance(depth, int):
            continue
        for mark in DEPTH_MARKS:
            if depth >= mark and str(mark) not in marks:
                marks[str(mark)] = state['turn']
    return marks


def milestones(states, cap, fractions=(0.25, 0.5, 0.75, 1.0)):
    """Level and max depth at turn fractions of the cap: the last sampled
    state (every 100 decisions) at or before that turn. The observer logs no
    gold or item value, so there is no net-worth figure here (docs/DESIGN.md,
    "Open questions", #9); zoo/borgrs.py's own milestones() adds gold on hand
    for the borg-rs specimens whose state stream carries it."""
    rows = []
    for f in fractions:
        t = int(cap * f)
        at_or_before = [s for s in states if s.get('turn') is not None and s['turn'] <= t]
        last = at_or_before[-1] if at_or_before else None
        rows.append({'turn': t, 'level': (last or {}).get('max_level', (last or {}).get('level')),
                     'max_depth': (last or {}).get('max_depth')})
    return rows


def summarise(cell, result, trace_text, profile, spec, suite, build_manifest):
    states = result.get('states') or []
    final = states[-1] if states else {}
    options = parse_options(trace_text)
    expected = cat_mod.expected_options(profile)
    mismatch = None
    if options is None:
        mismatch = 'no BORG_OPTIONS line in the trace'
    else:
        wrong = {k: (v, options.get(k)) for k, v in expected.items() if options.get(k) != v}
        if wrong:
            mismatch = 'settings not in effect: ' + ', '.join(
                f'{k} expected {v} got {g}' for k, (v, g) in sorted(wrong.items()))
    outcome = result.get('outcome', 'harness_failure')
    played = parse_character(trace_text)
    if cell.get('race') and played and played != (cell['race'], cell['class']):
        mismatch = (mismatch + '; ' if mismatch else '') + \
            f"character {played[0]} {played[1]}, expected {cell['race']} {cell['class']}"
    if mismatch and outcome in VALID:
        outcome = 'config_error'
    files = result.get('files_sha256') or {}
    stall_info = stall.observer(states, trace_text) if outcome not in VALID else None
    return {
        'schema': 'borg-zoo/cell@1',
        **cell,
        'harness_kind': 'better-borg-c',
        'specimen_ref': spec['ref'],
        'profile_sha256': cat_mod.profile_sha256(profile),
        'config_sha256': result.get('configuration_sha256'),
        'cap': suite['cap'],
        'birth': suite['birth'],
        'boundary': 'exact',
        'outcome': outcome,
        'runner_outcome': result.get('outcome'),
        'config_error': mismatch,
        'cause': result.get('cause'),
        'character': ' '.join(played) if played else result.get('character'),
        'played_race': played[0] if played else None,
        'played_class': played[1] if played else None,
        'final': {k: final.get(k) for k in ('kind', 'turn', 'depth', 'max_depth', 'level', 'max_level', 'hp', 'decisions')},
        'first_turn_at_depth': first_turns_at_depth(states),
        'milestones': milestones(states, suite['cap']) if states else None,
        'wall_seconds': result.get('wall_seconds'),
        'trace_sha256': files.get('trace.txt'),
        'play_sha256': play_sha256(trace_text),
        'effective_options': options,
        'error': result.get('error'),
        'stall': stall_info,
        'harness_commit': result.get('harness_commit'),
        'runner_sha256': result.get('runner_sha256'),
        'binary_sha256': build_manifest.get('binary_sha256'),
        'compiler': build_manifest.get('compiler'),
        'platform': build_manifest.get('platform'),
        'calendar': result.get('calendar_context'),
    }


def run_cell(cell, build_dir, harness, work, cat=None, keep=False, source=None, toolkit=None):
    cat = cat or cat_mod.catalogue()
    if cat['specimens']['specimens'][cell['specimen']].get('kind') == 'neo-original':
        from . import neo_original
        return neo_original.run_cell(cell, build_dir, work, cat, toolkit)
    if cat['specimens']['specimens'][cell['specimen']].get('kind') == 'borg-rs':
        from . import borgrs
        return borgrs.run_cell(cell, build_dir, work, cat)
    if cat['specimens']['specimens'][cell['specimen']].get('kind') == 'mandos':
        from . import mandos
        return mandos.run_cell(cell, build_dir, work, cat, source)
    applied, profile = cat_mod.resolve_profile(cat, cell)
    suite = cat['suites'][cell['suite']]
    spec = cat['specimens']['specimens'][cell['specimen']]
    build_dir = Path(build_dir).resolve()
    manifest = json.loads((build_dir / 'build.json').read_text())
    if manifest['source_commit'] != spec['ref']:
        raise ValueError(f"build {build_dir} is {manifest['source_commit']}, cell wants {spec['ref']}")
    out = Path(work).resolve() / cat_mod.cell_key(cell)
    if out.exists():
        if keep:
            raise ValueError(f'retained attempt already exists: {out}')
        shutil.rmtree(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    runner = load_runner(harness)  # a fresh module per cell, so per-cell birth keys never leak
    if cell.get('race'):
        keys = birth_input(runner, cell['race'], cell['class'])
        runner.birth_keys = lambda random_birth=False, _keys=keys: _keys
    shipped_path = build_dir / 'source/src/borg/borg.txt'
    shipped = shipped_path.read_text() if profile.get('base') == 'shipped' else None
    args = SimpleNamespace(build=build_dir, output=out, seed=cell['seed'], cap=suite['cap'],
                           timeout=suite['wall_seconds'], stall_timeout=suite['stall_seconds'],
                           no_saves=not suite.get('saves', False), load=None,
                           configuration=cat_mod.profile_text(profile, shipped).rstrip('\n') or None,
                           random_birth=suite['birth'] == 'random')
    try:
        runner.run(args)
    except (OSError, ValueError, KeyError) as exc:
        out.mkdir(parents=True, exist_ok=True)
        (out / 'result.json').write_text(json.dumps({'outcome': 'harness_failure', 'error': str(exc)}))
    result = json.loads((out / 'result.json').read_text())
    trace_path = out / 'trace.txt'
    trace = trace_path.read_text(errors='replace') if trace_path.exists() else ''
    record = summarise(cell, result, trace, profile, spec, suite, manifest)
    record['profile_applied'] = applied
    if not keep:
        for name in ('trace.txt', 'terminal.log'):
            path = out / name
            if path.exists():
                path.unlink()
    return record


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
