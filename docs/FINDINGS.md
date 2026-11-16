# Findings

What the zoo's completed experiments have shown, with the run behind each.

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
