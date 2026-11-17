# Running a build on a saved suite

A **suite** is a frozen bank of saved encounters with its protocol:
`scenario-suites/ID/suite.json`. **Suite 1** (`suite1-v1`) is the balanced999 bank of
borg-zoo#168: 999 saves, 111 per class. Each save starts with fresh Borg memory and the
saved engine RNG, and plays an exact 2,000-engine-turn horizon under a 5-second native wall
limit.

A **run** is one build on a suite, with one configuration. The build is an exact
borg-reborn-rs commit. The configuration is either the commit's stock `harness/borg.txt`, or
that file with a Zoo profile's settings. Another build or configuration is another run of
the same suite, never a new suite. Changing a suite's saves makes a new version (`suite1-v2`).

Each run is compared case by case with the suite's **references**: published runs whose
outcomes are reused, not rerun. Today the references are the baseline (6d1bca10, reborn core)
and speed30 (193d9076, borg-rs plus the speed30 profile) arms of run 44058010288.

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
Scenarios tab: per class, against every reference arm, and case by case with a
single-scenario command for the run's build and configuration.

## Re-run one scenario

From a borg-cemetery checkout of branch `evidence/paired-smoke-validation` (where `scripts/single_encounter.py` and its guide `docs/RUN-A-SCENARIO.md` live), with the bank unpacked:

```sh
python3 scripts/single_encounter.py --suite <shard> --case <case id> --source ../borg-reborn-rs \
  --source-commit <commit> --core borg-rs --native-tools ../borg-cemetery-tools \
  --borg-txt <borg-zoo>/scenario-inputs/NAME/borg.txt --out /tmp/<case>
```

Each case's page on the dashboard prints this command with the right values filled in.
