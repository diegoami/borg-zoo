# Evaluation plan: identity, synthetic scenarios and population evidence

The phased plan below records the design discussion. See [SCENARIO-DISPATCH](SCENARIO-DISPATCH.md) and [SUITE-RUNS](SUITE-RUNS.md) for execution paths.

Proposed plan change, 2026-11-16. This adds the generated-dungeon scenarios
in [borg-cemetery#5](https://github.com/diegoami/borg-cemetery/issues/5)
to the evaluation path discussed around
[borg-zoo#19](https://github.com/diegoami/borg-zoo/pull/19).
It proposes evidence requirements; it does not dispatch experiments or
claim that the synthetic runner is available for every specimen.

## Three questions, three kinds of evidence

| Question | Evidence | Owner |
| --- | --- | --- |
| Did a default or implementation change preserve intended behavior? | Deterministic identity checks with effective settings and play hashes | Zoo, using the target repository's harness |
| What changes in a controlled dungeon/build situation? | Paired synthetic scenarios and separately curated saved-position scenarios | Cemetery; target repository supplies execution |
| Does survival or progress improve across natural games? | Prespecified, sized seed-suite comparison and fresh confirmation | Zoo |

PR #19 reports 18/18 identical games for candidate default versus base
with `munchkin-wdr`, 18/18 for candidate class-rule-off versus base
default, and default-to-default differences only on the six Warrior,
Druid and Ranger cases. Retain those as historical identity evidence.
Two seeds per class do not establish general equivalence or a population
survival effect. Separate population findings already exist in
[FINDINGS.md](FINDINGS.md); they are not results of #19's identity pilot.

New legacy C comparisons must follow the existing
[explicit-mode and cutoff rules](DESIGN.md).
Use `normal` and `munchkin-class` where supported, check effective
settings, and reject unsupported settings. Preserve old results and
frozen suites; add new experiment definitions when execution is ready.
Do not pair across the cutoff or incompatible harness contracts.

## What the synthetic scenarios measure

A generated dungeon scenario is a generation specification, with no input
run or save file: seed, start depth, race/class, starting character build,
profile, dungeon rules and limits. A run-derived character catalog can
reference observations from real games without making those games or
their saves runtime dependencies of the suite.

Starting both candidates with the same developed character measures play
from that controlled start. It can bypass the early-game munchkin policy
changed by #19, including the character development that policy causes.
Therefore retain natural-start comparisons for the policy's total effect.
Report synthetic results only as effects on the declared scenarios; do
not infer the policy is neutral when the scenario never exercises it.
Record whether the intended mode actually activates.

## Ownership and execution dependencies

- Cemetery owns suite manifests, stable scenario IDs, character catalogs,
  generation, orchestration, classification and scenario reports.
- The engine/Borg repository owns generated-depth startup, application of
  the character build, deterministic play, synthetic marking and diagnostic
  facts. The Borg receives only ordinary game observations.
- Zoo owns natural population confirmation and links to cemetery reports;
  it does not duplicate the scenario bank or incorporate synthetic games
  into natural-game denominators.

For P1, cemetery CI checks out **borg-reborn-rs at an exact commit** and
builds it in a separate path. No engine source is copied into cemetery and
no dedicated runner repository/image is required initially. The execution
dependency is [reborn#371](https://github.com/diegoami/borg-reborn-rs/issues/371).
Prepared branches or PRs are not a qualified release: verify the selected
pin and its capabilities before advertising a scenario as runnable.

The better-borg-c specimens in #19 require a compatible C execution
adapter. A reborn C control is not automatically the same specimen or
harness. Record that dependency as blocked until startup, build
application, identity checks and diagnostic support are qualified for the
chosen C pins. Same numeric seeds alone do not establish comparable starts
across engines or harnesses.

## Phased work and gates

| Phase | Work | Gate before proceeding |
| --- | --- | --- |
| P1: small pilot | One class, depths 5/10/15, one or two seeds, birth kit plus one run-derived level tier: 6–12 scenarios per target binary/profile | Review deterministic generation, actual start/build verification, failure classification and readable report |
| P2: coverage and exposure | Expand run-derived class/level tiers; for #19 cover Warrior, Druid and Ranger plus an unaffected class; qualify null-move diagnostics | Review provenance, representative kits and mode activation; replay identical inputs deterministically |
| P3: paired impact | Execute the same scenario IDs against two pinned target builds or configurations | Validate compatible suite revision and execution contract, exact input hashes and expected target identities; account for every pair |
| Population confirmation | Natural-start zoo experiment with explicit policies and a prespecified endpoint | Successful smoke, measured work budget and owner-agreed confirmation suite under RULES.md |

P1 validates the pipeline, not an improvement claim. Character tiers must
come from observed class/level inventories, stats, HP/SP and consumables,
with source observations, selection method and missing-data notes. Do not
invent a deep endgame artifact kit. A representative tier is an input,
not a claim that every character at that level has that equipment.

Before dispatch, freeze the suite revision and canonical spec hashes,
scenario IDs, target and engine/harness commits, binary/build inputs,
character-build and profile hashes, calendar policy, cap boundary, turn
cap, wall limit, sharding and artifact retention. Specify one-way dungeon
semantics, including whether further descent is allowed. Measure the
small smoke's runtime before selecting a larger work budget.
Execution jobs hold no write credentials and accept reviewed data
manifests rather than arbitrary suite code.

## Outcomes and comparison contract

Keep terminal outcomes separate from exposure observations:

- Terminal: death, survived to cap, stopped/other, harness failure,
  identity mismatch or timeout. Retain partial evidence; never relabel a
  failure or timeout as death or survival.
- Qualified near-death: a null move/wait would allow incoming monster
  actions to kill the character before the next player decision. Record
  HP, attacks/status effects, speed/energy ordering and the diagnostic
  method/version. The check must not change actual play or depend on Borg
  fear. A scenario can have exposures and later die.
- Low HP or Borg `worst >= HP` may screen candidates provisionally. If the
  null-move qualifier is unavailable, report qualified near-death as
  unavailable, never zero or a relabelled screen count.

### Pairing and execution identities

Freeze a comparison manifest before either arm runs. It declares the exact
field paths allowed to differ (the target binary/build identity, profile
settings, or an explicitly declared combination), each arm's expected
values, and the canonicalization/hash-contract version. Hash that manifest;
never infer exclusions from differences observed after execution.

Keep the complete scenario specification and its canonical hash immutable.
Use two additional identities for comparison:

- **Pairing hash:** SHA-256 of canonical JSON containing the comparison
  manifest hash, logical scenario ID, suite revision and all resolved
  inputs except the manifest's explicitly declared comparison fields.
  Keep seed, depth, race/class, starting-character-build hash, dungeon
  rules, calendar, cap boundary and limits. Keep profile bytes/settings
  when profile is not a comparison axis. The starting character build is
  distinct from the target Borg binary and must never be excluded merely
  because the experiment compares Borg builds.
- **Execution hash:** SHA-256 of the complete canonical execution input,
  including the full scenario specification/hash, pairing hash, exact
  target binary/build identity, engine/harness contract and pins, and
  requested profile bytes/settings. Verify actual start, binary identity
  and effective settings against that input; a mismatch is a failure,
  not a new silently accepted execution identity.

Pair on logical scenario ID and pairing hash, and verify each execution
against its arm's expected inputs. Complete scenario and execution hashes
may differ on the declared axis; they need not match between arms.
Undeclared differences reject the pair. Hash equality does not override
the existing engine/harness compatibility rules.

For example, `normal` versus `munchkin-class` on one pinned binary has
equal pairing hashes and different execution hashes when profile is the
declared axis. Comparing two Borg binaries with one fixed profile does
likewise when target build is the declared axis. A changed starting kit,
seed or depth must invalidate either pairing. Require fake-harness
fixtures covering these allowed differences, rejected undeclared
differences and actual-versus-requested identity mismatches.

Report rescued (base
died, candidate survived to cap), newly killed (the reverse), same
terminal outcome, inconclusive and missing pairs. A stopped or failed run
cannot establish a rescue. Publish per-scenario rows, per-depth/character-
tier aggregates with eligible and expected denominators, death causes,
minimum-HP distributions, exposure observations and missing evidence.
Minimum HP is descriptive, not the near-death definition. No aggregate
improvement claim without paired scenarios; no population claim from them.

The bounded Zoo implementation of this contract is described in
[SCENARIO-DISPATCH.md](SCENARIO-DISPATCH.md) (#144). It initially permits only
target-build differences and links the immutable Cemetery bank.

## Storage and acceptance

Compact suite definitions and result JSON/reports may live in Git or a
results branch; raw logs stay outside Git with explicit retention. A
scenario and a death dossier are separate artifacts. Synthetic deaths
stay suite results by default, excluded from natural registries, death
counts and zoo population counts. Optional preserved synthetic evidence
must be clearly labelled and stored separately. Promotion of a natural
dossier to a saved-position scenario is explicit curation preserving the
source identity; it creates no additional natural death.

Before calling this plan implemented, require cemetery's fake-harness
tests for generation, duplicate/missing definitions, classification,
failure/missing pairs and registry exclusion; a real pinned small suite;
and a compatible two-target comparison with machine JSON and a readable
report. Qualified near-death claims additionally require the null-move
evidence. Existing saved-position scenarios continue alongside synthetic
ones; neither depends on adopting the proposed
[shared data foundation](data-foundation/README.md).
