# Findings

What the zoo's completed experiments have shown, with the run behind each.
Every figure is from the run's `cells.jsonl` on the `results` branch. Deaths
are before the suite's cap (100,000 game turns unless stated), out of the runs
that finished; runs that stalled, timed out or failed are excluded, never
counted as deaths. "Paired" figures count the seeds where only one arm died:
*rescued* means only the control died, *newly killed* means only the arm died,
and p is an exact two-sided McNemar test. `classes-1800` is a development suite,
so results on it are descriptive. A confirmation needs a prespecified
experiment on fresh seeds (`classes-1800-b`, `warriors-600`).

Update this file when an experiment finishes: add its finding, and edit or
remove any line it overturns.

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

## Open

- **Pinned elsewhere:** borg-agent still pins better-borg-c M6 for its bridge (diegoami/borg-agent `pins.json`).
- **Mode cutoff restart (borg-zoo#54, 2026-11-10):** existing results were polluted by the
  `borg_munchkin_by_class` default drift, so the zoo moved to explicit mode profiles (`normal`,
  `munchkin-class`, `munchkin-on`, `lunal`), a new specimen and harness pin (`4.2.6-bbc-9ca98661`:
  patch units 0100 stair escape, 0101 + correction 0101a Lunal take gated on the runtime mode),
  pre-cutoff labelling and straddling-comparison exclusion. The restarted class grid is
  [`classes-explicit`](../experiments/classes-explicit.json) (munchkin-class against normal on the new
  specimen); the acceptance smoke is
  [`bbc-explicit-smoke`](../experiments/bbc-explicit-smoke.json).
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
  classes scale returns as [`m10-smoke`](../experiments/m10-smoke.json), restarted on the explicit
  profiles (munchkin-class, normal).
