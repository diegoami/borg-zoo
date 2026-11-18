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

**Closed questions (2026-11-18): four switches that showed nothing at their largest tier.** Each is closed in its issue; the shipped value stands, and no next tier is proposed:
- **#235, the #539 flight switches at full (run 44216738125, 7,200 games on 9ecbfd1e):** control 142/1,800 deaths; phase+ranged 133/1,799 (rescued 68, newly killed 60, p 0.54), stairs+ranged 133/1,799 (74/66, p 0.55), all three 147/1,799 (83/89, p 0.70). One unfinished cell per switch arm. No combination differs from the control.
- **#240, the #544 breeder exit at distance 4/6/10 (small + medium, runs 44220465377 and 44220469487, starts 1-360 on 156c8e52):** control 28/360; d4 27, d6 29, d10 28, with 4-6 rescued and 4-6 newly killed per arm (p 1) and 265-277 of 360 games identical to the control. The exit rarely changes a game.
- **#246, the #549 stair-scum threat flag (small + medium + big, runs 44238199598, 44238075961 and 44245072671, starts 1-900 on d9ff9808):** 68/900 against 67/900 with the flag, 4 rescued and 3 newly killed (p 1), 763 of 900 games identical. Main ships the flag on (fba1c6e0); the evidence does not distinguish on from off.
- **#248 / #170, borg_trip_unknown_stacks:** see the entries above. 2-5 do not differ in deaths over 1,800 starts. Main ships 2 (fba1c6e0); borg-reborn-rs's notes trace one Blackguard death to that value, a single game.

**#279, the borg_worships_* equipment switches on main 92fafc61 (pilot, run 44308259323, 108 games): damage, speed, hp and mana never change a game; ac changes every game.** The gate passed: no config_error, each switch written TRUE in its arm's borg.txt, every game at the turn cap (no deaths in any arm). Damage, speed, hp and mana worship play the control's keys in 18 of 18 games, as the C Borg's switches-early found for speed, hp and damage. Their bonuses never change an equipment choice at this cap, so these four are dropped rather than grown. AC worship changes all 18 games, with no deaths and a lower mean max level (5.17 against 5.44). borg_worships_gold was left out (owner): with borg_town_plan = 1 the live planner replaces the C seller, so the unidentified-item selling it allows never runs.

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

## Open

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

The borg-reborn-rs side, buying a planned purchase's copies in one
transaction, is borg-reborn-rs#507 (PR #509).
