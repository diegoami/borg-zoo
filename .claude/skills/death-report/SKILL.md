---
name: death-report
description: Turn the deaths of a zoo run (all, one class, some seeds or one arm) into a published report with each death's last recorded screens, a ~/borg-play pack to replay or play them, and borg-cemetery dossiers. Use when the owner asks to look at, see, watch, replay or play the deaths of a run, asks for a death report or viewer like the ones published before, or types /death-report.
---

# /death-report

The owner reads deaths through three things, and asks for them often. Make all three unless they ask for fewer:

1. **A published report** (Artifact): findings first, then a viewer that steps through each death's last 50 screens, exactly as recorded.
2. **A play pack** in `~/borg-play/NAME`: an X11 build of the same commit, saves before each death, and `play.sh`.
3. **Cemetery dossiers** in borg-cemetery, with a case README that links the report.

Everything here is reproduced, not reconstructed. Every recording and every save comes from a replay whose keys hash to the zoo cell's `play_sha256`. A death that does not match is dropped and reported, never shown.

## Inputs

- **The run:** either an experiment name (e.g. `reborn-main-fde8-full`, which uses its latest run) or a run id. Run ids appear in the run page's address (`.../runs/EXPERIMENT/RUNID-ATTEMPT/index.html`) and in the issue comments.
  - To pick one, `python3 .claude/skills/death-report/scripts/runs.py [FILTER]` lists recent runs from the results branch with games, deaths and deaths per class, newest first. FILTER matches part of the experiment name, e.g. `full`, `fde8`, `leash`.
- **The selection:** a class (`--class Ranger`), seeds (`--seeds 1,2`) or an arm (`--profile NAME`).
- **A short pack name**, e.g. `fde8-rangers`.

The zoo runs (this repository) hold the death bundles as `deaths-*` artifacts for 90 days. Older runs can't be done this way.

Scripts are in `.claude/skills/death-report/scripts/`. Work in the session's scratchpad.

## Steps

1. **Bundles.**
   `python3 .claude/skills/death-report/scripts/fetch_bundles.py RUN_OR_EXPERIMENT --out W --class Ranger`
   Selected bundles go to `W/selected`, one line printed per death.

2. **Source at the specimen's commit.** The bundles' `BUILD_ID` / specimen name the commit. Use a read-only clone in the scratchpad:
   ```sh
   git clone https://github.com/diegoami/borg-reborn-rs W/src
   git -C W/src checkout --detach COMMIT
   ```
   A complete owner checkout at `~/projects/borg-reborn-rs` can accelerate
   the clone with `--reference ... --dissociate`. If the reference is
   incomplete or checkout reports missing objects, use a fresh independent
   clone. If the exact commit is unavailable there too, ask for its source
   ref or a bundle before recording the replay.
   Never build in the owner's own checkout.

3. **Read the deaths before writing anything.** For each bundle, read `messages.log`: the last 300 lines, the killer's first appearance, attack choices (`# Performing attack type 1` melee / `3` shot / `2` throw), flight and healing notes. Compare with another main or arm if the owner asked why. Write findings only from what the logs and counts show, and recount every number you state against the table you build (counts per class, CL at death, last attack, ammo). Earlier reports had miscounts caught only on a second pass.

4. **Recordings and screens.**
   `python3 .claude/skills/death-report/scripts/record.py W/selected --source W/src --work W [--frames 100]`
   - `--frames` sets how many screens per death the report steps through. The default is 50; the page shows the real count, and the size grows about 100 KB per 50 screens per death.
   - This builds `W/src/build/recorder` (`SUPPORT_BORG_RECORDING=ON`; `harness/build.sh` pins it off), records every death from birth, checks the keys, and writes `W/frames.json`: the last 50 screens, the gear at death, and per-death counts (shots, melee, throws, cures quaffed, ammo left, cure potions left, last attack).

5. **Play pack.**
   `python3 .claude/skills/death-report/scripts/play_pack.py W/selected --source W/src --pack ~/borg-play/NAME`
   - It builds `W/src/build/rust` with `BORG_X11=ON`, checks every replay, and cuts 4 saves per death. It writes `play.sh` (copies all of `user/`, including the scary list) and a README.
   - Don't touch other packs in `~/borg-play`.

6. **Cemetery.** In a borg-cemetery clone in the scratchpad, on a `runs/DATE-...` branch:
   - Run `python3 scripts/import_zoo_deaths.py --bundles W/selected --run-id RUN`. It calls `scripts/native/export-death.py`, which is what borg-reborn-rs `tools/export-death.py` forwards to.
   - Write `runs/DATE-NAME/README.md`: source, selection, a table of dossiers, observations, and the link to the report.
   - Check with `python3 scripts/death_ids.py --check` and `python3 -m unittest discover -s tests`.
   - Open a PR for the owner to review and merge (RULES 2).
   - Write the dossier ids per seed (from `runs/zoo-.../deaths.json`) to `cases.json` for the page.

7. **Report.**
   - Write three fragments:
     - `header.html`: eyebrow, h1, lede with the main number;
     - `findings.html`: sections, optionally a `<table id="cls">` with `<tbody></tbody>` for a per-class bar table fed by `classes.json`;
     - `footer.html`: provenance.
   - Then run `python3 .claude/skills/death-report/scripts/page.py W/frames.json --out W/NAME.html --title "..." --pack NAME --header ... --findings ... --footer ... [--classes classes.json] --cases cases.json`.
   - Open the generated HTML and check the viewer before publishing it with the available artifact tool.
   - The title is a name, e.g. "Ranger Deaths on fde8025a". Keep the template's look (Spectral / Public Sans / JetBrains Mono, green accent, dark terminal).

8. **Report back.**
   - Post the report link on the zoo issue and in the cemetery case README.
   - Give the owner the link, the pack command, and the cemetery PR.
   - Delete the scratchpad work (clones, recordings) when the owner says so.

## What to tell the owner about playing

- **Loading a save and pressing Ctrl-Z gives a different game.** A save restores the game, but not the Borg's memory: `main-borgh.c` says "A replay starts a NEW Borg; its private memory is not serialised". The new Borg chooses differently, and often lives.
- **The exact game:** `./play.sh NAME --to TURN`. The Borg replays from birth to TURN, checked against the zoo keys, then the window opens.
- **Watching:** the report's screens are the exact game.
- **The cemetery's `watch.sh`** refuses zoo dossiers by design. They're seed dossiers with no recording, and its recorder is qualified only for one commit. Don't promise it.

## Notes

- **Kit at death:** the zoo bundles carry no death dump (`CharOutput.txt` is a stub). The gear comes from the recorder's final frame (`details.gear`).
- **Screens:** the recorder writes `frames.jsonl` as deltas (`cells` = `[index, char, attr]` on an 80×24 grid). `record.py` replays them in order.
- **Cost:** recording runs at about game speed. A 60,000-turn death takes a few minutes; run long batches in the background.
