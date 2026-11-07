"""Specimens, profiles, suites and experiments: loading, validation, cells."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORCED = 'borg_cheat_death = FALSE\nborg_respawn_winners = FALSE\n'


def _load(path):
    return json.loads(Path(path).read_text())


def catalogue(root=ROOT):
    root = Path(root)
    return {
        'specimens': _load(root / 'catalogue/specimens.json'),
        'profiles': _load(root / 'catalogue/profiles.json')['profiles'],
        'suites': _load(root / 'catalogue/suites.json')['suites'],
    }


def experiment(path, cat=None):
    cat = cat or catalogue()
    exp = _load(path)
    specimens = cat['specimens']['specimens']
    for name in exp['specimens']:
        if name not in specimens:
            raise ValueError(f'unknown specimen: {name}')
    for name in exp['profiles']:
        if name not in cat['profiles']:
            raise ValueError(f'unknown profile: {name}')
    for name in exp['suites']:
        if name not in cat['suites']:
            raise ValueError(f'unknown suite: {name}')
    for name in exp['specimens']:
        if specimens[name].get('kind') == 'borg-rs':
            for suite in exp['suites']:
                if cat['suites'][suite]['birth'] != 'fixed':
                    raise ValueError(f'{name}: the borg-rs adapter supports fixed birth only (suite {suite})')
            for prof in exp['profiles']:
                if cat['profiles'][prof].get('base') == 'shipped':
                    raise ValueError(f'{name}: profile {prof} needs a shipped borg.txt base, '
                                     'which the borg-rs adapter takes from harness/borg.txt only')
    if exp['control'] not in exp['specimens']:
        raise ValueError('control must be one of the experiment specimens')
    if exp.get('control_profile', exp['profiles'][0]) not in exp['profiles']:
        raise ValueError('control_profile must be one of the experiment profiles')
    return exp


def setting_value(value):
    if value is True:
        return 'TRUE'
    if value is False:
        return 'FALSE'
    if isinstance(value, int):
        return str(value)
    raise ValueError(f'unsupported setting value: {value!r}')


def _override(text, name, value):
    line = f'{name} = {value}'
    pattern = re.compile(rf'^[ \t]*{re.escape(name)}[ \t]*=.*$', re.M)
    if pattern.search(text):
        return pattern.sub(line, text)
    marker = '[BEGIN FORMULA SECTION]'
    if marker in text:
        return text.replace(marker, line + '\n\n' + marker, 1)
    return text.rstrip('\n') + '\n' + line + '\n'


def profile_text(profile, shipped=None):
    """The borg.txt content a profile supplies, before the runner's forced lines.

    A profile with base "shipped" starts from the specimen's own
    src/borg/borg.txt (settings plus formula section) and overrides its
    settings; otherwise it supplies only its setting lines.
    """
    settings = sorted(profile['settings'].items())
    if profile.get('base') == 'shipped':
        if shipped is None:
            raise ValueError('profile needs the specimen\'s shipped borg.txt')
        text = shipped
        for name, value in settings:
            text = _override(text, name, setting_value(value))
        return text
    if profile.get('base') not in (None, 'none'):
        raise ValueError(f"unknown profile base: {profile.get('base')!r}")
    return ''.join(f'{name} = {setting_value(value)}\n' for name, value in settings)


def profile_sha256(profile):
    """Hash of the profile definition (the exact file is hashed per run)."""
    return hashlib.sha256(json.dumps(profile, sort_keys=True).encode()).hexdigest()


def expected_options(profile):
    """Effective values the observer must report, as integers."""
    return {name: int(value) for name, value in profile['settings'].items()}


def cells(exp, cat=None):
    cat = cat or catalogue()
    out = []
    for suite_name in exp['suites']:
        suite = cat['suites'][suite_name]
        for specimen in exp['specimens']:
            for profile in exp['profiles']:
                for seed in suite['seeds']:
                    out.append({'specimen': specimen, 'profile': profile,
                                'suite': suite_name, 'seed': seed})
    return out


def cell_key(cell):
    return f"{cell['suite']}/{cell['specimen']}/{cell['profile']}/{cell['seed']}"


def shard(cell_list, specimen, index, count):
    """Cells of one specimen, dealt round-robin into `count` shards."""
    mine = [c for c in cell_list if c['specimen'] == specimen]
    return mine[index::count]


def plan(exp, shards, cat=None):
    """Build and run matrices for a CI workflow."""
    cat = cat or catalogue()
    all_cells = cells(exp, cat)
    specimens = cat['specimens']['specimens']
    builds = [{'specimen': s, 'kind': specimens[s].get('kind', 'better-borg-c'),
               'repository': specimens[s]['repository'], 'ref': specimens[s]['ref']}
              for s in exp['specimens']]
    runs = []
    for b in builds:
        total = len([c for c in all_cells if c['specimen'] == b['specimen']])
        for index in range(min(shards, total)):
            runs.append({**b, 'shard': index, 'shards': min(shards, total)})
    return {'specimens': exp['specimens'], 'builds': builds, 'runs': runs, 'cells': len(all_cells)}
