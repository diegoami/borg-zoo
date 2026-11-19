"""What each borg.txt setting does, in the words of the borg.txt that ships it.

The Settings tab shows this first on each setting's page. The text is the
comment block above the setting in borg-reborn-rs's harness/borg.txt (the
reborn and borg-rs keys) or better-borg-c's src/borg/borg.txt (the C keys),
copied into catalogue/setting-descriptions.json with the commit it came from,
so the site build needs no network. Refresh it after those files change:

    python3 -m zoo.setting_descriptions
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'catalogue' / 'setting-descriptions.json'
SOURCES = [('diegoami/borg-reborn-rs', 'harness/borg.txt'), ('diegoami/better-borg-c', 'src/borg/borg.txt')]
# The borg_param_* registry: name => (default, unit, min, max, location, "description").
REGISTRY = ('diegoami/borg-reborn-rs', 'borg-core/src/params.rs')
KEY = re.compile(r'^(borg_\w+)\s*=')
SPEC = re.compile(r'^\s*(\w+)\s*=>\s*\(.*,\s*"((?:[^"\\]|\\.)*)"\),?\s*$', re.M)


def parse(text):
    """{key: description}: the comment block above a key, shared by the keys
    that follow it until the next comment. Section headers (###) are not text."""
    out, block, last_was_key = {}, [], False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith('#'):
            if last_was_key:
                block, last_was_key = [], False
            body = stripped.lstrip('#').strip()
            if stripped.startswith('###'):
                block = []
            elif body:
                block.append(body)
            continue
        m = KEY.match(stripped)
        if m:
            last_was_key = True
            if any(re.fullmatch(r'\w+ \(harness/borg_\w+\.txt\)', b) for b in block[-1:]):
                continue  # a generated class-file section: no description
            if block and m.group(1) not in out:
                out[m.group(1)] = ' '.join(block)
    return out


VALUE = re.compile(r'^(borg_[\w@]+)\s*=\s*(\S+)', re.M)
DEFAULT = re.compile(r'^\s*(\w+)\s*=>\s*\(\s*(-?\d+)\s*,', re.M)


def gh(*args):
    return subprocess.run(['gh', 'api', *args], check=True, capture_output=True, text=True).stdout


def refresh():
    found = {}
    for repo, path in SOURCES:
        commit = json.loads(gh(f'repos/{repo}/commits/HEAD'))['sha']
        text = gh(f'repos/{repo}/contents/{path}?ref={commit}', '-H', 'Accept: application/vnd.github.raw')
        for key, desc in parse(text).items():
            found.setdefault(key, {'text': desc, 'source': f'{repo}/{path}', 'commit': commit})
        if repo == 'diegoami/borg-reborn-rs':
            shipped = dict(VALUE.findall(text))
    repo, path = REGISTRY
    commit = json.loads(gh(f'repos/{repo}/commits/HEAD'))['sha']
    text = gh(f'repos/{repo}/contents/{path}?ref={commit}', '-H', 'Accept: application/vnd.github.raw')
    for name, desc in SPEC.findall(text):
        found.setdefault('borg_param_' + name, {'text': desc.replace('\\"', '"'), 'source': f'{repo}/{path}',
                                                'commit': commit})
    compiled = {'borg_param_' + name: value for name, value in DEFAULT.findall(text)}
    # What borg-reborn-rs main plays today: its borg.txt's value, else the compiled default.
    for key, d in found.items():
        if key in shipped:
            d['shipped'] = shipped[key]
        elif key in compiled:
            d['shipped'] = compiled[key]
            d['shipped_from'] = 'compiled default'
    PATH.write_text(json.dumps(dict(sorted(found.items())), indent=1, ensure_ascii=False) + '\n')
    return len(found)


CLASSES = ('warrior', 'mage', 'druid', 'priest', 'necromancer', 'paladin', 'rogue', 'ranger', 'blackguard')


def shipped(key, found=None):
    """(value, where) borg-reborn-rs main plays for a key today, or (None, None)."""
    found = load() if found is None else found
    d = found.get(key) or {}
    if 'shipped' not in d:
        return None, None
    return d['shipped'], d.get('shipped_from', 'borg.txt')


def load():
    return json.loads(PATH.read_text()) if PATH.exists() else {}


def describe(key, found=None):
    """(text, source) for a key, or (None, None). A per-class key (..._mage)
    is described by its general key, since the class files carry no comments."""
    found = load() if found is None else found
    m = re.fullmatch(r'borg_param_attack_preference_(\w+?)_(\w+)_permille', key)
    if m and m.group(1) in CLASSES and f'borg_param_attack_preference_{m.group(2)}_permille' in found:
        general = f'borg_param_attack_preference_{m.group(2)}_permille'
        return (f'The {m.group(1).capitalize()} value of {general}, which it overrides for that class. '
                + found[general]['text']), found[general]
    cls = next((c for c in CLASSES if key.endswith('_' + c)), None)
    if cls and key[:-len(cls) - 1] in found:
        base = found[key[:-len(cls) - 1]]
        return (f'The {cls.capitalize()} value of {key[:-len(cls) - 1]}, which it overrides for that class. '
                + base['text']), base
    if key in found:
        return found[key]['text'], found[key]
    from .profiles_page import LESSONS
    if key in LESSONS:
        return LESSONS[key], {'source': 'docs/PROFILES.md'}
    return None, None


if __name__ == '__main__':
    print(f'{refresh()} settings described in {PATH.relative_to(ROOT)}')
