#!/usr/bin/env python3
"""Make a ~/borg-play pack for the selected deaths: an X11 build, saves and play.sh.

    play_pack.py SELECTED_DIR --source BORG_REBORN_RS_CHECKOUT --pack ~/borg-play/NAME

SOURCE is the same checkout as record.py's (the specimen's commit). The script builds
SOURCE/build/rust with BORG_X11=ON (harness/build.sh), replays every death from birth with
it and requires the zoo cell's play hash, then cuts saves at about 3,000, 1,000 and 300
game turns before the death and 3 turns before it (-save-on-stop). It writes per death
user/ (borg.txt, scary list, plan), replay/ (the zoo's keys, messages, state, summary),
saves/ and start.env, plus the pack's bin/game, play.sh, deaths.json and README.md.

A save restores the game but not the Borg's memory (main-borgh.c: "its private memory is
not serialised"): loading one and pressing Ctrl-Z plays a different game. play.sh --to TURN
is the exact game: the Borg replays from birth, checked against the zoo keys.
"""
import argparse
import hashlib
from collections import Counter
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLASSES = ['Warrior', 'Mage', 'Druid', 'Priest', 'Necromancer', 'Paladin', 'Rogue', 'Ranger', 'Blackguard']
RACES = ['Human', 'Half-Elf', 'Elf', 'Hobbit', 'Gnome', 'Dwarf', 'Half-Orc', 'Half-Troll', 'Dunadan', 'High-Elf', 'Kobold']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('selected', type=Path)
    ap.add_argument('--source', required=True, type=Path)
    ap.add_argument('--pack', required=True, type=Path)
    a = ap.parse_args()
    pack = a.pack.expanduser()
    if not (a.source / 'build/rust/game/angband').exists() or 'X11' not in subprocess.run(['ldd', str(a.source / 'build/rust/game/angband')], capture_output=True, text=True).stdout:
        subprocess.run(['harness/build.sh'], cwd=a.source, env=os.environ | {'BORG_X11': 'ON', 'BORG_IMPL': 'rust'}, check=True)
    (pack / 'bin').mkdir(parents=True, exist_ok=True)
    shutil.rmtree(pack / 'bin/game', ignore_errors=True)
    shutil.copytree(a.source / 'build/rust/game', pack / 'bin/game')
    game = pack / 'bin/game'
    env = {k: v for k, v in os.environ.items() if not k.startswith('BORG_')} | {'TZ': 'UTC', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8'}

    def play(user, seed, race, cls, turns, out, save=None):
        for d in ('save', 'archive', 'panic', 'scores'):
            (out / d).mkdir(parents=True, exist_ok=True)
        cmd = ['./angband', '-mborgh', '-n', '-uPlayer', f'-duser={user}', f'-dsave={out}/save', f'-darchive={out}/archive',
               f'-dpanic={out}/panic', f'-dscores={out}/scores', '--', '-seed', str(seed), '-race', str(race), '-class', str(cls),
               '-turns', str(turns), '-keylog', f'{out}/keys.log', '-summary', f'{out}/summary.json', '-menu-letters',
               '-exact-turns', '-statelog', f'{out}/state.log']
        if save:
            cmd += ['-save-on-stop', save]
        subprocess.run(cmd, cwd=game, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1800)

    rows = []
    bundles = sorted(p.parent for p in a.selected.rglob('zoo-death.json'))
    # One seed can die in two different games (two arms): name those by death turn too.
    per_seed = Counter(json.loads((b / 'zoo-death.json').read_text())['seed'] for b in bundles)
    for b in bundles:
        z = json.loads((b / 'zoo-death.json').read_text())
        cfg = dict(l.split('=', 1) for l in (b / 'config.txt').read_text().split() if '=' in l)
        seed, race, cls, dt = z['seed'], int(cfg['race_idx']), int(cfg['class_idx']), z['final']['turn']
        name = f'{CLASSES[cls].lower()}-{seed}' + (f'-t{dt}' if per_seed[seed] > 1 else '')
        D = pack / name
        shutil.rmtree(D, ignore_errors=True)
        for d in ('user', 'saves', 'replay'):
            (D / d).mkdir(parents=True)
        for f in (b / 'user').iterdir():
            if f.suffix == '.txt' and f.name not in ('CharOutput.txt', 'lore.txt'):
                shutil.copy2(f, D / 'user' / f.name)
        for f in ('keys.log', 'messages.log', 'state.log', 'summary.json'):
            if (b / f).exists():
                shutil.copy2(b / f, D / 'replay' / f)
        with tempfile.TemporaryDirectory() as tmp:
            w = Path(tmp)
            play(D / 'user', seed, race, cls, cfg.get('turns', '100000'), w)
            ok = hashlib.sha256((w / 'keys.log').read_bytes()).hexdigest() == z['play_sha256']
        if not ok:
            print(f'{seed}: REPLAY DIFFERS from the zoo cell, dropped')
            shutil.rmtree(D)
            continue
        saves = []
        for t in sorted({max(1, dt - 3000), max(1, dt - 1000), max(1, dt - 300), max(1, dt - 3)}):
            if t >= dt:
                continue
            with tempfile.TemporaryDirectory() as tmp:
                w = Path(tmp)
                play(D / 'user', seed, race, cls, t, w, save=f'{w}/save/Player')
                if not (w / 'save/Player').exists():
                    continue
                last = (w / 'state.log').read_text().strip().splitlines()[-1]
                lv, dl = re.search(r'lv(\d+)', last), re.search(r' d(\d+)/', ' ' + last)
                shutil.copy2(w / 'save/Player', D / 'saves' / f"turn-{t:06d}-CL{lv.group(1) if lv else '?'}-DL{dl.group(1) if dl else '?'}.save")
                saves.append(t)
        (D / 'start.env').write_text(f'SEED={seed}\nRACE={race}\nCLASS={cls}\nDEATH_TURN={dt}\n')
        rows.append(dict(dir=name, cls=CLASSES[cls], race=RACES[race], seed=seed, cause=z['cause'], death_turn=dt,
                         death_level=z['final'].get('level'), saves=saves, play_sha256=z['play_sha256'], replay_matches=True,
                         specimen=z['specimen'], run=z.get('run_id')))
        print(f'{seed}: replay matches, saves {saves}')
    rows.sort(key=lambda r: r['death_turn'])
    (pack / 'deaths.json').write_text(json.dumps(rows, indent=1))
    shutil.copy2(HERE / 'play.sh', pack / 'play.sh')
    (pack / 'play.sh').chmod(0o755)
    table = '\n'.join(f"| {r['dir']} | {r['race']} {r['cls']}, CL{r['death_level']} | {r['cause']} | {r['death_turn']:,} |" for r in rows)
    first = rows[0]['dir'] if rows else 'NAME'
    (pack / 'README.md').write_text(f"""# Play the deaths: {pack.name}

Zoo run {rows[0]['run'] if rows else ''}, specimen `{rows[0]['specimen'] if rows else ''}`. `bin/game` is that commit built with the X11 frontend; every game was replayed from birth with it and matches the zoo run's play hash.

    ./play.sh                       # list the deaths and their saves
    ./play.sh {first}              # the last save before the death
    ./play.sh {first} TURN         # the stored save at or before game turn TURN
    ./play.sh {first} --to TURN    # the exact game: the Borg replays from birth to TURN, then you play

| folder | character | killed by | death at game turn |
|---|---|---|---|
{table}

A save restores the game but not the Borg's memory, so loading a save and pressing Ctrl-Z starts a new Borg that plays a different game. Use `--to` to reach a turn of the exact game.
""")
    print(f'{len(rows)} deaths -> {pack}')


if __name__ == '__main__':
    main()
