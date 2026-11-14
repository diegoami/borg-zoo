# Joint trip and improved-shopping zoo studies

Owner request: run the locally selected settings and nearby variations at
full zoo scale. All arms use borg-rs commit
`d9a56f48bac8675c91f551619492af36b698b4cf`, on its milestone-12 engine.
This is a pinned experimental specimen, not an accepted release tag.

**Improved shopping is live in every candidate arm.** Each has
`borg_town_plan=1` and `borg_trip_policy=1`. Only the existing-behaviour
control switches both off. The historical `borg_buy_strategy_default=0`
and `borg_buy_identify=0` fields do not disable the new planner: its own
knowledge weight and utility model choose purchases when town_plan is one.
The zoo requires the native summary to confirm every declared setting;
a setting that did not take effect makes the case a configuration error.

## Development: six choices on the same 1,800 cases

| Choice | Improved shopping | Trip policy | Inventory risk forecast | Return triggers |
|---|---|---|---:|---|
| Existing behaviour | off | off | unused | existing rules |
| Untuned live policies | on | on | 1,000 | 2 free spaces / 4 unknown gear stacks |
| Lower neighbour | on | on | 1,500 | ordinary |
| Selected candidate | on | on | 2,000 | ordinary |
| Higher neighbour | on | on | 2,500 | ordinary |
| Candidate with earlier returns | on | on | 2,000 | 4 free spaces / 2 unknown gear stacks |

This is `rs-joint-m12-development`, using `classes-1800`: 10,800 games,
100,000-turn cap, 200 cases per class with all eleven races represented.
The risk number changes the inventory forecast, not combat aggression.

## Confirmation: the fixed candidate on fresh cases

`rs-joint-m12-confirm` compares existing behaviour, untuned live policies
and the fixed 2,000 candidate on `classes-1800-b`: 5,400 games. The candidate
cannot be replaced by a development winner after seeing these results.

Primary: paired natural deaths, candidate against existing behaviour,
exact two-sided McNemar test at 0.05. Level, deepest level and DL3+ are
secondary descriptive measures, as is the comparison with untuned live
policies. Failures, stalls and timeouts stay visible and never become
deaths or survivors. The experiment JSON records the sizing assumptions.

## Resources and validation

Development uses 32 shards; confirmation 16. Each workflow allows eight
concurrent run jobs, with one process per job. Together they use at most
16 concurrent run jobs, leaving capacity within the account's 20-job limit.
They publish through the existing append-only results and Pages workflow.

Before dispatch: 110 zoo tests pass, all 57 catalogue experiments plan,
both new preflights report zero problems, and six local adapter canaries
reach their cap with every native setting verified. Canaries check
orchestration, not performance, and are excluded from the studies.

Published studies:

- [Development report](https://diegoami.github.io/borg-zoo/runs/rs-joint-m12-development/43643719860-1/index.html)
- [Fresh-seed confirmation report](https://diegoami.github.io/borg-zoo/runs/rs-joint-m12-confirm/43643769983-1/index.html)

The confirmation finished all 5,400 games: existing rules 530 deaths,
ordinary new policies 586, and the fixed 2x-risk candidate 559. The candidate
had 29 more deaths than control (paired McNemar p=0.2732); this does not
support adopting it for fewer deaths. These frozen runs precede the
object-coverage fixes. See FINDINGS.md for the paired counts.

## Town evidence correction (2026-11-14)

The first dispatches, development 43643719860 and confirmation 43643769983,
were frozen at abe128d without town message/policy capture. Both were still
queued when this correction was validated. Changing this checkout does not
change those runs. Owner approval is required before replacing the dispatches;
retain their run IDs and terminal status in the replacement provenance. Do not
mix their cells with corrected runs or select a different confirmation candidate.

Both experiment definitions now request raw evidence retention. The borg-rs
adapter passes this request through, rejects overwriting retained attempts,
records native messages and per-key state, and retains keys for every outcome.
Enabled policy profiles get separate per-cell town-plan and trip JSONL streams;
the control's policies remain off. An empty stream means no consultation was
recorded, not that a return or purchase happened. `town-recording.json` records
the command, stream paths, source and config identity. Partial failed attempts
remain available; game outcomes are not changed by receipt/wallet discrepancies.

`town-transactions.jsonl` contains native retail receipts, purchased quantities,
costs and per-key wallet checks. Compact per-item totals survive on the results
branch and in `town-purchases.csv`; the site shows purchases by profile and class.
Home transfers and return decisions can be inspected in the archived native
messages and policy records; the retail table does not claim to count them.
Raw archives use the existing workflow artifact path with SHA-256 inventories
and 90-day retention. Download them before expiry for durable recovery.

Validation uses the exact d9a56f4 combined runtime, not the separate town branch.
Eight native canary games paired logging off/on at a 3000-turn cap: Warrior and
Mage under control and live-reference profiles. All four pairs had identical
key hashes and final states. All 30 native retail purchases passed wallet
checks. The live Warrior produced both town and trip records; the live Mage
produced town records but no trip consultation. This is a logging check, not a
survival comparison. Receipt: [native-canary.json](validation/town-evidence-20261114/native-canary.json).
