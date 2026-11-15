#!/usr/bin/env python3
"""Recover original borg.txt bytes from a retained raw artifact, never regenerate.

Usage: python3 tools/recover-configurations.py ARTIFACT.zip SOURCE_URL
Only content-addressed files and their origin receipts are written; results
records remain immutable. Report rendering checks every cell's recorded hash.
"""
import gzip
import hashlib
import io
import json
import sys
import tarfile
import zipfile
from pathlib import Path


def recover(archive, source, destination):
    destination.mkdir(parents=True, exist_ok=True)
    manifest_path = destination / 'manifest.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    archive_hash = hashlib.sha256(archive.read_bytes()).hexdigest()
    count = 0
    with zipfile.ZipFile(archive) as zipped:
        for filename in zipped.namelist():
            if not filename.endswith('.tgz'):
                continue
            bundle = zipped.read(filename)
            checksum = filename.removesuffix('.tgz') + '.sha256'
            if checksum not in zipped.namelist() or zipped.read(checksum).decode().split()[0] != hashlib.sha256(bundle).hexdigest():
                raise ValueError('Raw archive SHA-256 receipt missing or mismatched')
            with tarfile.open(fileobj=io.BytesIO(bundle), mode='r:gz') as tar:
                for member in tar:
                    if not member.isfile() or not member.name.endswith('/user/borg.txt'):
                        continue
                    data = tar.extractfile(member).read()
                    digest = hashlib.sha256(data).hexdigest()
                    target = destination / f'{digest}.txt.gz'
                    if target.exists() and gzip.decompress(target.read_bytes()) != data:
                        raise ValueError('Conflicting content-addressed evidence')
                    target.write_bytes(gzip.compress(data, mtime=0))
                    entry = manifest.setdefault(digest, {'source': source, 'archive_sha256': archive_hash,
                        'bundle_sha256': hashlib.sha256(bundle).hexdigest(), 'members': []})
                    if member.name not in entry['members']:
                        entry['members'].append(member.name)
                    count += 1
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    return count


if __name__ == '__main__':
    target = Path(__file__).resolve().parents[1] / 'reports/configuration-evidence'
    print(recover(Path(sys.argv[1]), sys.argv[2], target), 'original files recovered')
