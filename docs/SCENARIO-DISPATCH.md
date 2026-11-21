# Cemetery scenario comparisons on Zoo (#144)

Zoo now has a separate bounded dispatch/impact path for Cemetery's generated
scenarios. It calls the pinned Cemetery generator, adapter, classifier and
per-target reporter; it does not copy the bank, synthesize equipment from the
incident index, or use Cemetery's stream-equality `verify` as an impact test.
Synthetic records never enter `results/*/*/cells.jsonl`, population tables or
natural-death registries.

The smoke below preserves the pinned generated-birth comparison. For
the frozen saved-state bank and its staged reruns, use [SUITE-RUNS](SUITE-RUNS.md).

## Reviewed definition and pushid resolution

`scenario-experiments/cemetery-warrior-smoke.json` is the two-cell CI/manual smoke:
one Human Warrior birth at starting depth 5, seed 101, 5,000 engine turns,
30 seconds per cell, sequential targets. The 90-second execution budget includes
Cemetery's 15-second per-cell outer cleanup allowance; source builds have separate
job limits derived from the per-target cell budget plus ten build minutes and
three setup/upload minutes. The build step is limited to ten minutes. Both
source pins support synthetic-start@2.

A `pushid` is the original operator-selected label in the definition. Its explicit
`specimen` resolves through Zoo's catalogue to a full source commit; abbreviated
labels never resolve through Git or a moving branch. Both the label and complete
specimen snapshot are frozen. Source/harness are the same exact reborn checkout.
`BUILD_ID` supplies actual source, binary, toolchain and build receipts, verified
by Cemetery against the clean checkout and executed binary. Failed/missing builds
have no fabricated binary receipt.

The default bank is the merged Cemetery P1 Warrior bank at exact commit
`9b38f76f279bfa1f7e93588dc19e8a02f086cabd`, with manifest, suite-spec and runner
SHA-256 digests. It is reachable from Cemetery main; no new tag or external
merge is required. The earlier caster definition and its evidence remain frozen
at PR #26 commit `5edfbbdd7f792f95599924bd51607f2d90ba6a77`, pending that
separate review/merge; the default workflow does not depend on it. The scenario selection names existing IDs without editing the bank
or its cap. Caster observed-equipment records are not executable suite cases;
unknown scenario IDs are refused and unsupported character-kit capabilities are
reported explicitly. Reborn #382 remains the equipment-execution dependency.

## Identity and pairing

The initial implementation supports only `comparison_axis: ["target_build"]`.
Profiles, kits and all starting conditions must be equal. Profile comparisons
require a separately reviewed adapter extension; no arbitrary field exclusions
are accepted. The initial adapter requires the reborn core's `params.json`:
explicit profile values are checked against effective values, and all effective
parameter values must match between targets. Silent default drift invalidates
the pair. Cores without this receipt need their own configuration adapter.
Every pushid must resolve to a different commit. Two to four source pins are supported, with at most 32
scheduled cells and 1,800 seconds of aggregate execution budget. These are safety
ceilings, not permission to expand the checked-in two-cell smoke.

The frozen plan includes the definition, exact catalogue resolutions, selected
Cemetery scenario specs and hashes, Zoo commit/runner digest, engine semantics
and budget. Its hash is verified at run/collection. A pairing hash covers that
plan, the complete shared scenario and engine semantics. An execution hash adds
the exact resolved target and verified build receipt plus observed UTC date.
Target changes therefore differ in execution hash without changing pairing hash.
An undeclared seed/depth/profile/loadout change is an identity failure.

Compatibility is conservative: the complete Git tree listing for pristine
`engine/angband`, `engine/patches`, `engine/frontend` and `engine/UPSTREAM` must
have the declared common SHA-256. Different engine/start semantics need a new
reviewed contract, even if both binaries advertise the same capability. The
frontend verifies native cave generation before activation, no saved-game load,
actual starting depth/build, one-way rules and applied profile. Birth kits remain
normal race/class-specific engine births. The native stop boundary is after-key;
actual turns can slightly exceed the cap and are retained.

Calendar policy is the real UTC clock. Different recorded UTC start dates make
a pair inconclusive, rather than pretending the engine date was frozen. Run the
arms within one workflow; do not combine different executions through labels.

## Running the smallest smoke

Build clean reborn checkouts at the two catalogue commits using Rust 1.100.0 and
the native dependencies from the Cemetery contract. The workflow checks out each
source at its exact commit and builds it under the shared lock. Local equivalent:

```sh
python3 -m zoo.scenarios plan --definition scenario-experiments/cemetery-warrior-smoke.json --bank /path/to/pinned-cemetery --out /tmp/scenario-plan.json
python3 -m zoo.scenarios run --plan /tmp/scenario-plan.json --bank /path/to/pinned-cemetery --source /path/to/reborn-99473510 --pushid 99473510 --out /tmp/scenario-cells/99473510
python3 -m zoo.scenarios run --plan /tmp/scenario-plan.json --bank /path/to/pinned-cemetery --source /path/to/reborn-d3ebe3c0 --pushid d3ebe3c0 --out /tmp/scenario-cells/d3ebe3c0
python3 -m zoo.scenarios collect --plan /tmp/scenario-plan.json --cells /tmp/scenario-cells --out /tmp/scenario-comparison
```

Every output path must be new. The adapter locks execution internally; do not
wrap it in a second lock. The CLI `run` exits nonzero on invalid execution, while
still recording its cells. Collection includes every expected cell even when a
build/job fails. Completed cells are flushed/fsynced before the next game; a
missing final per-target report cannot discard already completed records.
Original summary, process, configuration and effective-parameter receipt bytes
are retained and hash-checked in the compact cell, independently of raw-log expiry.
Collection independently checks the typed start, kit/rules, process/binary and
terminal facts in those receipts against the requested scenario and outcome.
These are consistency checks on unsigned receipts, not authentication against
an editor who changes receipts and hashes together. Trust in the original
execution and stream classification still rests on the pinned Cemetery adapter
and read-only execution job. Key/state/message hashes cannot be reverified
without the raw streams after artifact expiry; compact hashes do not reconstruct
missing bytes. No signed execution attestation is provided.

`.github/workflows/scenarios.yml` runs the fixed two-cell smoke on relevant pull
requests and allows manual dispatch of the reviewed definition. It freezes the plan, runs the
two targets sequentially in jobs with read-only permissions and no persisted
checkout credentials, and collects with `always()` after failed jobs. Cell/raw
artifacts retain partial evidence for 14 days; comparison artifacts live 90 days.
PR validation uses an isolated local Git remote to exercise the same archive
script/push and renders a downloadable site preview. It publishes no production
results or Pages changes. A separate manual-only archive job with write permission appends only compact comparison
JSON/HTML to `scenario-results/EXPERIMENT/RUN-ATTEMPT` on `results` and rebuilds
Pages. Concurrent result-branch pushes retry by rebasing without rewriting runs.
The archive job never executes engine or Cemetery code. A machine cancellation
before artifact upload can still lose local records; collection marks those
cells missing rather than fabricating outcomes.

## Reports and expansion gate

The Zoo site links a separate `/scenarios/` catalogue. Each report exposes exact
builds/pushids, every cell, paired outcomes, class/depth/loadout denominators,
complete input/execution hashes in JSON, an immutable Cemetery bank/catalog/
evidence link, and (for cloud executions) the workflow's execution artifacts and
Cemetery-generated per-target reports. Canonical scenario/reporting code and the
bank's retained gameplay evidence stay in Cemetery; Zoo stores the comparison.
Raw evidence is not copied into Git or promised beyond artifact retention.

Only death versus survival-to-cap establishes rescued/newly killed. Both-dead
and both-survived remain separate. Stopped pairs are inconclusive; failures are
invalid; missing attempts retain the full expected denominator. Duplicate
observations/attempts are rejected, not counted as extra independent lives.
Qualified null-move near-death is unavailable; HP screens do not substitute.

The smoke is orchestration evidence, not an improvement/population claim and not
a test of observed caster equipment. Inspect all cells, requested/applied settings,
identities, abnormal outcomes and measured runtime before proposing another tier.
Any larger tier needs a reviewed definition and owner agreement under RULES 14.
