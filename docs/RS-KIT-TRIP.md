# Expanded inventory and all-item returns: scheduled studies

Both studies pin the integrated inventory branch at
`dd3eeac646e097bcdd7c289c092e91400896a713` (milestone-12 Rust Borg).
This includes the inventory object-capability repair and the trip-return fix.
It is a new candidate; earlier zoo results at d9a56f4 do not measure it.

## What the choices mean

| Choice | New shopping and returns | Supply risk | Attack priority | Support priority | Learning priority | Return thresholds |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Existing rules | off | existing | existing | existing | existing | existing |
| Integrated defaults | on | 1x | 100 | 50 | 25 | 2 free spaces / 4 eligible unknown stacks |
| More provisioning | on | 1.5x | 100 | 50 | 25 | ordinary |
| Lower attack-supply priority | on | 1x | 50 | 50 | 25 | ordinary |
| Lower support priority | on | 1x | 100 | 25 | 25 | ordinary |
| Lower learning priority | on | 1x | 100 | 50 | 5 | ordinary |
| Earlier returns | on | 1x | 100 | 50 | 25 | 4 free spaces / 2 eligible unknown stacks |

Shopping actually buys, sells and transfers items at Home. Capability coverage
includes ammunition, oil, devices, books, food, mushrooms and equipment, with
explicit contextual exclusions. The native gate accounts for all 104 ordinary
shop kinds; this does not claim every possible object effect is fully modelled.
Risk changes the supply forecast, not combat aggression. Attack priority prices
ranged/throwing supplies; support includes tools and information services.
Magic and restoration priorities remain 100; attack/support intervals remain
100/1000 actions. The profiles declare all six new capability settings, plus
shared trip and inventory settings; native effective values are checked.

The unknown-stack threshold counts actionable or exploratory learning tasks
across all carried item types. Unchanged unresolved stacks cannot repeatedly
trigger returns by themselves. Home storage does not identify an item.
The existing-rule control disables both policies in the same source build;
these studies test their combined effect, not separate causal contributions.

## Development comparison

`rs-kit-trip-development`: seven choices × 1,800 starts = **12,600 games**.
Suite `classes-1800`, 100,000 engine turns per game, 200 starts per class with
all eleven races represented. The five variations each change one setting
from defaults, except earlier returns changes both return thresholds.

Rank fewer natural deaths first; then compare mean final character level,
mean deepest level and DL3+ count, including dead characters. All failures,
stalls and timeouts remain visible. This is development, not confirmation.

## Independent fixed confirmation

`rs-kit-trip-confirm`: integrated defaults versus existing rules × 1,800
fresh starts = **3,600 games**, using new frozen suite `classes-1800-c`.
Its seeds do not overlap earlier catalogue suites; existing frozen seed lists
are unchanged. Same class/race coverage and 100,000-turn cap.

The default candidate is fixed before dispatch and cannot be replaced by a
winner chosen from development. Primary: paired natural death, exact two-sided
McNemar alpha 0.05, pairs where both finish; report incomplete-pair counts and
outcome balance. Secondary descriptive measures: mean character level, mean
deepest level and DL3+, including deaths. Per-class figures are descriptive.
With assumed 0.36 discordance, 1,800 completed pairs plan for roughly 80% power
to detect a four-percentage-point absolute difference; this is a sizing
assumption, not measured evidence about the repaired model.

## Scheduling and checks

Total: **16,200 games**. Development uses 32 shards and confirmation 16.
Each workflow allows six concurrent run jobs, one game process each: at most
12 simultaneous game processes, leaving room for other workflows.

The report pages show readable choice names and their frozen settings, then
Deaths / Mean character level / Mean deepest level / Reached DL3+ / Incomplete.
Each page explicitly states that this build includes the coverage repair.
Raw identifiers and the statistical plan remain available.

Before dispatch: 115 unit tests pass; both study plans/preflights pass. All
seven profiles reached the 20,000-turn cap through the zoo adapter with every
declared native setting verified. [Canary receipts](validation/2026-11-15-kit-trip-zoo-canaries.json)
are wiring checks and are excluded from both studies. Existing frozen suites
were checked unchanged; the new confirmation has no seed overlap with them.
Workflow links are recorded after launch.
