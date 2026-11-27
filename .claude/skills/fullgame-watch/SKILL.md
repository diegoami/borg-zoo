---
name: fullgame-watch
description: Produce the exact, verified watchables for a zoo full-game benchmark run - the play pack (staged saves, play.sh/play-curses.sh), the exact-frame death report, and per-death or full-timeline screen viewers from birth to death - by rebuilding the specimen's binary in a docker ubuntu:24.04 container with the runner's exact gcc and recording enabled. Use when the owner asks to watch, replay, replicate or animate a full-game benchmark run (zoo #805 family), to run the vanilla Angband C Borg in parallel with the Rust Borg, or asks how far the Borg gets (CL/DL) in full games.
---

# /fullgame-watch [RUN_ID] [SPECIMEN]

Reproduce, verify, and make watchable. Every recording and save comes from a
replay whose keys hash to the zoo cell's `play_sha256`; anything that does not
match is dropped and reported, never shown (death-report rules apply).

The full-game program (owner, 2026-11-25, zoo #805): full games until death or
the turn cap, max character level first (CL20 the first headline), max dungeon
depth second. The vanilla C Borg (original as Angband 4.2.6 ships it,
`4.2.6-reborn-c-pristine`, Borg sources e473720) runs the same starts in
parallel as the benchmark. Reference: a good day reaches CLvl 50.

## 1. The run must be evidence-retained

Check the run's artifacts (`gh api .../runs/RUN_ID/artifacts`) for `raw-*`.
If absent, re-dispatch the experiment's definition with `retain_evidence: true`
(same seeds, same pins — deterministic engine, the games replay identically).

## 2. The exact binary — docker ubuntu:24.04, the runner's compiler

The zoo's games are pinned to the build machine's gcc (Ubuntu 24.04,
**gcc-13 13.3.0-6ubuntu2~24.04.1**). A local build on another distro or
compiler plays *different games* (#855 family) — key verification fails. Build
in the container:

```sh
docker run --rm -v W/src:/src -w /src ubuntu:24.04 bash -c "
  apt-get update -qq >/dev/null
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq cmake gcc-13 libc6-dev make python3 git libx11-dev libxext-dev libncurses-dev >/dev/null 2>&1
  python3 harness/control-overlay.py --make IMPL build/IMPL.src   # overlay the pinned Borg (c-pristine: 118 files of e473720:src/borg)
  cmake -S build/IMPL.src/angband -B build/exact -DCMAKE_BUILD_TYPE=Release \
    -DSUPPORT_BORG_HARNESS=ON -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
    -DBORG_IMPL=c -DSUPPORT_BORG_RECORDING=ON \
    -DBORG_FEATURES= -DSUPPORT_X11=OFF > build/exact.cmake.log 2>&1
  make -C build/exact -j\$(nproc) > build/exact.make.log 2>&1
  ls build/exact/game/angband"
```

Gotchas learned 2026-11-25:
- The engine tree at the benchmark era is vendored as **`angband/`**, not
  `engine/`; the overlay lands in **`build/IMPL.src/angband`** and cmake points
  there with `BORG_IMPL=c` (the tree refuses `c-pristine` as BORG_IMPL).
- `control-overlay.py` shells out to `git` and wants the overlay's **parent**
  directory (`--make IMPL build/IMPL.src`), not the final path.
- The **c impl insists on X11 dev libraries at configure time** even with
  `SUPPORT_X11=OFF` — hence `libx11-dev libxext-dev` above (the runner image
  ships them preinstalled, which is why zoo CI never noticed).
- Docker writes root-owned files: after the build,
  `docker run --rm -v W/src:/src ubuntu:24.04 chown -R $(id -u):$(id -g) /src/build`.

**Verify before recording**: replay one death's full turns with
`game/angband -mborgh -n -uPlayer -duser=… -- -seed SEED -race R -class C
-turns TURNS -keylog … -menu-letters -exact-turns -msglog …` and compare
`sha256(keys.log)` with the bundle's `play_sha256`. `EXACT MATCH` proves the
recording flag is play-neutral; `DIFFER` means stop and re-check the flags.

## 3. Record — the two name mismatches

Run record.py (in this repository at
`.claude/skills/death-report/scripts/record.py`) with **absolute**
`--source/--work` (it runs the game with `cwd` inside the build dir; relative
work paths silently write nowhere):

```sh
python3 .claude/skills/death-report/scripts/record.py \
  W/selected --source W/src --work W --frames 100
```

Then bridge the old engine's names — a shim `game/angband` that maps them:

```bash
#!/bin/bash
if [ -n "$ANGBAND_RECORD_DIR" ]; then export BORG_RECORD_DIR="$ANGBAND_RECORD_DIR"; fi
"$(dirname "$0")/angband.real" "$@"
rc=$?
if [ -n "$ANGBAND_RECORD_DIR" ] && [ -f "$ANGBAND_RECORD_DIR/native-messages.jsonl" ]; then
  ln -sf native-messages.jsonl "$ANGBAND_RECORD_DIR/messages.jsonl"
fi
exit $rc
```

(this engine reads `BORG_RECORD_DIR` and writes `native-messages.jsonl`; the
script sets `ANGBAND_RECORD_DIR` and reads `messages.jsonl` — both mappings
verified 2026-11-25). Re-run record.py; all deaths must report
`replay_matches: true` in `W/frames.json`.

## 4. Play pack and viewers

- **Play pack**: pre-place the exact binary at `W/src/build/rust/game`
  (satisfies play_pack's X11 check — build it with
  `SUPPORT_X11_FRONTEND=ON` too for a watchable window; verified the X11
  frontend is play-neutral), then
  `python3 .claude/skills/death-report/scripts/play_pack.py W/selected
  --source W/src --pack ~/borg-play/NAME`. Four staged saves per death,
  `play.sh NAME --to TURN` replays the exact game from birth (a loaded save
  starts a NEW Borg — memory is not serialised; say it every time).
- **X11 on the owner's desktop** needs legacy bitmap fonts
  (`xfonts-base xfonts-75dpi xfonts-100dpi` + `mkfontscale`/`mkfontdir` on the
  misc/75dpi/100dpi dirs + `xset fp rehash`). If Xwayland still refuses, ship
  the **GCU build** (`SUPPORT_GCU_FRONTEND=ON`) as `play-curses.sh` — terminal
  play, no fonts needed.
- **Full-timeline viewers** ("watch from the start"): per death, build a
  frames.json whose entry carries **all** frames from
  `record/frames.jsonl` (not just the last N), run page.py with
  `--title "CLS — the full game (dies to CAUSE at turn T)"`, and serve the
  pages directory (`python3 -m http.server 8790 --bind 127.0.0.1`). A bare
  index.html linking the pages plus the last-100 report is the front door.

## 5. Cemetery

Import the bundles on a `runs/DATE-NAME` branch
(`scripts/import_zoo_deaths.py --bundles W/selected --run-id RUN`), write the
case README (source, selection, dossier table, observations, report location),
`scripts/death_ids.py --check` + the tests, and open the PR for the owner
(RULES 2). Reconcile natural deaths from the retained bundles.
