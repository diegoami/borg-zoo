# Open work and handover state

The [Track P play-style candidate index](PLAY-STYLE-CANDIDATES.md) lists
plausible changes and neutral settings available to adopt for play style.

## Traps for a new session

- Claim the study after checking issue comments, branches, PRs and active
  runs (RULES 17). Use your own worktree.
- Merge first. If the merge fails, stop. Dispatch `compare.yml` using
  `experiment=experiments/NAME.json`, not the experiment's bare name.
  Check each named parameter at the pinned specimen ref. Preflight checks
  the plan, not the upstream parameter inventory.
- Dispatch a tier only after its pilot gate is READ, not when the run
  succeeds: the #750 watcher dispatched a ladder on run success and ran a
  whole tier with a broken arm (its own `nodear` set a parameter below its
  1-20 range).
- Start with a pilot and inspect its published gate before proposing the
  next tier. The owner's standing 2026-11-20 guidance allows pilots and
  small tiers. Ask before heavy tiers or 200-Ranger runs unless specifically
  authorized for that study.
- A rejected `results -> results (fetch first)` push is a collect failure.
  Use `gh run rerun RUN_ID --failed`, then verify the new
  `RUN_ID-ATTEMPT` directory. Do not redispatch games that already finished.
- Set `"external": true` on imported explicit seed lists to keep generated
  suite seeds frozen. On catalogue conflicts, regenerate from the merged
  catalogue and definitions, then regenerate `docs/PROFILES.md`.
- Preserve the replay build while it is available (7 days normally, 90
  with retained evidence). Suite 1's saved engine is `42cd156ac`. Builds
  on `574b618c` are rejected by the saved-suite identity check.

## Two lines of borg-reborn-rs: baselines (owner, 2026-11-22, #645)

borg-reborn-rs has two diverged lines. **track-p** is the working line (every source PR integrates there); **main** receives
reviewed milestone merges only (#822 merged track-p into main as `f57499d0` on 2026-11-21; main has since gained #900, which
track-p does not have). A result is tied to its exact source, so "the current build" always names a line.

- **Baselines.** A full ladder on track-p (pilot 45, small-rest 45, medium 270, big 540, full 900; one arm, shipped settings, classes-1800,
  100,000 turns) after every milestone and whenever the head has moved by several merged PRs; a lighter one on main (pilot, small-rest,
  medium = 360 starts) as an update. Current: track-p `9085c266` (#645) and main `b34196c5` (#645); earlier on main: `ed52fec1` (#601),
  `ab775d48` (#609), `f57499d0` (#623, the merge base of the two lines, so valid for both as a baseline and for neither's later PRs).
- **Experiments.** Development experiments pin the track-p head (or the requester's branch, which is built on it); the specimen label names
  the line and the merge base. A lead measured on one line is re-run on the working line before anyone ships it (kit_leash: #589 on
  `f57499d0`, #646 on track-p).
- **Tool.** `python3 -m zoo.lines` prints the two heads and where each specimen stands against them (docs/LINES.md is the generated list).
  `/next-experiments` checks the head of the specimen's line before proposing a next tier.

## Status checked 2026-11-24 (handover: gates read, six runs in flight)

**In flight** (all `compare`, dispatched 2026-11-24 on the owner's "start them all",
after each gate was read):

- #742 `reborn-guards-small` (450 cells, classes-1800 starts 1-90): run
  [45353585470](https://github.com/diegoami/borg-zoo/actions/runs/45353585470), from `main`.
- #749 walk-away verysmall (2 arms x 45 starts, classes-1800): runs
  [45353782160](https://github.com/diegoami/borg-zoo/actions/runs/45353782160) (normal world),
  [45353787944](https://github.com/diegoami/borg-zoo/actions/runs/45353787944) (patches-x8),
  [45353793296](https://github.com/diegoami/borg-zoo/actions/runs/45353793296) (poison-x8),
  branch `definition/new-params-wa-tiers`.
- #744 `reborn-dc2` pilots (4 arms x 18, specimen `4.2.6-reborn-rust-trackp-c5501d3c-pw`): runs
  [45353937365](https://github.com/diegoami/borg-zoo/actions/runs/45353937365) (normal world) and
  [45353942202](https://github.com/diegoami/borg-zoo/actions/runs/45353942202) (poison-x8),
  branch `definition/dc2-c5501d3c`.

**Next steps when these finish** (one tier at a time, gate read each time):

1. guards-small gate read -> dispatch `reborn-guards-medium` (defined, 1,350 cells, on `main`).
2. Each wa verysmall gate -> its world's small-rest tier (not yet defined; mirror
   `definitions/reborn-wa-pilot.yaml`, keep the `borg_world:` arm setting).
3. dc2 pilot gates -> the `reborn-dc2` verysmall (not yet defined).
4. PRs for `definition/new-params-wa-tiers` (carries the #749/#744 pilots too) and
   `definition/dc2-c5501d3c` (stacked on it) when the runs finish; preflight was 0 problems.
   **Collision, same day**: PR #759 (a parallel session) merged the SAME `c5501d3c`
   specimen block plus `reborn-dc2-receipt(-ps8)-pilot` (the #744 receipt repeats with
   `borg_town_plan: 1`) and the #752/#753 cure pilots onto `main`. The dc2 branch is
   stacked on `definition/new-params` and now conflicts with `main`: at merge time,
   regenerate the catalogue from the merged set (see Traps). Do not rewrite the dc2
   branch while its runs are in flight; both dc2 pilot runs read it as pushed.

**Gate reads posted 2026-11-23/24** (details in the issues): #742's pilots clean, but in
breeders-x4 ba/plus/poison replay ctl's keys 18/18 and guardsoff 11/18 - the guards are
barely exercised there at classes-18, so that world is "not tested", not "no difference".
#749's pilots: 0 deaths in all three worlds; the arm is fully exercised in patches-x8
(18/18 plays differ), 15/18 in normal and poison-x8. #744's pilots at `d96cc8de` passed,
then the study was **re-pinned to `c5501d3c`**: #1149 merged into track-p there, so `ship`
is upstream's shipped play from that commit (shipped values verified in `harness/borg.txt`:
neutralize 2 at 40 percent, ccw 2 at 112 percent, dear_after_recall 1), and walk-away
(#1148) ships in every arm. The `d96cc8de` results stay on the results branch as the
pre-merge read.

**#750 reborn-dear ladder read (2026-11-23, comment posted)**: clean null - 0 discordant
pairs over 360 paired starts; the only death in either arm is seed 1736476654 (Hobbit
Warrior, CL 1), a grey mushroom patch at turn 10,630, byte-identical in both arms (same
play hash). Ablation: `noscum` 3 extra deaths, `nopot` a DL3/DL5 cost - leads only;
`nohall` was not exercised at this tier (359/360 identical plays).

**Build fact**: track-p `13151fb5` (the #750 ablation and dear specimen) does **not**
contain #1147/#1148 - the walk-away merge `85f8800b` is 13 commits later. Do not read
`13151fb5`-era results as walk-away-included.

**Death report for seed 1736476654** (owner-served, not published): HTML at
`/tmp/opencode/death-1736476654/warrior-patch-1736476654.html` (served at
`http://127.0.0.1:8787/` while the session lives); play pack `~/borg-play/dear-1736476654`
(saves at 7630/9630/10330/10627; both the recorder's and the pack's replays match the
cell's play hash). Findings: the patch spawned on the DL1 arrival turn with line of sight;
the Borg stepped off its arrival staircase before the first spore; 0 of 5 confused swings
reached the patch; no cure potion was carried; Phase Door x6 never read. Deliberately not
done: cemetery dossier PR and any public link on #750 - the HTML is localhost-only, so
publish it first. Scratchpad `/tmp/opencode/death-1736476654` (clone and builds, about
200 MB) waits for the owner's cleanup word.

**Still waiting on the owner** (unchanged from 2026-11-23): #750 B-dial ladders (10
exercised dials named in the issue), #732 verysmall, #723 small (or close it - the pilot
shows a progress cost and no death benefit), #722 ladder, #713 small, #712 worlds,
#706 tiers, #693/#688 tiers, #123 medium, #687 (needs a named Mage seed set), and the
#735 re-measure on a post-#1150 head.

## Non-mushroom deaths of track-p 9085c266, full tier (2026-11-22, #645)

The 17 deaths of run 45028029063 that a grey mushroom patch did not cause, replayed locally on both heads. The leads, per death and turn,
are in [reports/reborn-trackp-9085c266-full-other-deaths](../reports/reborn-trackp-9085c266-full-other-deaths/README.md). They are
leads, not fixes.

- **track-p `4b2c2fcf`:** 15 of 17 still die, each in the identical game. The two cursed-torch town deaths survive (#899).
- **main `c29664e1`:** 0 of 17 die, each the identical game to f57499d0. The 15 deaths come from track-p-only code.
- **Where the games split:** track-p and main split in the first town visit on every seed; in 9 of 15, track-p buys Phase Door where main
  buys CLW, CSW or oil (#873). That is where the paths split, not a cause of death.
- **The mushroom count is 13 of 28, not 11.** Two "Grip" deaths (453254028, 857532386) are kill-on-sight swings at a grey mushroom patch
  while confused, with Grip biting.
- **The rest:** the #842 fast-fragile rules (unchanged against main), two two-step loops (the torch one is fixed on both heads; the
  white-jelly one is not), and singles.
- **Not dispatched:** a paired track-p arm with #873's staples set back would test the town lead; that is the owner's call.

## Fixes are tested twice: in an enriched world and in the normal world (owner, 2026-11-22; RULES 21)

A request for a fix aimed at one situation (a crow, a grey mushroom patch, a breeder room) is measured in two runs: a **parallel run in a
world where the situation is much more frequent**, and the normal world. In the normal world the situation is a few games in a thousand, so a
tier of 360 starts shows almost nothing; the enriched world shows whether the fix acts when it matters, and the normal world (paired by start
against the baseline) shows whether it harms elsewhere. The ticket proposes the scenario; the zoo files a companion issue where it did not
(#676-#683). The worlds exist: `harness/worlds/breeders-x4/x8` (breeders 4 and 8 times as likely, shallower) and, since borg-reborn-rs #970,
`favour = <race>` with `favour_weight = N` in `scripts/make-world.py` (`patches-x4`, `patches-x8`: the grey mushroom patch N times as likely,
depth unchanged). The world tool is taken from the specimen's source, so the pinned build must contain #970. A new fix for a monster gets its own
world (`favour = crow`, weight 4 or 8), pinned in the specimen's `worlds:` by sha256 as in #642, #659 and #678. Arms are compared only inside a
world; a world is a stress test, never a ranking of settings, and a lead in it still needs the normal-world run before a shipped value changes.

## Read these first

1. `docs/FINDINGS.md`: what the finished experiments showed. New results must
   be added here when their experiment finishes.
2. `docs/DESIGN.md`: the measurement design, the statistics, and the open
   design questions.
3. `docs/SUITE-RUNS.md`: saved-suite runs. Suite 1 is the balanced999 bank.
4. `docs/DEFINE.md`: experiments in YAML. The tiers are pilot, verysmall
   (starts 1-45), small (or small-rest after verysmall), medium, big and full.
5. `docs/OPEN-ISSUE-FOLLOWUPS.md`, `docs/M13-MEASUREMENT.md`: older debts.

**Several sessions work here at once.** Before starting an issue, read its
latest comments and `git log origin/main` for commits naming it. Work in your
own worktree. Resolve code conflicts by hand: merging both sides is only safe
for catalogue JSON and FINDINGS prose. Merge only when
`python3 -m unittest discover -s tests` passes.

## Skills

- `/pilot-deaths`: replay a pilot's (or verysmall's) deaths from the run's own
  build and write `reports/NAME-deaths/` (`python3 -m zoo.death_report`). Each
  report ends with a handover section for borg-reborn-rs. Offer it after every
  pilot gate.
- `/rerun-suite`: a sanity check of one compatible borg-reborn-rs build on
  Suite 1 (`suite-run.yml`), using that commit's shipped `harness/borg.txt`
  by default. See [SUITE-RUNS](SUITE-RUNS.md#engine-compatibility).
- `/profiles`: the named arm sets and the settings tried so far.
- `/next-experiments`: go through every run (`python3 -m zoo.history --pool`, tiers of
  one study read as one) and propose the best next experiments, each with a draft
  definition. Proposes only; the owner picks, and every new arm starts with a pilot
  (RULES 16).
- `/propose-config`: propose changes to borg-reborn-rs main's shipped `harness/borg.txt`
  from the zoo's evidence, one graded proposal per setting, and a borg-reborn-rs issue
  draft for the owner to file (the zoo never edits that repository, RULES 2).

## Status checked 2026-11-21

- The pilots queued behind #521 finished. See the results on #516, #517,
  #518, #520, #522 and #524. #516 and #517 were superseded. #520's native
  full45 finished with identical play in all 45 pairs.
- Collection retries recovered #563's 54-cell Recall reserve pilot
  (`44894144699-2`) and #566's 45-start verysmall slice
  (`44894181893-2`). All five #566 slices are archived, with 29 deaths
  in 1,800 distinct starts. See [FINDINGS](FINDINGS.md) for both gates.
- #495's landing check seldom changed play at 200k. The next attempt needs
  a saved encounter that reaches the check or longer games.
- Owner decisions remain on the study issues. Open decisions include a
  saved suite for the newer engine (#184), whether to pursue a saved-character
  workflow, and whether to continue any pilot whose mechanism was not
  exercised. See [FINDINGS](FINDINGS.md) for the measurements.

## Historical handovers

The dated handovers below preserve decisions and observations at the time.
Verify each issue, PR and run against GitHub before acting on its status.
The 2026-11-20 closure batch and cleanup notes remain in this file's history.

## Open issues (2026-11-16)

- **#144:** implementation adds pinned Cemetery dispatch, immutable pushid
  resolution, durable per-cell collection and paired impact reports separate
  from natural population results. See [SCENARIO-DISPATCH.md](SCENARIO-DISPATCH.md).
  The smallest two-pushid smoke and its receipts are prepared for review; no
  larger tier is authorized or launched. Caster equipment still depends on
  reborn #382.

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
independent of PR145's generated-birth qualification; it does not broaden that
contract or dispatch a larger tier. Inspect all eight source/build/profile/native-start
receipts and per-class outcomes before proposing any larger experiment.
Production result/site registration remains an explicit follow-up under #144.
