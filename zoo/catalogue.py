"""Specimens, profiles, suites and experiments: loading, validation, cells."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORCED = 'borg_cheat_death = FALSE\nborg_respawn_winners = FALSE\n'

# The mode cutoff (borg-zoo#54): better-borg-c fd683ced (PR 302) made
# borg_munchkin_by_class default TRUE, so specimens before it do not carry
# the class rule and play a different game under the same profile name.
# Catalogue entries carry their side as "mode_side"; these constants resolve
# entries recorded before the field existed (old run snapshots).
MODE_CUTOFF = 'fd683cedbc74e1cbfabed276526964d0b04ee93c'
MODE_CUTOFF_DATE = '2026-11-10'
MODE_CUTOFF_HARNESS = '9ca986616cca66fe0f09de2b4cdc48591f94d33d'
MODE_CUTOFF_REPOSITORY = 'diegoami/better-borg-c'
MODE_CUTOFF_POST = {
    'fd683cedbc74e1cbfabed276526964d0b04ee93c',  # 4.2.6-bbc-munchkin-by-class
    '017e038e8726a7a423887a366b5d40e89c0550a1',  # 4.2.6-bbc-m8
    '33207fbeeb582e67d6b18e9f40613617667905ae',  # 4.2.6-bbc-m9
    '6944d88e87d02e9d24e85438d25f0c6ef864c170',  # 4.2.6-bbc-m10
    '9ca986616cca66fe0f09de2b4cdc48591f94d33d',  # 4.2.6-bbc-9ca98661
    '39268ca8a470d1cbd44de27bf1fd1b3ee403bada',  # 4.2.6-bbc-m11
}

# The settings whose built-in default drifts across the cutoff, plus the
# modes introduced with it: a profile that names none of them leaves the
# modes on the build's own default, which is exactly what the observer
# cannot verify (issue #54).
MODE_SETTINGS = ('borg_munchkin_start', 'borg_munchkin_by_class',
                 'borg_self_lunal', 'borg_lunal_mode')


def _load(path):
    return json.loads(Path(path).read_text())


SEED_MAX = 2 ** 31 - 1

# Birth menu order at the pin (lib/gamedata/p_race.txt and class.txt).
RACES = ['Human', 'Half-Elf', 'Elf', 'Hobbit', 'Gnome', 'Dwarf', 'Half-Orc', 'Half-Troll',
         'Dunadan', 'High-Elf', 'Kobold']
CLASSES = ['Warrior', 'Mage', 'Druid', 'Priest', 'Necromancer', 'Paladin', 'Rogue', 'Ranger',
           'Blackguard']


def character(suite, seed):
    """The (race, class) a suite assigns to a seed, or None.

    birth "fixed" is Human Warrior; "random" lets the seeded game choose (None);
    "assigned" deals classes in turn over the seed list and cycles races once
    per round of classes, so every class meets every race. A subset suite
    carries its parent's assignment per seed.
    """
    if 'assigned_characters' in suite:
        race, cls = suite['assigned_characters'][str(seed)]
        return (race, cls)
    birth = suite['birth']
    if birth == 'fixed':
        return ('Human', 'Warrior')
    if birth == 'random':
        return None
    if birth == 'assigned':
        chars = suite['characters']
        classes, races = chars['classes'], chars['races']
        i = suite['seeds'].index(seed)
        return (races[(i // len(classes)) % len(races)], classes[i % len(classes)])
    raise ValueError(f'unknown birth rule {birth!r}')


def _rule_seeds(name, count, used):
    """Deterministic, well-spread seeds for a rule suite, skipping any seed
    another suite already uses. The rule is part of the frozen suite."""
    out, i = [], 0
    while len(out) < count:
        digest = hashlib.sha256(f'borg-zoo:{name}:{i}'.encode()).digest()
        seed = int.from_bytes(digest[:8], 'big') % (SEED_MAX - 1) + 1
        if seed not in used:
            used.add(seed)
            out.append(seed)
        i += 1
    return out


def expand_suites(suites):
    """Expand rule suites into seed lists, in catalogue order.

    Listed seeds are reserved first, so a rule suite never reuses a seed of
    any other suite.
    """
    used = {seed for s in suites.values() for seed in s.get('seeds', [])}
    out = {}
    for name, suite in suites.items():
        suite = dict(suite)
        if 'subset' in suite:
            parent = out.get(suite['subset']['suite'])
            if parent is None:
                raise ValueError(f'{name}: subset of an unknown or later suite')
            wanted = suite['subset']['class']
            chars = {seed: character(parent, seed) for seed in parent['seeds']}
            if any(c is None for c in chars.values()):
                raise ValueError(f'{name}: the parent suite does not assign characters')
            suite['seeds'] = [seed for seed in parent['seeds'] if chars[seed][1] == wanted]
            suite['birth'] = 'assigned'
            suite['assigned_characters'] = {str(seed): list(chars[seed]) for seed in suite['seeds']}
            out[name] = suite
            continue
        if suite.get('birth') == 'assigned':
            chars = suite.get('characters') or {}
            for race in chars.get('races', []):
                if race not in RACES:
                    raise ValueError(f'{name}: unknown race {race!r}')
            for cls in chars.get('classes', []):
                if cls not in CLASSES:
                    raise ValueError(f'{name}: unknown class {cls!r}')
            if not chars.get('races') or not chars.get('classes'):
                raise ValueError(f'{name}: assigned birth needs races and classes')
        if 'seed_rule' in suite:
            rule = suite['seed_rule']
            if rule.get('generator') != 'sha256-v1':
                raise ValueError(f'{name}: unknown seed generator {rule.get("generator")!r}')
            suite['seeds'] = _rule_seeds(name, rule['count'], used)
        out[name] = suite
    return out


def catalogue(root=ROOT):
    root = Path(root)
    return {
        'specimens': _load(root / 'catalogue/specimens.json'),
        'profiles': _load(root / 'catalogue/profiles.json')['profiles'],
        'suites': expand_suites(_load(root / 'catalogue/suites.json')['suites']),
    }


def mode_side(spec):
    """Which side of the mode cutoff (MODE_CUTOFF) a specimen plays on:
    "pre" (no munchkin-by-class rule), "post" (the rule is the default), or
    None for engines the cutoff does not apply to (borg-rs, Mandos, Neo).

    The catalogue entry's own "mode_side" wins; better-borg-c entries
    recorded before the field fall back to the commit set above.
    """
    side = spec.get('mode_side')
    if side in ('pre', 'post'):
        return side
    if spec.get('repository') == MODE_CUTOFF_REPOSITORY:
        return 'post' if spec.get('ref') in MODE_CUTOFF_POST else 'pre'
    return None


def mode_explicit(profile):
    """True when a profile names the mode settings itself: directly, per
    class ("by_class"), or through the shipped borg.txt, which spells the
    build's defaults out as text. Only "default" ({}), and profiles of
    single unnamed settings that leave every mode alone, stay implicit."""
    if 'by_class' in profile or profile.get('base') == 'shipped':
        return True
    return bool(set(profile.get('settings', {})) & set(MODE_SETTINGS))


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
        profile = cat['profiles'][name]
        if 'by_class' in profile:
            for cls in profile['by_class']:
                if cls not in CLASSES:
                    raise ValueError(f'{name}: unknown class {cls!r}')
            for part in profile_parts(cat, name):
                if part not in cat['profiles'] or 'by_class' in cat['profiles'][part]:
                    raise ValueError(f'{name}: {part!r} must be an ordinary profile')
            for suite in exp['suites']:
                if cat['suites'][suite]['birth'] == 'random':
                    raise ValueError(f'{name} depends on the class; suite {suite} has random birth')
    for name in exp['suites']:
        if name not in cat['suites']:
            raise ValueError(f'unknown suite: {name}')
    for name in exp['specimens']:
        if specimens[name].get('pending'):
            raise ValueError(f'{name} cannot be measured yet: {specimens[name]["pending"]}')
        if specimens[name].get('kind') == 'neo-original':
            if any(cat['profiles'][p].get('settings') or cat['profiles'][p].get('base') for p in exp['profiles']):
                raise ValueError('neo-original benchmark accepts only original default settings')
            if any(cat['suites'][n]['birth'] == 'random' for n in exp['suites']):
                raise ValueError('neo-original benchmark requires explicitly assigned birth')
        if specimens[name].get('kind') == 'mandos':
            from . import mandos
            for suite in exp['suites']:
                if cat['suites'][suite]['birth'] == 'random':
                    raise ValueError(f'{name}: Mandos plays its first birth as Human Warrior; it has no random '
                                     f'birth (suite {suite})')
            for prof in (p for name in exp['profiles'] for p in profile_parts(cat, name)):
                bad = mandos.unsupported_settings(cat['profiles'][prof])
                if bad:
                    raise ValueError(f'{name}: profile {prof} has settings Mandos cannot apply: {", ".join(bad)}')
        if specimens[name].get('kind') == 'borg-rs':
            for suite in exp['suites']:
                if cat['suites'][suite]['birth'] == 'random':
                    raise ValueError(f'{name}: the borg-rs adapter has no random birth (suite {suite})')
            for prof in (p for name in exp['profiles'] for p in profile_parts(cat, name)):
                if cat['profiles'][prof].get('base') == 'shipped':
                    raise ValueError(f'{name}: profile {prof} needs a shipped borg.txt base, '
                                     'which the borg-rs adapter takes from harness/borg.txt only')
    for suite in exp['suites']:
        if cat['suites'][suite].get('role') == 'sealed' and not exp.get('unsealed_by_owner'):
            raise ValueError(f'suite {suite} is sealed: only an experiment the owner has opened it for '
                             '("unsealed_by_owner": "<date and reason>") may use it')
    if exp['control'] not in exp['specimens']:
        raise ValueError('control must be one of the experiment specimens')
    if exp.get('control_profile', exp['profiles'][0]) not in exp['profiles']:
        raise ValueError('control_profile must be one of the experiment profiles')
    # Mode cutoff (borg-zoo#54): "default" names a different game on either
    # side of better-borg-c fd683ced, and the observer can only verify named
    # settings, so a mode that was never named can silently change play. An
    # experiment recorded before the cutoff says so ("pre_cutoff": "<date and
    # reason>") and keeps its arms as run; anything measured now must name a
    # mode profile on every post-cutoff better-borg-c specimen, and no
    # profile may name borg_munchkin_by_class for a build that predates it
    # (the build ignores the unknown line, and every cell would config_error).
    sides = {name: mode_side(specimens[name]) for name in exp['specimens']}
    if not exp.get('pre_cutoff'):
        if any(side == 'post' for side in sides.values()):
            for name in exp['profiles']:
                if not mode_explicit(cat['profiles'][name]):
                    raise ValueError(f'profile {name} leaves the modes unnamed: every experiment whose '
                                     f'better-borg-c specimens play after the mode cutoff ({MODE_CUTOFF[:9]}, '
                                     'PR 302) must name a mode profile (issue #54)')
        for name, side in sides.items():
            if side != 'pre':
                continue
            for prof in (p for p_ in exp['profiles'] for p in profile_parts(cat, p_)):
                if 'borg_munchkin_by_class' in cat['profiles'][prof].get('settings', {}):
                    raise ValueError(f'specimen {name} predates the mode cutoff and has no '
                                     f'borg_munchkin_by_class; profile {prof} names it, so every '
                                     'cell would be a config_error (issue #54)')
        for prof in (p for p_ in exp['profiles'] for p in profile_parts(cat, p_)):
            settings = cat['profiles'][prof].get('settings', {})
            if settings.get('borg_munchkin_by_class') is True and settings.get('borg_munchkin_start') is False:
                raise ValueError(f'profile {prof} names borg_munchkin_start FALSE while the class rule '
                                 '(borg_munchkin_by_class TRUE) forces it for Warrior, Druid and Ranger - '
                                 'leave borg_munchkin_start unnamed (issue #54, bbc-explicit-smoke run '
                                 '42841000338)')
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


def resolve_profile(cat, cell):
    """(name, profile) the cell actually plays.

    A class-dependent profile ("by_class": {class: profile}, "otherwise":
    profile) picks one ordinary profile from the class the suite assigns to
    the seed (fixed birth is a Warrior). It needs a birth that fixes the class
    before play.
    """
    profile = cat['profiles'][cell['profile']]
    if 'by_class' not in profile:
        return cell['profile'], profile
    character_ = character(cat['suites'][cell['suite']], cell['seed'])
    if character_ is None:
        raise ValueError(f"profile {cell['profile']} depends on the class, which random birth does not fix")
    name = profile['by_class'].get(character_[1], profile['otherwise'])
    return name, cat['profiles'][name]


def profile_parts(cat, name):
    """The ordinary profiles a profile can play: itself, or a class-dependent profile's choices."""
    profile = cat['profiles'][name]
    if 'by_class' not in profile:
        return [name]
    return sorted({*profile['by_class'].values(), profile['otherwise']})


def profile_sha256(profile):
    """Hash of the profile definition (the exact file is hashed per run)."""
    return hashlib.sha256(json.dumps(profile, sort_keys=True).encode()).hexdigest()


def expected_options(profile):
    """Effective values the observer must report, as integers."""
    return {name: int(value) for name, value in profile['settings'].items()}


def parse_arm(text):
    """'specimen:profile' -> (specimen, profile)."""
    specimen, sep, profile = (text or '').partition(':')
    if not sep or not specimen or not profile:
        raise ValueError(f'arm must be SPECIMEN:PROFILE, got {text!r}')
    return specimen, profile


def arms(exp):
    """Every arm (specimen, profile) of an experiment, in order."""
    return [(s, p) for s in exp['specimens'] for p in exp['profiles']]


def load_experiment(path, arm=None, cat=None):
    """The experiment file, validated whole; with `arm` ("specimen:profile"),
    narrowed to that one arm. A narrowed experiment keeps the experiment's
    name as its tag, so its results sit beside the other arms' of the same
    experiment and the dashboard consolidates them; 'full' keeps the whole
    definition for that step."""
    cat = cat or catalogue()
    exp = experiment(path, cat)
    if not arm:
        return exp
    specimen, profile = parse_arm(arm)
    if (specimen, profile) not in arms(exp):
        raise ValueError(f'{arm} is not an arm of {exp["name"]}')
    full = {k: v for k, v in exp.items() if k != 'full'}
    return {**exp, 'specimens': [specimen], 'profiles': [profile], 'control': specimen,
            'control_profile': profile, 'arm': f'{specimen}:{profile}', 'full': full}


def cells(exp, cat=None):
    cat = cat or catalogue()
    out = []
    for suite_name in exp['suites']:
        suite = cat['suites'][suite_name]
        for specimen in exp['specimens']:
            for profile in exp['profiles']:
                for seed in suite['seeds']:
                    cell = {'specimen': specimen, 'profile': profile, 'suite': suite_name, 'seed': seed}
                    if suite['birth'] == 'assigned':
                        cell['race'], cell['class'] = character(suite, seed)
                    out.append(cell)
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
               'repository': specimens[s]['repository'], 'ref': specimens[s]['ref'],
               'engine_repository': specimens[s].get('engine_repository', ''),
               'engine_ref': specimens[s].get('engine_ref', ''),
               'toolkit_repository': specimens[s].get('toolkit_repository', ''),
               'toolkit_ref': specimens[s].get('toolkit_ref', '')}
              for s in exp['specimens']]
    runs = []
    for b in builds:
        arm_shards = exp.get('shards_by_specimen', {}).get(b['specimen'], shards)
        if not isinstance(arm_shards, int) or not 1 <= arm_shards <= 256:
            raise ValueError('shards must be an integer between 1 and 256')
        total = len([c for c in all_cells if c['specimen'] == b['specimen']])
        for index in range(min(arm_shards, total)):
            runs.append({**b, 'shard': index, 'shards': min(arm_shards, total)})
    if len(runs) > 256:
        raise ValueError('run matrix exceeds GitHub Actions limit of 256 jobs')
    return {'specimens': exp['specimens'], 'builds': builds, 'runs': runs, 'cells': len(all_cells)}
