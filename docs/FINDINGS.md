# Findings

What the zoo's completed experiments have shown, with the run behind each.

**Balanced999 saved encounters (#168):** [full paired experiment](../reports/saved-encounters/balanced999-incidents/full-44058010288/README.md)
completed1998/1998 valid cells,111 scenarios per class in each setup. Baseline
reborn had528 deaths/471 finite-horizon survivals; the exact Zoo speed30 bundle
had291/708. Paired315 rescued and78 newly killed;213 both died and393 both
survived. Both compiled builds were reused across nonoverlapping balanced tiers.
Sources, controllers and complete configurations differ; this is descriptive
regression evidence on an incident-selected bank. Population and isolated
speed30 claims need separate studies. The completed comparison and all999 individual case pages are live in the Zoo
Scenarios dashboard after the owner-approved UI PR179 merge.

**Saved caster encounters on Zoo (#144):** [actual eight-case cloud run43966646449](../reports/saved-encounters/cemetery-mixed-caster-encounters-smoke/cloud-43966646449/README.md)
completed8/8 valid with two starts per pure caster class,5 deaths/3 finite-horizon
survivals and no invalid/missing cells. Native encounter execution took4.83s
after building source6d1bca10 once. The source/core/profile/save/build receipts
and parent-life lineage are retained; canonical native bytes are in Cemetery.
This is a saved-state baseline, not PR145's generated-birth comparison and not
an improvement/population result. No larger tier was dispatched.

**Cemetery scenario dispatch smoke (#144):**
[Two-pushid receipts and limits](../reports/scenarios/cemetery-caster-two-pushids-smoke/local-144/README.md).
One pinned Gnome Mage birth at depth 1, seed 202, completed on reborn
99473510 and d3ebe3c0: both survived the requested 3,000-engine-turn cap
(actual 3,003, about 300 player turns). All 2/2 cells passed source/binary,
start and effective-settings checks. This validates the separate synthetic
dispatch/impact path; it is not population or improvement evidence, and it
does not test observed caster equipment. Qualified near-death is unavailable.

**Local C/Neo birth-alignment pilot:**
[report and source evidence](../reports/c-neo-birth-alignment-pilot-v1/README.md).
Nine Human classes plus a repeat per engine verify recommended point buy,
initial HP/SP, and all46 initial/active Boolean options. Shared seeds initialize
the same WELL pool, but C's native birth-menu path consumes age/history draws
before HP, while Neo's headless path rolls HP first. Gear quantities, gold and
towns remain different. A discovered after-loop cap overrun (Necromancer2596
for requested2000) is retained; an opt-in exact-tick observer then stops all10
corrected Neo runs at2000, preserving their old command prefix. The native10
records already stop at2000. This is a configuration/RNG diagnostic, not a
survival comparison or catalogue cohort; no large experiment was launched.

For the catalogue experiments below, every figure is from the run's
`cells.jsonl` on the `results` branch. Deaths
are before the suite's cap (100,000 game turns unless stated), out of the runs
that finished; runs that stalled, timed out or failed are excluded, never
counted as deaths. "Paired" figures count the seeds where only one arm died:
*rescued* means only the control died, *newly killed* means only the arm died,
and p is an exact two-sided McNemar test. `classes-1800` is a development suite,
so results on it are descriptive. A confirmation needs a prespecified
experiment on fresh seeds (`classes-1800-b`, `warriors-600`).

Update this file when an experiment finishes: add its finding, and edit or
remove any line it overturns. Open issues, the failed `m12-m13-explicit` run
and the owner's stated decisions are in [OPEN-WORK.md](OPEN-WORK.md).

**Mode cutoff (2026-11-10, borg-zoo#54).** Everything below was measured
before the explicit mode profiles existed. Each recorded run is labelled
pre-cutoff on its page; version pairings that straddle better-borg-c
`fd683ced` (PR 302, where `borg_munchkin_by_class` became the default) are
excluded. Findings backed only by within-version profile comparisons
survive the cutoff as they are; findings that read across it are noted.
The restarted experiments are `bbc-explicit-smoke` and `classes-explicit`
on `4.2.6-bbc-9ca98661`; `default` is no longer a profile any new
experiment may use.

## C Borg: better-borg-c milestones

**No single milestone from M5 to M7 lowers deaths measurably on its own.**
[`classes-m7`](../experiments/classes-m7.json), run 42526892708, classes-1800:

| Version | Deaths | 95% range |
|---|---|---|
| `4.2.6` (original) | 34.4% | 32.2–36.6 |
| `4.2.6-bbc-m6` | 32.8% | 30.7–35.0 |
| `4.2.6-bbc-m7` | 31.3% | 29.2–33.5 |
| `4.2.6-bbc-munchkin-by-class` (M7 plus the munchkin start by class, better-borg-c main's default) | 26.2% | 24.2–28.3 |

- **M7 against the original:** 358 rescued, 303 newly killed, p = 0.036. A small gain, at the edge of chance.
- **M7 against M6:** 329 rescued, 303 newly killed, p = 0.32.
- **The milestones change play a great deal** (only 47 of 1,800 games are identical between M6 and M7), but the deaths each one prevents and causes roughly cancel.
- **M7's source equals `4.2.6-bbc-ca3cd62`'s;** only docs and a tool differ. `m7-smoke` (run 42518589151) confirmed identical play on 3 of 3 seeds.
- **Determinism:** the original and M6 arms reproduced their `classes-m6` games on 3,599 of 3,600 seeds. The exception is one wall timeout.
- **Straddling rows:** the original/M6/M7 arms sit before the mode cutoff and the `munchkin-by-class` arm after it
  (better-borg-c `fd683ced`, PR 302), so under the new rules those cross rows are no longer computed; the table's
  last row stands only as a descriptive single arm. The confirmed statement that the munchkin start by class helps
  rests on [`munchkin-by-class-confirm`](../experiments/munchkin-by-class-confirm.json) below, which compares
  profiles within one version and does not straddle.

**The munchkin start by class is the one change with a confirmed effect.**
[`munchkin-by-class-confirm`](../experiments/munchkin-by-class-confirm.json), run 42498695402, on the fresh `classes-1800-b`, prespecified:

| Comparison | Deaths | Rescued against newly killed | p |
|---|---|---|---|
| Primary: original, `munchkin-wdr` against `default` | 28.4% against 31.8% | 145 against 83 | 4.8e-5 |
| Secondary: M6, `munchkin-wdr` against `default` | 30.7% against 35.6% | 152 against 63 | 1.1e-9 |

- **Not prespecified:** M6's default against the original's default was 35.6% against 31.8% (382 newly killed against 314 rescued, p = 0.011). It's a lead, not a finding.
- **better-borg-c made it the default** (better-borg-c#302): Warriors, Druids and Rangers start in munchkin mode to depth 6.
- **`munchkin-default-check`** (run 42510439213, classes-18) confirmed the built-in default plays exactly like profile `munchkin-wdr`: 18 of 18 identical.
- **On classes-1800, M7** (`classes-m7`, descriptive) **with the munchkin start by class:**
  - Warriors' deaths fall from 25% to 9%, Rangers' from 34% to 26%, and Druids' from 64% to 42%.
  - The other classes are untouched.
  - 24.6% of games end alive at the cap having reached dungeon level 5, against 2.2% for plain M7.

**The stair-dash step (M5 s05) was not confirmed.**
[`stair-dash-confirm`](../experiments/stair-dash-confirm.json), run 42508284537, `warriors-600`, s05 against s04:
- deaths were 26.3% against 27.8%;
- 66 rescued against 57 newly killed, p = 0.47.

**The munchkin start by class still helps at 200,000 turns, double the usual cap.**
[`classes-200k-best`](../experiments/classes-200k-best.json), run 42647082970, and
[`classes-200k-recommended`](../experiments/classes-200k-recommended.json), run 42711519129,
both on `classes-1800-200k`:

| Version | Deaths (n) |
|---|---|
| `4.2.6` default | 43.4% (1,800) |
| `4.2.6` + `munchkin-wdr` | 35.6% (1,800) |
| `4.2.6-bbc-munchkin-by-class` (recommended mix) | 33.2% (1,800) |

- Munchkin against vanilla default: 204 rescued, 63 newly killed, p = 1.6e-18 - the same
  direction as the 100,000-turn finding above, not a new effect.
- The recommended mix's own `munchkin-wdr` arm was not run at this scale: it is a confirmed
  no-op there (see DESIGN.md's Costs section), so it would only have spent cells re-measuring
  `4.2.6-bbc-munchkin-by-class`'s own default.
- Deaths are higher across the board than at 100,000 turns (more turns, more chances to die
  before the cap) - the comparison's *direction* is what carries over, not the absolute rates.

**M10 adds no new tracker carry.** `4.2.6-bbc-m10` (tag `4.2.6-impact-v10`) carries stays 98,
unchanged from M9: its units are two local-only improvements never proposed upstream and a
crash correction to the already-carried patch 0099. No death-rate comparison yet - see "Open".

**Milestone 15 and the new upstream head (#432, 2026-11-19; runs 44604305970 and 44604334824, classes-1800).**
- **The new upstream head:** the original C Borg at Angband master 574b618c (10 commits past 42cd156) has 618 deaths, against 617 on 42cd156 (15 / 16). It is unchanged.
- **better-borg-c v15** (tag 4.2.6-impact-v15, 137 carries on that same game commit):
  - normal (modes off): 482 deaths, 26.8%;
  - munchkin-class: 452, 25.1%.
  These are the fewest of any milestone (v13: 526 and 469).
- **Depth under normal:** v15 reaches less depth than v13 (mean max DL 2.10 against 2.40) at the same CL.
- **Against the original on the same game:**
  - v15 normal has 136 fewer deaths (417 / 281, descriptive across the mode cutoff, #54);
  - Warriors, Rogues, Blackguards, Rangers and Druids gain most;
  - Necromancers (73 against 64) and Priests (54 against 50) die more.
- **Munchkin-class against normal:** fewer deaths (111 / 81, p 0.036). Warriors gain (26 → 10) and Druids gain (111 → 84), but Rangers die more (59 → 72).

## Rust Borg: borg-rs

**The port is exact at M4, M5 and M6.** The Rust Borg and the C Borg of the same borg-rs tree play identically on 1,800 of 1,800 seeds at each milestone:
- M4: [`classes-rs-m4`](../experiments/classes-rs-m4.json), run 42505918011;
- M5 and M6: [`classes-rs-m6`](../experiments/classes-rs-m6.json), run 42540746957.

**The Rust M6 reproduces better-borg-c M6's results**, even though the frontend differs and borg-rs has an engine correction (neo-angband-tracker#474):
- All 1,799 comparable seeds end the same way.
- All 590 deaths have the same cause at the same turn.

This compares two harness kinds, so the statistics don't pair them. The check was a direct comparison of the cells.

**No measurable difference between borg-rs milestones** (`classes-rs-m6`):

| Version | Deaths |
|---|---|
| rs-m4 | 33.6% |
| rs-m5 | 33.2% |
| rs-m6 | 32.8% |

| Comparison | Rescued against newly killed | p |
|---|---|---|
| M5 against M4 | 335 against 327 | 0.79 |
| M6 against M4 | 353 against 338 | 0.59 |
| M6 against M5 | 226 against 219 | 0.78 |

Warriors do best at M5: 17% deaths, against 27% at M4 and 28% at M6.

**Reserve shopping's apparent Rogue regression remains unconfirmed** (#79).
The existing `rs-family-buying-classes-1800` control/reserve410 cells reproduce
200 Rogue pairs: 32 rescued, 48 newly killed, exact McNemar p = 0.092912.
None of the nine post-hoc class comparisons establishes an effect; the
Necromancer's 200 pairs have identical play hashes. The site now reports
paired deaths by class. [Reanalysis and frozen-input hashes](../reports/rogue-shopping-79/REPORT.md).
A fresh Rogue confirmation still needs the owner's endpoint and sizing.

- **Neo parity-and-books small tier: the measurement holds; five stalls are Borg loops (borg-zoo#137).**
  `neo-b4-parity-books-v1-small`, run 43876073942, 90 games: starts 1–90 of
  `neo-seeded-v2-classes-1800` (10 per class, the parent's characters), 100,000
  exact ticks. Borg 1.4.0-beta.6.zoo.1, source `464a1555`; tracker master
  `b9beb64d` (#113) has the same tree, and master `2e468420` (#114) differs only
  in docs. Engine `d27ed50f`, toolkit `638979d`.
  - Integrity: all 90 records reconciled with their assigned characters; no
    `config_error`; evidence complete for all 90.
  - Outcomes: 46 deaths, 39 turn-cap stops, 5 stalls. Mean final level 3.1,
    mean deepest level 2.1, 5 reached DL5+. Median wall time 106 s per game,
    maximum 322 s.
  - Deaths per 10 by class: Druid 9, Mage 8, Ranger 8, Necromancer 7, Priest 4,
    Blackguard 3, Rogue 3, Warrior 3, Paladin 1. The main killers were Farmer
    Maggot's dogs (Fang 7, Grip 5).
  - The 5 stalls were stopped by the runner's no-progress check (the same
    action changing nothing 40 times running). Each is a Borg loop:
    - Elf Blackguard 907433825: keeps walking into a yellow mushroom patch
      while "too afraid to attack" it.
    - Half-Orc Rogue 1125182320: keeps trying to read while blind.
    - Half-Troll Necromancer 1211397579: keeps trying to cast while blind.
    - High-Elf Blackguard 1263080150: keeps tunnelling granite with its weapon.
    - Half-Orc Necromancer 1770109965: keeps trying to sell a Cloak in a shop.
  - Descriptive only. The older book cohort (43759670685) used engine
    `b4af703` and Borg `d6215a8`, so no fix-by-fix or improvement claim is made.

- **Max-depth plans × return settings, small tier: clean run, but the plan caps don't hold (borg-zoo#147).**
  `reborn-maxdepth-returns-small`, run 43925269890, 900 games on
  `4.2.6-reborn-rust-maxdepth` (borg-reborn-rs `6d1bca10`: #440's max-depth plans
  and #444's planner item values). Ten arms: two plans × return off / (4,2) /
  (4,1) / (3,2) / (3,1), as (unknown stacks, pack slack), all with the town
  planner; `classes-1800-small`.

  | Return | `errands_plan.txt` deaths / 90 | vs off rescued / killed | ambitious deaths / 90 | vs off rescued / killed |
  | --- | ---: | ---: | ---: | ---: |
  | off | 20 | – | 20 (+1 stalled) | – |
  | (4,2) default | 21 | 1 / 2 | 20 | 2 / 2 |
  | (4,1) | 21 | 1 / 2 | 20 | 2 / 2 |
  | (3,2) | 22 | 0 / 2 | 23 | 1 / 4 |
  | (3,1) | 22 | 0 / 2 | 23 | 1 / 4 |

  - Integrity: one binary, no `config_error`, every loaded plan matched its
    pin. There are no key outliers. One frozen-turn stall (ambitious, return
    off, Ranger 60792140: one burst of 1,095 keys) is just over the threshold.
  - **No return setting lowered deaths.** Tighter settings were equal or
    slightly worse, with mean levels and depths almost unchanged.
  - **Pack slack had almost no effect.** (4,2) and (4,1) played identical keys in
    179 of 180 games, and (3,2) and (3,1) in all 180. Only the unknown-stacks
    threshold and the trip switch itself changed play.
  - **The plan caps don't hold.**
    - 131 games went deeper than their plan's cap for their final level; 103
      of them by one level.
    - 35 games died or ended below the cap: 31 deaths, about 15% of the run's
      206 deaths. They come from 7 starts, repeated across arms.
    - A cap sets `borg_no_deeper`, which the core treats as a level it is "not
      prepared for", by design not a hard limit. The replays show the core
      passing it by reading unknown scrolls that are Deep Descent, by fleeing
      down stairs when it finds no up stairs, and by plain stair descents.
  - Descriptive only, at 10 starts per class.

**borg-rs Impact v15R against better-borg-c v15 (#463, 2026-11-20; tag 4.2.6-impact-v15, 007e3a1b, Angband 574b618c).**
- **The munchkin and lunal modes are gone:** borg-rs removed them (borg-rs#60), and a profile that turns one on is refused at start-up. The munchkin-class smoke arm stopped at turn 1 in 18 of 18 games. Runs of v15R use `normal` only.
- **Smoke, classes-18 `normal`** (run 44649268974): final turn, level, depth and cause are identical to bbc v15 in **18 of 18** games.
- **Medium, classes-1800-medium `normal`** (run 44652186610, 270 games): the endpoints are identical to classes-v15 in **264 of 270**. Deaths: Rust 69, C 70. **All 6 differing games are Necromancers** (6 of 30). The port reproduces C for the other eight classes on these starts. The release's 45-scenario check didn't catch the Necromancer difference.
- The play hashes differ in every game, while the endpoints match. The two harnesses record keys differently, so endpoint comparison is the test here.
- **Big, classes-1800-big `normal`** (run 44677153452, 540 games): identical endpoints in **532 of 540**; deaths Rust 144, C 141. All 8 differences are Necromancers. Medium + big: 796 of 810 identical; Necromancers differ in 14 of 90, the other eight classes in 0 of 720. Tracked in borg-rs#111.

## Neo Borg: Mandos lanes

**The port repairs never change play.**
[`mandos-api2-classes-1800`](../experiments/mandos-api2-classes-1800.json), run 42518586195, prespecified, `neo-b3-api2-port.2` against `neo-b3-api2-upstream`:
- **1,775 of 1,775 finished pairs played identically;** both arms had 82.4% deaths.
- **Even the unfinished runs match:** 23 stalls, one harness failure ("Core requested an item-choice UI not available in this headless profile") and one wall timeout, on the same seeds in both lanes.
- **The primary test is degenerate:** there were no seeds where the arms ended differently. So the repairs change play in under about 0.2% of these games.
- **Inference, not checked in the code:** the Neo Borg dies before it reaches the repaired code. Measuring the repairs needs a Neo Borg that survives the first dungeon levels.

**The Neo Borg dies far more often than the C Borg** (descriptive; a Neo seed is a different game from a C seed). Comparing the Neo upstream lane with `4.2.6` in `classes-m6`:

| | C 4.2.6 | Neo upstream |
|---|---|---|
| Deaths | 34.4% | 82.4% |
| Deaths before turn 10,000 | 12% | 48% |
| Median turn it first reaches dungeon level 1 | 861 | 20 |
| Killed by monsters that never move | 2.3% | 18.1% |
| Killed by a floating eye | 1 game | 87 games |
| Killed by Farmer Maggot's dogs | 6.3% | 17.0% |

- **No purchase command** appears among the Neo Borg's 3 million commands.
- **The owner's own analysis** of the original-source benchmark, `originals-20261108-classes-1800`, studies these patterns with full evidence. It's in PR #28 (issue #25): the Druid book-throw loss, the supply gap and early hazards. It is the authority on causes; this table only shows the pattern.

## Rust Borg: borg-reborn-rs (#128, #183)

**The reborn Rust Borg does not leave dungeon level 1 on `classes-1800`, and the #183 guard roughly doubles its deaths.** Arms A (`3113c2e2`, guard off, run 43501324055) and B (`5f626d17`, guard on, run 43501327741), both through `harness/build.sh` with the defaults profile; control `angband-e473-original` (run 43024245702). Full tables, intervals and the margin question: [reports/reborn-g1-classes-1800/REPORT.md](../reports/reborn-g1-classes-1800/REPORT.md).
- **Primary endpoint (reach DL5 by 100,000 turns):** 0/1,800 for A and for B, 6.9% (124/1,800) for the control. B - control = -6.9 points (95% -8.1 to -5.7): not non-inferior at 5 points, non-inferior overall at 10 (the margin stored with the run); Warrior, Rogue and Ranger fail both.
- **#183:** B dies in 503 of 1,800 games against 245 for A (McNemar p < 0.0001), mostly Mage, Necromancer, Druid, Ranger and Priest, at level 2 on DL1 (median turn 10,807). The caveat is that both arms play almost entirely on DL1; the guard's effect on a Borg that dives was not measured.

**#181, borg-reborn-rs main fdaf18e5 with its shipped defaults (pilot, run 44071581589, 18 games): 3 deaths, no unknown-item use.** Specimen `4.2.6-reborn-rust-main-fdaf18e5` (main at #480's merge, with #473; binary 3d0d6d93, source hash 258ccc77), one arm `reborn-shipped-defaults` with no settings: the shipped borg.txt sets the speed30 bundle, no plan. Gate passed: no config_error, one binary, the 18 `borg_param_*` lines and the trip settings in the written borg.txt with no `borg_plan`, no stalls, every cell death or turn_cap. The four sanity starts of the request match their local play hashes. Replayed (18/18 hashes match): no `unknown` quaff/read/eat notes and no Deep Descent read. There are 31 trip returns and 210 `no up stairs found, going down` notes (82 in Rogue 1502695781).
- **Outcomes:** 3/18 deaths (Blackguard 888896726 to a crow on DL2, Druid 102023799 to a rock lizard, Necromancer 300036923 to a wild cat), mean deepest DL 2.06, mean max level 4.61. The control of run 44054277431 on 193d9076 had 3/18, 2.22 and 4.94, but those are different games from the first turns, so this compares outcomes only.
- **Death report:** [reports/reborn-main-defaults-pilot-deaths/README.md](../reports/reborn-main-defaults-pilot-deaths/README.md). The cornered Borgs fought in melee with oil, a sling or spell points unused.

**#181, main fdaf18e5 shipped defaults (medium tier, run 44072424588, 270 games, starts 91-360; small skipped by the owner): fewer deaths than the 193d9076 control, and no game goes below DL4.** Gate passed: no config_error, one binary (3d0d6d93), the shipped settings and no `borg_plan` in all 99 distinct borg.txt files. One cell is `stalled`: Ranger 745617169, a frozen-turn loop of 1,084 keys at game turn 60,106 (as borg-reborn-rs#421); its observed outcome is turn_cap at max DL3. 22 games exceed twice the median of 10,195 keys.

| Build (same starts and settings) | Deaths | Mean deepest DL | Reached DL5 | Deepest | Mean max level |
|---|---|---|---|---|---|
| main fdaf18e5 (#473, #480) | 22/270 (8.1%) | 2.05 | 0 | 4 | 4.83 |
| 193d9076, control of run 44065025814 | 34/270 (12.6%) | 2.37 | 14 | 22 | 4.92 |

- **Paired on the same start** (different games; only 1 identical): 30 starts died on 193d9076 and live on main, and 18 the reverse, McNemar p = 0.11. Fewer deaths on main for Blackguards (2 against 5), Priests (3 against 6) and Rogues (2 against 5); Mages 6 against 5.
- **Causes:** main's commonest is poison (4); 193d9076's were a soldier (5), a crow (4), lava (3) and a giant white mouse (3).
- **Depth:** the 14 dives to DL5-22 on 193d9076 are gone on main. That fits #473 discarding Deep Descent and never reading unknown scrolls, but it was not checked: the 193d9076 medium run kept no logs.
- **The 22 deaths** (all 270 games replayed, hashes match CI): [reports/reborn-main-defaults-medium-deaths/README.md](../reports/reborn-main-defaults-medium-deaths/README.md). 19 had run out of Cure Light Wounds. 9 ended in melee at low HP. 10 carried 9-23 Flasks of oil. 5 were killed by Farmer Maggot's dogs at character level 1-2, and 4 by poison. Two Mages fainted casting Phase Door with 0 SP and died paralysed. A poisoned level-1 Rogue died in town walking to the Alchemist, and a Paladin at full HP stepped into town lava (`Twitchy!`).

**#170, speed30 with each plan (pilot, run 44045223515, 54 games): the plans did not differ at 18 starts.** Every setting of `reborn-bundle-plan-speed30` on `4.2.6-reborn-rust-speed-fight` (binary cdfee89a), with no plan, errands_plan.txt and errands_plan_ambitious.txt. Gate passed: no config_error, one binary, every setting written to borg.txt in all arms, plan pins matched (and no plan in the no-plan arm), no stalls or frozen-turn bursts, every cell death or turn_cap.
- **Deaths:** 3/18 in each arm. With the errands plan, Ranger 1739161339 survives and Warrior 1085222502 dies instead (on DL18 at level 8, to Nár). Blackguard 888896726 and Druid 934061548 die in all three arms. The ambitious plan dies on the same three starts as no plan, and 16 of its 18 games play identically to no plan.
- **Depth:** mean deepest level 2.22 with no plan, 3.22 with the errands plan (the Warrior's DL18 dive alone accounts for most of the gap) and 2.17 with the ambitious plan.
- **Repeat:** the errands-plan arm replays the #170 pilot's speed30 arm (run 43994684018) identically in 18/18 games.

**#170, speed30 with each plan (small tier, run 44050742897, 270 games, starts 1-90): still no detectable difference between the plans.** Same three arms as the pilot. Gate passed: no config_error, one binary (cdfee89a), every setting written in all 270 borg.txt files, plan pins matched (none in the no-plan arm), no stalls or frozen-turn bursts, every cell death or turn_cap. Key outliers (over 20,000 keys, about twice the median of 9,914) are 14 Ranger games that reach the turn cap, the same four starts in every arm.

| Plan | Deaths | Mean deepest DL | Reached DL5 | Mean max level |
|---|---|---|---|---|
| None (control) | 6/90 | 2.24 | 4 | 5.06 |
| errands_plan.txt | 4/90 | 2.26 | 5 | 5.10 |
| errands_plan_ambitious.txt | 7/90 | 2.28 | 5 | 5.01 |

- **Paired against no plan:** the errands plan rescued 3 (Blackguard 446353753, Ranger 129607500, Warrior 740860644) and newly killed 1 (Druid 507571350), McNemar p = 0.63, with 45/90 games identical. The ambitious plan rescued none and newly killed the same Druid, p = 1.0, with 70/90 identical.
- Without speed30, the #164 small tier had 5/90 deaths with no plan and 4/90 with the errands plan. That is a different specimen and run, so it is not a paired comparison.

**#170, borg_trip_unknown_stacks 2-5 on the speed30 bundle with no plan (pilot, run 44054277431, 72 games): no difference in deaths.** `reborn-bundle-none-speed30` on `4.2.6-reborn-rust-speed-fight` with unknown_stacks 2, 3, 4 and 5 (5 = control). Gate passed: no config_error, one binary (cdfee89a), every setting and the arm's `borg_trip_unknown_stacks = N` written in every borg.txt, no plan loaded, no stalls or frozen-turn bursts, every cell death or turn_cap.

| unknown_stacks | Deaths | Mean deepest DL | Mean max level | Identical to 5 |
|---|---|---|---|---|
| 2 | 3/18 | 2.89 | 4.61 | 7/18 |
| 3 | 3/18 | 2.50 | 5.28 | 12/18 |
| 4 | 3/18 | 2.17 | 5.11 | 14/18 |
| 5 (control) | 3/18 | 2.22 | 4.94 | - |

- Only 2 changes who dies: Ranger 1739161339 survives and Rogue 1502695781 dies (DL2, level 3). Blackguard 888896726 and Druid 934061548 die in every arm.
- The control replays the speed30 x plan pilot's no-plan arm (run 44045223515) identically in 18/18 games.
- **Deaths in the pilot** (local replay, 54/54 play hashes match CI): [reports/reborn-unknown-stacks-pilot-deaths/README.md](../reports/reborn-unknown-stacks-pilot-deaths/README.md). Where 2 or 3 split from 5, the split is a trip `return` for unknown items. With no up stair known, the Borg goes down instead (`no up stairs found, going down`). The unknown3 Ranger did this 16 times without reaching town.

**#170, borg_trip_unknown_stacks 2-5 (small tier, run 44055270651, 360 games, starts 1-90): no value is distinguishable from 5.** Gate passed: no config_error, one binary (cdfee89a), every setting written (`borg_trip_unknown_stacks = N`) in all 360 borg.txt files, no plan loaded. One cell is flagged `stalled`: Ranger Half-Orc 1071405808 with unknown3, a frozen-turn loop of 1,085 keys at game turn 75,918 (as in borg-rs#90 / borg-reborn-rs#421). Its observed outcome is turn_cap at DL6, level 8. 17 games exceed twice the median of 9,956 keys.

| unknown_stacks | Deaths | Mean deepest DL | Reached DL5 | Mean max level | Identical to 5 |
|---|---|---|---|---|---|
| 2 | 8/90 | 2.54 | 5 | 5.26 | 25/90 |
| 3 | 6/90 (+1 stalled) | 2.46 | 7 | 5.08 | 48/90 |
| 4 | 3/90 | 2.13 | 2 | 5.04 | 68/90 |
| 5 (control) | 6/90 | 2.24 | 4 | 5.06 | - |

- **Paired against 5:** 2 rescued 4 and newly killed 6 (3 of them Druids), McNemar p = 0.75; 3 rescued 3 and killed 3, p = 1.0; 4 rescued 3 and killed none, p = 0.25. The 3 rescued by 4 (Blackguard 446353753, Ranger 129607500, Warrior 740860644) are also rescued by 2 and 3.
- Lower values go somewhat deeper (more DL5 games with 2 and 3) and play differently more often. 4 has the fewest deaths, but 3 against 0 is far from significant.
- The control replays the speed30 x plan small tier's no-plan arm (run 44050742897) identically in 90/90 games.

**#170, borg_trip_unknown_stacks 3-5 (medium tier, run 44065025814, 810 games, starts 91-360; value 2 dropped by the owner): no value differs from 5 on 360 starts.** Gate passed: no config_error, one binary (cdfee89a), every setting written in all 810 borg.txt files, no plan loaded, no stalls or frozen-turn bursts. 71 games exceed twice the median of 9,441 keys (max 26,827), all at the turn cap.

| unknown_stacks | Medium deaths | Small + medium deaths (360) | Mean deepest DL (360) | Reached DL5 (360) | Mean max level (360) | Identical to 5 (360) |
|---|---|---|---|---|---|---|
| 3 | 32/270 | 38 (+1 stalled) | 2.48 | 23 | 4.96 | 197 |
| 4 | 36/270 | 39 | 2.39 | 19 | 4.99 | 276 |
| 5 (control) | 34/270 | 40 | 2.34 | 18 | 4.96 | - |

- **Paired against 5 on 360 starts:** 3 rescued 12 and newly killed 10 (McNemar p = 0.83); 4 rescued 4 and killed 3 (p = 1.0). The small tier's lead for 4 (3 against 6 deaths) did not hold in medium (36 against 34).
- **Per class:** deaths are within one or two of each other in every class, except Warriors with 3 (8 against 4).
- Lower values go slightly deeper (DL5 in 23, 19 and 18 games) without fewer deaths. The records hold no message logs, so trip returns that became descents are not counted here; that needs a replay (`python3 -m zoo.death_report`).

**The heal + trip policy + attack preference bundle, with and without `errands_plan.txt` (#164).** borg-reborn-rs `f02cd294`, specimen `4.2.6-reborn-rust-heal`. Pilot (`classes-18`, run 43973026635, 72 cells) and small tier (`classes-1800-small`, 90 starts per arm, run 43977574813, 180 cells). Both passed their gates: no `config_error`, one binary, settings written, plan pins matching, no stalls.
- **Pilot, 4 arms of 18 starts:** deaths 4 (control, no plan), 3 (control, plan), 4 (bundle, no plan), 2 (bundle, plan). The two deaths of the last arm are in all four arms with the same keys. Saved in borg-cemetery#52.
- **Small, bundle without and with the plan:** deaths 5/90 and 4/90 (95% ranges 2-12% and 2-11%), median max level 5 in both. Paired on the same start, the plan rescued 3 starts, newly killed 2 and both died in 2; play was identical in 46 of 90 starts. The mean deepest level was 2.42 without the plan and 2.21 with it.
- **Reading:** the plan makes no detectable difference to the bundle at this size. This run has no neutral control arm, so it does not measure the bundle against the unchanged build (RULES 8); the only such comparison is the pilot's 18 starts (4 deaths each).

**#183, Suite 1 on borg-reborn-rs main 7e08c920 with its own defaults (full, 999 saved encounters; runs 44107809205, 44108466606, 44108889978, 44109534305, 44110967531): 281 deaths, and one scenario cut off by the 5 s wall limit.** A sanity check of main: the commit's own `harness/borg.txt` (04dd52f7...), nothing overridden, reported alone. Every stage up to big passed its gate. The full stage collected all 999 cells, with no stopped cell.
- **Outcomes:** 281 deaths (28.1%), 717 survived the 2,000-turn horizon, 1 not finished.
- **Deaths per class (of 111):** Warrior 23, Mage 25, Druid 46, Priest 26, Necromancer 35, Paladin 33, Rogue 33, Ranger 35, Blackguard 25.
- **The unfinished scenario:** Rogue c6-r7-s1060140-i000 hit the 5 s wall at game turn 96,481 of 97,007. The game was fighting a breeding swarm of giant white lice (8,172 `Tracking a monster` notes). Replayed locally, it times out at 5 s every time; with a 60 s wall it reaches the horizon alive in 6.9 s. On the same save, speed30 (193d9076) needed 3.6 s and the reborn baseline 1.3 s. No other scenario took more than 1.7 s on 7e08c920. The archived record labels the cell `invalid_receipt`; the runner now labels such a cell `wall_timeout`.

**#224, cornered mode 2×2×2 on main 6101ca01 (pilot, run 44196757011, 144 games): only the on/off switch matters; radius and big-level margin change nothing.** The gate passed: one binary (259eb8a5), no config_error, all three settings written, nothing flagged. The four cornered-off arms play identically (18/18 each), and so do the four cornered-on arms: radius 2 or 3 and margin 0 or 1 changed no game. Cornered on against off: 3 deaths against 4. It changes 4 of 18 games and saves a CL2 Warrior killed by Sméagol. Mean max level is 4.94 against 4.61. The remaining deaths (two Druids, one by poison at CL6; a Ranger by poison at CL7) are the same in both arms.

**#224, cornered mode off vs on, all 1,800 starts of main 6101ca01 (run 44198028729, 3,600 games): a small effect, not significant.** The gate passed: one binary (259eb8a5), no config_error, the settings written in all 198 borg.txt files, nothing flagged. Deaths are 151 (8.4%, 7.2-9.8) off and 142 (7.9%, 6.7-9.2) on. On the same start, on rescues 21 and newly kills 12 (McNemar p = 0.16); 1,418 of 1,800 games are identical. Mean max level 4.91 / 4.93, DL5 reached 22 / 26, CL1-3 deaths 96 / 96. Melee classes gain most: Rogues 11 → 5, Warriors 5 → 1. Casters are unchanged or slightly worse (Priests 19 → 21, Blackguards 11 → 14). Both arms have the named list on; their deaths are close to the #227 named arm (148).

**#225, borg-reborn-rs#487 healing by class and the digger gate (pilot, run 44173139346, 90 games on main a8ac685a).** The gate passed: one binary (012a06ed), no config_error, every line written, nothing flagged, and the four sanity hashes reproduced. Deaths: ctl 4, digger 4, heal 3, both (shipped) 2, speedres 2, of 18. The shipped healing cuts healing gold from 166-227 to 113-133 per game and moves it to ammunition and armour. The digger gate cuts Shovels from 12-17 to 5 per arm. No arm with the shipped healing bought a weapon. Unknown kinds are the largest spend everywhere (260-325 gold per game). Report: [reports/reborn-heal-class-pilot-deaths/README.md](../reports/reborn-heal-class-pilot-deaths/README.md).

**#227, scary rule on main a8ac685a: none vs C's named list vs damage 60% (pilot, run 44178676657, 54 games).** The gate passed: one binary (012a06ed), no config_error, both settings written, nothing flagged, and all 54 replays match CI. Deaths: no rule 4 (all at CL1-3); named list 3 (none at CL1-3, all at CL4-7); damage60 2 (both at CL2: a Necromancer to a small kobold and a Priest to Fang). The damage rule fires rarely (10 `Scary guy` notes in 18 games against 11,804 for the list) and plays like no rule in 15 of 18 games. The list costs about 0.6-0.9 character levels and triples the level bouncing. Report: [reports/reborn-scary-rule-pilot-deaths/README.md](../reports/reborn-scary-rule-pilot-deaths/README.md).

**#227, the scary rule on all 1,800 starts of main a8ac685a (run 44183532358, 7,200 games): C's named list halves deaths. The damage rule at 60% does almost nothing; at 40% it helps a little.** The gate passed: one binary (012a06ed), no config_error, both settings written in all 396 distinct borg.txt files, no stalls, loops or purchase bursts, and every cell ended in death or turn cap.

| arm | deaths | 95% interval | deaths at CL1-3 | mean max CL | mean max DL | reached DL5 | vs no rule: rescued / newly killed (McNemar p) | same play as no rule |
|---|---|---|---|---|---|---|---|---|
| no rule | 297 (16.5%) | 14.9-18.3 | 194 | 5.83 | 2.43 | 75 | - | - |
| named list | 148 (8.2%) | 7.0-9.6 | 102 | 4.92 | 2.13 | 26 | 255 / 106 (< 0.0001) | 2 |
| damage 40% | 256 (14.2%) | 12.7-15.9 | 167 | 5.85 | 2.44 | 78 | 162 / 121 (0.017) | 665 |
| damage 60% (shipped) | 286 (15.9%) | 14.3-17.7 | 187 | 5.85 | 2.44 | 74 | 46 / 35 (0.27) | 1,504 |

- **The named list lowers deaths in every class.** Against damage 60% it rescues 244 and newly kills 106 (p < 0.0001).
  - Warriors 15 → 1, Rogues 14 → 5, Mages 48 → 23, Druids 51 → 26, Priests 46 → 22, Necromancers 39 → 21.
  - It costs about 0.9 character levels, 0.3 dungeon levels, and two thirds of the DL5 games (75 → 26).
- **The damage rule plays like no rule.** At 60% it does in 1,504 of 1,800 games. At 40% it changes 1,135 games and lowers deaths by 2.3 points (p = 0.017). Against 60%, 40% rescues 149 and newly kills 119 (p = 0.08). Necromancers don't benefit from either threshold (39 / 37 / 43 deaths).
- One development suite, so this is descriptive. The data-file list (#228, borg-reborn-rs#527) is the planned successor to the compiled list.

**#216, borg-reborn-rs#503's two flags, 2×2 on main 233ef23e (pilot, run 44147930313, 72 games): turning off C's named scary list is what changes play.** The gate passed: no config_error, one binary (3f122aed), both flags written in every arm, no stalls or purchase bursts, and the request's four sanity hashes reproduced. Deaths: ctl (breeder_fight 0, scary_named 1) 1/18; fight (1,1) 1; nolist (0,0) 5; both (1,0, the shipped default) 4. With the list off, the `Scary guy on level.` notes vanish, down-then-up bounces fall from about 1,450 to 450, and mean max level rises from 5.0 to 5.7-5.8. Four starts die in both list-off arms, two of them at character level 1 against monsters on the old list. The breeder stand alone changes 10 of 18 games but no outcome. Report: [reports/reborn-breeder-scary-pilot-deaths/README.md](../reports/reborn-breeder-scary-pilot-deaths/README.md).

**#216 small tier (run 44157865502, 360 games, starts 1-90): the pilot's pattern holds.** The gate passed: one binary, no config_error, both flags written, nothing flagged, and all 360 replays match CI. Deaths: ctl 9, fight 9, nolist 14, both (shipped) 11, of 90 each. Against ctl: nolist rescues 7 and newly kills 12 (p = 0.36); both rescues 7 and newly kills 9 (p = 0.80). With the named list off, mean max level rises from 4.8 to 5.6-5.7, down-then-up bounces fall to a third, and the `Scary guy` notes vanish. Necromancers die 0 times in ctl and 4 times with the list off, all at CL1 (Grip three times, a battle-scarred veteran once), and Priests die 1 time against 3. The breeder stand alone changes 38 games but no outcome. Report: [reports/reborn-breeder-scary-small-deaths/README.md](../reports/reborn-breeder-scary-small-deaths/README.md).

**#216, named list off with and without `errands_plan.txt` (pilot, run 44163377539, 36 games on main 233ef23e): the plan changes 8 of 18 games but no outcome.** The gate passed: one binary, no config_error, both flags written, the plan loaded (pin matches) in the plan arm only, nothing flagged. The control replays the #503 pilot's `both` arm exactly (18/18). Deaths are 4 in each arm, on the same four starts: Druid 934061548, Rogue 1381972077, and the CL1 Priest 1569794094 and Necromancer 1574344917. With the plan the Druid dies earlier, to Fang at CL4 instead of a kobold shaman at CL6. Mean max level is 5.78 without the plan and 5.83 with it. The plan does not protect the level-1 casters that the named list protected.

**#216, named list × errands plan, 2×2 with the breeder stand on (pilot, run 44165070793, 72 games on main 233ef23e): the list decides deaths, the plan does not.** The gate passed: one binary, no config_error, flags written, the plan loaded (pin matches) in the plan arms only, nothing flagged. `both`, `both-plan` and `fight` replay their earlier pilots exactly (18/18 each). Deaths: list off 4 (no plan) and 4 (plan), two of them at CL1; list on 1 and 1, none at CL3 or below (the same Mage, at CL4, to a giant white mouse). Turning the list on rescues 4 and newly kills 1, with and without the plan. The plan changes 8 of 18 games and no outcome, with the list either on or off. Mean max level is 5.8 with the list off and 5.0 with it on.

**#255, Word of Recall in flight: ctl (flight Recall) vs gate (shipped) vs reserve vs hold on main 0fa5c34d (pilot 44243556206, small 44244730818, medium 44246229174, big 44248148439, full 44250411032; all 1,800 starts, 7,200 games): the gate neither saves nor clearly costs lives.** Every tier's gate passed: one binary, no config_error, settings written, no frozen-turn loops, every death bundle reproduced (6, 112, 179, 247). Deaths over 1,800 starts: ctl 127 (7.1%), gate 141 (7.8%), reserve 140 (7.8%), hold 136 (7.6%). Gate vs ctl: ctl alone dies 84, gate alone 98 (p = 0.34); the gate changes 1,580 of 1,800 games and goes slightly deeper (mean max DL 2.20 vs 2.12, CL 5.04 vs 5.02). Reserve vs gate: 1,480 games identical, outcomes differ in 3 starts. Hold vs gate: gate alone dies 10, hold alone 5 (p = 0.30). Discordant deaths split evenly by class. The pilot (18 starts, 0 vs 2 deaths) was direction only, and the larger tiers did not confirm a cost.

**#191, caution_rising_explore_ticks 0/150/300/450 on main d9ff9808 (pilot, run 44230664898, 72 games): no deaths in any arm.** The gate passed: one binary (44b1d2f3), no config_error, the setting written in every arm, the shipped scary list loaded and recorded in all 72 cells, nothing flagged. All 72 replays match CI. Every game reached the turn cap. Mean max level is 5.28-5.39 and mean max DL 2.11-2.17 in every arm. 14 of 18 games play identically to the off arm.

| ticks | `exploring for them (rising)` notes | `no up stairs found, going down` | down-then-up bounces | town visits |
|---|---|---|---|---|
| 0 (off) | 0 | 84 | 1,408 | 1,268 |
| 150 | 59 | 70 | 1,368 | 1,235 |
| 300 (default) | 111 | 63 | 1,387 | 1,259 |
| 450 | 122 | 72 | 1,364 | 1,235 |

The hold fires more as the budget grows, and the going-down notes fall from 84 to 63-72. The level bouncing and town visits hardly change. A first run of this pilot (44230015413) failed at the build, before any game, because the specimen did not yet pin the shipped scary list.

**#170, borg_trip_unknown_stacks 2/3/4/5 on main d9ff9808 (pilot, run 44236318055, 72 games): no deaths in any arm; lower values make the Borg pendulum.** The gate passed: one binary (44b1d2f3), no config_error, the value written in every arm, nothing flagged. s5 replays the rising-ticks pilot's t300 arm exactly (18/18). All 72 replays match CI. Every game reached the turn cap. Mean max level is 5.17-5.28 and mean max DL 2.11-2.22 in every arm. Games identical to s5: 5 (s2), 10 (s3) and 13 (s4) of 18.

| unknown_stacks | unknown-item trip returns | `no up stairs found, going down` | rising holds (`exploring for them`) | town visits |
|---|---|---|---|---|
| 2 | 109 | 198 | 2,380 | 1,375 |
| 3 | 48 | 107 | 460 | 1,294 |
| 4 | 50 | 100 | 403 | 1,234 |
| 5 (shipped) | 18 | 63 | 111 | 1,259 |

Lower values send the Borg back for unknown items more often. Each return brings more `going down` notes and far more rising holds, the pattern the 193d9076 death report found, now partly held by the rising hold. With no deaths, the pilot cannot rank the values on survival.

**#170, borg_trip_unknown_stacks 2/3/4/5 on main d9ff9808 (medium tier, run 44238139015, 1,080 games, starts 91-360): no value differs from 5.** The gate passed: one binary (44b1d2f3), no config_error, values written, no stalls, loops or purchase bursts. Deaths: s2 24 (8.9%), s3 26 (9.6%), s4 26 (9.6%), s5 25 (9.3%) of 270, with 18-19 of them at CL1-3 in every arm. Against s5: s2 rescues 7 and newly kills 6, s3 1 and 2, s4 0 and 1 (p = 1.0 for each). Games identical to s5: 44, 108 and 176 of 270. Mean max level is 4.85-4.99 and mean max DL 2.02-2.11. The top killers over all arms are wild cats (27), soldiers (17), crows (9), grey mushroom patches (7), small kobolds (5) and Grip (5). The zero-death pilots of main d9ff9808 were 18 easy starts: on 270 per arm main dies in about 9% of games, close to 6101ca01's 7.9-8.4%.

**#170, borg_trip_unknown_stacks 2/3/4/5 on main d9ff9808 (all 1,800 starts, run 44241978132, 7,200 games): the value does not change deaths.** The gate passed: one binary (44b1d2f3), no config_error, values written, no frozen-turn loops, 506 of 506 death bundles reproduced. Its starts 91-360 replay the medium run exactly (1,080 of 1,080 key logs). Deaths: s2 125 (6.9%), s3 128 (7.1%), s4 126 (7.0%), s5 127 (7.1%) of 1,800. Every pair differs in at most 83 starts, split evenly (s2 vs s5: 40 and 42; all p >= 0.8). Higher values go slightly further: mean max level 4.91, 4.95, 4.98, 5.02 and mean max DL 2.05, 2.09, 2.09, 2.12. The shipped 5 stays.

**#224, cornered danger threshold (5, 10) × radius (2, 4) on main d9ff9808 (pilot, run 44237508546, 72 games): no deaths in any arm.** The gate passed: one binary (44b1d2f3), no config_error, settings written, nothing flagged. d10-r2 (the shipped values) replays the shipped arm of the unknown_stacks pilot exactly (18/18). Games identical to d10-r2: 16 (d10-r4), 13 (d5-r2) and 13 (d5-r4) of 18. Mean max level is 5.28 at threshold 10 and 5.11 at 5. Triggering earlier changes more games than a wider radius; neither can be ranked on deaths at this size.

**#224, cornered danger threshold (5, 10) × radius (2, 4) on main d9ff9808 (medium tier, run 44241753524, 1,080 games, starts 91-360): no setting differs from the shipped one.** The gate passed: one binary, no config_error, settings written, no frozen-turn loops, 100 of 100 death bundles reproduced. Deaths: d10-r2 (shipped) 25 (9.3%), d10-r4 26 (9.6%), d5-r2 25 (9.3%), d5-r4 24 (8.9%) of 270. Against d10-r2 the others differ in at most 7 starts (0/1, 3/3, 3/2; p >= 0.6). Mean max level is 4.93-4.99 and mean max DL 2.10-2.11. The shipped threshold 10 and radius 2 stay.

**Four switches with no measurable effect at their largest tier (2026-11-18): every tested value is neutral (RULES 18).** Their issues were closed on the owner's word (tidy-up, 2026-11-18). No tested value has a measurable cost, so each is safe to adopt if preferred:
- **#235, the #539 flight switches at full (run 44216738125, 7,200 games on 9ecbfd1e):** control 142/1,800 deaths; phase+ranged 133/1,799 (rescued 68, newly killed 60, p 0.54), stairs+ranged 133/1,799 (74/66, p 0.55), all three 147/1,799 (83/89, p 0.70). One unfinished cell per switch arm. No combination differs from the control.
- **#240, the #544 breeder exit at distance 4/6/10 (small + medium, runs 44220465377 and 44220469487, starts 1-360 on 156c8e52):** control 28/360; d4 27, d6 29, d10 28, with 4-6 rescued and 4-6 newly killed per arm (p 1) and 265-277 of 360 games identical to the control. The exit rarely changes a game.
- **#246, the #549 stair-scum threat flag (small + medium + big, runs 44238199598, 44238075961 and 44245072671, starts 1-900 on d9ff9808):** 68/900 against 67/900 with the flag, 4 rescued and 3 newly killed (p 1), 763 of 900 games identical. Main ships the flag on (fba1c6e0); the evidence does not distinguish on from off.
- **#248 / #170, borg_trip_unknown_stacks:** see the entries above. 2-5 do not differ in deaths over 1,800 starts. Main ships 2 (fba1c6e0); borg-reborn-rs's notes trace one Blackguard death to that value, a single game.

**#279, the borg_worships_* equipment switches on main 92fafc61 (pilot, run 44308259323, 108 games): damage, speed, hp and mana never change a game; ac changes every game.** The gate passed: no config_error, each switch written TRUE in its arm's borg.txt, every game at the turn cap (no deaths in any arm). Damage, speed, hp and mana worship play the control's keys in 18 of 18 games, as the C Borg's switches-early found for speed, hp and damage. Their bonuses never change an equipment choice at this cap: the four are **neutral** (inert at 100,000 turns, safe to adopt, nothing more to measure at this length). AC worship changes all 18 games, with no deaths and a lower mean max level (5.17 against 5.44). borg_worships_gold was left out (owner): with borg_town_plan = 1 the live planner replaces the C seller, so the unidentified-item selling it allows never runs.

**#274, attack preferences by class on main 4a482c58 (pilot, run 44308236915, 72 games): the class preferences change play in most classes, not deaths.** The gate passed: no config_error, the 16 class lines written in every non-control arm, every game ended in death or at the turn cap. Deaths: 1/18 in ctl, flat and strong (the same Blackguard 1472012981 to a cave spider in all four arms), 2/18 in half (that Blackguard and Ranger 226104090 to an apprentice at CL7 on DL3). Games identical to the shipped preferences: flat 8, half 11, strong 15 of 18. By class, Priests and Blackguards played the control's keys in every arm, and Necromancers differed in every arm with the same outcome. Two starts per class show only where the preferences act; ranking a class's values needs the next tiers.

**#256, borg-reborn-rs#515 scary latch (caution_scary_latch 1 shipped vs 0) on main 162f96af (pilot 44277668188, small 44279232439, medium 44282955475, big 44312919382, full 44315227824; 1,818 paired starts): unlatching does not change survival.** Every tier's gate passed (medium needed one shard rerun after the runner hung in apt-get before any game). Deaths: latched 128 (7.0%), unlatched 138 (7.6%); rescued 43 / newly killed 53 (p = 0.36). Unlatching changes 82% of games and goes slightly further (mean CL 5.35 vs 5.22, max DL 2.25 vs 2.17). In the medium tier's messages (473 of 540 games; one shard's raw evidence hit GitHub's egress limit) the flag cleared in 207 of 270 unlatched games, and 4 unlatched deaths came within 2,000 game turns of a clear, all survived by the latched arm; 3 of those scares ended when the scary monster was only forgotten (a Priest died of poison 9 turns after forgetting a white worm mass). The shipped latch stays; clearing only on a known kill is borg-reborn-rs's call.

**#267, borg-reborn-rs#557/#565 flight-Recall depth gate (caution_flee_recall_gate_below_depth) on main 68cf9eb5.** First pilot (run 44293222019, 0/1/2): 1 is the no-op the code says, identical keys to 0 in all 18 cells. Then 1 (C, control), 2 (shipped) and 3 up to the big tier (pilot 44295931569, small 44297937576, medium 44299647679, big 44301742234; 918 paired starts): **neither gate is shown to save or cost lives.** Deaths 56 (6.1%), 66 (7.2%; 32 rescued / 42 newly killed, p = 0.30), 65 (7.1%; 32 / 41, p = 0.35). The medium tier alone had 2 against 1 at 5 / 15 (p = 0.041); big did not repeat it (22 / 24). In the small tier's messages, 2 moves flight Recalls off DL1 (77 to 13, the rest the breeder/chaser exception) and 3 cuts them to a quarter, at the price of far more stand-and-fight notes on DL1-2 (796 against 259). The lean against the gate matches #255.

**#275, outmatched healing (caution_heal_when_outmatched, caution_heal_outmatched_min_loss) on main 92fafc61 (pilot 44299561765, medium 44302992227): the rule helps, and the shipped threshold 50 is the best tested.** Medium, 270 starts per arm: off 25 deaths (9.3%; 0 rescued / 9 newly killed against 50, p = 0.004, 0.02 after correcting for five arms); 30: 20, 40: 19, **50: 16 (5.9%)**, 60: 18, 70: 20, each only adding deaths against 50 (none significant alone). The rule fires rarely (2-4 of 18 pilot games per arm), so arms differ in 13-46 of 270 games. No class prefers another threshold, so per-class values (`@<class>`) have nothing to aim at.

**#285, fear-cure stock (town_fear_cure_count 2 shipped vs 0) on main bb4e5d1c (pilot 44309646816, medium 44328278095): the shipped cap leans better.** Pilot: no deaths; Boldness bought 5 at 2 against 29 at 0. Medium: 17 deaths (6.3%) at 2 against 24 (8.9%) at 0; 7 rescued / 14 newly killed by 0 (p = 0.19), mostly early DL1 deaths, Necromancers 1 against 6. Not significant; a big tier would firm it up.

**#277, borg-reborn-rs#558 breeder hunt (count 2/4/6, no-rest gate 0/50) on main bb4e5d1c (pilot 44313296425): no difference on 18 starts.** No deaths; 17 of 18 games identical in every arm (only the Mage 801785300 changes, as the request's sanity cells predicted).

**#267 complete, flight-Recall depth gate 1/2/3 on main 68cf9eb5, all 1,800 starts (adds full 44361568858 to the tiers above; 1,818 paired starts): neither gate saves lives.** Deaths: 1 (C) 109 (6.0%), 2 (shipped) 122 (6.7%; 66 rescued / 79 newly killed, p = 0.32), 3 125 (6.9%; 68 / 84, p = 0.22). Like #255's flight gate, keeping the flight Recall off the shallow levels never helped survival; it only changes the Recall economy.

**#277 medium, breeder hunt (run 44346827787, 1,080 games): no difference.** Deaths 16, 17, 16, 17 of 270 for count 4 / gate 0 (control), 4 / 50, 2 / 50, 6 / 50; one Priest is the only death that moves. Closed.

**#286, #548 down-staircase flight on PR #566 head b054287b (pilot 44345853505), and #307 cornered 0/1 on main 8e7dbad4 (pilot 44354583363, medium 44367258196): no survival effect.** #286 pilot: no deaths; the narrowed flight changes 1 of 18 games, keeping stairs through the jumpstart 6. #307 medium: flight off 17/270, cornered 1 17 (changes 18 games), cornered 0 19 (changes 193 games, 2 rescued / 4 newly killed, p = 0.69).

**#303, town planner weights on main 8e7dbad4 (pilot 44349934443, medium 44352270059, big 44367212173, full 44376882104): the shipped weights stay.** In the live planner, borg_town_w_knowledge is forced to 0 and light_depth / food_trip are read only by the old v4 model; they were dropped. Pilot: w_poison played ctl's keys in all 18 games at half and double. Medium (11 arms): nothing significant; share 5 (11 vs 17) and w_food 50 (12) led, bleeding either way and power or trip halved leaned worse. Big: share 5 reversed (42 vs 39). Full: w_food 50 was worse (71 vs 57, p = 0.038); over medium + big + full it is level (119 vs 113 of 1,710).

**#309, Word of Recall value x prepared depth x stairs before Recall on main 8e7dbad4 (pilot 44355657179, medium 44367307516, value-alone pilot 44369247745): stairs first is the setting that matters; the value is a progress knob.** Pilot: every Recall-first arm lost the same Blackguard, every stairs-first arm kept it. Medium (six stairs-first arms): 16-18 deaths of 270 in every arm whatever the value (100/300/1000) or prepared depth (5/3); higher values change more games and go slightly further. Value alone at 75/100/125/150: 1-2 of 18 games change, the same 2 scrolls bought from 100 up.

**#224 expanded, cornered (0,1) x radius (2,3) x big-level margin (0,1) on main 8e7dbad4 (pilot 44376837291, medium 44379732219): the margin is dead, the radius nearly so, cornered mode neutral.** Medium: margin 0 and 1 play identical keys in all 270 games; radius 3 changes 5 games and adds 1 death; cornered on vs off 17 vs 16 deaths (2 / 3). With the 6101ca01 run on all 1,800 starts (142 vs 151, p = 0.16), cornered mode does not measurably change survival on either build.

**#319, attack focus by class on main f660aecc (pilot, then small + medium + big, runs 44423205315, 44423223366 and 44423242333, starts 1-900, 2,700 games): lowering the families a class file does not raise changes no outcome.** Each class kept its shipped class-file preferences, and every other attack family (melee, projectile, thrown, spell, device, activation) went from the neutral 1000 to 750 or 500. The gate passed: one binary, no config_error, lines verified, no frozen-turn loops, every cell ended in death or at the turn cap; the death bundles were not replayed locally. Deaths: ctl 62/900, low750 60 (rescued 6, newly killed 4, p 0.75), low500 61 (8/7, p 1). Mean max CL 5.05-5.08 and DL 2.05 in every arm. Every class is within two deaths of ctl. Rangers play differently in 97 of 100 starts, Rogues in 45-66, Necromancers in 31-33 and Druids in 21-36; Warriors, Mages, Priests and Paladins play ctl's keys in 88-98. **Bins (RULES 18):** low750 and low500 are **neutral**: no measurable cost, safe to adopt if preferred. #274 (the same preferences scaled toward or away from 1000, on 4a482c58) is a separate study.

**#191, caution_rising_explore_ticks 300-2000 on main f660aecc (pilot, then small + medium + big, runs 44377398372, 44377423630 and 44430005739, starts 1-900, 4,500 games): holding a descent longer costs progress and buys no survival.** The gate passed (one binary, no config_error, values verified, no frozen-turn loops; the death bundles were not replayed locally). Deaths: 300 (shipped) 62/900, 500 56 (rescued 12, newly killed 6, p 0.24), 1000 58, 1500 60, 2000 59 (all p ≥ 0.5). Mean max CL falls with the hold, from 5.08 at 300 to 5.03, 4.92, 4.80 and 4.76, in nearly every class. In the pilot's retained messages the Borg held the descent ("exploring for them") 1,101 times at 300 and 3,202-3,904 times at 1,000-2,000, with fewer trip returns (104 against 63-74). **Bins (RULES 18):** 500 is **neutral** (56 deaths against 62, the same progress; safe to adopt). 1000 is **neutral** on deaths with a small progress cost (CL 4.92 against 5.08). 1500 and 2000 are **harmful** on progress (CL 4.80 and 4.76, falling in every tier) and neutral on deaths. With the earlier pilots (0-600 on e85b80e1 and d9ff9808), no value of this setting has changed deaths.

**#299, the scary list's class spread on main f660aecc: raising the fragile end does nothing at 100,000 turns; lowering the tough end by 5 raises tough-class progress (open).**
- **Spread pilot (run 44346946815, 72 games):** fragile + 3 and + 6 played the shipped keys in 18 of 18 games, with the lines verified in the run's list. No character outgrows the shipped fragile limit in 100,000 turns: Mages reach CL 4-5 and Necromancers CL 5, against a limit of 8 for the earliest monsters.
- **Tough end, pilot then small + medium + big (runs 44359605720, 44377349082, 44377372817 and 44429988454; starts 1-900, 2,700 games):** tough − 3 and − 5 with the fragile end unchanged. The gate passed. Deaths: ctl 62/900, t3 69 (rescued 4, newly killed 11, p 0.12), t5 57 (13/8, p 0.38). Mean max CL 5.08 / 5.26 / 5.45; DL 2.05 / 2.11 / 2.19. With t5, Warriors reach CL 7.0 against 6.3, Paladins 5.2 against 4.2 and Blackguards 6.5 against 5.1; Paladin deaths fall from 9 to 4 of 100. Mages and Necromancers play ctl's keys in every start. The dose is not monotone. **Bins (RULES 18):** t5 is **helpful** on progress and neutral on deaths; t3 **leans harmful** (69 against 62, rescued 4 against newly killed 11, p 0.12); fragile + 3 / + 6 are **neutral** (inert).
- **Full (run 44440277055, starts 901-1800, ctl and t5): over all 1,800 starts,** ctl 119 deaths and t5 115 (rescued 24, newly killed 20, p 0.65). Mean max CL 5.08 against 5.42, DL 2.08 against 2.19; the full tier alone gave 57 against 58 and CL 5.08 against 5.39. Paladins 14 against 9 of 200. **Bin:** t5 is helpful on progress in every tier and neutral on deaths, so it is safe to adopt. #350 tests lowering both ends.

**#330, borg_plays_risky on main 6438e1cf (pilot, run 44429970417, 36 games): risky play kills.** The gate passed. With TRUE, 7 of 18 characters die against 0 with the shipped FALSE (rescued 0, newly killed 7, McNemar p 0.016): Druid ×2, Necromancer ×2, Paladin, Rogue and Mage, all at CL2-4 on DL1-2. Every game plays differently, and mean max CL falls from 5.50 to 4.61. **Bin (RULES 18): TRUE is harmful** (p 0.016 at pilot size). The C Borg's switches-early (15 against 16 and 13 against 13 of 50) does not carry over to borg-reborn-rs.

**#290, point-blank divisor for Rangers and Rogues on main f660aecc (pilot, then medium, big and full on their own starts, runs 44359581333, 44360811472, 44360836868 and 44367279069; all 200 Ranger and 200 Rogue starts of classes-1800, 1,200 games): Rangers do better with no point-blank penalty (lead).** The gate passed. Rangers: divisor 2 (shipped) 18/200 deaths, 1 11/200 (rescued 11, newly killed 4, p 0.12), 3 17/200; mean max CL 5.51 / 5.56 / 5.59. Rogues: 3 (shipped) 6/200, 2 8/200, 4 5/200 (4 plays the shipped keys in 151 starts). The earlier all-class tiers (starts 1-360, common 5 / lo / hi) had 23 deaths in every arm. **Bins (RULES 18):** Ranger 1 is **helpful** (a lead, p 0.12); Ranger 3 is **neutral**; Rogue 2 and 4 are **neutral** (8 and 5 deaths against 6); and the all-class common / lo / hi arms are **neutral**. Ranger divisor 1 goes to confirmation on fresh seeds (classes-1800-b Rangers).
- **Confirmation (run 44440258841, the 200 Ranger starts of classes-1800-b, prespecified exact McNemar at 0.05): not confirmed.** Ranger divisor 1: 12 deaths against 15 (rescued 8, newly killed 5, p 0.58), mean max CL 5.55 against 5.67. Over both suites, 23 against 33 of 400. **Bin:** neutral, leaning helpful on deaths; safe to adopt, but it cannot be claimed to save Rangers.

**#274, attack preferences by class (verysmall, run 44329289001, 135 games on 4a482c58):** shipped 3/45 deaths, flat 3/45, half 5/45 (0 rescued, 2 newly killed). Neither alternative leads. With #319 (lowering the unfavoured families over 900 starts changed no outcome), the class attack preferences show no effect on survival in either direction. **Bins (RULES 18):** flat is **neutral**; half **leans harmful** (2 deaths against 1 in the pilot and 5 against 3 here, with a lower level), not significant.

**#291 medium, scary latch x calm on f660aecc (pilot 44317626468, medium 44425156291): the calm settings do nothing; unlatching is level.** Medium, 270 per arm: shipped 17, calm off 17 (259 games identical), unlatch 15, unlatch + calm off 15 (8 rescued / 6 newly killed); unlatching goes slightly further (CL +0.11, depth +0.14).

**#279 medium, borg_worships_* switches on 92fafc61 (pilot 44308259323, medium 44425189094): hp, mana and speed are inert; none helps.** hp, mana and speed play ctl's keys in all 270 games (gold was dropped from the pilot for the same reason: the live planner bypasses it); damage changes 21 games and ac 245, each 17 deaths against 16.

**#312 medium, Fox Form for a fleeing Druid on dbe99509 (pilot 44365539348, medium 44425221666): no effect.** 12 deaths in each arm of 270; 26 games change.

**#329 / #318, the scary flag clears only after a kill (caution_scary_unlatch_kill) x latch on 6438e1cf (pilot 44428541791, medium 44431942508): the shipped latch is best.** Pilot: kill-unlatch clears the flag only after a kill (46 times in 15 games) and never on a forgotten monster; plain unlatching cleared 56 times, 38 right after a "Forgetting a monster" note; with kill-unlatch on, the latch makes no difference (identical keys). Medium: shipped latch 11 deaths of 270; kill-unlatch 15 (1 rescued / 5 newly killed, p = 0.22); plain unlatch 18 (1 / 8, p = 0.039, early DL1 deaths to Grip, small kobolds and poison).

**#328, caution_town_never_scary on 6438e1cf (pilot 44431977979): changes every game; 2 new deaths, both on DL1.** Off 0, on 2 of 18 (a Druid CL2 and a Mage CL4 to wild cats on DL1); none in town. Direction only.

**#280, flight Recall on DL1 again (dl1off) on f660aecc, big tier (run 44440293820), pooled with starts 1-360: the lead did not hold.** Starts 1-900: ctl 62 deaths, dl1off 59 (rescued 36, newly killed 33, p 0.81). The big tier alone gave 39 against 42. Mages 13 against 8 and Paladins 9 against 4 lean helpful; Rangers 7 against 10 and Blackguards 2 against 5 lean harmful. **Bins (RULES 18):** dl1off and the other four Recall arms are neutral, safe to adopt if preferred.

**#342, #597's switches (caution_twitch_avoid_lava, caution_stair_parked_fallback; compiled 0, shipped 1) on 6438e1cf (pilot, run 44440312372, 54 games):** both play the shipped keys in 18 of 18 games with each switch off, and no deaths. **Bins:** neutral (inert at this size).

**#265, healing by class re-piloted on main 38858846 (run 44445305823, 108 games): two builds agree.** Deaths: ctl 0, curve-lo 3, curve-hi 0, reserve-lo 2, reserve-hi 1, common 2 of 18. On 4a482c58: 1, 2, 1, 3, 1 and 2. On both builds no alternative has fewer deaths than the shipped class files, every alternative ends lower in level, and Druids die with common, curve-lo and reserve-lo but never with the shipped values. **Bins (descriptive, 2 starts per class):** curve-lo, reserve-lo and common lean harmful; curve-hi and reserve-hi are neutral on deaths with a lower level.

**#350, lowering the scary list's fragile end together with the tough end on 38858846 (pilots, runs 44446160367 and 44446177348): lowering the whole range raises progress; the fragile end alone barely acts.**
- **100,000 turns (classes-18):** ctl 0 deaths, mean max CL 5.50. t5 (tough − 5) 0 deaths, CL 5.67. all5 (both ends − 5) 0, CL 5.83. t5f6 (tough − 5, fragile − 6) 2, CL 5.50: a Druid to a kobold and a Priest to Fang.
- **200,000 turns (first 18 starts of classes-1800-200k):** ctl 3 deaths, CL 6.17, DL 2.28. all5 1 death, CL 8.22, DL 3.33 (rescued 3, newly killed 1). t5f6 2 deaths, CL 8.22, DL 3.33. f3 (fragile = tough) and fraghalf (class fragility halved) play ctl's keys in 10 and 16 of 18 games, with the same 3 deaths.
- **Why the fragile end barely acts:** even at 200,000 turns no caster passes CL 8 in ctl (Mages 5 and 7), so the fragile end of most monsters is never reached.
- **Bins (direction only):** all5 is helpful on progress at both lengths and neutral or helpful on deaths; t5f6 is helpful on progress at 200k and leans harmful at 100k; f3 and fraghalf are neutral.
- **Tiers at 100,000 turns, starts 1-360 (small + medium, runs 44459418261 and 44459437284):** ctl 13 deaths, t5 18 (rescued 2, newly killed 7, p 0.18), all5 18 (4 / 9, p 0.27). Mean max CL 5.25 / 5.53 / 5.73. The extra deaths are mostly Paladins (5 against 1 in both arms) and soldiers (all5 4, t5 3, ctl 1).
- **200,000 turns, starts 19-90 (run 44459456699):** ctl 4/72 deaths, CL 6.83; all5 6/72, CL 7.65 (0 / 2). Two all5 deaths are Druids at CL2, killed by an apprentice and by Grip.
- **Deeper cuts (pilots 44459366821 and 44459384054; ctl and all5 replay the #350 pilots, 36 of 36 at each length):** all8 (both ends − 8) and early-none (the 14 early monsters removed) have 3 deaths of 18 at 100k against 0 (0 rescued; Fang, Grip, soldiers, a crow and a wild cat, at CL1-4). At 200k they have 0 and 1 against 3, with CL 8.4.
- **Bins (RULES 18):** all5 and t5 are helpful on progress in every tier but **lean harmful on deaths** on this build: a trade-off whose cost sits at CL1-4. all8 and early-none are **harmful** at 100k. The floor pilots (#369) keep the early fear and cut it above.

**#265 small tier on main 38858846 (run 44459475886, starts 1-90, 360 games): lowering the class healing values is harmful.** Deaths: shipped class files 2/90, common 6 (rescued 0, newly killed 4, p 0.12), curve-lo 8 (2 / 8, p 0.11), reserve-lo 7 (0 / 5, p 0.062). Every lowered arm also levels slower (CL 4.96-5.03 against 5.36), and Druids die most in each. The direction is the same in both pilots (4a482c58, 38858846) and here. **Bins:** curve-lo, reserve-lo and common are harmful; the shipped class values are the best tested.

**#361, the bundle of safe-to-adopt changes on 38858846 (pilot, run 44459401300, 54 games):** no deaths in any arm. scary all5 + Ranger divisor 1 + Recall gate 0 reaches CL 5.89 against 5.50; without all5 the pair plays ctl's keys in 16 of 18 games. **Bins:** both neutral on deaths. The bundle's progress comes from all5, whose early-death cost (above) argues for carrying the winning scary variant instead.

**#369, the scary list cut with a level floor on 38858846 (pilots 44465218294 and 44465235895; ctl and all5 replay #350's pilots exactly):** at 100k no arm has a death. At 200k: ctl 3/18 deaths and CL 6.17; all5 1 and CL 8.22; all5-pal (Paladins keep the shipped levels) 2 and 7.83; floor3 3 and 7.06; floor4 3 and 6.61. The floors keep exactly the ctl's three early deaths (CL2-3 on DL1: a cave spider, a giant white centipede and Fang), which all5 avoids, and they give part of all5's progress gain. **Bins (direction only):** floor3, floor4 and all5-pal are neutral on deaths. The early-death cost all5 showed over 360 starts at 100k (18 against 13) needs a 360-start tier of ctl, all5 and floor3 to settle.
- **floor3 at 100,000 turns, starts 1-360 (runs 44498103824 and 44498131613; ctl replays #350's ctl in 360 of 360; all5 and t5 paired from #350's runs on the same starts):** ctl 13 deaths and mean max CL 5.25; **floor3 13 deaths (rescued 2, newly killed 2) and CL 5.60**; all5 18 and 5.73; t5 18 and 5.53. floor3 against all5: 9 rescued, 4 newly killed. floor3 keeps ctl's causes of death (wild cats, poison, a crow, Fang) without all5's soldier and Paladin deaths (Paladins 0, against 1 for ctl and 5 for all5), and every class levels at least as well as ctl. **Bin:** floor3 is helpful on progress and neutral on deaths. It is the best scary variant tested and safe to adopt.
- **floor3 over all 1,800 starts (big 44507514816, full 44519974488; 200k small 44507490759):** ctl 100 deaths, floor3 103 (rescued 16, newly killed 19, p 0.74). Mean max CL 5.11 against 5.49, DL 2.06 against 2.18: the progress gain holds in every tier, while the 1-900 death lead (49 against 51) evened out (full alone 54 against 49). At 200k, starts 19-90: 5 deaths against 4, CL 7.47 against 6.83. **Final bin:** floor3 is helpful on progress and neutral on deaths.
- **floor3 bundle (#361, pilot 44507465460) and floor3 × errands (#405, pilot 44551470526):** no visible gain at pilot size. The bundle plays ctl's outcome; floor3 + errands has 3 deaths against 1 (a Warrior to a kobold, a Paladin in lava). Both are neutral, and a 360-start tier is needed to see whether the two gains add up.

**#244, kill_live_min_power re-piloted on main 38858846 (run 44465254082, 36 games):** no deaths in either arm. Turning it off changes 17 of 18 games and lowers the mean max CL (5.11 against 5.50). **Bin:** off is neutral on deaths and leans harmful on progress. On c9e58ca0 the shipped 1 had 22 deaths against 28 over 360 starts.

**#329 / #318 complete, kill-unlatch x latch on 6438e1cf (adds big and full 44453041589; all 1,800 starts, 1,728 paired per arm): kill-unlatch costs nothing; plain unlatching leans worse.** Every tier's gate passed (156 of 156 death bundles reproduced in the full tier). Deaths: shipped latch 98 (5.7%), kill-unlatch 98 (rescued 20, newly killed 20, p 1.0; mean max CL 5.18 against 5.10, DL 2.10 against 2.06), plain unlatch 115 (29 / 46, p 0.064). **Bins (RULES 18):** kill-unlatch is **neutral, safe to adopt**, with a small progress gain; plain unlatch **leans worse**.

**#334, #584's Phase Door rule on PR #612 head 2075f54e (pilot 44436156652, 54 games):** ctl 0 deaths, rule-100 1, rule-150 2; Phase Door reads fall from 30 to 12 and 4, and every game changes. **Bins (direction only):** rule-100 neutral, rule-150 leaning worse. Superseded by #347, which measures the version merged to main.

**#335, flight Recall from danger on 38858846 (pilot 44453013990, 7 arms, 126 games):** one death (g2d200) in 126 games; every arm changes 12-16 of 18 games. **Bins:** all neutral at pilot size.

**Pilots of 2026-11-19 (classes-18, 18 starts per arm, all gates passed, direction only):**
- **#355, caution_scary_damage_percent 40/50/60 on main 07844cf1 (run 44456214066):** 60 (shipped) 0 deaths, 50 1, 40 1, the same Druid (seed 934061548, CL1, wild cat on DL1); 1-2 of 18 games change. All neutral.
- **#356, caution_rising_explore_ticks 300/500/700/900 on 07844cf1 (run 44456243022):** 0, 0, 1 (a Warrior CL7 on DL2 under 700), 0 deaths; every longer value changes 9 of 18 games and ends slightly lower (CL 5.39-5.50 against 5.67). All neutral; consistent with #191 (longer holds cost progress).
- **#347, #584's Phase Door rule as merged, on main 4acf071f (run 44458680428, 5 arms):** ctl 1 death, thr-100 2, thr-150 1, fight 2, fight-landing 1; the shared death is the same Druid; the rule changes 17-18 of 18 games. fight-landing is the only arm level with ctl on progress (CL 5.22, DL 2.11). All neutral.
- **#357, caution_scary_unlatch_calmed on PR #595 head 49933db7 (run 44458706433):** no deaths in any arm; calmed, kill and both change 14 of 18 games, with calmed and both alike as expected. All neutral.
- **#358, caution_recall_wait_as_usual on PR #627 head cdd065ca (run 44458734474):** no deaths; 1 of 18 games changes (most flight Recalls here are read on DL1, where the switch does not act). Neutral.

**Next tiers of 2026-11-19 (every gate passed: one binary, no config_error, values written, every death bundle reproduced, no frozen-turn loops; deaths of 270 per arm unless stated):**
- **#335 medium, flight Recall from danger on 38858846 (run 44462222798): holding back the flight Recall is harmful.** ctl (shipped) 11; g2 25 (6 rescued / 20 newly killed, p 0.009), g2d100 27 (4 / 20, p 0.002), r0 27 (6 / 22, p 0.004), r0d100 27 (4 / 20, p 0.002). Every class but Warriors and Rangers pays; the danger share does not win the cost back (g2d100 27 against g2 25, r0d100 27 against r0 27). **Bins:** all four **harmful**.
- **#347 medium, #584's Phase Door rule on 4acf071f (run 44462174256):** ctl 11, thr-100 8 (6 / 3, p 0.51), thr-150 12, fight 15, fight-landing 14; mean max CL 5.08 / 5.11 / 5.09 / 5.02 / 5.01. **Bins:** thr-100 **neutral, leaning better** (safe to adopt); thr-150 neutral; fight and fight-landing neutral, leaning worse. **Big tier (run 44497293750, starts 361-900):** ctl 35, thr-100 20 of 540 (23 / 8, p 0.011). **Full tier (run 44518290845, starts 901-1800): the lead did not repeat,** 46 against 47 of 900 (26 / 27). **Whole study (1,728 paired starts):** ctl 93, thr-100 77 (55 / 39, p 0.12), mean max CL 5.10 against 5.13; Druids 19 against 12. **Bin: thr-100 is neutral, leaning better,** safe to adopt (no cost on any tier).
- **#356 medium, caution_rising_explore_ticks on 07844cf1 (run 44462187014):** 300 (shipped) 9, 500 11, 700 10, 900 8; each longer value changes about 145 games and lowers mean max CL (5.17 against 5.08 / 5.10 / 5.01). **Bins:** all **neutral** on deaths with a small progress cost, as in #191.
- **#357 medium, caution_scary_unlatch_calmed on PR #595 head 49933db7 (run 44462208269):** latch 11, calmed 14 (1 / 4, p 0.38), kill 15 (1 / 5, p 0.22). **Bins:** calmed neutral, kill leaning worse at this tier (level over #329's 1,800 starts). **Big tier (run 44497319223):** latch 38, calmed 32 of 540 (10 / 4, p 0.18); over medium + big 49 against 46 (11 / 8, p 0.65), CL 5.21 against 5.10. **Bin: calmed is neutral, safe to adopt, with a progress gain.**
- **#355 medium, caution_scary_damage_percent on 07844cf1 (run 44462257617):** 60 (shipped) 9, 50 10 (17 games change), 40 12 (0 / 3, p 0.25). **Bins:** 50 neutral, 40 neutral leaning worse.
- **#364 small + medium, breeder-colony avoidance on PR #632 head 985c772a (run 44462234908, starts 1-360, 360 per arm):** ctl 14, avoid 14 (6 / 6), avoid-nofight 15, avoid-exit 15; about 330 of 360 games change, progress level. **Bins:** all **neutral, safe to adopt**.
- **#358, caution_recall_wait_as_usual at 200,000 turns on PR #627 head cdd065ca (run 44462245391, classes-1800-200k starts 19-90, 72 per arm):** 4 deaths in each arm, the same characters; the switch changes 19 of 72 games. **Bin:** neutral, safe to adopt.

**#379, point-blank divisor Ranger 1 / Rogue 2 on main 3ba17e2c (pilot 44505026276, rest 44505764140; all 200 Ranger and 200 Rogue starts of classes-1800, 800 games): the Ranger lead of #290 reverses; Rogue 2 leads.** The gate passed (50 of 50 death bundles reproduced). Rangers: main's 2 12 deaths, 1 21 (rescued 6, newly killed 15, p 0.078), mean max CL 5.71 against 5.54. Rogues: main's 3 11, 2 7 (4 / 0, p 0.125), CL 5.56 against 5.49; 69 of 200 games identical. **Bins (RULES 18):** Ranger 1 **leaning worse** (main's 2 stays better on this build); Rogue 2 **leaning better**, safe to adopt.

**#385, the town changes on main 0892ebd7 (pilot 44518308077, 72 games):** shipped 1 death (CL 5.61), town-off (#622 and #621 undone) 2 (CL 5.00), kill-on-sight 1 (3 of 18 games change), never-scary 3, all CL1-2 on DL1 (CL 4.78). The deaths match the request's local sanity cells. **Bins (direction only):** the shipped town changes look right; kill-on-sight neutral; never-scary leaning worse, as in #328.

**#383, the errands plan on main 3ba17e2c (pilot, then small, medium, big and full: all 1,800 starts, 5,400 games): errands_plan.txt lowers deaths.** The gate passed, with each cell's plan recorded and pinned and no stalled or borg_stopped cells. Deaths: none (shipped) 105, **errands 91 (rescued 18, newly killed 4, exact McNemar p 0.004)**, ambitious 102 (6 / 3, p 0.51). errands is lower or equal in every tier (small 3 / 3, medium 18 / 20, big 32 / 37, full 38 / 45) and saves Warriors (0 against 4) and Blackguards (2 against 7). Mean max CL is unchanged in every class. **Bins:** errands is helpful on deaths and neutral on progress; ambitious is neutral. This is a development-suite result: the confirmation on classes-1800-b (another session, `reborn-errands-main-confirm`) decides the claim. Shipped main's deaths are early: 62% at CL1-2, almost all on DL1-2. The top killers are crows (21 of 105), soldiers (13), wild cats (11) and Farmer Maggot's dogs (16).

**Pilots of untested settings on main 3ba17e2c (2026-11-19, 18 starts each; the one ctl death is the same Priest to a rock lizard in every pilot):**
- **Town gold reserve (#392):** every reserve arm (300, 1000, 25%, 50%) changes all 18 games, with 13 deaths in total against 4 and a lower level (CL 4.50-5.39 against 5.61). **Lean harmful**; the shipped 0 / 0 is best tested.
- **Bless (#388):** never casting, or stopping sooner, changes 3 games with no outcome change; the other two arms are inert. **Neutral.**
- **Phase Door thresholds (#389):** unique and anti-summon arms are inert; ordinary danger 20 is neutral; **ordinary danger 5 leans harmful on progress** (CL 5.11).
- **Town attack on dangerous townspeople (#390):** changes 3-4 games, no outcome change. **Neutral.**
- **Scary stand off (#393):** 2 deaths against 1, **neutral**. **Detect Invisible after every rest (#393):** changes 16 games and **leans harmful on progress** (CL 5.00).
- **Crows scary at CL1-2 (#408):** every arm plays ctl's keys in 18 of 18 games. The lines are in the list and crows appear, but the scare never fires on these starts, which have no crow death. **Not tested:** it needs the crow-death starts themselves.

**Suite 1 smoke on borg-cemetery 3d1d0374 and borg-reborn-rs main 38858846 (run 44523525112, #183):** 18 of 18 encounters ran, none invalid or stopped; 9 deaths and 9 survivals. The class-value check that failed runs 44442676041 and 44446442326 passes on this pin.

**#379, Rogue point-blank divisor 2: the fresh-seed confirmation does not hold (run 44524153538, the 200 Rogue starts of classes-1800-b, main 3ba17e2c).** Main's 3 8 deaths, 2 9 (0 / 1, p 1.0), CL 5.59 against 5.55. With the development starts: 16 against 19 (4 / 1). **Final bin:** Rogue 2 is neutral, safe to adopt but with no measured benefit.

**#347, thr-100 at 200,000 turns (run 44524189120, classes-1800-200k starts 19-90, main 4acf071f):** 5 deaths against 5 (3 / 3), CL 6.68 against 6.86. **Bin:** neutral; no extra deaths after turn 100,000.

**#396, the safe-to-adopt bundle on main 3ba17e2c (calmed 1, Recall wait-as-usual 1, Phase Door thr-100, Rogue divisor 2; pilot 44524209558, medium 44553471958, big 44570626345): helpful.** Medium: ctl 20, bundle 11 of 270 (15 / 6, p 0.078). Big (starts 361-900): 37 against 22 of 540 (22 / 7, **p 0.008**). Medium + big: 57 against 33 of 810 (37 / 13, p 0.001). Mean max CL +0.13 (95% CI +0.04 to +0.22) and DL +0.03 over 828 paired starts; no class is worse. **Bin: helpful.** The parts were each developed on classes-1800, so a classes-1800-b confirmation would settle it.

**Untested settings on main 3ba17e2c, small tiers (starts 1-90, with the pilot 108 per arm; every gate passed):**
- **Trip gold return (#402, small 44570213189):** g0 (shipped, never) 4 deaths, g50 4, g150 6, g400 4. g50 costs 0.30 CL and 0.36 DL, and g150 0.14 CL and 0.19 DL. **Bins:** neutral on deaths with a progress cost; shipped 0 stays.
- **Town trip forecast (#403, small 44570316850):** ctl 4; gain2 8, explore500 9, explore2000 6, stair25 9, stair100 8, attack50 7, attack200 7, **support2000 12 (1 / 9, p 0.021)**, support500 3. **Bins:** support2000 harmful (uncorrected for nine arms; 0.19 corrected); explore500, stair25 and stair100 leaning worse; the rest neutral. Nine of ten changes die more than shipped. support500 is the only candidate.
- **Breeder settings (#404, small 44570413639):** ctl 4, acidfear 5, nostand 5, esc3 6, esc10 5; 6-32 of 90 games change, and no arm saves a game. **Bins:** all neutral, rarely reached.

**#413, new flags on main HEAD 592c6984 (pilot 44560354236, small 44570516913; 108 starts per arm):** the three #637 flags (town wand, caster walk, whole bonus) play byte-identical games to on_sight alone in 18 of 18 pilot starts, so they are **not reached** in early games. ctl 4 deaths; onsight 4, foxtown 4 (12 of 108 games change), recall-rest (#640, 200 turns) 6 (1 / 3), phase-rule 5 (3 / 4, CL +0.21), errands 5 (0 / 1). **Bins:** onsight and foxtown neutral, as on 3ba17e2c; recall-rest neutral leaning worse; the Phase Door rule and errands re-checks run normally on the new main, but 108 starts cannot see their 3ba17e2c effects.

**#383, the errands plan: confirmation and 200,000 turns (main 3ba17e2c).** Confirmation on classes-1800-b (1,800 fresh starts): none 128 deaths, **errands 117 (p 0.035)**, CL −0.09 and DL −0.08. Survival is confirmed, and DL just misses the prespecified −0.10 non-inferiority margin. At 200,000 turns (starts 1-360, pilot + small + medium): 23 against 22 (4 / 3), CL −0.07, **DL −0.23**. All of the depth cost is at CL7-14: mean ΔDL −0.29 at control CL7-9 and −1.60 at CL10-14, against +0.04 to +0.12 below CL7, where the caps are 1-2 and the survival lead is. **Bins:** helpful on deaths at 100k, with a depth cost that grows with game length. A variant that keeps the caps of 1-2 and takes the ambitious plan's caps after (`errands_plan_early.txt`) is proposed on borg-reborn-rs#674. It needs the file in a main commit before a pilot.

**#369, floor3 Rogue confirmation (the 200 Rogue starts of classes-1800-b, main 3ba17e2c):** ctl 8 deaths, floor3 7 (7 / 6, p 1.0), CL +0.46. **Bin:** neutral on deaths, helpful on progress for Rogues. On main, floor3 is on #416's "not to ship" list for its all-class deaths (105 to 127).

**#415 study 2, Mage and Priest on main 592c6984 (pilot, 20 starts per arm):** ctl 1 death; heal-hi (Mage 225 / 450, Priest 185 / 375) 2 (1 / 2); spell preference 1500 1, with 17 of 20 games identical. **Bins:** heal-hi neutral; spell 1500 neutral and mostly inert.

**Death-start replays on main 3ba17e2c (#408, #429): they measure reach, not effect.** These runs replay only the starts where shipped main died: 55 crow / wild-cat deaths, and all 233 deaths of the development and confirmation suites. ctl replays every death exactly.
- **Scary-list crow arms** (crow2, crow3, crowcat2): they change 0-1 of the 55 games. **Not reached:** the Borg is already fleeing when the crow catches it.
- **The death bank** (233 starts): the Phase Door rule 86 deaths (changes 163 games), calmed 178 (66), errands 198 (37), all three 80 (169).
- **The crow escape replay** (55 starts): the rule 30 deaths, rule + throwing 1500 30 (53 of 55 identical to the rule: inert), rule + more oil (`borg_town_w_attack` 200, `attack_turns` 50) 10 (changes 50).
- **Caveat:** a game that changes dies only 5-17% of the time, whatever the change, close to the 6% random-start death rate. A start's death is mostly the bad luck of one path. So rescue counts measure how often an arm changes the game, not whether its mechanism saves.
- **No bin from these runs.** Only "not reached" is a reading.
- **Oil on random starts:** in the #415 casters pilot (40 starts, 592c6984), oil has 6 deaths against 2 (1 / 5, p 0.22). It buys 190 more flasks in total, and 27 fewer Cure Light Wounds and 11 fewer Phase Door. The extra deaths were not to oil-related situations. The per-class oil curves of #433 test it on random starts.

**Studies on borg-reborn-rs main e5cc5469 and a87b4c96 (2026-11-19 evening; every gate passed):**
- **The new base has a new death:** a CL3 Paladin (seed 766958386, classes-18) dies of poison in town at turn 5,100 in every arm on e5cc5469. The same start reached the cap on 0d8b61d7 and 592c6984.
- **#426, ranged first against immobile attackers** (pilot 44599279288, 0d8b61d7):
  - deaths 0 → 1, a Blackguard to a yellow worm mass (the local run's case);
  - 13 of 18 games change;
  - CL +0.28.
  - **Bin:** neutral.
- **#427, throws rated like melee** (pilot 44599308992, PR #687 head 7c9b4cd1):
  - 1 death against 1, the shared Paladin;
  - 16 of 18 games change;
  - CL −0.06.
  - **Bin:** neutral.
- **#428, the rest of the bundle on e5cc5469** (pilot 44599338458, small 44602792133; 108 starts per arm). ctl 2 deaths.
  - **Recall wait-as-usual:** 2 deaths; changes 3 of 108 games. **Bin:** neutral, barely reached.
  - **Errands:** 3 deaths (0 / 1), **mean max DL −0.18** (2.24 → 2.06). **Bin:** leaning worse.
  - **Both:** the same as errands.
  - With calmed and the Phase Door rule shipped, the plan's 3ba17e2c survival gain is gone at this size, and its depth cost stays.
- **#403, support500 at medium** (44599368117, 3ba17e2c):
  - medium: 17 against 20 (6 / 9);
  - with pilot and small (378 per arm): 20 against 24 (7 / 11, p 0.48), with CL and DL unchanged.
  - **Bin:** neutral. Shipped 1000 stays.
- **Suite 1 on e5cc5469** (smoke 44599396105, #183): 8 deaths of 18. Per class, it matches the 38858846 smoke.
- **#437, Blackguards and the Phase Door rule on a87b4c96** (pilot 44607237940, the 10 Blackguard starts of classes-1800-small):
  - no deaths in either arm;
  - rule-off changes all 10 games, CL +0.7 and DL +0.6.
  - **Bin:** neutral on deaths, leaning better on progress. Medium is proposed.
- **#436, caster oil on a87b4c96** (pilot 44607268031, 40 caster starts):
  - `borg_town_w_attack` 200: 3 deaths against 3 (3 / 3), CL +0.25;
  - it rescues the two CL1-2 deaths and adds three later ones.
  - **Bin:** neutral.
  - The oil-curve arms wait for profile-writable class lines (borg-reborn-rs#696).

**Studies on borg-reborn-rs main dbc92d18 and PR builds (2026-11-19/20).** Every gate passed: one binary, no config_error, every cell finished, no stalls or frozen-turn bursts.
- **#443, no detection prayer by panel below CL10 for the casters (`light_detect_evil_spell_min_level` 10, shipped by #703), small + medium (runs 44634350382, 44634363516; pilots on PR head 3ed059b6 and on dbc92d18):** 12 deaths in each arm, the same 12 characters. **CL +0.49 (±0.10)**, DL +0.14. Mage +1.50, Priest +1.25, Paladin +1.02, Necromancer +0.68, each interval above 0. Every Warrior, Rogue, Ranger, Blackguard and Druid game is identical. **Bin: helpful on progress, neutral on deaths**: the clearest progress effect of the day, supporting the shipped value.
- **#433, the owner's per-class Phase Door and oil curves (#688) against all scales 100:**
  - On a87b4c96, starts 1-360: 13 against 9 deaths (8 / 4, p 0.39).
  - Restarted on dbc92d18 after #686 changed flask damage, all 1,800 starts (3,600 games): **67 against 66 (47 / 46, p 1.0)**, CL −0.01 ±0.06. No class differs (Holm p = 1). Mage's lead on starts 1-360 (5 → 1) reversed to 10 → 13.
  - Blackguard 1 → 5 (p 0.22), with the Phase Door curve and the healing changed together. On the 200 classes-1800-b Blackguard starts (run 44652435342), shipped has 4 deaths. Phase Door 100 and healing 75 / 150 each have 2 (4 / 2, p 0.69).
  - **Bins:** neutral overall and for every class; the Blackguard values are neutral and safe to keep.
- **#411, kill breeders first (`caution_breeder_stoppable`, with `caution_breeder_avoid`):**
  - Pilots: ed8e270d 1 / 3 / 2 deaths; dbc92d18 1 / 2 / 2. On dbc92d18, stop rescues the shipped Necromancer's blue-worm-mass death.
  - Small + medium on dbc92d18 (runs 44634375920, 44634389746): ctl 12, stop 11, stop-avoid 11 (7 / 6 each, p 1.0), CL −0.06 and −0.09 ±0.13. stop has 4 poison deaths against 0.
  - **Bins:** neutral, safe to adopt with no measured benefit.
- **#448, walk out of a slower crowd (`caution_slow_crowd_exit`, PR #702 head c3747cc9), small + medium (runs 44619277864, 44619292193):** 9 against 7 (2 / 0, p 0.50). 352 of 360 games are identical. The rescues include a Priest lost to a blue worm mass, the rule's own case (CL 5 → 11). **Bin: neutral, safe to adopt**; it fires too rarely to measure.
- **#457, store at home only when overweight (`town_store_only_overweight`, PR #714 head d9e5a37e):** pilot 1 → 0 deaths, CL sum 103 → 109. Small + medium (runs 44650547561, 44650559030): 12 against 10 (9 / 7, p 0.80), CL +0.04, and 358 of 360 games change. **Bin: neutral, safe to adopt.**
- **#438, the hunt removed in steps (`kill_flow_mode`, PR #695 head f9c44b35), 200,000-turn pilot:** deaths 2 / 1 / 2 / 1 for modes 0-3, CL 6.72 / 7.06 / 6.56 / 7.17. No game passes CL10, so the question (CL10 and above) is not reached. **Direction only:** modes 1 and 3 lead.
- **#450, never-varied town settings, pilot on dbc92d18 (run 44632887493):**
  - The device value at 50 / 100 / 200 is **not reached** (17-18 of 18 games identical).
  - The missile reserve 50 / 100 changes 8-10 games with no outcome change (CL +0.06 to +0.17). Other-ranged 50 plays like reserve 100 alone.
  - Town flee no-worse changes 2 games.

**Later tiers and new pilots (2026-11-20; every gate passed unless noted):**
- **#436, caster oil, medium** (44616509514, 120 caster starts, a87b4c96): `borg_town_w_attack` 200 has 4 deaths against 5 (5 / 4). With the pilot: 7 against 8 (8 / 7), DL −0.10. **Bin:** neutral.
  - The cause is upstream: the pack stashes the oil the planner buys (borg-reborn-rs#712, below), so a higher buying weight can't work yet.
- **#437, Blackguards and the Phase Door rule, medium** (44616480589, 30 Blackguard starts, a87b4c96): rule-off has 3 deaths against 0 (0 / 3). With the pilot, 3 against 0 on 40. **Bin:** leaning worse for rule-off. It doesn't support the Blackguard exception (borg-reborn-rs#673). Stopped here.
- **#428, errands on e5cc5469, medium** (44616539032, starts 91-360): 12 against 12 (2 / 2). Over 378 starts: errands 15 against 14 (2 / 3), CL −0.13, **DL −0.11**. **Bin:** neutral on deaths, leaning worse on progress. The 3ba17e2c survival gain is gone, because main's own deaths fell to 3.7%.
- **#446, the errands plan as a depth cap (`prepared_depth_plan`, PR #701 head 8ffee286):**
  - pilot (44639042890, 100k): no deaths; the cap changes 4 of 18 games.
  - 200,000 turns, starts 1-90 (44649264554): ctl 6, formula 8 (0 / 2), errands 6 (2 / 2).
  - Depth: formula −0.12 DL, errands −0.19 (−0.11 and −0.24 for CL7+ characters).
  - **Bin:** neither saves games. The formula costs about half the plan's depth. Ship neither.
- **#461, immobile creatures kept at range (`caution_ranged_vs_immobile` 0-3, PR #717 head 5af2f79f):**
  - pilot (44645867864): 1 death in every arm, the same worm mass.
  - Big, starts 361-900 (44649259904): mode 0: 22 deaths, mode 1: 22 (6 / 6), mode 2 (the PR's default): 24 (9 / 11), mode 3: 27 (10 / 15). **Druids 5 → 6 / 9 / 10.**
  - **The gate fails on one cell:** mode 3 seed 1350297981 crashed with SIGABRT, "race 624 has no blow array" in `immobile_kept_at_range`, reproduced locally (borg-reborn-rs#726). Mode 2 runs the same code.
  - **Bins:** mode 1 neutral; modes 2 and 3 leaning worse. The default of 2 isn't supported.
- **#460, the five breeder switches (PR #702 head 0a76dc19):**
  - pilot (44645872606, 8 arms): exit and crowd 0 deaths against 1; the four arms with `stoppable` each have 2, including the same CL1 floating-eye death.
  - small + medium (44651947475, 5 arms): ctl 12, rest 9 (5 / 2), crowd 11 (1 / 0), kill-first 10 (8 / 6, 25 of 360 identical), exit 14 (1 / 3).
  - big (44655845685, 3 arms): ctl 22, rest 21 (2 / 1), crowd 22 (0 / 0, 535 of 540 identical).
  - **Over 918 starts:** rest 31 against 35 (7 / 3, p 0.34); crowd 33 (2 / 0; with #448, 4 / 0).
  - **Bins:** rest leaning better, crowd neutral and safe, kill-first neutral, exit leaning worse. Breeders killed 2 of ctl's 13 deaths over pilot, small and medium.
- **Suite 1 on main e5cc5469** (#183): small 26 of 90 (7e08c920: 26), medium 80 of 360 (85), big **228 of 900 (250)**.
  - In big, Priests −8, Rangers −5, Warriors −4, Mages −3. Necromancers are the only class up (+2).
- **Cures and oil, from the retained logs (borg-reborn-rs#710):**
  - **Cures quaffed fell** from 5.4 to 2.4-2.8 per game between 9ecbfd1e and e5cc5469. That's because there are fewer fights (melee notes 92 → 53; cures per melee note 0.059 → 0.053); the healing settings didn't change.
  - **Bought, then stashed at home:** in 11-15 of 18 games on every recent main, and 36 of 40 caster games, the Borg buys Cure Serious Wounds and stashes them. Pack power rewards CSW only after max CL 10 (borg-reborn-rs#711, tested by #457).
  - **Oil:** Flasks of oil count with launcher ammunition under a cap of 20 for non-Ranger/Warrior classes, so casters with a sling stash their oil (borg-reborn-rs#712). Two poisoned Druid deaths had their cures and oil in the home.
  - The Rust Borg throws 17-29 flasks per game; the C Borgs throw 4-5.
- **Paladin 766958386, the yellow jelly** (borg-cemetery#79, dossier D-540138fafac2, borg-reborn-rs#713):
  - It meleed an adjacent yellow jelly for 120 game turns with 24 Flasks of oil unused, then died of poison in town.
  - #461's rule is the fix under test.

**Results of 2026-11-20, afternoon (borg-reborn-rs on engine 574b618c; every gate passed unless noted):**
- **Shipped main, full classes-1800 runs:**
  - **94032140** (#484, run 44679955697): **42 deaths of 1,800 (2.3%)**, CL 5.39, DL 2.00. Main now ships the depth cap (`prepared_depth_plan` 1, class values from #735). Against main dbc92d18 (66 deaths; different engine, so outcomes only), the falls are in the capped classes (Priest 10 → 3, Mage 13 → 9, Paladin 3 → 1), and those classes lose about 1.1-1.4 CL and 0.5 DL. A paired cap 1 against 0 check on this specimen has not been run.
  - **fde8025a** (#488, run 44681930409): **33 deaths of 1,800 (1.8%)**, CL 5.41, DL 1.98; all 33 on DL1-2, 24 at CL1-3. Against 3ba17e2c (105) deaths fell about threefold in every class except **Rangers: 12**, against 5 on 94032140 half an hour earlier (11 of the 12 survive there). The only Ranger-specific change between them is #725 (#716, arrows capped at 50). 10 of the 12 last attacks were melee with 24-86 arrows in the pack.
- **#480, the shipped switches on main b895e352** (runs 44676098130, 44677651675; starts 1-360): `attack_throw_as_melee` off 20 deaths against 11 (6 / 15, p 0.078, Holm 0.39): **keep it on (leaning helpful)**. `town_store_only_overweight` off 8 (neutral). **Detection min level 10 for the casters: CL +0.53 ±0.09**, deaths 11 against 11 (Mage +1.62, Priest +1.27, Paladin +1.10, Necromancer +0.72); for every class +0.59. `caution_ranged_vs_immobile` 1: neutral. The fourth measurement with the same detection result; filed as borg-reborn-rs#744 (re-ship 10, undo #728).
- **#475, our stairs leash for CL1-4 (`flow_leash` 1) on the re-pinned head 80646820** (run 44710808541, starts 1-360): 7 deaths against 6 (6 / 7, p 1.0), CL −0.14, 0 of 360 games identical. The earlier lead on 769132df (29 → 16 on starts 1-900) did not hold. **Bin: neutral.** The leash was dropped (borg-reborn-rs PR #734 closed); C's leash is now parameters on main (PR #755), screened in #506.
- **#477, #736's three parts (stairs on a clean path, step-away, mobile threat) on 7750b604, pilot** (run 44676442008): no deaths in any arm; CL +0.11 shipped and +0.33 with step-away. Superseded by fde8025a (#488); step-away has no pilot on current main.
- **#482, the breeder policy in the breeders-x4 world** (PR #740 e41eb758; small + medium 44709994372, 44710005901; big 44716984886):
  - Starts 1-360 against shipped p3 (8 deaths): p0 (C) 11, p1 12, p2 10, each with **CL −0.15 to −0.23 (interval below 0)**: harmful on progress. p4 8 and p5 6: neutral. **Shipped policy 3 is supported.**
  - 7 Druid cells on DL1 did not finish (frozen-turn loops in every arm, p3 included).
  - Big, p3 alone (starts 361-900): 19 of 540 deaths (3.5%), CL 5.51, at least 5 to breeders; **no frozen-turn bursts in 540 cells**, all 60 Druids included, so the loop is rare.
- **#495, `escape_teleport_landing_either` at 200,000 turns, pilot on c74a8155** (run 44726418111): 1 death in each arm, the same Mage; 17 of 18 games identical; no game passes CL9. **Bin: not tested.** It needs characters that carry Destruction or Teleport Level (saved-encounter suites, #184).
- **#501, the six flight fixes together on e8b3acfd** (pilot 44737523620; the 200 Ranger starts 44738419997; starts 1-360 44738432656, 44738444831):
  - Rangers 9 against 10 (1 / 2); all classes 5 against 6 (3 / 4), CL −0.09 ±0.09. **Bin: neutral on deaths, leaning slightly worse on progress.** As in #429, rescues on chosen death starts did not carry over to fresh starts.
  - Every death was re-recorded with its last screens ([report](https://claude.ai/artifact/SnqujSa3vHiJUebG9hLu87), borg-cemetery#86 and #87): 31 deaths in 22 games, 7 games byte-identical in both arms. 8 Rangers die at CL1 on DL1 with 58-80 arrows, the last attack melee in 6. The fixes don't reach this pattern, the largest group of early deaths.
- **Zoo infrastructure:** cells record their engine (#476); saved-encounter suites refuse builds on another engine, so Suite 1 can't run on main from 14ad671a on (#473). borg-reborn-rs worlds (`borg_world`) are generated per cell and recorded (#486).

**Results of 2026-11-20, evening (pilots and small tiers only; descriptive, RULES 14; every gate passed unless noted):**
- **#506, C's leash values on main ec0f3b28** (pilot 44769379993, re-pilot 44791716325; classes-18): the first pilot's `none` arm was config_error in 18 of 18 (`flow_leash_depth_margin -100`, bounds 0-127), the rest: loose 0 deaths (CL 6.17), margin0 CL 5.72, margin10 the same game as ctl in 14 of 18, tight 1. The re-pilot `none` = `{flow_leash_pickup_max_level: 0, flow_leash_stairs_max_level: 0}` against ctl: 1 death each (ctl the Druid 102023799; `none` a CL1 Mage on DL2, floating eye), 1 rescued / 1 newly killed, DL +0.22, 0 of 18 identical. A wash at 18 starts; a small tier of ctl, loose and none is the owner's call.
- **#507, Recall wait (#754) on PR #762 613f1ba5** (pilot 44779354512): one death in every arm, the same Druid. `esc` plays ctl's keys in 17 of 18 starts (not tested on this suite); `nox` and `both` fire in 8 starts and move CL and DL by hundredths. Nothing to separate; stop at the pilot unless a Recall-heavy suite is asked for.
- **#510, flight mode 3 (#757) on 50c23a5e:** pilot 44774313553 (10 arms): **gate failed for one cell**, `nodanger` Druid 934061548 froze at turn 65,803 (38,937 keys on one turn, gold unchanged); fixed upstream as borg-reborn-rs #775 (the town loop). `flight3` and `flight3r` rescued the one dead start with no one newly killed; `ranged`, `flee` and `hold` played ctl's keys in 18 of 18 (not tested alone). **Small tier** (ctl, flight3; starts 1-90; 44791789114): ctl 0 deaths, flight3 1 (Paladin 1584060551, poison, CL3), 15 of 90 identical, CL 5.90 against 6.00. **The pilot's rescue did not carry over.**
- **#511, attack categories, winning fights, safe flight Recall on 78b8f297** (pilot 44774352123; 5 arms): no arm leads on survival. attack-sight 2 deaths (1 / 2), winning-fight 1 (1 / 1, CL 5.67), recall-safe 2 (0 / 1, CL 5.72; 10 of 18 identical), all 2 (1 / 2; best CL 6.33 and DL 2.44) against ctl 1. The new deaths are a Rogue (poison), Mage (wild cat), Necromancer (grey mushroom patch), Ranger (crow, and Fang), Rogue (crow). **The death report waits for a new build** (owner, 2026-11-20: some of the deaths are caused by things borg-reborn-rs wants to change first).
- **#513, Phase Door first (#761) on 992e0351:** pilot 44774388022 (10 arms): nobody newly killed; `oil` CL 6.67 against 6.00, six arms rescued the one dead start, `ranger`, `floor` and `floorfirst` played ctl's keys in 15-16 of 18. **Small tier** (ctl, oil, phase; starts 1-90; 44791749875): ctl 0 deaths, `oil` 0 (CL 6.00, 9 of 90 identical), `phase` 2 (Ranger 129607500 and Priest 652511567, both CL1; CL 5.70, Ranger mean 4.9 against 5.8). **The pilot's `oil` lead did not carry over**, and `phase` newly killed two.
- **What the pilots and small tiers say together:** at 18 starts one dead start (Druid 102023799 in every arm of every pilot of this build family) carries every "rescued"; at 90 starts ctl had no deaths, so nothing could be rescued and the new arms can only add deaths. A pilot lead on CL (oil +0.67, flight3 rescue) was not reproduced. The pilot is a gate, not a result.
- **Parameters tested:** of the 2,229 `borg_param_*` settings in borg-reborn-rs main a04e5471, 102 have been varied in any zoo experiment and 37 in only one. Never: `power_` (774), `danger_` (256 of 257), `home_` (237), `sell_`, `wear_`, `item_`, `buy_`, `shopping_` (96), 209 of 258 `caution_`, 111 of 120 `escape_`, 38 of 42 `recover_`, 16 of 19 `prepared_`. The per-class `attack_preference_*` count is understated (the class sits in the name). The `prepared_` dive gates are the first calibration (#522).
- **PR #521's queued pilots finished:** see the results on #518 (dive gates),
  #520 (P6 compatibility), #516 (flight), #517 (Phase Door), #522
  (preparedness) and #524 (weighted routing).
- **Zoo infrastructure:** the #521 merge conflict led to premature dispatches
  (44808965870, 44809000599, 44809037298). See
  [the current dispatch and collection steps](../README.md#running-an-experiment).

## Results of 2026-11-20 and 2026-11-21

These are descriptive results on the named builds and cohorts. CL is
character level and DL is dungeon level. The issue reports include the
run links, arm counts, gates and provenance.

| Study | Result | Follow-up |
| --- | --- | --- |
| [#522](https://github.com/diegoami/borg-zoo/issues/522) Preparedness gates, `a04e5471` | At 100k, the small tier had 0/90 deaths for control and HP −25%, and 2/90 for HP +25%. Lower HP gates led slightly on progress there. At 200k the same Mage died in all seven pilot arms, and the progress lead did not repeat. | The Cure gates were scarcely exercised. |
| [#524](https://github.com/diegoami/borg-zoo/issues/524) Weighted flight, `4a2eade9` | Weight 5 changed all 90 small-tier games against mode 3, with 1 rescue, 2 newly killed and mean CL 0.20 lower. | No lead for medium on this build. |
| [#526](https://github.com/diegoami/borg-zoo/issues/526) Phase Door reserve, `d745d9fc` | Two arms rescued the control death without a new death in the 200k pilot. In the disjoint 72-start slice, control, reserve 1 at 200% and reserve 2 at 400% had 1, 2 and 1 deaths. All were at CL1. | The pilot survival lead did not carry over. |
| [#528](https://github.com/diegoami/borg-zoo/issues/528) Shipped fight/Recall bundle, `f827f844` | Both arms finished all 18 starts from the retained-600 manifest alive. Shipped changed every game, with mean CL +0.28 and DL +0.22 against explicit off. | Further tiers on that manifest are the owner's call. |
| [#529](https://github.com/diegoami/borg-zoo/issues/529) Attack on sight and winning fight, `c4163095` | Both on and both off had 0/18 deaths. Both on led by CL +0.50 and DL +0.28. Winning-fight off alone newly killed one Druid. CL10/CL20 list variants played identical keys throughout. | The list's level cap was unexercised. |
| [#530](https://github.com/diegoami/borg-zoo/issues/530) Breeder policy in the normal world, `c4163095` | All 90 games finished alive. Policies 0 and 2 reduced mean CL by 0.33 and 0.28 against 3. Policies 4 and 5 rarely diverged from 3 and had similar progress. | Survival is unresolved at pilot scale. |
| [#535](https://github.com/diegoami/borg-zoo/issues/535) Fight/Recall ablation, `d7e58cd` | The 200k small slice had 1/72, 3/72 and 2/72 deaths for all-off, winning-fight alone and all-on. Winning-fight alone newly killed the CL9 Warrior and CL12 Blackguard. Both replay hashes matched in the [death report notes](https://github.com/diegoami/borg-zoo/issues/535#issuecomment-7056305152). | The combined switches had no survival lead in this slice. |
| [#538](https://github.com/diegoami/borg-zoo/issues/538) Town hunt, `8e0f20af` | Hunt and combined had 0/18 deaths with modest progress gains. The two variants with winning-fight off each lost the same Ranger to Grip. | Count shopping loops from the retained logs before a mechanism claim. |
| [#543](https://github.com/diegoami/borg-zoo/issues/543) Shipped `2801ba18` verysmall | Both caps (100k and 300k) finished all 45 cells. The same Rogue died to Fang at CL2. The 300k run reached at most CL13. | The [death report link](https://github.com/diegoami/borg-zoo/issues/543#issuecomment-7054704108) records the hash-checked replay. |
| [#544](https://github.com/diegoami/borg-zoo/issues/544) Paladin HP gate, `2fdfd41c` | Both arms survived all 10 starts with identical play. | A case at the 45–49 max-HP gate is still needed. |
| [#546](https://github.com/diegoami/borg-zoo/issues/546) Dark entry detection, `cd0ed207` | All 20 starts per arm survived. Ten paired games diverged, with equal mean CL and DL −0.05 in the variant. | The retained cast, detection and rest traces still need review. |
| [#548](https://github.com/diegoami/borg-zoo/issues/548) Dogs and early killers, `2801ba18` | 107/108 cells reached 200k alive. The remaining cell was a configuration-blob race, fixed in [#561](https://github.com/diegoami/borg-zoo/pull/561). | The failed cell stays in the denominator. A repeat would be a new attempt. |
| [#549](https://github.com/diegoami/borg-zoo/issues/549) Low HP gate and Phase Door bundle, `2801ba18` | All 72 cells reached 200k alive. Each of the three variants had lower mean CL and DL than control. | No lead for a larger tier. |
| [#550](https://github.com/diegoami/borg-zoo/issues/550) Non-Ranger death bank, `2801ba18` | All 30 previously lethal starts reached 200k alive on the shipped settings. | Earlier deaths came from different builds and profiles. |
| [#556](https://github.com/diegoami/borg-zoo/issues/556) Fresh baseline | Both `fde8025a` and `d7e58cd` survived all 18 fresh starts. The newer build changed every game and reached DL5 in one. | Further tiers on this fresh block require the owner's gate. |
| [#557](https://github.com/diegoami/borg-zoo/issues/557) Unseen settings, `2801ba18` | All 108 cells survived. Reverting throw-first left all 18 keys streams identical. Removing unseen bump or separate oil, or flattening the Phase curve, reduced mean CL. | The requested `d7e58cd` lacked the unseen-bump settings. |
| [#558](https://github.com/diegoami/borg-zoo/issues/558) Flight ablation, `d7e58cd` | All 126 cells survived. Reverting threat weight or the fast-danger threshold changed play and raised mean CL in this pilot. The four other reversions matched shipped in 17–18 of 18 starts each. | The pilot could not rank survival. |
| [#563](https://github.com/diegoami/borg-zoo/issues/563) Recall reserve, `ae904090` | The [collection retry](https://github.com/diegoami/borg-zoo/actions/runs/44894144699/attempts/2) archived all 54 cells with zero missing and no deaths. Each higher reserve changed play in 6 of 18 starts. The pilot report found only 2, 3 and 4 Recall reads followed by a purchase before the next read in the three arms. | The pilot gate passed. Exposure to the refill policy was sparse. |
| [#566](https://github.com/diegoami/borg-zoo/issues/566) The deaths of shipped head `3b4924ba`, all 1,800 starts | 29 deaths against 33 on `fde8025a`; no start dies on both builds. Read one by one ([report](https://claude.ai/artifact/SPjLaJ4Z8BeBQp2qQr4BwF)): 7 fixable play (Phase Door under a no-teleport curse, resting by an invisible attacker, staying by a confuser), 7 kit (the restock rules ask for no cures or Phase Door at DL1–5; 15 of 29 die with no cures or no Phase Door, 13 of them with 10 gold or less), 15 matchup or luck (crows at CL1, floating eyes, paralysis traps). | borg-reborn-rs #829–#831, #837, #838, #840, #842; every death replays from borg-cemetery (#98, #100) |
| [#576](https://github.com/diegoami/borg-zoo/issues/576) `caution_ranged_vs_immobile` 2, `3b4924ba` | Pilot: no deaths. Big (starts 361–900): shipped 6, immobile2 10 (3 rescued / 7 newly killed, p 0.34), ΔCL −0.05 ±0.08; the shipped arm replays #566's big run game for game. 5 of the 7 new deaths are to immobile monsters (a cure held while confused, then a confused stairs walk; a step away undone by the next flow; an unseen floating eye). **Leaning worse, as on 5af2f79f (#461): keep 0.** | borg-reborn-rs #837 (the gaps), #838 (a ranged-only list); borg-cemetery #101 |

Related checks: [#520](https://github.com/diegoami/borg-zoo/issues/520)
matched the exact native full45 builds in all 45 paired games.
[#539](https://github.com/diegoami/borg-zoo/issues/539) exercised the resolved
settings receipt in a 36-cell pilot. [#545](https://github.com/diegoami/borg-zoo/pull/545)
defined the #543 run, and [#547](https://github.com/diegoami/borg-zoo/pull/547)
kept imported manifests from shifting generated suites.
All five [#566](https://github.com/diegoami/borg-zoo/issues/566) shipped-head
slices are archived. The [collection retry](https://github.com/diegoami/borg-zoo/actions/runs/44894181893/attempts/2)
published the 45 verysmall starts under `44894181893-2`. The five archives
contain 1,800 distinct starts, 29 deaths and 1,771 turn caps, with zero missing
cells in each attempt.


## Historical findings and open questions

- **Pinned elsewhere:** borg-agent still pins better-borg-c M6 for its bridge (diegoami/borg-agent `pins.json`).
- **Mode cutoff restart (borg-zoo#54, 2026-11-10):** existing results were polluted by the
  `borg_munchkin_by_class` default drift, so the zoo moved to explicit mode profiles (`normal`,
  `munchkin-class`, `munchkin-on`, `lunal`), a new specimen and harness pin (`4.2.6-bbc-9ca98661`:
  patch units 0100 stair escape, 0101 + correction 0101a Lunal take gated on the runtime mode),
  pre-cutoff labelling and straddling-comparison exclusion. The restarted class grid is
  [`classes-explicit`](../experiments/classes-explicit.json) (munchkin-class against normal on the new
  specimen); the acceptance smoke is
  [`bbc-explicit-smoke`](../smoke/bbc-explicit-smoke.json).
- **The acceptance smoke reproduced cleanly.** Run 42842197246, `bbc-explicit-smoke`,
  4.2.6-bbc-9ca98661, 3 fixed Warrior seeds × {`munchkin-class`, `normal`}: 6/6 finished at the
  cap, no config_error, no stall. `munchkin-class` reached DL6 on every seed (the class rule's
  munchkin start at depth 6, working as the product default); `normal` stayed at DL1-2 (modes off).
  Its first dispatch (run 42841000338) config_errored every munchkin-class cell because the profile
  also named `borg_munchkin_start = FALSE`, which the class rule overrides for WDR classes - the
  profile now names only `borg_munchkin_by_class`, a plan-time guard rejects the contradictory
  shape, and the play hashes of both runs match move for move: the games were the product default
  all along, only the settings check objected.
- **The milestones' apparent survival gain is the munchkin policy, not the code (2026-11-10).**
  Read under one policy and one cap — the munchkin start for Warrior, Druid and Ranger
  (`munchkin-wdr`), 100,000 turns — plain Angband 4.2.6 loses 34.4% of its runs, Angband 4.2.6 +
  munchkin 28.4% (`munchkin-by-class-confirm`, 1,799 cells), better-borg-c M8 27.5% and borg-rs M8
  27.5% (`classes-m8-munchkin`). The three munchkin arms are within one point of each other, so the
  full runs recorded so far give no measurable code gain over vanilla with the same policy.
  The milestones' shipped *defaults* look better than the pre-cutoff baseline (M10 25.5%, M9 26.3%
  against 34.4%) because from better-borg-c `fd683ced` the default **is** the class rule: the
  observer records `borg_munchkin_start = 1, borg_munchkin_depth = 6` for Warrior/Druid/Ranger and
  `0, 16` for the other six on M10 (`classes-m9-m10`), while 4.2.6 records `0, 16` everywhere.
  Only those three classes differ: in `munchkin-by-class-confirm` the six other classes play
  byte-identically (200 of 200 seeds each), Warrior differs on 197 of 200, Ranger 194, Druid 170
  (1,239 of 1,800 paired cells identical overall). So a "default" arm on M8 and later is a
  mixed-class configuration, and pairing it with a pre-cutoff default compares the munchkin policy,
  not the Borg. What is still owed is a `normal`-policy class grid on 4.2.6, M10 and rs-M8 — the
  cleaner version of the arm borg-zoo#54 asked for.
- **v11 is catalogued, and its smoke is clean.** `4.2.6-bbc-m11` is tag `4.2.6-impact-v11`
  (`39268ca8a`) with **116** carried fixes, up from 98: 17 new units (0100–0117) plus the 0101a
  correction that gates the Lunal take skip on the runtime munchkin mode, covering stair-escape
  ordering, flow-kill per-monster state, the danger model (armour/to-hit, constitution drain,
  Crush, granite), pickup from the nearest staircase, the rest-after-prep timer and preparedness
  reason, and the home/shop flows. Its own matrix is green: 95 groups / 290 cases, no failed
  group, 237/250 compared cases byte-identical (the 13 differences are six fixture groups that
  predate the cycle plus `preparation`, where 0105's wider timer prints a different value with
  identical decisions). [`m11-smoke`](../smoke/m11-smoke.json), run 42879898811, compared
  M10 and M11 under `munchkin-class` and `normal`: 12/12 cells finished at the cap, no
  config_error, no stall, both builds compiled from the tag. v11 measured **no per-mode arm** — it
  records each unit's per-mode effect as *not measured*, not neutral — so this is a build sanity
  check, not a result; the per-mode batch stays with
  [`classes-explicit`](../experiments/classes-explicit.json).
- **The first Lunal arm is deferred.** `borg_self_lunal` enters Lunal only when the Borg is prepared
  for 15 levels deeper and `maxdepth >= depth + 15` (`borg-think-dungeon.c`); no zoo suite reaches
  that reliably (the deepest cap is 400k turns, and the zoo has no deep-start mechanism — the
  runner's `load` hook has no suite field). An arm that never enters the mode would read as neutral,
  the exact failure borg-zoo#54 fixes. Define it when better-borg-c exposes a deep start the harness
  can drive (DESIGN.md, open question 10).
- **M9 vs M10 on the standard 100,000-turn suite: superseded by the mode cutoff.**
  [`classes-m9-m10`](../experiments/classes-m9-m10.json), run 42816432188 (dispatched
  2026-11-10), compared the pre-rule original against post-rule M9/M10 under one profile name, so
  its cross-version pairings straddle better-borg-c `fd683ced` and are no longer computed; the run
  stays on the results branch, labelled pre-cutoff. At smoke scale (3 seeds,
  `m9-m10-munchkin-smoke`), M9 and M10 diverge within one specimen: seed 11 ends at a different
  depth/level/HP (M10's local improvements shift an extra Borg-RNG draw there, as better-borg-c's
  own M10 review doc already reported), and seeds 29/47 keep the same final state but a different
  play hash — that comparison is same-version and still valid. The M9-vs-M10 question at
  classes scale returns as [`m10-smoke`](../smoke/m10-smoke.json), restarted on the explicit
  profiles (munchkin-class, normal).

- **Joint shopping/trip candidate did not reduce deaths in the fresh-seed confirmation.**
  [`rs-joint-m12-confirm`](https://diegoami.github.io/borg-zoo/runs/rs-joint-m12-confirm/43643769983-1/index.html)
  finished all 5,400 games: 530/1,800 deaths with the existing rules,
  586/1,800 with the new shopper and trip policy at ordinary provisioning,
  and 559/1,800 with the fixed 2x-risk supply forecast. The prespecified
  candidate-versus-control pairing rescued 312 characters and newly killed
  341 (exact two-sided McNemar p=0.2732). This does not support adopting
  the candidate for fewer deaths. All arms use pinned borg-rs `d9a56f4`,
  with the original limited object coverage; subsequent coverage fixes are
  not tested by these results. The report now explains each arm directly,
  alongside means including dead characters and the detailed statistics.

- **Post-fix Neo seeded-v2 measurements (2026-11-15):** the18-game100000-tick
  acceptance retained10deaths,7wall timeouts and1tunnel stall. Partial traces
  show live advancement before the120-second watchdog; a separate600-second
  repeat finishes both Warrior cases normally (one death65338, one cap100000).
  The [measurement receipts](neo-merged-seeded-v2/README.md) preserve both runs
  and the exact-command-prefix control. The fresh1800-game cohort43670231534
  is dispatched with the calibrated budget. Its results are pending; no C parity
  or survival improvement follows from these acceptance counts.

- **Neo measurement host correction (2026-11-14):** smoke43615649575
  measured candidate9c17cb0 with a message-deaf headless host: it recorded
  attack text but supplied no GameEvents bus or API2 message subscription.
  The retained Human Mage1548306106 rests through invisible touches and dies
  at7248; exact command-hash replay and host-event controls confirm the cause
  of the missing fear input. See port-tracker#92/#93 and borg-zoo#89. The
  historical run remains unchanged; its deaths do not establish faithful
  browser behavior. Corrected acceptance/full runs use specimen
  neo-fork-9c17cb0-events, Borg9c17cb0, toolkit02c33cf and engine06a2321c.
  No survival improvement is inferred from these cross-host comparisons.

- **Corrected Neo cohort completed (2026-11-14):**
  [run43617859717](https://github.com/diegoami/borg-zoo/actions/runs/43617859717),
  Borg9c17cb0/toolkit02c33cf/engine06a2321c, has all1,800 cells:
  **1,352 deaths,415 caps,32 stalls,one wall timeout**. Deaths are75.11%
  of assigned cells,76.51% of the1,767 death/cap endpoints; the33 abnormal
  outcomes remain counted separately. Of deaths,1,099 occur at levels1–2;
  Grip/Fang account for273. This is a descriptive single arm, not a
  confirmed improvement over the older message-deaf run or native C.
  [Death triage, class/cause tables, pins and reproducer](../reports/neo-9c17cb0-events-43617859717/README.md)
  distinguish the existing C danger-cache defect from a confirmed engine
  blindness-refresh ordering defect, cancelled Remove Curse prompts and an
  alternating-direction tunnel timeout. Eye/mushroom/mold deaths replay
  exactly; several approach/perception causes remain unresolved. No source
  behavior was changed by this analysis.

- **Shared-seed startup correction (2026-11-15):** eleven bounded C/Neo pairs
  now match initial stats/HP/SP, exact gear/gold, all town terrain, the active
  game RNG pool/index and Borg startup seed. This needs native-menu birth
  sequencing, two separately proposed engine list-order corrections, and an
  explicit GCC14.2 coordinate-evaluation adapter. See the
  [v2 continuation report](../reports/c-neo-seed-continuation-v2/README.md).
  Same integer seeds are usable; later game trajectories are not yet shown
  equivalent. This is not a new survival estimate or a dispatched large cohort.


- **Neo truth-corrected seeded-v2 cohort completed (2026-11-16).**
  [Run 43702732056](https://diegoami.github.io/borg-zoo/runs/neo-truth-100-seeded-v2-1800/43702732056-1/index.html),
  1,800 assigned-birth starts, 100,000 ticks, 600-second watchdog, Borg and
  toolkit pinned together to `967b28f5fe12c4974a6a793040f73246eb7d1200` with
  engine `b4af703`: 989 deaths, 732 turn-cap finishes, 75 stalls and 4 wall
  timeouts, so 989/1,721 = 57.5% of finished games died, with median level 3
  and median depth 2.
  - The earlier cohort [43670231534](https://github.com/diegoami/borg-zoo/actions/runs/43670231534)
    is kept as an immutable historical run: it was built at Borg `76f25aa`
    before the merged danger/HP/retreat repairs, and its headless host denied
    monster truth reads. Its 64.9% death rate is **not** a repaired-Borg
    baseline, and the two runs are separate measurements, not a paired
    comparison.
  - The truth fix is visible in the causes: deaths now include monsters that
    could not attack at all under the truth-denied host.
  - Descriptive only. No C parity claim, no population-improvement claim, and
    the unresolved engine clock issue (neo-angband-tracker#640) still applies.

- **Neo books-509 seeded-v2 cohort completed (2026-11-16).**
  [Run 43759670685](https://github.com/diegoami/borg-zoo/runs/neo-books-509-seeded-v2-1800/43759670685-1/index.html),
  1,800 assigned-birth starts: 860 deaths, 843 turn-cap finishes, 95 stalls
  and 2 wall timeouts, so 50.5% of finished games died, median level 3 and
  median depth 2. The carried-book value correction is a separate arm from
  the truth-corrected cohort above; PR #121 proposes a further repeat with
  only that correction.

- **PR85 return-threshold development grid completed (2026-11-15).**
  [Run 43720870587](https://diegoami.github.io/borg-zoo/runs/rs-pr85-full/43720870587-1/index.html)
  retained all 10,800 endpoints on `classes-1800-d`: six choices on the same
  1,800 assignments at the 100,000-turn after-key cap, pinned borg-rs
  `71cff24ef45731e55aa9687930cd2d766dd0695e`. There were no stalls, wall
  timeouts, harness failures or configuration errors in the collected cells.

  | Choice | Deaths / 1,800 | Alive at cap |
  | --- | ---: | ---: |
  | Existing shopping and returns | 535 | 1,265 |
  | New shopping, legacy returns | 385 | 1,415 |
  | Full pack; learning returns disabled (0,0) | 487 | 1,313 |
  | One free slot; two eligible unknown stacks (1,2) | 435 | 1,365 |
  | One free slot; four eligible unknown stacks (1,4) | 471 | 1,329 |
  | Two free slots; four eligible unknown stacks (2,4) | 471 | 1,329 |

  These are descriptive development counts, not a confirmed winner or an
  adoption decision. The equal totals for (1,4) and (2,4) do not by themselves
  establish identical play. Pairings, class differences, purchases and return
  diagnostics belong to the linked report; a subsequent fresh-seed,
  prespecified confirmation is required for an improvement claim.

- **Neo truth-corrected cohort and book omission (2026-11-15):**
  [Run43702732056](https://github.com/diegoami/borg-zoo/actions/runs/43702732056)
  completed all1800cells:989deaths,732caps,75stalls,4wall timeouts. Deaths are
  57.47%of death/cap endpoints,54.94%of assigned lives. Raw caster traces show
  early starting-book stashing across several classes, including109/200Priests
  and200/200Mages/Necromancers. [The report and repeat protocol](../reports/neo-books-509/README.md)
  separates later potentially legitimate stashes from the confirmed missing
  carried-book count/value (central Neo509, mod PR113). Owner authorized a
  repeat on the previous967b28fbaseline with only that correction, after
  separate smoke acceptance. No new survival result or improvement claim yet.

  Book-fix smoke [43759325350](https://github.com/diegoami/borg-zoo/actions/runs/43759325350)
  passed18cases at5000ticks:15caps/3deaths, all16casters kept their starting
  book and none stashed it. Actual settings/options/truth and raw hashes pass.
  These are acceptance controls, not a survival estimate. The authorized full
  repeat [43759670685](https://github.com/diegoami/borg-zoo/actions/runs/43759670685)
  is now dispatched; its1800-game results remain pending.

- **The M12/M13 explicit-mode grid produced no usable cells.**
  Run 43703176769 collected all 7,200 cells as `harness_failure` with
  `error: no record collected (job failed or was cancelled)`. The plan and
  build jobs succeeded. All 8 run shards were cancelled at exactly 5 hours,
  the run job's `timeout-minutes: 300` (`.github/workflows/compare.yml`),
  before any of them wrote records: the grid was too large for 8 shards, not
  broken. Nothing about M12 versus M13 can be read from this run; it is a
  harness failure, not a result. See [OPEN-WORK.md](OPEN-WORK.md).

- **The borg-reborn-rs option-C pilot: the ladder errand looks better, on
  one development suite.**
  [`reborn-pilot-c-classes-1800`](https://diegoami.github.io/borg-zoo/runs/reborn-pilot-c-classes-1800/43702957409-1/index.html),
  run 43702957409, 3,600 games on `classes-1800`, borg-reborn-rs at the
  option-C pilot pin: borg-rs's core without an errand died in 524/1,800
  (29.1%), the same core with `borg_reborn_errand = ladder` in 448/1,800
  (24.9%), paired 338 rescued against 262 newly killed. Median final level
  (4) and median deepest level (2) were the same in both arms.
  - Descriptive on one development suite: no confirmation suite has been run,
    so this is a lead, not a finding.
  - The source contract is in borg-reborn-rs#227, whose first review round
    found three blocking defects in the errand shell (leave hooks advancing
    the plan prematurely, bypassing the core's readiness and return-home
    decisions, and reporting restocking as success) and whose re-review found
    three more blocking ones (`/explored` and `/stall` not completing levels,
    downward travel still forcing an unprepared level, and restocking and
    selling being misread as fear). All were fixed, but findings 5–7 and the
    `/explored`/`/stall` firing in play were never verified in play.

- **The errands plan × M13 shopping pilot ran cleanly (borg-zoo#123).**
  `reborn-plan-m13-classes-18`, run 43845673921, 72 games on `classes-18`,
  specimen `4.2.6-reborn-rust-plan-m13` (borg-reborn-rs `2f74e1c5`, without
  the #355 survival fix). It passed its prespecified checks: every cell
  ended in `death` or `turn_cap`, none was `config_error` or needed a rerun,
  and all 36 plan cells recorded plan sha256 `922372ba…`. No cell ended
  `borg_stopped`. Deaths per 18: control 9, shop 4, plan 4, plan-shop 5.
  Mean final level was 3.8–4.5 and mean deepest level 1.8–2.6.
  - A plumbing check, not a measurement: 18 games per arm say nothing about
    effects.
  - The largest key count was 19,028 (plan-shop). Nothing like the 69,838
    keys of the oil store/take loop (borg-rs#90), which the zoo still does
    not detect.

- **The five-arm pilot ran cleanly, and confirms the two specimens play the
  same game (borg-zoo#123).** `reborn-plans-m13-classes-18`, run
  43851628610, 90 games on `classes-18`, specimen
  `4.2.6-reborn-rust-plans-m13` (borg-reborn-rs `1c4b351b`, without #355
  and still with the borg-rs#90 loop).
  - Every cell ended in `death` or `turn_cap`. None was `config_error`,
    stalled or a key outlier, and none needs a rerun.
  - The loaded-plan copies matched their pins: `922372ba…` in the plan arms,
    `9d7d8a39…` in ambitious-shop, and none in the no-plan arms.
  - The busiest single turn of any cell had 383 keys, far below the
    1,000-key loop threshold.
  - The four arms it shares with the four-arm pilot (run 43845673921,
    `2f74e1c5`) played identical keys in all 72 cells.
  - Ambitious-shop died in 5 of 18 games, with mean final level 4.4 and mean
    deepest level 2.3.
  - A plumbing check, not a measurement. Its shop arms predate the
    borg-rs#90 fix and are not comparable with the development study's.

- **Neo parity-and-books candidate accepted at smoke scale (2026-11-16).**
  [Smoke43861787363](https://github.com/diegoami/borg-zoo/actions/runs/43861787363)
  records18/18 exact5000-tick caps with no abnormal endpoints, all18dungeon
  entries,16/16caster starting books retained and all108raw-file receipts verified.
  Borg1.4.0-beta.6.zoo.1 /464a155, beta.4 engined27ed50f and toolkit638979d.
  The first smoke failed at packaging before games; the corrected toolkit's
  SDK alias fix preserves runtime-host bytes. [Protocol and acceptance](../reports/neo-parity-books-v1/README.md).
  This does not establish survival improvement or complete class/spell fidelity.

- **The 3×3 trip-policy pilot found a new frozen-turn livelock (borg-zoo#123).**
  `reborn-trip-3x3-classes-18`, run 43863985583, 162 games on
  `4.2.6-reborn-rust-plans-m13-fix90` (borg-reborn-rs `8a0b57c8`: borg-rs#92's
  Home guard and #88's additive trip policy). Plan (none, errand, ambitious)
  × (default, town planner, town planner + trip (2,4)).
  - Plumbing was clean: no `config_error`, and the loaded plans matched their pins.
  - The trip policy barely changed play. Planner-only and planner + trip
    played identical keys in 42 of 54 paired games. Deaths per 18 were 5 v 5
    (no plan), 3 v 3 (errand) and 3 v 4 (ambitious). Too small to say whether
    the trip policy helps; the development study keeps it off.
  - Half-Elf Warrior seed 1019921749 stalls with the ambitious plan and the
    town planner, with the trip policy on or off: 79,397 keys and 22
    frozen-turn bursts. At the frozen turns the Borg crosses the DL0/DL1
    stairs with no game time passing. The plan's town override ("loop town
    overrides the loop, target DL0") alternates with the core's "Fleeing
    level … Leaving via up stairs". Reported as borg-reborn-rs#421.

- **Small tier of the #123 development study: gate passed.**
  `reborn-plan-m13-small`, run 43868362767, 450 games: starts 1–90 of
  `classes-1800` (10 per class) × five arms on `8a0b57c8`, with the trip
  policy off everywhere.

  | Arm | Deaths / 90 | Stalled | Mean final level | Mean deepest level | DL5+ |
  | --- | ---: | ---: | ---: | ---: | ---: |
  | control | 22 | 0 | 4.4 | 2.5 | 9 |
  | town | 15 | 0 | 5.0 | 2.5 | 7 |
  | plan | 24 | 0 | 3.8 | 2.0 | 3 |
  | plan-town | 23 | 0 | 4.2 | 2.1 | 5 |
  | ambitious-town | 29 | 2 | 4.2 | 2.2 | 3 |

  - Gate: no `config_error`; one binary; every loaded-plan copy matched its
    pin, and none appeared in the no-plan arms.
  - The two stalls are both ambitious-town and both the borg-reborn-rs#421
    stair livelock, reproduced locally. Half-Troll Rogue 926210318 had 2
    bursts, the largest 1,098 keys. Half-Orc Rogue 1269315224 had 9 bursts,
    the largest 8,992, and 51,937 keys (5 times its arm's median).
  - Paired against control: town rescued 17, newly killed 10; plan 14 / 16;
    plan-town 16 / 17; ambitious-town 15 / 22. Ambitious-town against
    plan-town: 5 / 11.
  - Timing: about 14 s of wall time per game. The shards took 6–9 minutes
    for about 112 games each.
  - Descriptive only, at 10 starts per class.

- **The #123 small tier repeated with the #423 survival fixes: gate passed (borg-zoo#138).**
  `reborn-survival-small`, run 43874782892, 450 games on
  `4.2.6-reborn-rust-plans-m13-survival` (borg-reborn-rs `4ecb93d7`: flee
  healing #369 and Phase Door stock #380). The same 90 starts and five arms
  as `reborn-plan-m13-small`, trip policy off. It is a different game in every
  arm, control included, so the two runs are compared start by start and not
  pooled.

  | Arm | Deaths / 90 (on `8a0b57c8`) | Stalled | Mean final level | Mean deepest level | DL5+ | vs control rescued / newly killed | vs `8a0b57c8` rescued / newly killed |
  | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
  | control | 21 (22) | 0 | 4.5 | 2.6 | 8 | – | 9 / 8 |
  | town | 17 (15) | 0 | 4.9 | 2.6 | 10 | 16 / 12 | 6 / 8 |
  | plan | 25 (24) | 0 | 3.8 | 1.8 | 0 | 14 / 18 | 5 / 6 |
  | plan-town | 18 (23) | 0 | 4.3 | 2.1 | 3 | 13 / 10 | 10 / 5 |
  | ambitious-town | 23 (29) | 1 | 4.4 | 2.4 | 5 | 11 / 13 | 13 / 7 |

  - Gate: no `config_error`; one binary; loaded plans matched their pins, and
    none appeared in the no-plan arms.
  - The one stall is the same borg-reborn-rs#421 livelock as before: Half-Troll
    Rogue 926210318, with identical bursts.
  - Deaths fell from 113 to 104 over the five arms. The largest drops are
    plan-town (23 to 18; caster deaths 18 to 12) and ambitious-town (29 to 23).
  - Descriptive only, at 10 starts per class. Medium waits for the owner.

- **The borg-reborn-rs#421 fix removes the stair livelock: small tier passed (borg-zoo#141).**
  `reborn-livelock-small`, run 43882239507, 450 games on
  `4.2.6-reborn-rust-plans-m13-livelock` (borg-reborn-rs `d3ebe3c0`, #428: the
  #421 fix on top of `4ecb93d7`). The same 90 starts and five arms as
  `reborn-survival-small`.

  | Arm | Deaths / 90 (on `4ecb93d7`) | Stalled (on `4ecb93d7`) | Mean final level | Mean deepest level | DL5+ | Identical keys to `4ecb93d7` | vs `4ecb93d7` rescued / newly killed |
  | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
  | control | 21 (21) | 0 (0) | 4.5 | 2.6 | 8 | 90 / 90 | 0 / 0 |
  | town | 17 (17) | 0 (0) | 4.9 | 2.6 | 10 | 90 / 90 | 0 / 0 |
  | plan | 22 (25) | 0 (0) | 3.7 | 1.8 | 0 | 76 / 90 | 3 / 0 |
  | plan-town | 20 (18) | 0 (0) | 4.3 | 2.2 | 4 | 65 / 90 | 2 / 4 |
  | ambitious-town | 17 (23) | 0 (1) | 4.4 | 2.0 | 2 | 42 / 90 | 9 / 3 |

  - Every #141 criterion holds:
    - no frozen-turn stall and no key outlier in any arm; the busiest single
      turn was 752 keys, against a 1,000-key threshold;
    - control and town play keys identical to `4ecb93d7` in all 90 starts each;
    - no `config_error`; one binary; every loaded plan matched its pin.
  - Ambitious-town fell from 23 deaths to 17.
  - Descriptive only, at 10 starts per class. Medium waits for the owner.

## Correction: purchase bursts were counted as stalls (borg-zoo#205, 2026-11-17)

Until #205 the frozen-turn check called any game turn with 1,000+ keys a
stall, and named borg-rs#90 and borg-reborn-rs#421 (fixed by #428) whatever
the cause. A Ranger buying a stack of ammunition one copy per transaction
also passes 1,000 keys: shop transactions take no game time. The check now
reads the state log at the burst turn. When gold falls at least once per 25
keys, the burst is shopping: it is flagged `purchase_burst` and the outcome
is kept. Only a burst with no purchases is a stall.

These published cells are `stalled` on the results branch, which is
append-only, but were purchase bursts. Each was replayed with the fix and
its keys were identical to CI:

| Run | Experiment | Cell | Burst | Actual outcome |
| --- | --- | --- | --- | --- |
| 44117547473 | reborn-pb-class-pilot (#198) | pb1, Dwarf Ranger 807773433 | 1,085 keys, 120 purchases, turn 86,658 | turn_cap |
| 44117547473 | reborn-pb-class-pilot (#198) | pb3, Half-Troll Ranger 60792140 | 1,083 keys, 120 purchases, turn 92,602 | turn_cap |
| 44117547473 | reborn-pb-class-pilot (#198) | pb4, Half-Troll Ranger 60792140 | 1,083 keys, 120 purchases, turn 92,602 | turn_cap |
| 44072424588 | reborn-main-defaults-medium (#181) | Dwarf Ranger 745617169 | 1,084 keys, 120 purchases, turn 60,106 | turn_cap |
| 44055270651 | reborn-unknown-stacks-small (#170) | unknown3, Half-Orc Ranger 1071405808 | 1,085 keys, 120 purchases, turn 75,918, gold 167 → 42 (replayed, keys identical to CI) | turn_cap |

These cells of reborn-heal-curve-medium (run 44131024789, dispatched before
#207 merged) are purchase bursts too, replayed with the fix, keys identical
to CI, all reaching the turn cap: r0-c100 Ranger 801109004 (1,094 keys, 121
purchases), r0-c200 Ranger 154156985 (1,094, 121), r200-c50 Ranger 810310797
(1,085, 120), r200-c100 Ranger 1024472395 (1,004, 111), r200-c200 Ranger
956258985 (1,094, 121), r400-c50 Ranger 810310797 (1,049, 116), r400-c200
Rangers 1222599014 (1,093, 121) and 1256116424 (1,121, 124).


## Town planner healing curve scale × reserve, speed 66 (borg-zoo#192, 2026-11-17)

borg-reborn-rs e0aa2e0a (shipped defaults, no plan), healing speed 66, reserve
0/200/400 × curve scale 50/100/200; pilot (run 44125061301), then small and
medium together (runs 44131018812, 44131024789): starts 1-360, 3,240 games,
no config_error, 284 deaths, all reproduced in the cemetery. The c100 arms
replay the speed-66 small tier's keys on all 270 shared games.

| reserve \ curve | 50 | 100 | 200 |
|---|---|---|---|
| 0 | 28 | 36 (control) | 31 |
| 200 | 32 | 35 | 31 |
| 400 | 28 | 38 (shipped) | 25 |

Deaths of 360. The shipped r400-c100 has the most deaths; curve 100 is the
worst curve at every reserve. Best: r400-c200, against r400-c100 +29 rescued
/ -16 newly killed, exact McNemar p = 0.07; nothing reaches p < 0.05 over 16
comparisons. Mean level and depth are flat across arms. A lead for a
prespecified confirmation (RULES 8), not a result.

The borg-reborn-rs side, buying a planned purchase's copies in one
transaction, is borg-reborn-rs#507 (PR #509).
