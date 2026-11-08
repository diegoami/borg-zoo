# Original Angband native benchmark adapter

This toolkit runs **angband/angband master e473720ed88a0f0c7ca66815cef3000eb4a38bc3** with zero consumer gameplay corrections. That is the official master observed on 2026-11-08; it is not the peeled 4.2.6 release tag f3082213b73f3e463e3d0d60bff4b00462beae6e. Headless observation comes from the separately pinned, already used better-borg-c harness fc9d97cb46aa0aaa27773e5c83a41ec395d515fc, not that fork's gameplay HEAD.

Prerequisites: Linux, Python 3.12+, CMake, a C compiler and X11 development headers. Run heavy local checks through the shared workspace lock if other Angband sessions use this machine. A standalone maintainer machine can omit `flock`.

```sh
git clone https://github.com/diegoami/better-borg-c.git native-harness
git -C native-harness checkout --detach fc9d97cb46aa0aaa27773e5c83a41ec395d515fc
git -C native-harness fetch https://github.com/angband/angband.git master
# Confirm FETCH_HEAD equals the original pin above. Never silently replace it.
cd native-harness
flock /tmp/angband-validation.lock python3 tools/measure-native.py prepare \
  --ref e473720ed88a0f0c7ca66815cef3000eb4a38bc3 --observe --output artifacts/original-build
cd ..
python3 native-source-seal.py --build native-harness/artifacts/original-build --out fresh-source-proof
flock /tmp/angband-validation.lock python3 native-run.py \
  --harness native-harness --build native-harness/artifacts/original-build \
  --seed 884072154 --race Human --class Warrior --turns 100000 \
  --timeout 900 --stall-timeout 90 --out fresh-attempt
```

`native-run.py` uses ordinary native birth menu keys with default point buy and normal starting gear. It checks the actual `CHARACTER` trace against the assigned race/class. No gameplay actions are supplied after Borg activation. All 11 native races and 9 classes are accepted; no class/race policy patch is applied. Borg configuration uses original compiled defaults, explicitly keeping cheat death and winner respawn false. The effective native Borg/game options are in each trace and record. Dynamic formulas and munchkin mode are false in these original defaults.

The cap is the C game's global `turn` counter: the observer checks immediately after every increment and stops exactly at 100000, including during long actions. Normal speed receives 10 energy per tick and a normal action spends 100 energy, so 10 ticks correspond to one normal-speed action. Birth's first observed turn is retained, rather than treating decisions, elapsed ticks and action count as synonyms. Neo caps must be labeled with their own semantics. Equal numeric seeds across C and Neo are **different games**, not paired starting worlds.

The wrapper refuses an existing output path. It verifies the exact harness tool bytes, runtime source pin, source archive hash, binary hash and (via the existing runner) data hashes. Every run retains `result.json`, `native-record.json`, input/configuration, `trace.txt`, `terminal.log`, and any native `.map` in `archive/`. Native maps contain the Borg's final map/player/inventory diagnostics. The trace retains Borg notes, RNG/player state every 100 Borg decisions, final outcome/cause and recent messages. `native-record.json` hashes every existing evidence file; it does not hash itself. Preserve every failed attempt and retry under a new path.

Outcomes stay separate: natural `death`, alive `turn_cap`, `completion`, `stalled`, `wall_timeout`, `crash`, `harness_failure` and birth `config_error`. A stall/watchdog is not a death or a survivor. `cause` on a live run is the game's literal `(alive and well)`, not a death cause. Native completion means actual game completion, not merely reaching the cap.

Limitations: this minimal observer does not record initial birth stats/gear separately or raw generated key commands. `result.json` has a legacy fixed Human Warrior label even when menu assignment differs; `native-record.json.actual_birth` and the trace are authoritative. Save/replay recording is off; raw dossiers are unassessed evidence, not replay-fidelity certificates or causal diagnoses. The native source seal discloses every instrumentation edit; repeated deterministic pilot traces alone do not prove general observation neutrality. Calendar/timezone and wall time are recorded because native clock-dependent behavior is an external input; do not claim seed-only reproducibility across arbitrary calendar dates. Build path/compiler can change binary hashes; compare declared tool/source/data identity as well.

For the 1800 suite, reuse the frozen Zoo `classes-1800` seed list and assigned-character manifest. Do not pick deaths or survivors to choose seeds. Run with `--keep` and upload **all** raw native attempt directories and the source proof/build manifest, not only compact cells. Compact outcome summaries alone cannot support later death investigation. Keep repeat attempts separate from independent lives. Hashes are meaningful within the declared adapter; do not compare the native trace hash to Neo's API2 intent hash as if they represented the same command stream.
