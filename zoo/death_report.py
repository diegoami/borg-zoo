"""Death report for a pilot or verysmall run: replay, evidence, README.

    python3 -m zoo.death_report --experiment experiments/NAME.json --run RUN_ID

Reads the run's cells from the results branch, groups the deaths by game
(class, seed, play hash), downloads the run's own build artifact, replays one
arm per distinct death (plus the control arm, for the point where play
splits) with traces kept, checks every replayed play hash against CI, and
writes reports/NAME-deaths/ with a README and per-death evidence: what was
worn and carried at death, the last game messages and Borg notes, the trip
decisions, and the first log line where the game differs from the control.

borg-rs specimens only (the kept files are borg-rs's). The README ends with
an Observations section for the session to write by reading the evidence;
nothing here is a causal diagnosis.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from . import catalogue as cat_mod

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = ('Character Equipment', 'Character Quiver', 'Character Inventory', 'Home Inventory (page 1)')
MESSAGE = re.compile(r'\s*(\d+)\s+(\d+)\s+\d+\s(.*)')
COUNTED = {
    'Cure potions quaffed': re.compile(r'# Quaffing Potions? of Cure'),
    'Phase Door read': re.compile(r'# Reading Scrolls? of Phase Door'),
    'Unknown potions quaffed': re.compile(r'# Quaffing unknown potion'),
    'Healing (outmatched) notes': re.compile(r'# Healing \(outmatched\)'),
    'Potion of Speed quaffed': re.compile(r'# Quaffing Potions? of Speed'),
    'Failed teleports': re.compile(r'failed to teleport'),
    'Trip returns': re.compile(r'# Trip: return'),
}


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def run_cells(name, run_id):
    git('fetch', '-q', 'origin', 'results')
    dirs = [d for d in git('ls-tree', '--name-only', f'origin/results:results/{name}/').split()
            if d.startswith(f'{run_id}-')]
    if not dirs:
        raise SystemExit(f'no results for {name} run {run_id} on the results branch')
    text = git('show', f'origin/results:results/{name}/{sorted(dirs)[-1]}/cells.jsonl')
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def death_groups(cells):
    """One group per distinct dying game: the arms that play it, in profile order."""
    groups = {}
    for c in cells:
        if c['outcome'] == 'death':
            groups.setdefault((c['class'], c['seed'], c['play_sha256']), []).append(c)
    return list(groups.values())


def dump_sections(text):
    """Named sections of a Borg.map death dump, without empty slots."""
    out, name = {}, None
    for line in text.splitlines():
        m = re.match(r'\s*\[(.+)\]\s*$', line)
        if m:
            name = m.group(1)
            out[name] = []
        elif name and line.strip() and '(nothing)' not in line:
            out[name].append(line.rstrip())
    return {k: out.get(k, []) for k in SECTIONS}


def messages(path):
    rows = []
    for line in Path(path).read_text(errors='replace').splitlines():
        m = MESSAGE.match(line)
        if m:
            rows.append((int(m.group(2)), m.group(3), line))
    return rows


def counts(rows):
    out = {}
    for label, rx in COUNTED.items():
        out[label] = sum(1 for _, text, _ in rows if rx.search(text))
    down = 0
    for i, (_, text, _) in enumerate(rows):
        if COUNTED['Trip returns'].search(text) and any(
                'no up stairs found, going down' in t for _, t, _ in rows[i + 1:i + 6]):
            down += 1
    out['Trip returns followed by "going down"'] = down
    return out


def first_split(rows, control_rows, context=6):
    for i, (a, b) in enumerate(zip(rows, control_rows)):
        if a[2] != b[2]:
            return {'line': i, 'turn': a[0],
                    'arm': [r[2] for r in rows[max(0, i - context):i + context]],
                    'control': [r[2] for r in control_rows[i:i + context]]}
    return None


def replay(exp_path, exp, arm_profile, build, work, jobs):
    out = work / f'cells-{arm_profile}.jsonl'
    if not out.exists():
        subprocess.run([sys.executable, '-m', 'zoo', 'run', '--experiment', str(exp_path),
                        '--specimen', exp['specimens'][0], '--arm', f"{exp['specimens'][0]}:{arm_profile}",
                        '--build', str(build), '--work', str(work / arm_profile), '--out', str(out),
                        '--jobs', str(jobs), '--keep'], cwd=ROOT, check=True)
    return {(c['profile'], c['seed']): c for c in map(json.loads, out.read_text().splitlines())}


def handover(exp, specimen, spec, run, reruns):
    """README section for a borg-reborn-rs session that works on these deaths."""
    return ['## Handover: working on these deaths in the Borg\'s repository', '',
            f"For a session in {spec.get('repository', 'the specimen repository')} that changes parameters or code "
            'against these deaths. That repository owns the Borg; the zoo only measures, and any change is measured '
            'here later as a new specimen.', '',
            f"- **Build:** `{spec.get('repository')}` at `{spec['ref']}` (zoo specimen `{specimen}`): "
            '`BORG_IMPL=rust harness/build.sh`, or the run\'s CI artifact: '
            f'`gh run download {run} -R diegoami/borg-zoo -n build-{specimen}`.',
            '- **Settings:** each death\'s exact `user/borg.txt` is `evidence/<death>/borg.txt` (with its plan file, if '
            'the arm sets `borg_plan`, from the specimen\'s `harness/plans/`).',
            '- **Evidence:** `evidence/<death>/`: inventory at death, last 300 log lines, trip decisions, summary.', '',
            'Re-run one death from the built `game/` directory, with no `BORG_*` variables set and `OUT` holding '
            '`user/borg.txt` and empty `save/ archive/ panic/ scores/`:', '',
            fence(['env -u BORG_PROFILE -u BORG_CORE -u BORG_ERRAND -u BORG_PLAN TZ=UTC LANG=C.UTF-8 LC_ALL=C.UTF-8 \\',
                   '  ./angband -mborgh -n -uBorg -duser=$OUT/user -dsave=$OUT/save -darchive=$OUT/archive '
                   '-dpanic=$OUT/panic -dscores=$OUT/scores \\',
                   '  -- -seed SEED -race R -class C -turns 100000 -keylog $OUT/keys.log -summary $OUT/summary.json '
                   '-menu-letters \\',
                   '  -exact-turns -statelog $OUT/state.log -msglog $OUT/messages.log']), '',
            '`sha256sum keys.log` must start with the play hash below, or it is not the same game.', '',
            '| Death | Seed | -race | -class | Arm | Play sha256 |', '|---|---|---|---|---|---|', *reruns, '',
            f"In borg-zoo, `python3 -m zoo.death_report --experiment experiments/{exp['name']}.json --run {run}` replays and "
            'checks them all. After a change: a PR in the Borg\'s repository, then ask the borg-zoo session for a new '
            'specimen at the merged commit and a pilot (or verysmall) of the same arms.', '']


def fence(lines):
    return '```\n' + '\n'.join(lines) + '\n```'


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--experiment', required=True)
    p.add_argument('--run', required=True, help='the GitHub Actions run id')
    p.add_argument('--work', help='scratch directory for the build and replays (default: /tmp)')
    p.add_argument('--out', help='report directory (default: reports/NAME-deaths)')
    p.add_argument('--jobs', type=int, default=18)
    p.add_argument('--tail', type=int, default=30, help='messages and notes shown per death')
    a = p.parse_args(argv)

    exp_path = (ROOT / a.experiment).resolve()
    exp = json.loads(exp_path.read_text())
    name, specimen = exp['name'], exp['specimens'][0]
    cat = cat_mod.catalogue()
    if cat['specimens']['specimens'][specimen].get('kind') != 'borg-rs':
        raise SystemExit('zoo.deaths reads borg-rs evidence only')
    control = exp.get('control_profile')
    work = Path(a.work or f'/tmp/zoo-deaths-{name}-{a.run}').resolve()
    out = Path(a.out or ROOT / 'reports' / f'{name}-deaths')
    work.mkdir(parents=True, exist_ok=True)

    cells = run_cells(name, a.run)
    groups = death_groups(cells)
    if not groups:
        print(json.dumps({'experiment': name, 'run': a.run, 'deaths': 0}))
        return 0
    build = work / 'specimens' / specimen
    if not build.exists():
        subprocess.run(['gh', 'run', 'download', a.run, '-R', 'diegoami/borg-zoo', '-n', f'build-{specimen}',
                        '-D', str(work / 'dl')], check=True)
        (work / 'specimens').mkdir(exist_ok=True)
        subprocess.run(['tar', '-C', str(work / 'specimens'), '-xzf',
                        str(work / 'dl' / f'build-{specimen}.tgz')], check=True)

    ci = {(c['profile'], c['seed']): c for c in cells}
    arms = sorted({g[0]['profile'] for g in groups} | ({control} if control else set()))
    replayed, mismatched = {}, []
    for arm in arms:
        got = replay(exp_path, exp, arm, build, work, a.jobs)
        replayed.update(got)
        mismatched += [k for k, c in got.items() if c['play_sha256'] != ci[k]['play_sha256']]

    def cell_dir(profile, seed):
        c = ci[(profile, seed)]
        return work / profile / cat_mod.cell_key(c)

    out.mkdir(parents=True, exist_ok=True)
    total = sum(c['outcome'] == 'death' for c in cells)
    lines = [f'# Deaths in {name}' + (f" (borg-zoo#{exp['issue']})" if exp.get('issue') else ''), '',
             f'Run [{a.run}](https://github.com/diegoami/borg-zoo/actions/runs/{a.run}), specimen `{specimen}`. '
             'A reading aid written by `python3 -m zoo.death_report`, not a cemetery entry or a causal diagnosis.', '',
             f'{total} deaths in {len(cells)} games, {len(groups)} distinct dying games. Replayed locally from the run\'s '
             f'own build artifact, arms {", ".join(f"`{x}`" for x in arms)}: '
             + ('every replayed play hash matches CI.' if not mismatched else
                f'**{len(mismatched)} replayed games do not match CI**: {mismatched}.'), '',
             '| Game | Dies in | Killed by | Char level | Dungeon level | Game turn | Keys |',
             '|---|---|---|---|---|---|---|']
    sections, reruns = [], []
    for g in groups:
        c = g[0]
        slug = f"{c['class'].lower()}-{c['seed']}-{c['play_sha256'][:8]}"
        d = cell_dir(c['profile'], c['seed'])
        ev = out / 'evidence' / slug
        ev.mkdir(parents=True, exist_ok=True)
        dump = dump_sections((d / 'archive/Borg.map').read_text(errors='replace'))
        rows = messages(d / 'messages.log')
        notes = [r[2] for r in rows if r[1].startswith('#')]
        game = [r[2] for r in rows if not r[1].startswith('#')]
        trips = [r[2] for r in rows if r[1].startswith('# Trip:')]
        state = (d / 'state.log').read_text().splitlines()[-1] if (d / 'state.log').exists() else ''
        borg_log = (d / 'archive/borg-log.txt').read_text(errors='replace').strip()
        (ev / 'borg-log.txt').write_text(borg_log + '\n')
        (ev / 'inventory-at-death.txt').write_text(
            '\n'.join(f'[{k}]\n' + '\n'.join(v) for k, v in dump.items()) + '\n')
        (ev / 'messages-tail.log').write_text('\n'.join(r[2] for r in rows[-300:]) + '\n')
        (ev / 'trip-decisions.log').write_text('\n'.join(trips) + '\n')
        (ev / 'summary.json').write_text((d / 'summary.json').read_text())
        (ev / 'borg.txt').write_text((d / 'user/borg.txt').read_text())
        reruns.append(f"| [{c['class']} {c['seed']}](#{slug}) | {c['seed']} | {cat_mod.RACES.index(c['race'])} ({c['race']}) "
                      f"| {cat_mod.CLASSES.index(c['class'])} | `{c['profile']}` | `{c['play_sha256'][:16]}` |")

        in_arms = [x['profile'] for x in g]
        others = [x for x in cells if x['class'] == c['class'] and x['seed'] == c['seed'] and x['profile'] not in in_arms]
        split = None
        if control and control not in in_arms:
            split = first_split(rows, messages(cell_dir(control, c['seed']) / 'messages.log'))
        f = c['final']
        lines.append(f"| [{c['class']} {c['race']} {c['seed']}](#{slug}) | {', '.join(f'`{x}`' for x in in_arms)} | "
                     f"{c['cause']} | {f['max_level']} | {f['depth']} (max {f['max_depth']}) | {f['turn']} | {f['keys']} |")
        sec = [f'<a id="{slug}"></a>', f"## {c['class']} {c['race']} {c['seed']}: {c['cause']}", '',
               f"- Dies in: {', '.join(f'`{x}`' for x in in_arms)}, the same game (play `{c['play_sha256'][:16]}`).",
               '- Same start elsewhere: ' + (', '.join(f"`{x['profile']}` {x['outcome']}" +
                                                       (' (same play)' if x['play_sha256'] == c['play_sha256'] else '')
                                                       for x in others) or 'none') + '.',
               f'- Last state line: `{state}`', '',
               '- ' + '; '.join(f'{k}: {v}' for k, v in counts(rows).items()) + '.', '',
               '### Worn and carried at death', '', fence(borg_log.splitlines()[1:4]), '']
        for k, v in dump.items():
            if v:
                sec += [f'**{k}**', '', fence(v), '']
        if split:
            sec += [f"### Where it splits from the control `{control}` (game turn {split['turn']})", '',
                    fence(split['arm']), '', 'Control at the same point:', '', fence(split['control']), '']
        if trips:
            sec += ['### Last trip decisions', '', fence(trips[-8:]), '']
        sec += [f'### Last {a.tail} game messages', '', fence(game[-a.tail:]), '',
                f'### Last {a.tail} Borg notes', '', fence(notes[-a.tail:]), '']
        sections.append('\n'.join(sec))
    lines += ['', '## Observations', '',
              '_To be written by the session after reading the evidence: what each death had and did not use, '
              'and what the varied setting changed. Observations only, no diagnosis._', '']
    lines += handover(exp, specimen, cat['specimens']['specimens'][specimen], a.run, reruns)
    (out / 'README.md').write_text('\n'.join(lines) + '\n' + '\n'.join(sections))
    print(json.dumps({'experiment': name, 'run': a.run, 'deaths': total, 'distinct': len(groups),
                      'replayed_arms': arms, 'mismatched': len(mismatched), 'report': str(out / 'README.md')}))
    return 1 if mismatched else 0


if __name__ == '__main__':
    sys.exit(main())
