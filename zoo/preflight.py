"""Checks that run before a job is started, so a run that cannot work fails
in seconds, not after a build or as a silent wall of harness_failure cells.

What is checked, per specimen of the experiment (or of the one arm):
- the specimen is not marked pending;
- every ref is a full 40-character commit id;
- for a Neo original, the pinned toolkit's build script does not hard-code
  other source pins than the specimen's own (borg-zoo#79 follow-up: the
  toolkit at tracker 2668adc5 refuses any engine but 5a9cab2, and the first
  smoke of neo-765-original failed there, skipping every run job).

Network lookups go through `fetch(repository, ref, path)`, which returns the
file's text or None, so tests can stand in for it.
"""
import re
import subprocess
import tempfile
from pathlib import Path

from . import catalogue as cat_mod

SHA = re.compile(r'^[0-9a-f]{40}$')
PIN = re.compile(r'["\']([0-9a-f]{40})["\']')


def git_fetch_file(repository, ref, path):
    """The text of `path` at commit `ref` of a public GitHub repository, or None."""
    url = f'https://github.com/{repository}'
    with tempfile.TemporaryDirectory() as tmp:
        def git(*args):
            return subprocess.run(['git', '-C', tmp, *args], capture_output=True, text=True, timeout=120)
        if git('init', '-q').returncode or git('fetch', '-q', '--depth', '1', url, ref).returncode:
            return None
        shown = git('show', f'FETCH_HEAD:{path}')
        return shown.stdout if shown.returncode == 0 else None


def check(exp, cat=None, fetch=git_fetch_file):
    """The list of problems found for the experiment; empty when it can start."""
    cat = cat or cat_mod.catalogue()
    specimens = cat['specimens']['specimens']
    problems = []
    for name in exp['specimens']:
        spec = specimens[name]
        if spec.get('pending'):
            problems.append(f'{name}: pending: {spec["pending"]}')
            continue
        for field in ('ref', 'engine_ref', 'toolkit_ref'):
            if field in spec and not SHA.match(spec[field]):
                problems.append(f'{name}: {field} is not a full commit id: {spec[field]!r}')
        if spec.get('kind') == 'neo-original':
            script = f'{spec["toolkit_path"]}/build.mjs'
            text = fetch(spec['toolkit_repository'], spec['toolkit_ref'], script)
            if text is None:
                problems.append(f'{name}: cannot read {script} at {spec["toolkit_repository"]}@'
                                f'{spec["toolkit_ref"][:8]}')
                continue
            pins = set(PIN.findall(text))
            own = {spec['ref'], spec['engine_ref']}
            if pins and not pins <= own:
                problems.append(f'{name}: the toolkit build script at {spec["toolkit_ref"][:8]} hard-codes '
                                f'source pins {sorted(p[:8] for p in pins - own)} that this specimen does not '
                                f'use (its engine {spec["engine_ref"][:8]}, Borg {spec["ref"][:8]}); the build '
                                'will refuse it')
    return problems
