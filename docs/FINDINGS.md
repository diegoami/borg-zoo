# Findings

What the zoo's completed experiments have shown, with the run behind each.

**Balanced999 saved encounters (#168):** [full paired experiment](../reports/saved-encounters/balanced999-incidents/full-44058010288/README.md)
completed1998/1998 valid cells,111 scenarios per class in each setup. Baseline
reborn had528 deaths/471 finite-horizon survivals; the exact Zoo speed30 bundle
had291/708. Paired315 rescued and78 newly killed;213 both died and393 both
survived. Both compiled builds were reused across nonoverlapping balanced tiers.
Sources, controllers and complete configurations differ; this is descriptive
regression evidence on an incident-selected bank. Population and isolated
speed30 claims need separate studies. Dashboard data are archived; UI PR179
awaits the explicit merge approval required by automatic approval review.

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
