#!/usr/bin/env python3
"""Write a death report for one arm of a finished experiment, from a local replay.

The zoo's results branch keeps no key logs, so a death is replayed locally with
`python3 -m zoo run ... --keep` (the game is deterministic). This script reads
the kept work directory, checks every replayed keys.log against the recorded
play_sha256, and writes reports/NAME-deaths/README.md with one section per
death plus the evidence needed to read it (keys.log, summary.json, the last
messages). It reads; it changes no Borg and no result (RULES 1, 4).

  python3 tools/report-deaths.py --results RUN_DIR --work WORK --profile PROFILE \
      --experiment NAME --issue N --out reports/NAME-deaths
RUN_DIR holds the run's cells.jsonl (for example a checkout of the results branch).
"""
import argparse
import collections
import hashlib
import json
import re
import shutil
from pathlib import Path

MSG = re.compile(r'^(\d+) (\d+) (\d+) (.*)$')


def load_cells(path):
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]


def messages(path):
    out = []
    for line in path.read_text(errors='replace').splitlines():
        m = MSG.match(line)
        if m:
            out.append((int(m.group(1)), int(m.group(2)), m.group(4)))
    return out


def last_state(path):
    last = None
    for line in path.read_text().splitlines():
        if line.strip():
            last = line
    return last


def decisions(notes):
    """Counts of the Borg's own notes (lines starting with '#') worth reading."""
    keys = ['Healing (outmatched)', 'Quaffing', 'Flee', 'Fleeing', 'Phase', 'Scary guy', 'Boosting bravery',
            'Spent too long', 'Looking for up stairs', 'returning', 'Leaving']
    c = collections.Counter()
    for _, _, text in notes:
        if text.startswith('#'):
            for k in keys:
                if k in text:
                    c[k] += 1
    return c


def section(cell, d, sha_ok, others):
    seed = cell['seed']
    msgs = messages(d / 'messages.log')
    notes = [m for m in msgs if m[2].startswith('#')]
    game = [m for m in msgs if not m[2].startswith('#')]
    summ = json.loads((d / 'summary.json').read_text())
    st = last_state(d / 'state.log')
    pot = sum('Potion' in t and 'You have' in t for _, _, t in game)
    quaff = sum('Quaffing' in t for _, _, t in notes)
    heal = sum('Healing (outmatched)' in t for _, _, t in notes)
    phase = sum('Phase Door' in t and 'Reading' in t or 'You have no more Scrolls of Phase' in t for _, _, t in game)
    lines = [f"## Seed {seed}: {cell['class']} {cell['race']}, killed by {cell['cause']}", '',
             f"- Death: character level {summ['clevel']}, dungeon level {summ['depth']}, game turn {summ['game_turns']}, "
             f"{summ['keys']} keys, max HP {summ['max_hp']}.",
             f"- Replayed with the pinned build: keys.log sha256 {'matches' if sha_ok else 'DOES NOT match'} "
             f"the recorded play_sha256 `{cell['play_sha256'][:16]}`.",
             f"- Last state line (`turn x,y depth hp sp ...`): `{st}`",
             f"- `# Healing (outmatched).` notes: **{heal}**. Cure potion quaffs the Borg announced: {quaff}.",
             f"- Phase Door scrolls used up near the end: {phase}." if phase else '',
             f"- Same start in the other arms of this run: {others}", '',
             '### Last 30 game messages', '', '```']
    lines += [f'{k:>5} {t:>7} {m}' for k, t, m in game[-30:]]
    lines += ['```', '', '### Last 25 Borg notes', '', '```']
    lines += [f'{k:>5} {t:>7} {m}' for k, t, m in notes[-25:]]
    lines += ['```', '']
    return [l for l in lines if l is not None]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--results', required=True)
    ap.add_argument('--work', required=True)
    ap.add_argument('--profile', required=True)
    ap.add_argument('--experiment', required=True)
    ap.add_argument('--issue', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    cells = load_cells(Path(a.results) / 'cells.jsonl')
    arm = [c for c in cells if c['profile'] == a.profile]
    deaths = [c for c in arm if c['outcome'] == 'death']
    work = Path(a.work)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    by_seed = collections.defaultdict(dict)
    for c in cells:
        by_seed[c['seed']][c['profile']] = c
    head = [f'# Deaths in `{a.profile}`: {a.experiment}', '',
            f'Replay of one arm of [borg-zoo#{a.issue}](https://github.com/diegoami/borg-zoo/issues/{a.issue}). '
            f'{len(deaths)} deaths in {len(arm)} games. This is a reading aid, not a cemetery entry or a '
            f'causal diagnosis; the borg-cemetery tools register natural deaths.', '',
            '| seed | class, race | killed by | CL | DL | keys | turn | replay matches record |',
            '|---|---|---|---|---|---|---|---|']
    body = []
    for c in deaths:
        d = work / c['suite'] / c['specimen'] / a.profile / str(c['seed'])
        keys = (d / 'keys.log').read_bytes()
        ok = hashlib.sha256(keys).hexdigest() == c['play_sha256']
        f = c['final']
        head.append(f"| [{c['seed']}](#seed-{c['seed']}-{c['class'].lower()}-{c['race'].lower()}-killed-by-"
                    f"{re.sub('[^a-z0-9]+', '-', c['cause'].lower()).strip('-')}) | {c['class']} {c['race']} | "
                    f"{c['cause']} | {f['level']} | {f['depth']} | {f['keys']} | {f['turn']} | {'yes' if ok else '**no**'} |")
        others = ', '.join(f"{p.replace('reborn-', '')}: {o['outcome']}"
                           + (f" ({o['final']['keys']} keys, same play)" if o['play_sha256'] == c['play_sha256'] and p != a.profile else '')
                           for p, o in sorted(by_seed[c['seed']].items()) if p != a.profile)
        body += section(c, d, ok, others)
        ev = out / 'evidence' / str(c['seed'])
        ev.mkdir(parents=True, exist_ok=True)
        shutil.copy(d / 'keys.log', ev / 'keys.log')
        shutil.copy(d / 'summary.json', ev / 'summary.json')
        (ev / 'messages-tail.log').write_text(''.join(l + '\n' for l in (d / 'messages.log').read_text(errors='replace').splitlines()[-400:]))
    spec = arm[0]['specimen'] if arm else ''
    repro = ['## Replay', '', 'Build the pinned specimen and run the arm with the logs kept (the zoo holds the shared lock for heavy local runs, RULES 9):', '',
             '```sh', f'flock /tmp/angband-validation.lock python3 -m zoo build --specimen {spec} --source CHECKOUT_AT_PIN --out build',
             f'flock /tmp/angband-validation.lock python3 -m zoo run --experiment experiments/{a.experiment}.json --specimen {spec} \\',
             f'    --arm {spec}:{a.profile} --build build --work work --out out --jobs 4 --keep', '```', '',
             'Each death is then in `work/SUITE/SPECIMEN/PROFILE/SEED/` with `keys.log`, `messages.log`, `state.log`, '
             '`trace-core.jsonl`, `trip.jsonl` and `town-plan.jsonl`. `evidence/SEED/` here holds the key log, the summary and the last 400 messages of each death.', '']
    (out / 'README.md').write_text('\n'.join(head + [''] + body + repro))
    print(f'{len(deaths)} deaths -> {out / "README.md"}')


if __name__ == '__main__':
    main()
