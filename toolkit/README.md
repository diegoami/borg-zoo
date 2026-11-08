# Original Angband / Neo Borg measurement toolkit

This is an owner-requested, descriptive **1,800 lives per original engine**
benchmark. It tests official source, with no consumer gameplay corrections.
Canonical coordination: [workspace #42](https://github.com/diegoami/angband-workspace/issues/42)
and [Zoo #25](https://github.com/diegoami/borg-zoo/issues/25).

The fresh experiment is
[`originals-20261108-classes-1800`](../experiments/originals-20261108-classes-1800.json).
Source heads were resolved and frozen before its outcomes:

| Component | Official repository | Commit |
| --- | --- | --- |
| Angband and C Borg | angband/angband | e473720ed88a0f0c7ca66815cef3000eb4a38bc3 |
| Neo engine, content, SDK and API2 host | neostryder/neo-angband | 5a9cab20621278b74f8376996eba1f6fda14c523 |
| Neo Borg | neostryder/neo-angband-mod-borg | 014c810466ec7ac0b9b7a83416e075238c72edd0 |
| Native observer/runner, separately from game source | diegoami/better-borg-c | fc9d97cb46aa0aaa27773e5c83a41ec395d515fc |

The native pin is official **master**, not the 4.2.6 release tag. The Neo
pins are official source heads, not a claim that an npm release contains
them. The external Neo tools-only proposal and its exact commit are recorded
in `catalogue/specimens.json`. The canonical Neo proposal is [engine tracker PR #542](https://github.com/diegoami/neo-angband-tracker/pull/542), pinned at `2668adc5ab3e2b6e194c2f1561e248b88850ea98`. Its original engine and original Borg inputs
stay separate from that measurement code.

## What the experiment can establish

The frozen `classes-1800` suite assigns 200 starts to each of nine classes,
cycling eleven races. Each engine uses its own ordinary birth implementation,
starting gear and default settings. Both caps are 100,000 engine ticks; ten
ticks correspond to one normal-speed action. The native observer can stop at
the exact tick; Neo stops at a Core loop boundary and records actual ticks
and any overshoot. A death beyond the requested cap is retained as a
post-cap death, while the endpoint is classified alive at the cap.

**A C seed and a Neo seed are different games.** Cross-engine results are
unpaired descriptive patterns, not matched game trajectories, a gameplay
improvement claim or automatic proof of a port defect. Native notes/state
trace hashes and Neo intent-stream hashes are different encodings. Ordinary
birth methods are recorded, not assumed statistically equivalent.

Death, cap, stall, explicit Borg stop, decision safety cap, wall timeout,
crash, configuration mismatch and harness failure remain separate. A failed
or missing attempt stays in the denominator of planned attempts and in the
outcome accounting. Only actual recorded deaths count as deaths. Observation
is not diagnosis: generated death dossiers are initially **unassessed**.

## Reproduce

Use Linux, Python 3.12+, Node 22, Corepack/pnpm, CMake, a C compiler and X11
headers. Check out the Zoo commit named in the run's `meta.json`. The catalogue
contains immutable game, observer and Neo proposal pins. Fetch those exact
objects; do not silently replace them with today's heads.

```sh
python3 -m unittest discover -s tests
python3 -m zoo plan --experiment experiments/originals-20261108-classes-1800.json
```

For one native life and a disclosed source/observer diff, use
[`native/README-native.md`](native/README-native.md). Run its scripts from
`toolkit/native/`, or qualify their paths. Its pilot report preserves all
attempts, including repeated starts (not additional independent lives).

For a whole assigned native shard through the same orchestration as Actions:

```sh
python3 -m zoo build --specimen angband-e473-original --harness native-harness \
  --out specimens/angband-e473-original
python3 -m zoo run --experiment experiments/originals-20261108-classes-1800.json \
  --specimen angband-e473-original --shard 0 --shards 1800 \
  --harness native-harness --build specimens/angband-e473-original \
  --work fresh-work --out fresh-cells.jsonl --jobs 1 --keep
```

`--shards 1800 --shard 0` selects the first assigned start only. It is a rerun,
not a new independent life in the published cohort. Select another shard
index to rerun another assigned seed. Preserve every rerun under fresh paths.
The source seal is generated before packaging native builds in Actions.

The Neo calling adapter is `zoo/neo_original.py`; it calls the engine tracker's
pinned `tools/original-borg/build.mjs` and `run.mjs`. Zoo contains no Neo host
or Borg implementation. Build once from the exact engine and Borg checkouts;
subsequent processes use the resulting bundle and adjacent content pack:

```sh
python3 -m zoo build --specimen neo-5a9-original --engine engine \
  --source original-borg --toolkit neo-toolkit --out specimens/neo-5a9-original
python3 -m zoo run --experiment experiments/originals-20261108-classes-1800.json \
  --specimen neo-5a9-original --shard 0 --shards 1800 \
  --toolkit neo-toolkit --build specimens/neo-5a9-original \
  --work fresh-neo-work --out fresh-neo-cells.jsonl --jobs 1
```

Local heavy build/play commands share `/tmp/angband-validation.lock` in the
Angband workspace. On another standalone maintainer machine, that workspace
lock is unnecessary.

## Records and death evidence

`borg-zoo/cell@1` is one planned attempt's outcome, cause, actual birth,
progress, final state, settings, counter/cap semantics and provenance. The
Neo raw `run.json`, states, intents and messages retain the richer original
proposal record; the native raw directory retains result, trace, terminal
log, input/configuration and final `.map` files. Native birth stats/gear and
raw generated key commands are not separately recorded by this minimal
observer; do not claim otherwise.

For this experiment, all raw attempt directories survive; they are not
limited to failures. Each directory has `evidence.json` with relative paths,
byte lengths and SHA-256 hashes. The cell embeds this inventory. Shard raw
archives have separate SHA-256 files. `deaths.json` and `deaths.csv` index
actual and post-cap deaths. `evidence-status.json` flags missing raw
inventories and required native death maps, rather than presenting missing
files as complete evidence. Build artifacts include original-source identities
and source/observer diffs.

Each retained shard flushes completed records immediately. Collection inserts
explicit harness-failure records for missing planned keys. All attempts remain
visible when a hosted job fails, times out or is interrupted. The run's
`meta.json` preserves the expanded seed/birth manifest, profile, source and
harness pins, Zoo commit and workflow URL.

Raw artifacts are retained for **90 days**, not forever. Compact records,
per-file hash inventories and death indexes are append-only on `results`.
Before artifact expiry, a maintainer must download and verify the archives to
keep the raw evidence. A compact hash inventory alone does not recover raw
files. Do not claim verified long-term recovery merely because upload passed.
Calendar and timezone are recorded, since the native game's seasonal behavior
can depend on them. Wall time is metadata, not a substitute for game turns.

## Delivery and claims

The source/toolkit proposal, exact run and raw artifact links are the
maintainer-facing entry point. Post the final descriptive report only after
reviewing actual outcomes and evidence completeness. No official Angband
issue or PR is part of this delivery. New causal investigations should cite a
specific recorded life and first distinguish game policy, source differences
and host/measurement limitations. No engine or Borg repair is included here.
