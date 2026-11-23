#!/usr/bin/env python3
"""Record the selected deaths with a recorder build and extract their last screens.

    record.py SELECTED_DIR --source BORG_REBORN_RS_CHECKOUT --work DIR [--frames 50]

SOURCE must be a borg-reborn-rs checkout at the specimen's commit (the bundles' BUILD_ID
names it; the script refuses another commit). It builds SOURCE/build/recorder with
SUPPORT_BORG_RECORDING=ON (harness/build.sh pins it off; the source tree is not modified),
replays every bundle from birth with ANGBAND_RECORD_DIR set, and requires the replay's
keys.log to hash to the zoo cell's play_sha256: a mismatch is reported and the death is
dropped, because it would not be the same game.

Writes WORK/frames.json: one entry per death with the last N screens that changed (rows,
colour attributes, HP, turn, the messages and Borg notes since the previous screen), the
messages after the last screen, the gear at death (from the recorder's final frame) and
counts read from the replay's messages (shots, melee swings, throws, cures quaffed, ammo
left, last attack, cure potions left in the pack).
"""
import argparse
import hashlib
from collections import Counter
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

A = '0123456789abcdefghijklmnopqrstuvwxyz'
RACES = ['Human', 'Half-Elf', 'Elf', 'Hobbit', 'Gnome', 'Dwarf', 'Half-Orc', 'Half-Troll', 'Dunadan', 'High-Elf', 'Kobold']
CLASSES = ['Warrior', 'Mage', 'Druid', 'Priest', 'Necromancer', 'Paladin', 'Rogue', 'Ranger', 'Blackguard']


def build(source):
    b = source / 'build/recorder'
    binary = b / 'game/angband'
    if binary.exists():
        return b / 'game'
    b.parent.mkdir(parents=True, exist_ok=True)
    with open(f'{b}.cmake.log', 'w') as log:
        subprocess.run(['cmake', '-S', str(source / 'engine'), '-B', str(b), '-DCMAKE_BUILD_TYPE=Release',
                        '-DSUPPORT_BORG_RECORDING=ON', '-DBORG_FEATURES=', '-DSUPPORT_X11=OFF'], check=True, stdout=log, stderr=log)
    with open(f'{b}.make.log', 'w') as log:
        subprocess.run(['make', '-C', str(b), f'-j{os.cpu_count()}'], check=True, stdout=log, stderr=log)
    return b / 'game'


def counts(text):
    calls = re.findall(r'# Performing attack type (\d+)', text)
    last = {'1': 'melee', '3': 'shot', '2': 'throw'}.get(calls[-1], f'type {calls[-1]}') if calls else 'none'
    ammo = re.findall(r'You have (\d+|no more) (?:Arrows|Iron Shots|Pebbles|Bolts|Shots|Mithril Arrows|Seeker)', text)
    cure = re.findall(r'You have (\d+|no more) Potions? of Cure (?:Light|Serious|Critical)', text)
    return dict(shots=len(re.findall(r'# Firing missile', text)), melee=len(re.findall(r'# Attacking with weapon', text)),
                throws=len(re.findall(r'# Throwing painful', text)), cures=len(re.findall(r'# Quaffing Potions? of Cure', text)),
                ammo=(0 if ammo[-1] == 'no more' else int(ammo[-1])) if ammo else 0,
                cure_left=(0 if cure[-1] == 'no more' else int(cure[-1])) if cure else 0, last=last)


def gear(frame):
    out = []
    for g in (frame.get('details') or {}).get('gear') or []:
        k = g['actual_kind'].replace('& ', '').replace('~', '')
        q = g['quantity']
        out.append(k + (f' ×{q}' if q > 1 else '') + (f" ({g['timeout']} turns)" if 'Torch' in k or 'Lantern' in k else ''))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('selected', type=Path)
    ap.add_argument('--source', required=True, type=Path)
    ap.add_argument('--work', required=True, type=Path)
    ap.add_argument('--frames', type=int, default=50)
    ap.add_argument('-j', '--jobs', type=int, default=1, help='replays run at once')
    a = ap.parse_args()
    head = subprocess.run(['git', '-C', str(a.source), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
    bundles = [p.parent for p in sorted(a.selected.rglob('zoo-death.json'))]
    if not bundles:
        raise SystemExit('no bundles')
    want = (json.loads((bundles[0] / 'zoo-death.json').read_text()).get('build') or {}).get('git_rev') \
        or dict(l.split('=', 1) for l in (bundles[0] / 'BUILD_ID').read_text().split() if '=' in l).get('git_rev', '')
    if want and not head.startswith(want[:12]) and not want.startswith(head[:12]):
        raise SystemExit(f'source is at {head[:12]}, the bundles were built from {want[:12]}')
    game = build(a.source)
    env = {k: v for k, v in os.environ.items() if not k.startswith('BORG_')} | {'TZ': 'UTC', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8'}
    data = []
    # One seed can die in two different games (two arms): name those by death turn too.
    per_seed = Counter(json.loads((b / 'zoo-death.json').read_text())['seed'] for b in bundles)
    # An arm's name: the part of its profile name that differs between the
    # profiles in the selection (reborn-ro-ranged-x8 -> ranged).
    profiles = sorted({json.loads((b / 'zoo-death.json').read_text()).get('profile') or '' for b in bundles})
    parts = [p.split('-') for p in profiles]
    pre = 0
    while len(parts) > 1 and all(len(q) > pre + 1 for q in parts) and len({q[pre] for q in parts}) == 1:
        pre += 1
    suf = 0
    while len(parts) > 1 and all(len(q) > pre + suf + 1 for q in parts) and len({q[-1 - suf] for q in parts}) == 1:
        suf += 1
    arms = {p: '-'.join(q[pre:len(q) - suf]) for p, q in zip(profiles, parts)} if len(profiles) > 1 else {}

    def one(b):
        z = json.loads((b / 'zoo-death.json').read_text())
        cfg = dict(l.split('=', 1) for l in (b / 'config.txt').read_text().split() if '=' in l)
        seed, race, cls = z['seed'], int(cfg['race_idx']), int(cfg['class_idx'])
        arm = arms.get(z.get('profile') or '', '')
        name = f'{CLASSES[cls].lower()}-{seed}' + (f'-{arm}' if arm else '') + (f"-t{z['final']['turn']}" if per_seed[seed] > 1 and not arm else '')
        w = a.work / 'rec' / name
        shutil.rmtree(w, ignore_errors=True)
        for d in ('user', 'save', 'archive', 'panic', 'scores', 'record'):
            (w / d).mkdir(parents=True)
        for f in (b / 'user').iterdir():
            if f.suffix == '.txt' and f.name not in ('CharOutput.txt', 'lore.txt'):
                shutil.copy2(f, w / 'user' / f.name)
        for f in (b / 'user').glob('*plan*.txt'):
            shutil.copy2(f, w / 'user' / f.name)
        # A world (borg-reborn-rs #704): the game data harness/run.sh made with
        # scripts/make-world.py, checked against the cell's data SHA-256.
        data_args = []
        world = cfg.get('borg_world', '')
        if world and world != 'none':
            out = subprocess.run(['python3', str(a.source / 'scripts/make-world.py'), '--config', str(a.source / 'harness/worlds' / f'{world}.txt'),
                                  '--lib', str(game / 'lib'), '--out', str(w / 'world')], capture_output=True, text=True, check=True).stdout.strip()
            if out != cfg.get('borg_world_data_sha256'):
                print(f'{seed}: world {world} data {out[:12]} is not the cell\'s {cfg.get("borg_world_data_sha256", "")[:12]}, dropped')
                return None
            data_args = [f'-dgamedata={w}/world/gamedata', f'-dpref={w}/world/customize', f'-dhelp={w}/world/help', f'-dscreens={w}/world/screens']
        subprocess.run(['./angband', '-mborgh', '-n', '-uPlayer', f'-duser={w}/user', f'-dsave={w}/save', f'-darchive={w}/archive',
                        f'-dpanic={w}/panic', f'-dscores={w}/scores', *data_args, '--', '-seed', str(seed), '-race', str(race), '-class', str(cls),
                        '-turns', cfg.get('turns', '100000'), '-keylog', f'{w}/keys.log', '-summary', f'{w}/summary.json',
                        '-menu-letters', '-exact-turns', '-msglog', f'{w}/messages.log'],
                       cwd=game, env=env | {'ANGBAND_RECORD_DIR': str(w / 'record')}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1800)
        ok = hashlib.sha256((w / 'keys.log').read_bytes()).hexdigest() == z['play_sha256']
        if not ok:
            print(f'{seed}: KEYS DIFFER from the zoo cell, dropped')
            return None
        frames = [json.loads(l) for l in open(w / 'record/frames.jsonl')]
        msgs = {}
        for l in open(w / 'record/messages.jsonl'):
            m = json.loads(l)
            msgs.setdefault(m['frame'], []).append(m['text'])
        grid, att, screens = [' '] * 1920, ['1'] * 1920, []
        for f in frames:
            for i, ch, at in f['cells']:
                if 0 <= i < 1920:
                    grid[i] = chr(ch) if ch >= 32 else ' '
                    att[i] = A[at] if 0 <= at < len(A) else '1'
            if f['cells']:
                screens.append(dict(i=f['index'], turn=f['turn'], hp=f['hp'], mhp=f['max_hp'], sp=f['sp'], msp=f['max_sp'], dl=f['depth'],
                                    cl=f['level'], rows=[''.join(grid[r * 80:(r + 1) * 80]) for r in range(24)], attr=''.join(att)))
        last = screens[-a.frames:]
        idx = [x['i'] for x in last]
        out = [x | {'msgs': [t for q in range(idx[k - 1] + 1 if k else x['i'], x['i'] + 1) for t in msgs.get(q, [])]} for k, x in enumerate(last)]
        fin = z.get('final') or {}
        print(f'{seed}: keys match, {len(frames)} frames', flush=True)
        return dict(dir=name, arm=arm or z.get('profile'), world=world or None, cls=CLASSES[cls], race=RACES[race], seed=seed, cause=z['cause'],
                         cl=fin.get('level'), dl=fin.get('depth'), turn=fin.get('turn'), keys=sum(1 for _ in open(w / 'keys.log')),
                         play=z['play_sha256'], replay_matches=True, specimen=z['specimen'], run=z.get('run_id'),
                         frames=out, after=[t for q in sorted(msgs) if q > idx[-1] for t in msgs[q]],
                         equip=[], quiver=[], inv=gear(frames[-1]), total_frames=len(frames),
                         **counts((w / 'messages.log').read_text(errors='replace')))

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max(1, a.jobs)) as pool:
        data = [d for d in pool.map(one, bundles) if d]
    data.sort(key=lambda d: d['turn'] or 0)
    (a.work / 'frames.json').write_text(json.dumps(data))
    print(f'{len(data)} deaths -> {a.work / "frames.json"}')


if __name__ == '__main__':
    main()
