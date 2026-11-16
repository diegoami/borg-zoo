# Open work and handover state

What is open in this repository, why, and what the next session should read
first. Written 2026-11-16 after a session that merged PRs #90, #92, #97, #98,
#100, #101, #104 and #110, closed issues #48, #79, #81 and #88, and dispatched
several large experiments. The repository's own rules still apply: results are
append-only, a specimen/profile/suite/experiment is a catalogue change with a
pull request, and starting a large experiment is the owner's call.

## Read these first

1. `docs/FINDINGS.md` — what the finished experiments showed. New results must
   be added here when their experiment finishes.
2. `docs/DESIGN.md` — the measurement design, the statistics, and the open
   design questions (primary endpoint, net worth, Lunal arm).
3. `docs/OPEN-ISSUE-FOLLOWUPS.md` — older issue follow-ups, including what is
   still owed for the no-store baseline observer invariant.
4. `docs/M13-MEASUREMENT.md` and `docs/measurement/` — the per-fix M13 mode
   debt, with each owed arm marked not measured, unreachable, or cleanup.

## Open issues

| Issue | State | What is needed |
| --- | --- | --- |
| [#123](https://github.com/diegoami/borg-zoo/issues/123) | Adapter merged (#125); four-arm pilot passed (run 43845673921); five-arm pilot passed (run 43851628610, play identical to the four-arm pilot in all 72 shared cells); five-arm specimen `4.2.6-reborn-rust-plans-m13` (1c4b351b, #354's merge; the same game as 2f74e1c5 plus the ambitious plan; no #355, which main reverted in #379) added with the five-arm pilot `reborn-plans-m13-classes-18`; the development run is **on hold** for the borg-rs#90 fix specimen (see below) | borg-reborn-rs errands plan × M13 shopping. The adapter now ships a specimen's pinned `"plans"` (`harness/plans/NAME`, hash-checked at build and run) as `OUT/user/NAME` when a profile sets `borg_plan`, records `plan: {name, sha256}` per cell and `plans` in the build manifest, treats exit status 2 without a summary as `config_error`, reports `borg_stopped` as its own outcome for plan specimens, and clears ambient `BORG_*` overrides. Specimen `4.2.6-reborn-rust-plan-m13` (2f74e1c5) and the four 2×2 profiles are in the catalogue; experiments `reborn-plan-m13-classes-18` (pilot, 72) and `reborn-plan-m13-classes-1800` (7,200) are defined. The ambitious arm runs on the five-arm specimen; the development prespecification is amended for it. For plan specimens the adapter also checks the core's copy of the loaded plan (`OUT/errands_plan.txt`) against the requested hash, and records a cell with 1,000+ keys at one game turn (borg-rs#90's oil store/take loop) as `stalled`, keeping its observed outcome. Proposed scale: a 72-game `classes-18` pilot, then 7,200 games on `classes-1800`. Two constraints are recorded in the issue: the ambitious plan did not deepen play within 100k turns (mean max DL 2.1 versus 3.6 for shopping alone), and an M13 town-planner stall (oil buy/store loop) is routed upstream as borg-rs#90, so that arm measures a known-defective configuration. |
| [#114](https://github.com/diegoami/borg-zoo/issues/114) | Planning | Shared data storage and redesign of Borg zoo and cemetery. |
| [#105](https://github.com/diegoami/borg-zoo/issues/105) | Ledger open | Post-fix Neo measurement ledger. The truth-corrected cohort and the books-509 cohort have since completed; their results need adding to `docs/FINDINGS.md`. |

## #123: switched to the borg-rs#90 fix

borg-reborn-rs#415 (closes #368) merged as `8a0b57c8`, which vendors borg-rs `8c5d000a` (#92 Home guard, #88 additive trip policy). The development experiment now runs on `4.2.6-reborn-rust-plans-m13-fix90` with five arms, all with the trip policy off (owner decision): control, town, plan, plan-town and ambitious-town, 9,000 games. Its amended prespecification records the ref, the different source hash, the stall and key-outlier flags, and the earlier loop-era pilots that are not comparable. Whether the trip policy belongs in the study is tested by the 3×3 pilot `reborn-trip-3x3-classes-18` on the same specimen. It runs in tiers (RULES 14): the 3×3 pilot (run 43863985583) and the small tier (run 43868362767, gate passed) are done. Medium (`reborn-plan-m13-medium`, 1,350 games) waits for the owner's go. The stair livelock borg-reborn-rs#421 stalls about 1–2% of ambitious-town cells. The small tier's town against plan-town deaths (38, D0031–D0068) and their investigation are in borg-cemetery#19: the plan's extra deaths are mostly casters held in town-endpoint phases, who die at a lower level than their no-plan twins.

## Closed as obsolete (owner, 2026-11-16)

- **#129**, PR92's Home fix with PR88's returns in borg-rs. Its specimen `4.2.6-rs-pr92-home-fix`, the experiment `rs-home-fix-returns` and its smoke stay in the catalogue, unused. The smoke (run 43858601495) is on the results branch. All six arm runs were cancelled before collecting: 43859526668, 43861258250, 43861270610, 43861283691, 43861297380 and 43861310431.
- **#87**, the M13 per-mode arms. They won't be measured, and `m12-m13-explicit` won't be re-dispatched. `docs/M13-MEASUREMENT.md` stays as the record of that debt.

#123 is the borg-reborn-rs study still being worked on. Its 3×3 pilot `reborn-trip-3x3-classes-18` crosses plan (none, errand, ambitious) with shopping (default, new inventory, new inventory + trip (2,4)), 162 games on `8a0b57c8`.

## Open pull requests

- [#121](https://github.com/diegoami/borg-zoo/pull/121) — repeat the Neo
  seeded-v2 study with only the carried-book value correction.
- [#124](https://github.com/diegoami/borg-zoo/pull/124) — plan: include
  cemetery synthetic scenarios in Borg evaluation.

## Failed run that needs attention

**`m12-m13-explicit`, run 43703176769** — cause found: all 8 run shards hit the run job's 300-minute timeout and were cancelled before writing records, so the grid needs more shards or smaller arms, not a code fix. Every one of the 7,200 cells is
`harness_failure` with `error: no record collected (job failed or was
cancelled)`. No result is usable and the run must not be read as evidence that
M12 and M13 differ. The plan/build jobs succeeded, so the failure is in the
run shards. Read the run's job logs before dispatching a replacement; the
cause may be the same class of problem as the results-branch push race that
hit run 43703201583 attempt 1 (see below).

## Results-branch push race

The `collect` job checks out the results branch, commits one directory and
pushes. Two concurrent collects can both succeed locally and then have the
second push rejected as non-fast-forward, which fails the whole workflow even
though the gameplay succeeded. This happened to run 43703201583 attempt 1
(the reviewed-E reborn smoke): 6/6 cells, no missing cells, but the push was
rejected because the town-negative collect had landed first. Rerunning the
failed job fixed it. If several collects are in flight, expect some push
failures and rerun them rather than re-dispatching the experiments.

## Owner decisions and preferences stated in this session

- **Dashboard "best" is a weighted combination**, not a lexicographic order:
  60% survivability plus 40% normalised depth + level, with progress
  normalised within the eligible candidates of the same line. A setup with
  almost no progress is excluded from selection. This replaced an earlier
  "depth + level first, survivability as tiebreaker" rule, which the owner
  rejected explicitly.
- **Reports must make identity obvious.** Every report page carries an open
  "Builds compared" table (specimen, repository, exact commit, link to the
  immutable tree), and the policy-study summaries carry a "Configuration
  difference" column and a death percentage. The owner wants to be able to
  see what was compared and get back to the source without reverse-engineering
  catalogue identifiers.
- **Cancelled pointless work rather than letting it finish.** Two joint-M12
  evidence reruns (43703277532, 43703284175) were cancelled because they
  re-measured a policy that had already failed to show an effect; the owner
  wanted the reason investigated, not more aggregate numbers. Note the
  consequence: the existing M12 studies recorded outcomes only, so the
  mechanism (over-purchasing, return timing, delay cost, gold policy,
  object-coverage blind spots) is still unestablished. The likely candidate is
  object coverage: the M12 studies predate the coverage fixes that the later
  `rs-kit-trip` work made.
- **Review, merge, then run.** For a batch of open PRs the owner chose to
  review and merge them in dependency order, then dispatch the experiments
  they define, rather than merging without running or running without
  merging.
- **Do not wait to be told to finish routine steps.** The owner does not want
  to have to say "commit, push, merge" for ordinary PR handling.

## Experiments dispatched by this session and their outcomes

Runs listed as completed are on the `results` branch; see `docs/FINDINGS.md`
for the ones already written up.

| Experiment | Run | Outcome |
| --- | --- | --- |
| `neo-merged-seeded-v2-1800` | 43670231534 | Completed but **superseded**: built at Borg `76f25aa` before the merged danger/HP/retreat repairs, and the headless host denied monster truth reads. 1,076 deaths, 581 caps, 139 stalls, 4 timeouts. Kept as an immutable historical run; not a repaired-Borg baseline. |
| `neo-truth-100-seeded-v2-1800` | 43702732056 | Completed: 989 deaths, 732 caps, 75 stalls, 4 timeouts; 57.5% of finished games died, median level 3, median depth 2. |
| `neo-books-509-seeded-v2-1800` | 43759670685 | Completed: 860 deaths, 843 caps, 95 stalls, 2 timeouts; 50.5% died. |
| `rs-pr85-full` | 43720870587 | Completed, no failures in any cell: 10,800 games on `classes-1800-d`, borg-rs `71cff24e`. New shopping with legacy returns reached 385 deaths against 535 for existing rules; the four threshold arms landed between. Written up in `docs/FINDINGS.md`; still a development calibration, not a confirmed winner. |
| `m12-m13-explicit` | 43703176769 | **All 7,200 cells `harness_failure`.** See above. |
| `reborn-pilot-c-classes-1800` | 43702957409 | Completed: 3,600 games. borg-rs core without the ladder errand 524 deaths (29.1%); with the ladder errand 448 (24.9%), paired 338 rescued against 262 newly killed. Median level and depth unchanged at 4 and 2. One development suite, so descriptive only. |
| `town-negative` | 43703038895 | Completed: 36 games, no config errors, 4 rescued against 4 newly killed. No signal. |
| `town-class-shadow-smoke` | 43703164822 | Completed: configuration-routing checks. |
| `m12-m13-modes-smoke` | 43703188519 | Completed: 18-cell mode check. |
| `reborn-e-reviewed-smoke` | 43703201583 attempt 2 | Completed after rerunning the push race described above. |

## What was deliberately left undone

- The joint-M12 mechanism question was **not** answered. The evidence
  retention that would answer it was implemented (`zoo/town.py`,
  `zoo/town_shadow.py`, retained native receipts and policy streams, see
  `docs/TOWN-SHADOW.md`), but the two runs that would have used it were
  cancelled on the owner's instruction.
- The `m12-m13-explicit` grid was **not** re-dispatched, because the cause of
  the shard failure has not been diagnosed.
- The no-store baseline observer invariant for #81 remains **owed** to
  borg-rs: parsing the setting, watching gold rise, or seeing retail receipts
  do not prove that `shop_num` stayed -1 and that no shop or Home entry
  occurred. See `docs/OPEN-ISSUE-FOLLOWUPS.md`.

## Owner-requested saved caster encounters (#144)

The owner explicitly requests Zoo to run Cemetery's mixed-class saved suite.
The separate eight-case smoke is defined in
`definitions/cemetery-mixed-caster-encounters-smoke.yaml`; see
[SAVED-ENCOUNTERS.md](SAVED-ENCOUNTERS.md). It uses source6d1bca10 and exact
Cemetery bank fecca62c6b3f98452123a8256860f8251e653eb7, with two starts per pure
caster class. Relevant PR CI executes the actual games with read-only tokens
and publishes a job-summary report/artifacts. This is a saved-state baseline,
independent of PR145's generated-birth qualification; it does not merge that PR
or dispatch a larger tier. Inspect all eight source/build/profile/native-start
receipts and per-class outcomes before proposing any larger experiment.
Production result/site registration remains an explicit follow-up under #144.
