# Zoo saved caster encounter smoke (#144)

The owner asked Zoo to run the actual saved scenarios with a mix of classes.
`Saved caster encounters on Zoo` builds one exact reborn source and executes
Cemetery's eight-case smoke: **two each Mage, Druid, Priest and Necromancer**.
The workflow posts the readable outcome table in its GitHub job summary and
uploads JSON/Markdown/HTML reports with the exact execution receipts.

This is a separate saved-state baseline contract, not the generated-birth
comparison contract in PR145 and not a natural seed-suite experiment. It
requires `loaded:true`, fresh private Borg memory and saved engine RNG. It
makes no paired-impact, population or improvement claim. The generated-birth
`loaded:false`/one-way restrictions are not changed. No large Zoo tier starts.

## Frozen definition and run

The source is `definitions/cemetery-mixed-caster-encounters-smoke.yaml`.
Generate/check the immutable JSON reference through the normal YAML command:

```sh
python3 -m zoo define definitions/cemetery-mixed-caster-encounters-smoke.yaml
python3 -m zoo define --check definitions/cemetery-mixed-caster-encounters-smoke.yaml
```

The definition uses the existing catalogue specimen
`4.2.6-reborn-rust-maxdepth`, exact source
`6d1bca10bc67d02150a1a717f111891976e98069`. The saved-state controller is explicitly
**reborn** with Cemetery's pinned profile, independent of natural-game profiles
that may run the same source with borg-rs. Cemetery bank pin:
`fecca62c6b3f98452123a8256860f8251e653eb7` (Cemetery #49). Native tools pin:
`1afd9423d7f8a1340eca9d74cff85443e769b1a9`, matching the source's byte-checked
`death-tools-pin.txt`. A separate checkout for each pin is required.

On a relevant PR, the workflow runs the fixed smoke automatically with read-only
permissions and no persisted checkout credentials. After this workflow lands
on default, operators can also use Actions → Saved caster encounters on Zoo →
Run workflow. It does not publish production Pages or append production results
before review; its job summary and downloadable report are the initial Zoo run
interface. The workflow's artifact page links the report (90 days) and canonical
native evidence produced by the pinned adapter (14 days). Artifacts are not a
permanent evidence store. Persistent comparison snapshots/site discovery are a
follow-up integration under #144, not an implemented claim here.

For a local Zoo execution using three clean pinned checkouts:

```sh
python3 -m zoo.encounters plan \
  --definition scenario-experiments/cemetery-mixed-caster-encounters-smoke.json \
  --bank /path/to/cemetery-bank --source /path/to/built-reborn \
  --tools /path/to/pinned-native-tools --out /tmp/new-plan.json
python3 -m zoo.encounters run --plan /tmp/new-plan.json \
  --bank /path/to/cemetery-bank --source /path/to/built-reborn \
  --tools /path/to/pinned-native-tools --out /tmp/new-attempt
python3 -m zoo.encounters collect --plan /tmp/new-plan.json \
  --attempt /tmp/new-attempt --out /tmp/new-report
```

All output paths must be fresh. The pinned Cemetery runner acquires the shared
engine lock internally; never wrap it in another flock. Preparation/build time
is separate from the short encounter execution time. The smoke retains the
original 1,000-engine-turn/5-second-per-case limits, with a360-second outer
execution watchdog for cleanup, and a separate ten-minute build limit.

## Checks and failure accounting

The plan binds exact Zoo/runner, YAML-generated definition, catalogue specimen,
Cemetery bank/runner, source/input hash, engine and native-tools pins. It
requires eight distinct saved starts with the exact2/2/2/2 class distribution.
Zoo calls Cemetery's existing suite qualifier and execution adapter; it does
not reconstruct gear or change the bank. Ambient BORG/ANGBAND overrides are
cleared, and a private output directory is used.

Each completed cell is fsynced before another game finishes, including after an
interrupted batch. Collection emits every expected row, even when the build,
run or artifact upload fails. It independently checks native loaded identity,
start turn/depth/HP/SP, source and binary/process receipts, saved-RNG flags,
profile hash/effective parameter values and terminal facts. Raw receipt bytes,
their hashes and source-life lineage remain in compact result cells. Copied,
mutated or missing receipts cannot become horizon survival. These are unsigned
consistency checks, not cryptographic execution attestation. Raw gameplay
hashes/bytes and native death exports remain in the adapter artifact; they are
not permanent after artifact expiry.

Reports show all eight outcomes and keep separate per-class denominators.
Stopped cells are separate from deaths/survival; failures and missing cells
stay visible. Repeated/related encounters remain correlated. Qualified
near-death diagnostics are unavailable. The local development check completed
8/8 valid with five deaths and three horizon survivals; the cloud run is the
actual Zoo execution evidence and must be inspected before proposing a next
tier. Larger runs require a written gate and owner agreement under RULES14.
Cemetery owns canonical saves/scenarios/evidence; Zoo owns execution,
aggregation and presentation. No Borg source or Cemetery files are changed.
