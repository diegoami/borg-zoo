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
CLASSIC = re.compile(r'\b([bi])\(c"(borg_\w+)",\s*(-?\w+)\)')
RETIRED = re.compile(r'retired\(c"(borg_\w+)"')
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
    # The classic settings' compiled defaults, and the retired (inert) ones.
    init = gh(f'repos/{repo}/contents/borg-core/src/borg_init.rs?ref={commit}', '-H', 'Accept: application/vnd.github.raw')
    for kind, name, value in CLASSIC.findall(init):
        compiled.setdefault(name, {'true': 'TRUE', 'false': 'FALSE'}.get(value, value) if kind == 'b' else value)
    retired = set(RETIRED.findall(init))
    # The class files (#520): a class's own value, else the general one.
    for cls in CLASSES:
        try:
            ctext = gh(f'repos/{repo}/contents/harness/borg_{cls}.txt?ref={commit}', '-H', 'Accept: application/vnd.github.raw')
        except subprocess.CalledProcessError:
            continue
        for name, value in VALUE.findall(ctext):
            general = name.removeprefix('borg_param_')
            m = re.fullmatch(r'attack_preference_(\w+)_permille', general)
            for alias in ([f'borg_param_attack_preference_{cls}_{m.group(1)}_permille'] if m else []) + [
                    f'{name}_{cls}', f'{name}@{cls}']:
                shipped.setdefault(alias, value)
    for key in list(found):
        if key not in shipped and key not in compiled:
            m = re.fullmatch(r'borg_param_attack_preference_(\w+?)_(\w+)_permille', key)
            cls = next((c for c in CLASSES if key.endswith('_' + c)), None)
            general = (f'borg_param_attack_preference_{m.group(2)}_permille' if m and m.group(1) in CLASSES
                       else key[:-len(cls) - 1] if cls else None)
            if general and (general in shipped or general in compiled):
                found[key]['shipped'] = shipped.get(general, compiled.get(general))
                found[key]['shipped_from'] = 'general value (no class line)'
    for key in retired:
        found.setdefault(key, {'text': 'Retired in borg-reborn-rs: read and ignored.', 'source': f'{repo}/borg-core/src/borg_init.rs',
                               'commit': commit})
        found[key]['shipped'] = 'retired'
        found[key]['shipped_from'] = 'retired (inert)'
    # No borg_plan line: main plays without an errands plan.
    found.setdefault('borg_plan', {'text': 'The errands plan file the Borg follows.', 'source': f'{repo}/harness/borg.txt',
                                   'commit': commit})
    if 'borg_plan' not in shipped:
        found['borg_plan']['shipped'] = 'none'
        found['borg_plan']['shipped_from'] = 'not set in borg.txt (no plan)'
    # What borg-reborn-rs main plays today: its borg.txt's value, else the compiled default.
    for key in shipped:
        if key not in found:
            found[key] = {'text': '', 'source': f'{repo}/harness', 'commit': commit}
    for key, d in found.items():
        if 'shipped' in d:
            continue
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
    if 'shipped' in d:
        return d['shipped'], d.get('shipped_from', 'borg.txt')
    # A per-class key with no class line anywhere plays the general value.
    m = re.fullmatch(r'borg_param_attack_preference_(\w+?)_(\w+)_permille', key)
    cls = next((c for c in CLASSES if key.endswith('_' + c)), None)
    general = (f'borg_param_attack_preference_{m.group(2)}_permille' if m and m.group(1) in CLASSES
               else key[:-len(cls) - 1] if cls else None)
    if general and 'shipped' in (found.get(general) or {}):
        return found[general]['shipped'], 'general value, no class line'
    if key.startswith('borg_') and key not in found:
        return 'not read', 'not a borg-reborn-rs setting'
    return None, None


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
