---
name: rerun-suite
description: Sanity-check borg-reborn-rs main (HEAD, its own default settings) on a frozen saved-encounter suite (Suite 1 = the balanced999 bank). Use when the owner asks to rerun the scenarios or the suite on the current or a given build, or to grow such a run to its next stage.
---

# /rerun-suite [SUITE] [REF] [SETTINGS]

This is a sanity check of the main branch, so keep it simple:
- **SUITE:** `suite1-v1`.
- **REF:** the current borg-reborn-rs `main` HEAD. Resolve it to a full SHA and say which.
- **SETTINGS:** `stock`, meaning the commit's own `harness/borg.txt`, unchanged. Its defaults live in borg-reborn-rs, not in the Zoo; the snapshot is only a pinned copy. Override them with a profile only when the owner asks.
- **No other arms:** report the run alone. Compare it with another build only when the owner asks.

The format and the gate are in `docs/SUITE-RUNS.md`. The suites are in `scenario-suites/`.

## A new run

1. **Resolve the ref.** Check the source can load the suite's saves:
   - its `engine/UPSTREAM` commit must equal the suite's `protocol.engine_commit`;
   - note its `death-tools-pin.txt`.

   Suite 1 pins `42cd156ac`. A build on `574b618c` fails validation (#473).
   If the engine differs, report the mismatch. A compatible pinned ref can
   still run Suite 1. Use a newer engine only after the owner decides how
   to qualify the bank.
2. **Name the run** `suite1-reborn-<branch or label>-<sha8>-<stock|profile>`. Check that no
   `scenario-inputs/NAME` or `scenario-experiments/NAME.json` exists yet.
3. **Freeze the inputs.** Use a clean detached worktree of borg-reborn-rs at the SHA, never
   the owner's checkout. Then run
   `python3 -m zoo.suite_runs snapshot --source <worktree> --name NAME [--profile P]`.
4. **Write `definitions/NAME.yaml`** from the latest suite-run definition. Change the name,
   the issue (the run request's), the question, the source commit, the inputs hashes from the
   snapshot output, the native-tools pin, `owner_authorization` (the owner's words and date)
   and `prespecified`. Then run `python3 -m zoo define definitions/NAME.yaml` and
   `python3 -m unittest tests.test_suite_runs`.
5. **Open a PR** on a branch `suite-run/NAME`, then dispatch the smoke:
   `gh workflow run suite-run.yml -R diegoami/borg-zoo --ref suite-run/NAME -f definition=scenario-experiments/NAME.json -f stage=smoke`.
   Comment the run link on the issue.
6. **Check the gate** when it finishes:
   - the `collect` job's summary: 0 missing, 0 invalid, 0 stopped;
   - the `archive` job appended `saved-incident-results/NAME/RUN-ATTEMPT/comparison.json`;
   - the pages rebuild shows the run under Scenarios.

   Then report to the owner:
   - the death share;
   - deaths per class;
   - anything invalid, missing or stopped;
   - the Scenarios link: `https://diegoami.github.io/borg-zoo/scenarios/saved/NAME/RUN-ATTEMPT/index.html`.

## The next stage

Only on the owner's go, one stage at a time (RULES 14): small, medium, big, full. Run
`gh workflow run suite-run.yml ... -f stage=<next> -f parent_run=<the previous stage's run id>`.
The workflow reuses the parent's build and cells and refuses a parent that failed its gate.
Check and report each stage as in step 6. Add the finished run to `docs/FINDINGS.md`.
