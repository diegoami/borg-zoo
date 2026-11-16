# Two-pushid Cemetery dispatch smoke (#144)

This local validation executes one immutable Cemetery Gnome Mage birth scenario
(seed 202, starting depth 1) against two exact reborn builds. It exercises Zoo's
new dispatch, cell journal and impact collector, not a population comparison.

- Zoo execution code: `a16564f9c155081827a53565c6ce256fc7014692`.
- Cemetery bank/runner: `5edfbbdd7f792f95599924bd51607f2d90ba6a77` (PR #26).
- Scenario: `low-level-casters-4dbd9db86cec10ca02a4d1f7`.
- Source/harness pins: `99473510940b8a7bd6e77ad61e3a2b00c72a6e6d` and
  `d3ebe3c0e0e181a45893ca9e2ac855f7b5365b92`.
- Profile: the same pinned Cemetery profile on the reborn core in both cells.
- Shared engine/patch/frontend/UPSTREAM tree digest:
  `4d80ed3b12a19beef624f8f639d0a84350dec5df8f9d76e52c3acbae79684567`.
- Limits: 3,000 engine turns, 30 wall seconds per cell, sequential execution.

| Pushid | Outcome | Actual engine turns | Player turns | Borg decisions | Keys |
| --- | --- | ---: | ---: | ---: | ---: |
| 99473510 | Survived to cap | 3,003 | 300 | 302 | 617 |
| d3ebe3c0 | Survived to cap | 3,003 | 300 | 302 | 617 |

Measured process times were 1.16 s and 1.08 s respectively, below the 30-second
wall limit. These local timings do not size larger tiers or promise cloud costs.

All 2/2 requested cells are present and valid; the paired result is
**both survived**. There are no rescued/newly-killed claims, failures, mismatches,
timeouts or missing cells in this smoke. Both runs verified clean source and
binary receipts, actual generated cave/start, the unchanged profile and equal
effective parameter values. Pairing hashes are equal and execution hashes differ.
No synthetic outcome created a natural-death registry. Stop semantics are after-key,
so the 3,003 actual ticks are retained rather than relabeled as exactly 3,000.

[comparison.json](comparison.json) retains the frozen definition/plan, original
pushids and specimen snapshots, full build receipts and hashes, complete compact
summary/process/configuration/effective-parameter receipt bytes, cell outcomes,
per-class/depth/loadout denominators and paired classification. [checks.json](checks.json)
records the independently inspected smoke assertions. The site renders this JSON
as a separate scenario report linked from Zoo's home page.

The bank, catalogs, scenario definitions, reporter and canonical bank evidence
remain in [Cemetery at its immutable revision](https://github.com/diegoami/borg-cemetery/tree/5edfbbdd7f792f95599924bd51607f2d90ba6a77/synthetic/low-level-casters).
Raw execution logs and Cemetery-generated per-target reports remain outside Git
under `work/scenario144-validated/`. Those local paths are not permanent public
downloads. Future workflow executions upload them with explicit retention.
Earlier development attempts are not additional independent samples or inputs
to this comparison.

This is a short build/configuration/orchestration smoke: about 300 player turns,
one race/class, one seed and one depth. It tests ordinary birth kits only, not
the observed caster equipment indexed in the bank. Equipment execution remains
blocked on reborn #382. Qualified near-death count is null/unavailable; sampled
HP is only a candidate screen. No survival improvement or wider-tier authorization
is inferred. Review the implementation and this small smoke before any expansion.
