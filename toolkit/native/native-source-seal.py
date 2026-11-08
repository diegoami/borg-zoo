#!/usr/bin/env python3
"""Retain exact archive-to-observer source delta and per-file hashes."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import tarfile

EXPECTED_MODIFIED = {'CMakeLists.txt', 'src/borg/borg-commands.c', 'src/borg/borg-io.c', 'src/borg/borg.c', 'src/game-world.c', 'src/main-test.c', 'src/ui-game.c'}
EXPECTED_ADDED = {'version', 'src/native-observer.h', 'src/native-observer.c'}
def sha(data):
    return hashlib.sha256(data).hexdigest()
def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((a.build / 'build.json').read_text())
    with tarfile.open(a.build / 'source.tar') as tar:
        original = {m.name: tar.extractfile(m).read() for m in tar if m.isfile()}
    actual = {str(f.relative_to(a.build / 'source')): f.read_bytes() for f in (a.build / 'source').rglob('*') if f.is_file()}
    changed = {n for n in original if actual.get(n) != original[n]}
    added = set(actual) - set(original)
    if changed != EXPECTED_MODIFIED or added != EXPECTED_ADDED:
        raise ValueError(f'unexpected source changes: modified={sorted(changed)}, added={sorted(added)}')
    delta = []
    files = {}
    for name in sorted(changed | added):
        before, after = original.get(name, b''), actual[name]
        files[name] = {'original_sha256': sha(before) if name in original else None, 'instrumented_sha256': sha(after)}
        delta.extend(difflib.unified_diff(before.decode().splitlines(True), after.decode().splitlines(True), fromfile='original/' + name, tofile='observed/' + name))
    (a.out / 'source-observer.patch').write_text(''.join(delta))
    seal = {
        'schema': 'original-angband/source-seal@1',
        'source_repository': 'https://github.com/angband/angband',
        'source_commit': manifest['source_commit'],
        'harness_commit': manifest['harness_commit'],
        'source_archive_sha256': sha((a.build / 'source.tar').read_bytes()),
        'binary_sha256': sha((a.build / 'build/game/angband').read_bytes()),
        'data_sha256': manifest['data_sha256'],
        'modified': sorted(changed), 'added': sorted(added), 'file_hashes': files,
        'unchanged_original_files': len(original) - len(changed),
        'patch_sha256': sha((a.out / 'source-observer.patch').read_bytes()),
        'qualification': 'Exact source delta is disclosed for inspection. This source seal alone does not prove observation neutrality; consult repeated pilot traces and the hook review.',
    }
    (a.out / 'source-seal.json').write_text(json.dumps(seal, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: seal[k] for k in ('source_commit', 'harness_commit', 'binary_sha256', 'unchanged_original_files', 'patch_sha256')}))
if __name__ == '__main__':
    main()
