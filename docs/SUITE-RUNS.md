# Running a build on a saved suite

A **suite** is a frozen bank of saved encounters with its protocol:
`scenario-suites/ID/suite.json`. **Suite 1** (`suite1-v1`) is the balanced999 bank of
borg-zoo#168: 999 saves, 111 per class. Each save starts with fresh Borg memory and the
saved engine RNG, and plays an exact 2,000-engine-turn horizon under a 5-second native wall
limit.

A **run** is a sanity check of one build: by default borg-reborn-rs `main` at its current HEAD,
with its **own default settings**, which are the commit's `harness/borg.txt`, unchanged. Those
settings are not maintained in the Zoo. `scenario-inputs/NAME/borg.txt` is a byte-for-byte copy
taken when the run is defined, only so the run records exactly what it played. Settings are
overridden, with a Zoo profile on top, only when the owner asks. A run is reported alone, with
no other build beside it, unless the owner asks for a comparison. Another build or
configuration is another run of the same suite, never a new suite. Changing a suite's saves
makes a new version (`suite1-v2`).

## Start a run

`/rerun-suite` does all of this. By hand:

1. **Freeze the inputs** from a clean borg-reborn-rs checkout at the commit:

   ```sh
   python3 -m zoo.suite_runs snapshot --source ../borg-reborn-rs --name suite1-reborn-main-<sha8>-stock
   # or, with a profile:  --profile reborn-bundle-none-speed30
   ```

   This writes `scenario-inputs/NAME/`:
   - `borg.txt`, the shipped file unchanged;
   - the plan file, if the settings name one;
   - `provenance.json`: source commit, Rust source hash, native-tools pin, settings.

   It refuses a configuration this runner can't play: a core other than borg-rs, or an errand.
2. **Write `definitions/NAME.yaml`.** Copy `definitions/suite1-reborn-main-4d83dd26-stock.yaml`
   and change the name, issue, source commit, inputs hashes, native-tools pin (the source's
   `death-tools-pin.txt`), authorization and prespecification. Then run
   `python3 -m zoo define definitions/NAME.yaml`.
3. **Open a PR.** The workflow reads the definition from the branch it runs on.
4. **Dispatch the smoke** (18 cases, 2 per class):

   ```sh
   gh workflow run suite-run.yml -R diegoami/borg-zoo --ref BRANCH \
     -f definition=scenario-experiments/NAME.json -f stage=smoke
   ```

5. **Grow the run**, one stage at a time and on the owner's go: small 90, medium 360, big
   900, full 999. Each stage names the preceding stage's run:

   ```sh
   gh workflow run suite-run.yml -R diegoami/borg-zoo --ref BRANCH \
     -f definition=scenario-experiments/NAME.json -f stage=small -f parent_run=<smoke run id>
   ```

   A later stage reuses the parent's build, plan and cells. It revalidates the parent's
   cells, refuses to continue if the parent had a missing, invalid or stopped cell, and plays
   only the cases the stage adds.

## What a stage checks

Each cell's native receipts must show:
- the source commit, the binary and the build;
- the save and its saved RNG;
- the loaded turn, depth, HP and SP;
- the initial pack, equipment and rune hashes, equal to the suite's (`gear.json`, taken from
  run 44058010288, where both arms agreed on every case);
- the borg-rs core;
- every `borg_*` setting of the frozen file written as frozen;
- every `borg_param_*` effective, with origin `borg.txt`;
- the plan loaded if one was frozen, and none loaded otherwise;
- a death or the exact horizon.

Missing, invalid and stopped cells stay in the denominator, and fail the gate.

## Where the results go

Each stage uploads its raw report and cumulative cells, kept 90 days, and its native evidence,
kept 14 days. It also appends a dashboard record to the `results` branch under
`saved-incident-results/NAME/RUN-ATTEMPT/`. The pages workflow then shows the record on the
Scenarios tab: the build's death share, deaths per class, and every scenario's outcome with a
single-scenario command for the build and configuration.

## Re-run one scenario

From a borg-cemetery checkout of branch `evidence/paired-smoke-validation` (where `scripts/single_encounter.py` and its guide `docs/RUN-A-SCENARIO.md` live), with the bank unpacked:

```sh
python3 scripts/single_encounter.py --suite <shard> --case <case id> --source ../borg-reborn-rs \
  --source-commit <commit> --core borg-rs --native-tools ../borg-cemetery-tools \
  --borg-txt <borg-zoo>/scenario-inputs/NAME/borg.txt --out /tmp/<case>
```

Each case's page on the dashboard prints this command with the right values filled in.

## Prepare the next independent suite

A new preparation bank is a new suite number; a different executable or settings
file on existing saves is another run of that suite. Do not regenerate Suite 1.

Suite 2 is tracked by #184. Its preparation definition is
`definitions/suite2-v1-harvest.yaml`; the pinned Cemetery
`synthetic/suite2-v1/harvest-spec.json` freezes the source, controller,
configuration hashes, full and smoke seed allocations, checkpoint cadence,
incident definition, time limits, and Suite 1 exclusion inventory **before** play.
It uses borg-reborn-rs `50ae902a68a8732d56a6e1adf47deca4a9db7d7f`, the HEAD
resolved for the owner's request, with its own shipped borg-rs defaults.

The supported preparation dispatch is separate from a suite execution:

```sh
gh workflow run harvest-incidents.yml -R diegoami/borg-zoo --ref BRANCH \
  -f definition=scenario-experiments/suite2-v1-harvest.json -f stage=smoke
# Inspect the completed all-class harvest and the 18 native restart receipts.
# The full requested harvest requires that successful smoke on the exact same head.
gh workflow run harvest-incidents.yml -R diegoami/borg-zoo --ref BRANCH \
  -f definition=scenario-experiments/suite2-v1-harvest.json -f stage=harvest \
  -f smoke_run=SMOKE_RUN_ID
```

This is **preparation**, not a population study or an execution of all 999 cases.
The smoke uses separate seeds, two saved starts per class; the full harvest must
produce 111 per class. Every natural death and failed/rejected attempt remains in
its class's `incident-raw-N` artifact, not only the lives whose starts were
selected. These raw artifacts last 90 days; copy them to canonical permanent
Cemetery storage when freezing the bank. A short class fails assembly rather
than borrowing a different class or duplicating a start.

To add Suite 3, first freeze a new Cemetery `synthetic/suite3-v1/` preparation
manifest and its source/configuration snapshots. Allocate disjoint source seeds
and an exclusion inventory covering **every** earlier suite's initial save
hashes and source seeds. Keep the same incident witnesses, level-1 collection,
class quotas, and bounded native validation. Add a harvest YAML using the new
`suite_id` and exact Cemetery/source/tools commits; generate its JSON. Dispatch
and inspect its own smoke before the owner-authorized full harvest. Never reuse
an existing archive path or frozen suite ID for changed inputs.

Only after all 999 starts are validated, the mixed-class restart smoke passes,
and the native archive/checksum/provenance are published in Cemetery, add
`scenario-suites/suite3-v1/suite.json` with its exact archive location, digest,
case plan, initial gear reference and execution protocol. Registered suites
appear automatically in Scenarios. Use `suite: suite3-v1` in a `suite-run` YAML
to select it, pinning the tested Borg/settings separately as described above.
Differences between separate banks are coverage differences, never paired
rescues or newly killed cases.

### Suite 2 capture blocker

The first preparation smoke, [44121110906](https://github.com/diegoami/borg-zoo/actions/runs/44121110906),
built and played the pinned HEAD, but its completed attempts emitted no
`encounters.jsonl`. `BORG_ENCOUNTER_LOG` is absent from this source. The
`BORG_OBSERVATION_LOG` / `BORG_KNOWLEDGE_LOG` hooks live inside the separate
reborn controller; the shipped borg-rs controller does not produce them.
A saved checkpoint plus an HP log cannot establish the required first
observable threat or full initial equipment coverage. Do not substitute a
terminal death frame or fabricate that information.

Suite 2 is **not frozen and not selectable for execution**. Scenarios shows its
preparation status, while the execution catalogue continues to accept only
validated `suite.json` entries. The requested full harvest was not dispatched.
A source-compatible capture interface must be added and validated on borg-rs,
then preparation must be pinned again and its all-class smoke must pass.
The source preflight now rejects this known unsupported interface before
scheduling more natural lives. The original failed evidence remains retained
in Cemetery; no Suite 1 input or historical report is replaced.
