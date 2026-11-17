"""Death report for a pilot or verysmall run: replay, evidence, README.

    python3 -m zoo.deaths --experiment experiments/NAME.json --run RUN_ID

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

"""Death bundles for borg-cemetery (borg-zoo#176).

A cell that ends in a natural death is replayed once, after its record is
written, with the logs a cemetery dossier needs: -msglog, -statelog and
BORG_RUN_DIR (the core's decision trace and parameters). The replay must
play the same keys as the cell: its keys.log sha256 is checked against the
record's play_sha256, and a bundle that differs is kept but marked
`not_reproduced`. The replay never changes the cell record.

A bundle directory is the run directory borg-cemetery's
scripts/native/export-death.py reads, so the cemetery imports it with
scripts/import_zoo_deaths.py:

  summary.json keys.log messages.log state.log
  trace-core.jsonl (last TRACE_KEEP lines) trace-core.lines (full count)
  params-core.json user/borg.txt user/<plan> config.txt BUILD_ID
  zoo-death.json   the cell record, the run, and the reproduction status

config.txt holds what the cemetery's rerun-death.py needs to rebuild the
cell's borg.txt (seed, race and class indices, cap, borg_txt_sha256, the
profile's settings, zoo_* provenance), in the format of the zoo dossiers
already in the cemetery.

Only borg-rs cells (borg-rs and borg-reborn-rs) are bundled. A death of
another harness kind is listed in the index as `unsupported`, never
dropped. An experiment opts out with "cemetery_deaths": false.
"""
import hashlib
import json
import os
import shutil
import subprocess
from collections import deque
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
            f"In borg-zoo, `python3 -m zoo.deaths --experiment experiments/{exp['name']}.json --run {run}` replays and "
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
             'A reading aid written by `python3 -m zoo.deaths`, not a cemetery entry or a causal diagnosis.', '',
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

SCHEMA = 'borg-zoo/death-bundle@1'
INDEX = 'index.jsonl'

# The core trace of a 100k-turn game is tens of MB; a dossier keeps its
# last 200 thinks, so the bundle keeps those TRACE_KEEP lines and writes the
# full count to trace-core.lines, which the cemetery reports as the total.
TRACE_KEEP = 200


def trim_trace(path, keep=TRACE_KEEP):
    """Keep the last KEEP lines of a JSONL trace; (total lines, sha256 of the full file)."""
    path = Path(path)
    if not path.is_file():
        return None
    digest, tail, total = hashlib.sha256(), deque(maxlen=keep), 0
    with path.open('rb') as f:
        for line in f:
            digest.update(line)
            total += 1
            tail.append(line)
    path.write_bytes(b''.join(tail))
    path.with_suffix('.lines').write_text(f'{total}\n')
    return {'lines': total, 'kept': len(tail), 'sha256': digest.hexdigest()}


def enabled(exp):
    return exp.get('cemetery_deaths', True) is not False


def wanted(record):
    """Whether a cell record is a death the cemetery should receive."""
    return record.get('outcome') == 'death'


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def config_text(record, cell, spec, profile, race_i, cls_i, borg_txt, plan_sha, provenance, streams=()):
    """config.txt in the zoo-dossier format (borg-cemetery rerun-death.py)."""
    lines = [f"seed={cell['seed']}", f'race_idx={race_i}', f'class_idx={cls_i}',
             f"turns={record['cap']}", f"exact_turns={1 if spec.get('exact_turns') else 0}",
             f'borg_txt_sha256={hashlib.sha256(borg_txt.encode()).hexdigest()}',
             f"zoo_experiment={provenance.get('experiment') or ''}",
             f"zoo_run={provenance.get('run_id') or ''}",
             f"zoo_profile={cell['profile']}", f"zoo_specimen={cell['specimen']}",
             f"zoo_suite={cell['suite']}"]
    if streams:
        # Observation-only record paths the cell set (a retained-evidence or
        # town-shadow cell); a rerun sets them too, to be the cell exactly.
        lines.append('zoo_record_streams=' + ','.join(streams))
    for name, value in sorted(profile['settings'].items()):
        if name == 'borg_plan':
            # The format of the zoo dossiers already in the cemetery. Its
            # rerun-death.py (borg-cemetery#59, zoo_plan) maps this back to
            # borg_plan = NAME and checks the dossier's errands_plan.txt
            # against errands_plan_sha256; the older harness path of that
            # tool reads borg_errands_plan_sha256 and cannot rerun zoo cells.
            lines += [f'borg_errands_plan=user/{value}', f'errands_plan_sha256={plan_sha}']
        else:
            lines.append(f'{name}={cat_mod.setting_value(value)}')
    return '\n'.join(lines) + '\n'


def record_streams(spec, profile, keep):
    """The record variables borgrs.run_cell set for a cell: {VARIABLE: file}."""
    if not (keep or spec.get('town_shadow_records')):
        return {}
    return {name: filename for setting, name, filename in (
        ('borg_town_plan', 'BORG_TOWN_PLAN_RECORD', 'town-plan.jsonl'),
        ('borg_trip_policy', 'BORG_TRIP_RECORD', 'trip.jsonl'))
        if profile['settings'].get(setting) == 1 or (setting == 'borg_town_plan' and spec.get('town_shadow_records'))}


def replay_borgrs(record, cell, build_dir, cat, out, provenance, keep=False):
    """Replay a borg-rs death cell into OUT with full logs; the bundle status."""
    from . import borgrs
    applied, profile = cat_mod.resolve_profile(cat, cell)
    suite = cat['suites'][cell['suite']]
    spec = cat['specimens']['specimens'][cell['specimen']]
    build_dir = Path(build_dir).resolve()
    manifest = json.loads((build_dir / 'build.json').read_text())
    if manifest['source_commit'] != spec['ref'] or manifest['impl'] != spec['impl']:
        raise ValueError(f'build {build_dir} does not match specimen {cell["specimen"]}')
    if out.exists():
        raise ValueError(f'refusing to overwrite death bundle: {out}')
    for d in ('user', 'save', 'archive', 'panic', 'scores'):
        (out / d).mkdir(parents=True)
    race, cls = cat_mod.character(suite, cell['seed']) or ('Human', 'Warrior')
    race_i, cls_i = cat_mod.RACES.index(race), cat_mod.CLASSES.index(cls)
    text = borgrs.config_text(build_dir, profile, race_i, cls_i)
    if hashlib.sha256(text.encode()).hexdigest() != record.get('config_sha256'):
        raise ValueError('borg.txt differs from the one the cell played')
    (out / 'user/borg.txt').write_text(text)
    plan = profile['settings'].get('borg_plan')
    plan_sha = borgrs.ship_plan(spec, manifest, build_dir, out, plan) if plan is not None else None
    game = build_dir / 'game'
    argv = borgrs.command(game / 'angband', out, cell, race_i, cls_i, suite, spec, keep=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith(borgrs.AMBIENT_PREFIX)}
    env.update(TZ='UTC', LANG='C.UTF-8', LC_ALL='C.UTF-8', BORG_RUN_DIR=str(out))
    # The cell's own record streams, if it had any: the replay is the cell's
    # configuration plus logs, not a different process configuration.
    streams = record_streams(spec, profile, keep)
    for name, filename in streams.items():
        env[name] = str(out / filename)
        (out / filename).touch()
    try:
        with (out / 'stderr.log').open('w') as err:
            rc = subprocess.run(argv, cwd=game, env=env, stdout=subprocess.DEVNULL, stderr=err,
                                timeout=suite['wall_seconds']).returncode
    except subprocess.TimeoutExpired:
        rc = 'timeout'
    if plan is not None and plan != 'errands_plan.txt':
        # export-death.py keeps user/errands_plan.txt as the dossier's plan;
        # copied after play, so the replay's user/ is the cell's.
        shutil.copy(out / 'user' / plan, out / 'user/errands_plan.txt')
    keys = out / 'keys.log'
    keys_sha = sha256(keys) if keys.exists() else None
    summary = json.loads((out / 'summary.json').read_text()) if (out / 'summary.json').exists() else {}
    if keys_sha and keys_sha == record.get('play_sha256') and summary.get('dead'):
        status, why = 'reproduced', None
    else:
        status = 'not_reproduced'
        why = (f'replay keys {str(keys_sha)[:12]}, cell played {str(record.get("play_sha256"))[:12]}'
               f'; exit {rc}; dead {summary.get("dead")}')
    (out / 'config.txt').write_text(config_text(record, cell, spec, profile, race_i, cls_i, text, plan_sha, provenance, sorted(streams)))
    (out / 'BUILD_ID').write_text(''.join(f'{k}={v}\n' for k, v in sorted((manifest.get('build_id') or {}).items())))
    for d in ('save', 'archive', 'panic', 'scores'):
        shutil.rmtree(out / d, ignore_errors=True)
    trace = trim_trace(out / 'trace-core.jsonl')
    return status, why, {'impl': spec['impl'], 'repository': spec.get('repository'), 'ref': spec['ref'],
                         'source_sha256': (manifest.get('build_id') or {}).get('source_sha256'),
                         'binary_sha256': manifest.get('binary_sha256'), 'replay_keys_sha256': keys_sha,
                         'trace_core': trace}


def bundle(record, cell, build_dir, cat, root, provenance, keep=False):
    """Write a death bundle under ROOT for a death record; its index entry."""
    key = cat_mod.cell_key(cell)
    spec = cat['specimens']['specimens'][cell['specimen']]
    kind = spec.get('kind', 'better-borg-c')
    entry = {'schema': SCHEMA, 'cell': key, 'seed': cell['seed'], 'suite': cell['suite'],
             'specimen': cell['specimen'], 'profile': cell['profile'], 'harness_kind': kind,
             'character': record.get('character'), 'cause': record.get('cause'),
             'final': record.get('final'), 'play_sha256': record.get('play_sha256'), **provenance}
    if kind != 'borg-rs':
        return {**entry, 'status': 'unsupported', 'error': f'no death bundle for harness kind {kind}'}
    # Absolute: the game runs with the game directory as its working directory
    # (compare.yml passes a relative --deaths; run 44098927907 lost all 11 bundles).
    out = Path(root).resolve() / key
    try:
        status, why, build = replay_borgrs(record, cell, build_dir, cat, out, provenance, keep=keep)
    except Exception as exc:  # reported per death, never dropped
        return {**entry, 'status': 'error', 'error': f'{type(exc).__name__}: {exc}'}
    entry = {**entry, 'status': status, 'error': why, 'build': build, 'bundle': key}
    (out / 'zoo-death.json').write_text(json.dumps({**entry, 'record': record}, indent=2, sort_keys=True) + '\n')
    return entry


def provenance_from_env(exp):
    """The run this bundle came from, from the GitHub Actions environment."""
    run_id = os.environ.get('GITHUB_RUN_ID')
    server, repo = os.environ.get('GITHUB_SERVER_URL'), os.environ.get('GITHUB_REPOSITORY')
    return {'experiment': exp['name'], 'run_id': run_id,
            'run_attempt': os.environ.get('GITHUB_RUN_ATTEMPT'),
            'run_url': f'{server}/{repo}/actions/runs/{run_id}' if run_id and server and repo else None,
            'zoo_commit': os.environ.get('GITHUB_SHA')}
