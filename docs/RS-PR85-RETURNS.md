# PR85 full-suite return-threshold development study

Owner instructions, 2026-11-15: merge the repaired inventory branch, restore
the old selling-pressure fallback, and test exactly
`(borg_trip_pack_slack, borg_trip_unknown_stacks) = (0,0), (1,2), (1,4), (2,4)`.
The owner also requested a way to measure how often the new policy actually
changes going home, rather than counting recommendations as completed trips.

Source is pinned to **71cff24ef45731e55aa9687930cd2d766dd0695e** in
`diegoami/borg-rs`: merged [PR85](https://github.com/diegoami/borg-rs/pull/85)
and [PR86](https://github.com/diegoami/borg-rs/pull/86), on the milestone-12
engine. All arms use this one Rust build. This is a configuration comparison,
not a comparison of different source versions. Previous dd3eeac studies,
results and suites remain unchanged.

## Fixed choices

| Choice | Shopping | Trip policy | Free-slot threshold | Eligible-unknown threshold |
| --- | --- | --- | ---: | --- |
| Existing rules | existing | existing | existing | existing |
| Shopping-only control | calibrated new shopper | existing | existing | existing |
| (0,0) | same calibrated shopper | enabled | 0: pack full | disabled |
| (1,2) | same calibrated shopper | enabled | 1 | 2 stacks |
| (1,4) | same calibrated shopper | enabled | 1 | 4 stacks |
| (2,4) | same calibrated shopper | enabled | 2 | 4 stacks |

All four threshold arms retain the original selling-pressure return checks
and descent hold. They may request an earlier return; they cannot veto a
return already requested by the general Borg. Native effective settings are
verified. Supply risk stays 1000; Ranger missile weight/interval stay 250/50;
learning priority stays 25; depth margin and gold-return trigger stay zero.
No class-specific return settings are introduced in this first development run.

The full suite is `classes-1800-d`: **1800 fresh starts**, 200 per class,
cycling all eleven races, cap **100000 world turns** after-key. Six arms give
**10800 games**. All existing suite definitions and expanded seed assignments
were checked unchanged, with no seed overlap. The nine-class canary namespace
is separate and excluded from the study. Shards: 32; maximum six concurrent
run jobs, one game process each. Other workflows are neither cancelled nor
modified.

This is **development calibration**. Deaths come first, followed by final
character level, deepest level and DL3+ including dead characters. Missing,
crashed, stalled and timed-out cells remain explicit. All paired statistics
are descriptive across these multiple development contrasts; no observed
winner is a confirmed improvement. A later fixed candidate and fresh
confirmation are required. Compare (1,4) with (2,4) to vary pack slack alone;
compare (1,2) with (1,4) to vary the unknown threshold alone. (0,0) changes both.

## What the knobs mean

`borg_trip_pack_slack=1`: request a return when one or fewer pack slots are
free. A stack occupies a slot regardless of its quantity; native quiver
reservation reduces capacity. Zero waits until the pack is full; it is not
an off switch for pack pressure.

`borg_trip_unknown_stacks=1`: request a return when at least one unknown
stack has an actionable or exploratory learning opportunity in town. The
condition is `threshold > 0 && eligible >= threshold`, so zero explicitly
disables this trigger. Unchanged unresolved tasks already taken through town
are normally deferred; raw unknown-item count is not the eligible count.
Moving an item into the Home does not identify it.

These are independent additional triggers. Emergency caution/escape runs
first; restocking, preparedness, restoration and some periodic-return checks
remain. Preparedness can ask for a one-level ascent without requesting town.
The old selling backstop retains its own level/boredom conditions at twelve
sellable stacks, plus the low-level/low-gold thirteen-stack descent hold.
The new settings do not override those conditions. A request uses the
existing route logic: shallow trips generally walk via stairs; Recall
requires depth/resources and the existing execution gates. None of these
settings guarantees immediate arrival or a deeper dive.

This remains a threshold-based trip policy; the shopping utility does not
yet price the complete expected benefit, travel time and risk of going home.
This study measures its behavior without removing inherited backstops simply
to make a knob produce an effect. A null effect can mean another rule acts
first, which the diagnostics must make visible.

## Observed influence, not just advice

The report and `town-returns.csv` distinguish:

- Actual native transitions from dungeon to town, excluding initial birth.
- v3 recommendation records, which may repeat and are not trips.
- v4 policy applications, including an already-set homeward goal.
- Newly set homeward goals; their custom pack/learning/purse subset excludes
  co-firing shared restocking.
- Actual arrivals after a newly set custom goal, and unfinished trips after
  such a request.
- Observed selling/food/restoration/periodic/scared notes on each journey.
- Native-state-sampled time in town versus the dungeon.

An already-set goal may come from an earlier policy consultation; it is not
labelled a legacy cause. A newly set goal is a real transition at that call,
but cannot establish the counterfactual that the character would never go
home otherwise. Several reasons can overlap on one journey. Missing state
observations and malformed/truncated trip rows are visible; they do not
abort or silently remove a measured outcome.

The workflow retains native messages, keys, states, source/config/binary
identity and policy streams for every cell. Town plans are recorded when the
shopper is enabled, and trip v3/v4 rows when its policy is enabled. Native
retail receipts and recorded wallets support purchases; planned buys and
Home transfers are not retail purchases. Raw archives have checksums and
90-day retention. Inspect/download them before treating that retention as
a permanent local archive. Report purchase tables remain available by class.

## Wiring validation before dispatch

145 Zoo tests pass. All existing/new experiment and smoke files plan;
the new study and canary preflights pass. The actual native canary report
renders the return tables. The [54 native canaries](validation/2026-11-15-pr85-return-canaries.json)
(one start per class per choice, 2000 turns) all reach their caps with the
correct source/birth/settings and complete evidence. No canary is counted as
an independent study life, and they establish no performance improvement.

The Borg's [fallback correction validation](https://github.com/diegoami/borg-rs/blob/71cff24ef45731e55aa9687930cd2d766dd0695e/docs/validation/2026-11-15-trip-sale-fallback/README.md)
includes 291 Rust tests, both clippy toolchains, 3/3 C/Rust smoke matches and
three longer recording-on/off comparisons. In those illustrative diagnostics
the Necromancer returned eighteen times with no new custom goal; the Ranger
returned nine times with one arrival after a new custom goal. These are why
we separate general returns from added policy requests; they are not efficacy
results for this study.

The large workflow is dispatched only after this catalogue/tooling PR passes
checks and merges. Dispatch identity and the live run link are recorded below
when available. No existing run or frozen experiment is rewritten.
