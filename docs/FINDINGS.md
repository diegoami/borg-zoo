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

- **PR #28:** the owner's bounded analysis of `originals-20261108-classes-1800`. It's open, and merging it is the owner's call.
  - Its branch also carries the `.gitignore` exception `!reports/**/*.tgz`.
  - Until #28 is merged, main still ignores `*.tgz`, so any report attachment needs `git add -f` or that exception.
  - Its `selected-raw-traces.tgz` was rebuilt from the run's artifacts. See that report's `selected-raw-traces.json`.
- **Issue #30:** measuring borg-reborn-rs, opened by another session.
- **Pinned elsewhere:** borg-agent still pins better-borg-c M6 for its bridge (diegoami/borg-agent `pins.json`).
