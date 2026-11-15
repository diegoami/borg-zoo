# Neo carried-book correction509: repeat protocol

Owner authorized repeating the completed1800-game experiment after fixing the spellbook omission. Source proposal: [upstream113](https://github.com/neostryder/neo-angband-mod-borg/pull/113), canonical [issue509](https://github.com/neostryder/neo-angband/issues/509).

The new measurement snapshot is `d6215a8e63d101e0c6d392120fb8eacef9544480`, built from previous measured `967b28f5fe12c4974a6a793040f73246eb7d1200` plus the source correction from `c46849aa5c90b8f8c43f3f0f4b9c94086f3293e1`. Its runtime diff is limited to carried-book counts, quality metadata and power; its plugin is rebuilt. The15regressions bring the required test count1194→1209. Harness files remain byte-identical to967b28f. This snapshot intentionally excludes later upstream/fork gameplay and recorder changes so the repeat does not mix them into the book correction.

Engine remains `b4af703493d314aa35cb719604f06103aa4918f4`; toolkit remains967b28f. The full experiment reuses frozen `neo-seeded-v2-classes-1800`:200starts/class,100000exact engine ticks,600seconds/game,36shards,four concurrent jobs,two processes/job. Explicit C point-buy/no-selling/native-menu startup and GCC coordinate adapter remain unchanged. Clock640 and other known perception/API/port limitations remain unresolved. Existing results are append-only.

Before the full dispatch, the separate new18-case smoke (two starts/class,5000ticks,600seconds) must finish. Inspect every cell, actual source/engine/toolkit/settings and durable truth receipt, all abnormal endpoints, and book retention/cast behavior. Smoke results are acceptance checks, not extra full-cohort lives. Do not run the smoke and full experiment together. Do not dispatch another cohort if acceptance is blocked.

## What the completed baseline actually did

[Run43702732056](https://github.com/diegoami/borg-zoo/actions/runs/43702732056) recorded989deaths,732caps,75stalls and4wall timeouts across all1800assignments. All1600caster command/message traces below were checked against evidence hashes. Two timed-out Priest runs lack final run.json but retain both raw streams; they are included here. Counts mean a game message confirms the **starting book type** was stashed at least once, not proof that every later stash discarded a sole usable copy. No-cast counts reflect submitted cast commands, not starting-level eligibility or success.

| Class | Assigned | Starting book stashed | Stashed by tick1000 | No cast command |
| --- | ---: | ---: | ---: | ---: |
| Mage | 200 | 200 | 184 | 107 |
| Priest | 200 | 109 | 83 | 70 |
| Druid | 200 | 28 | 0 | 0 |
| Necromancer | 200 | 200 | 167 | 91 |
| Paladin | 200 | 199 | 185 | 142 |
| Rogue | 200 | 200 | 194 | 194 |
| Ranger | 200 | 200 | 191 | 178 |
| Blackguard | 200 | 42 | 0 | 2 |

Druid/Blackguard stashes are later and may be legitimate surplus copies. The late-learning classes must not be judged by cast absence alone. The confirmed omission is the lack of book counting/value in the player-power path, not every individual stash.

## Interpretation

The first question is whether known-usable first books now remain carried and casting becomes available. Death/cap counts, class breakdowns, stalls/timeouts, progress and purchase/escape use are descriptive secondary outcomes. Compare the previous run with explicit compiler/platform/calendar differences; do not claim a prespecified or confirmed population improvement. Freeze every new cell, source/bundle hash and raw trace. No C fidelity follows from seeds or a survival percentage.
