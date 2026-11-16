"""Experiments defined in YAML: definitions/NAME.yaml is the source of every
experiment file (experiments/NAME.json, or smoke/NAME.json).

A definition names its specimen(s), its suite(s) and its arms, in one of
three ways:
- `vary`: each entry multiplies the arms; option names make profile names;
- `arms`: each arm spelled out with its settings;
- `profiles`: existing catalogue profiles reused by name.
`python3 -m zoo define definitions/NAME.yaml` writes what it implies into
the catalogue: a new specimen, one profile per new arm and the experiment
file. Existing specimens and profiles are reused when they match and are
never changed; a mismatch is an error. `--check` writes nothing and fails
when the catalogue does not match. docs/DEFINE.md has the format.
"""
import argparse
import itertools
import json
from pathlib import Path

from . import catalogue as cat_mod

ROOT = Path(__file__).resolve().parents[1]

# The development suite each tier plays (RULES 14).
TIERS = {'pilot': 'classes-18', 'small': 'classes-1800-small', 'medium': 'classes-1800-medium',
         'big': 'classes-1800-big', 'full': 'classes-1800-full'}

# Specimen defaults per repository; a definition can override any of them.
SPECIMEN_DEFAULTS = {
    'diegoami/borg-reborn-rs': {'kind': 'borg-rs', 'impl': 'rust', 'exact_turns': True,
                                'depth_stream': True, 'role': 'candidate'},
    'diegoami/borg-rs': {'kind': 'borg-rs', 'impl': 'rust', 'depth_stream': True, 'role': 'candidate'},
}

KEYS = {'name', 'file', 'issue', 'question', 'folder', 'description', 'prespecified', 'owner_authorization',
        'tier', 'suite', 'suites', 'specimen', 'specimens', 'settings', 'vary', 'arms', 'profiles',
        'profile_prefix', 'control', 'control_specimen', 'control_profile', 'extra'}


def load(path):
    import yaml  # only `zoo define` needs PyYAML; runners read the generated JSON
    d = yaml.safe_load(Path(path).read_text())
    if not isinstance(d, dict):
        raise ValueError(f'{path}: a definition is a YAML mapping')
    unknown = sorted(set(d) - KEYS)
    if unknown:
        raise ValueError(f'{path}: unknown keys {unknown}; allowed: {sorted(KEYS)}')
    if 'name' not in d:
        raise ValueError(f'{path}: missing \'name\'')
    if sum(k in d for k in ('specimen', 'specimens')) != 1:
        raise ValueError(f'{path}: give exactly one of "specimen" or "specimens"')
    if sum(k in d for k in ('vary', 'arms', 'profiles')) != 1:
        raise ValueError(f'{path}: give exactly one of "vary", "arms" or "profiles"')
    if not any(k in d for k in ('suite', 'suites')) and d.get('tier') not in TIERS:
        raise ValueError(f'{path}: tier must be one of {list(TIERS)} (or give "suite"/"suites")')
    return d


def option_name(name):
    """An arm or option name as text. YAML reads unquoted on/off/yes/no as
    booleans, which would make silent names like "True"; quote them instead."""
    if isinstance(name, bool):
        raise ValueError(f'option name {name!r} was read as a boolean: quote it (\'on\', \'off\')')
    if not isinstance(name, (str, int)):
        raise ValueError(f'option name {name!r} must be text')
    return str(name)


def profile_name(d, names):
    prefix = d['name'] if d.get('profile_prefix') is None else d['profile_prefix']
    return '-'.join(([prefix] if prefix else []) + names)


def arms(d):
    """[(profile name, settings or None, option names)] in definition order.
    Settings are None for reused profiles (`profiles`)."""
    if 'profiles' in d:
        return [(p, None, [p]) for p in d['profiles']]
    base = dict(d.get('settings') or {})
    if 'arms' in d:
        return [(profile_name(d, [option_name(n)]), {**base, **(s or {})}, [option_name(n)])
                for n, s in d['arms'].items()]
    out = []
    for combo in itertools.product(*(list(dim.items()) for dim in d['vary'].values())):
        settings = dict(base)
        for _, s in combo:
            settings.update(s or {})
        names = [option_name(n) for n, _ in combo]
        out.append((profile_name(d, names), settings, names))
    return out


def specimens(d):
    """[(name, specimen block or None)]; None reuses a catalogue specimen."""
    out = []
    for s in ([d['specimen']] if 'specimen' in d else d['specimens']):
        if isinstance(s, str):
            out.append((s, None))
            continue
        s = dict(s)
        name = s.pop('name')
        spec = {**SPECIMEN_DEFAULTS.get(s.get('repository'), {}), **s}
        for key in ('repository', 'ref', 'kind'):
            if key not in spec:
                raise ValueError(f'specimen {name}: missing {key!r}')
        out.append((name, spec))
    return out


def suites(d):
    return d.get('suites') or [d.get('suite') or TIERS[d['tier']]]


def relative(path, root=ROOT):
    path = Path(path).resolve()
    try:
        return path.relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def target(d, root=ROOT):
    """The experiment file: folder/NAME.json, or folder/FILE when an older
    file's name differs from its experiment name."""
    return Path(root) / d.get('folder', 'experiments') / d.get('file', f"{d['name']}.json")


def experiment(d, path, profiles, root=ROOT):
    names = [p for p, _, _ in profiles]
    spec_names = [n for n, _ in specimens(d)]
    if 'control_profile' in d:
        control_profile = d['control_profile']
    elif d.get('control') is not None:
        wanted = d['control'] if isinstance(d['control'], list) else [d['control']]
        match = [p for p, _, opts in profiles if opts == [str(w) for w in wanted]]
        if len(match) != 1:
            raise ValueError(f"control {d['control']!r} names no single arm")
        control_profile = match[0]
    else:
        control_profile = names[0]
    exp = {'schema': 'borg-zoo/experiment@1', 'name': d['name']}
    if d.get('issue'):
        exp['issue'] = d['issue']
    exp['definition'] = relative(path, root)
    if d.get('question'):
        exp['question'] = d['question']
    exp['description'] = d.get('description') or (
        f"{d.get('question') or d['name']} Generated from {relative(path, root)}: "
        f"{len(names)} arms on {', '.join(spec_names)}, suite {', '.join(suites(d))}.")
    if d.get('prespecified'):
        exp['prespecified'] = d['prespecified'].strip()
    exp.update({'specimens': spec_names, 'profiles': names, 'suites': suites(d),
                'control': d.get('control_specimen') or spec_names[0], 'control_profile': control_profile})
    if d.get('owner_authorization'):
        exp['owner_authorization'] = d['owner_authorization']
    exp.update(d.get('extra') or {})
    return {k: v for k, v in exp.items() if v is not None}


def plan(path, root=ROOT):
    """(definition, problems, changes) for one definition file."""
    d = load(path)
    root = Path(root)
    specs = json.loads((root / 'catalogue/specimens.json').read_text())['specimens']
    profs = json.loads((root / 'catalogue/profiles.json').read_text())['profiles']
    problems, changes = [], []
    for name, spec in specimens(d):
        have = specs.get(name)
        if spec is None:
            if have is None:
                problems.append(f'specimen {name} is not in the catalogue')
        elif have is None:
            changes.append(('specimen', name, spec))
        else:
            problems += [f'specimen {name}: {k} is {have.get(k)!r} in the catalogue, {v!r} here'
                         for k, v in spec.items() if k != 'label' and have.get(k) != v]
    profiles = arms(d)
    for name, settings, opts in profiles:
        have = profs.get(name)
        if settings is None:
            if have is None:
                problems.append(f'profile {name} is not in the catalogue')
        elif have is None:
            desc = (f"borg-zoo#{d['issue']} " if d.get('issue') else '') + \
                f"({Path(path).name}): arm " + ', '.join(opts) + '.'
            changes.append(('profile', name, {'description': desc, 'settings': settings}))
        elif have.get('settings') != settings or set(have) - {'description', 'settings'}:
            problems.append(f'profile {name} exists with other settings; give the arm another name '
                            f'(profiles are frozen once used)')
    exp = experiment(d, path, profiles, root)
    file = target(d, root)
    if not file.exists():
        changes.append(('experiment', relative(file, root), exp))
    elif json.loads(file.read_text()) != exp:
        changes.append(('experiment-update', relative(file, root), exp))
    return d, problems, changes


def write(changes, root=ROOT):
    root = Path(root)
    specs_path, profs_path = root / 'catalogue/specimens.json', root / 'catalogue/profiles.json'
    specs, profs = json.loads(specs_path.read_text()), json.loads(profs_path.read_text())
    for kind, name, body in changes:
        if kind == 'specimen':
            specs['specimens'][name] = body
        elif kind == 'profile':
            profs['profiles'][name] = body
        else:
            (root / name).write_text(json.dumps(body, indent=2) + '\n')
    specs_path.write_text(json.dumps(specs, indent=2) + '\n')
    profs_path.write_text(json.dumps(profs, indent=2) + '\n')


def export(exp_path, root=ROOT):
    """A definition that regenerates an existing experiment file exactly."""
    root = Path(root)
    exp = json.loads(Path(exp_path).read_text())
    profs = json.loads((root / 'catalogue/profiles.json').read_text())['profiles']
    d = {'name': exp['name']}
    if exp.get('issue'):
        d['issue'] = exp['issue']
    folder = Path(exp_path).parent.name
    if folder != 'experiments':
        d['folder'] = folder
    if Path(exp_path).name != f"{exp['name']}.json":
        d['file'] = Path(exp_path).name
    for key in ('question', 'description', 'prespecified', 'owner_authorization'):
        if exp.get(key):
            d[key] = exp[key]
    d['specimens'] = list(exp['specimens'])
    d['suites'] = list(exp['suites'])
    plain = all(set(profs[p]) <= {'description', 'settings'} for p in exp['profiles'])
    if plain:
        d['profile_prefix'] = ''
        d['arms'] = {p: dict(profs[p].get('settings', {})) for p in exp['profiles']}
    else:
        d['profiles'] = list(exp['profiles'])
    d['control_specimen'] = exp['control']
    d['control_profile'] = exp.get('control_profile', exp['profiles'][0])
    done = {'schema', 'name', 'issue', 'definition', 'question', 'description', 'prespecified',
            'owner_authorization', 'specimens', 'suites', 'profiles', 'control', 'control_profile'}
    extra = {k: v for k, v in exp.items() if k not in done}
    if 'control_profile' not in exp:
        extra['control_profile'] = None  # the file has none; keep it absent
    if extra:
        d['extra'] = extra
    return d


def dump(d):
    import yaml

    class Literal(str):
        pass

    def literal(dumper, s):
        return dumper.represent_scalar('tag:yaml.org,2002:str', s, style='|' if '\n' in s or len(s) > 100 else None)
    yaml.SafeDumper.add_representer(Literal, literal)

    def wrap(v):
        if isinstance(v, str) and len(v) > 100:
            return Literal(v)
        if isinstance(v, dict):
            return {k: wrap(x) for k, x in v.items()}
        if isinstance(v, list):
            return [wrap(x) for x in v]
        return v
    return yaml.safe_dump(wrap(d), sort_keys=False, allow_unicode=False, width=100)


def main(argv=None):
    ap = argparse.ArgumentParser(prog='python3 -m zoo define', description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('definition', nargs='*')
    ap.add_argument('--check', action='store_true', help='write nothing; fail if the catalogue differs')
    ap.add_argument('--update', action='store_true', help='allow rewriting an existing experiment file')
    ap.add_argument('--export', nargs='*', metavar='EXPERIMENT_JSON',
                    help='write definitions/NAME.yaml for experiment files that have none')
    a = ap.parse_args(argv)
    if a.export is not None:
        for f in a.export:
            d = export(f)
            out = ROOT / 'definitions' / f"{d['name']}.yaml"
            if out.exists():
                print(f'{f}: {out.relative_to(ROOT)} exists; not overwritten')
                continue
            out.write_text(f"# Exported from {Path(f).as_posix()}; edit here, then run python3 -m zoo define.\n"
                           + dump(d))
        return 0
    failed = False
    for path in a.definition:
        d, problems, changes = plan(path)
        for p in problems:
            print(f'{path}: {p}')
        if a.check:
            for kind, name, _ in changes:
                print(f'{path}: catalogue lacks {kind} {name}')
            failed |= bool(problems or changes)
            continue
        blocked = [c for c in changes if c[0] == 'experiment-update' and not a.update]
        if problems or blocked:
            for _, name, _ in blocked:
                print(f'{path}: {name} differs; rerun with --update to rewrite it')
            failed = True
            continue
        write(changes)
        exp = cat_mod.experiment(target(d))  # validates
        print(json.dumps({'definition': path, 'experiment': d['name'], 'issue': d.get('issue'),
                          'arms': len(exp['profiles']), 'cells': len(cat_mod.cells(exp)),
                          'written': [f'{k} {n}' for k, n, _ in changes]}))
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
