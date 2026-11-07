"""Adapter over better-borg-c's native runner (tools/measure-native.py).

The zoo does not re-implement building or running. It loads the runner from a
checkout of the pinned harness commit and calls its prepare() and run().
"""
import hashlib
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

from . import catalogue as cat_mod

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


def build(specimen_name, harness, out, cat=None):
    cat = cat or cat_mod.catalogue()
    specimens = cat['specimens']
    check_harness(harness, specimens['harness']['commit'])
    spec = specimens['specimens'][specimen_name]
    runner = load_runner(harness)
    runner.prepare(SimpleNamespace(ref=spec['ref'], output=Path(out), observe=True,
                                   recording=False, retry=False))
    manifest = json.loads((Path(out) / 'build.json').read_text())
    if manifest['source_commit'] != spec['ref']:
        raise ValueError(f"built {manifest['source_commit']}, expected {spec['ref']}")
    return manifest


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
    if mismatch and outcome in VALID:
        outcome = 'config_error'
    files = result.get('files_sha256') or {}
    return {
        'schema': 'borg-zoo/cell@1',
        **cell,
        'specimen_ref': spec['ref'],
        'profile_sha256': cat_mod.profile_sha256(profile),
        'config_sha256': result.get('configuration_sha256'),
        'cap': suite['cap'],
        'birth': suite['birth'],
        'outcome': outcome,
        'runner_outcome': result.get('outcome'),
        'config_error': mismatch,
        'cause': result.get('cause'),
        'character': result.get('character'),
        'final': {k: final.get(k) for k in ('kind', 'turn', 'depth', 'max_depth', 'level', 'max_level', 'hp', 'decisions')},
        'first_turn_at_depth': first_turns_at_depth(states),
        'wall_seconds': result.get('wall_seconds'),
        'trace_sha256': files.get('trace.txt'),
        'play_sha256': play_sha256(trace_text),
        'effective_options': options,
        'error': result.get('error'),
        'harness_commit': result.get('harness_commit'),
        'runner_sha256': result.get('runner_sha256'),
        'binary_sha256': build_manifest.get('binary_sha256'),
        'compiler': build_manifest.get('compiler'),
        'platform': build_manifest.get('platform'),
        'calendar': result.get('calendar_context'),
    }


def run_cell(cell, build_dir, harness, work, cat=None, keep=False):
    cat = cat or cat_mod.catalogue()
    profile = cat['profiles'][cell['profile']]
    suite = cat['suites'][cell['suite']]
    spec = cat['specimens']['specimens'][cell['specimen']]
    build_dir = Path(build_dir).resolve()
    manifest = json.loads((build_dir / 'build.json').read_text())
    if manifest['source_commit'] != spec['ref']:
        raise ValueError(f"build {build_dir} is {manifest['source_commit']}, cell wants {spec['ref']}")
    out = Path(work).resolve() / cat_mod.cell_key(cell)
    if out.exists():
        shutil.rmtree(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    runner = load_runner(harness)
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
    if not keep:
        for name in ('trace.txt', 'terminal.log'):
            path = out / name
            if path.exists():
                path.unlink()
    return record


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
