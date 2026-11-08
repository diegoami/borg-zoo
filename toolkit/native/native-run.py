#!/usr/bin/env python3
"""Run original Angband with the pinned existing observer; retain every attempt."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

SOURCE = 'e473720ed88a0f0c7ca66815cef3000eb4a38bc3'
HARNESS = 'fc9d97cb46aa0aaa27773e5c83a41ec395d515fc'
RACES = ['Human', 'Half-Elf', 'Elf', 'Hobbit', 'Gnome', 'Dwarf', 'Half-Orc', 'Half-Troll', 'Dunadan', 'High-Elf', 'Kobold']
CLASSES = ['Warrior', 'Mage', 'Druid', 'Priest', 'Necromancer', 'Paladin', 'Rogue', 'Ranger', 'Blackguard']
LETTERS = 'abcdefgimnopqrstuvwxyz'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--harness', type=Path, required=True)
    p.add_argument('--build', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--seed', type=int, required=True)
    p.add_argument('--race', choices=RACES, required=True)
    p.add_argument('--class', dest='cls', choices=CLASSES, required=True)
    p.add_argument('--turns', type=int, default=100000)
    p.add_argument('--timeout', type=int, default=900)
    p.add_argument('--stall-timeout', type=int, default=90)
    a = p.parse_args()
    if not 0 <= a.seed <= 0xffffffff or a.turns < 2 or a.timeout < 1 or a.stall_timeout < 1:
        p.error('seed must be uint32, turns >= 2 and watchdog limits positive')
    if a.out.exists():
        p.error('output already exists; use a fresh attempt path')
    a.harness = a.harness.resolve()
    actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=a.harness, text=True).strip()
    if actual != HARNESS:
        p.error(f'harness is {actual}, expected {HARNESS}')
    build = json.loads((a.build / 'build.json').read_text())
    if build.get('source_commit') != SOURCE or build.get('recording_schema'):
        p.error('require exact original source and ordinary observer, not recording profile')
    if digest(a.build / 'build/game/angband') != build.get('binary_sha256'):
        p.error('binary hash differs from build manifest')
    if digest(a.build / 'source.tar') != build.get('source_archive_sha256'):
        p.error('original source archive hash differs from build manifest')
    # Hash all loaded native tool dependencies against their immutable Git blobs.
    for name in ('measure-native.py', 'native-observer.c', 'native-observer.h'):
        path = a.harness / 'tools' / name
        frozen = subprocess.check_output(['git', 'show', f'{HARNESS}:tools/{name}'], cwd=a.harness)
        if path.read_bytes() != frozen:
            p.error(f'changed pinned tool: {name}')
    spec = importlib.util.spec_from_file_location('original_native_runner', a.harness / 'tools/measure-native.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    original = runner.birth_keys(False)
    marker = 'key a\nkey a\nkey a\n'
    if original.count(marker) != 1:
        p.error('unexpected pinned birth input')
    def tap(i):
        return 'key a\n' if i == 0 else f'key {LETTERS[i]}\nkey {LETTERS[i]}\n'
    keys = tap(RACES.index(a.race)) + tap(CLASSES.index(a.cls)) + 'key a\n'
    assigned = original.replace(marker, keys)
    runner.birth_keys = lambda random_birth=False: assigned
    args = SimpleNamespace(build=a.build, output=a.out, seed=a.seed, cap=a.turns,
                           timeout=a.timeout, stall_timeout=a.stall_timeout,
                           no_saves=True, load=None, configuration=None, random_birth=False)
    runner.run(args)
    out = a.out.resolve()
    result = json.loads((out / 'result.json').read_text())
    trace = (out / 'trace.txt').read_text()
    line = next((s for s in trace.splitlines() if s.startswith('CHARACTER ')), None)
    played = line.split()[-2:] if line else None
    mismatch = played != [a.race, a.cls]
    record = {
        'schema': 'original-angband/native-record@1',
        'source_repository': 'https://github.com/angband/angband',
        'source_commit': SOURCE, 'harness_commit': HARNESS,
        'toolkit_sha256': digest(Path(__file__)),
        'inputs': {'seed': a.seed, 'race': a.race, 'class': a.cls,
                   'turn_cap': a.turns, 'wall_seconds_limit': a.timeout,
                   'stall_seconds_limit': a.stall_timeout},
        'birth_method': 'ordinary UI menus; default point buy; native starting gear',
        'actual_birth': played, 'birth_verified': not mismatch,
        'birth_stats_recorded': False, 'birth_gear_recorded': False,
        'outcome': 'config_error' if mismatch else result['outcome'],
        'runner_outcome': result['outcome'], 'cause': result.get('cause'),
        'final': (result.get('states') or [None])[-1],
        'wall_seconds': result.get('wall_seconds'),
        'calendar_context': result.get('calendar_context'),
        'compiler': build.get('compiler'), 'platform': build.get('platform'),
        'native_maps': [str(f.relative_to(out)) for f in sorted((out / 'archive').glob('*.map'))],
        'effective_borg_options': next((s for s in trace.splitlines() if s.startswith('BORG_OPTIONS ')), None),
        'effective_game_options': next((s for s in trace.splitlines() if s.startswith('ACTIVE_OPTIONS ')), None),
        'evidence_sha256': {str(f.relative_to(out)): digest(f) for f in sorted(out.rglob('*')) if f.is_file()},
        'limits': ['Equal C and Neo seeds are different games.',
                   'Raw evidence is unassessed, not a replay or causal diagnosis.',
                   'No raw key-command stream or birth stats/gear snapshot.',
                   'Pinned runner result.character is a legacy Human Warrior label; actual_birth above is authoritative.'],
    }
    (out / 'native-record.json').write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'out': str(out), 'outcome': record['outcome'], 'cause': record['cause'], 'birth_verified': not mismatch}))
    return 1 if mismatch or result['outcome'] in ('harness_failure', 'crash') else 0

if __name__ == '__main__':
    raise SystemExit(main())
