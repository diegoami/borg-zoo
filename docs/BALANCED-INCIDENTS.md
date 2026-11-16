# Balanced999 death and critical-recovery scenarios

Owner scope (Zoo #168): **999 saved encounters, exactly111 for each of all
nine classes**. The correction to equal class counts supersedes the earlier
caster weighting. No level threshold filters deaths. Equipment and spell state
come from each full native save, rather than a constructed common loadout.

Preparation runs on Zoo with exact Cemetery tools/specification and the
read-only observation projection in reborn #468. Harvest workflow
[43979480269](https://github.com/diegoami/borg-zoo/actions/runs/43979480269)
is in progress. Its definition is `definitions/balanced999-incidents-harvest.yaml`.
A completed class contributes111 usable unique starts; assembly fails for any
short or missing class. All attempted natural lives and death evidence are
retained, including deaths excluded because no usable observable trigger exists.

A candidate is either an actual terminal death or observed actual HP loss to
at most25% HP followed by recovery to at least50%. The latter is a critical-HP
recovery screen, not a qualified counterfactual near-death. Starts precede the
first observable threat/contact of that incident, with a2000-engine-turn bound.
Selection follows prespecified seed order, not process completion speed; no
repeated saves or ordinary-fight padding can meet a quota.

## Execution contract

`zoo.incident_bank` verifies the exact prepared archive, all input hashes,
native start state and equal class counts before planning. Source6d1bca10 is
the accepted execution baseline; the observation-only source prepares inputs.
The saved-state path remains separate from generated-birth comparisons.

A single compiled build is reused. Each case has fresh Borg memory, saved
engine RNG, a2000-engine-turn horizon and5-second native wall budget. Private
execution copies leave the canonical inputs unchanged. Completed native receipts
are flushed immediately; collection rechecks their source/build/load/config,
outcome and receipt identities. Missing, invalid and interrupted cells remain
in their expected denominators, with per-class counts.

The owner's explicit request covers the full999 execution. It runs as nested
balanced stages: smoke18 (two/class), small90 (ten/class), medium360 (40/class),
big900 (100/class), full999 (111/class). Each stage executes only newly added
cases, in bounded≤40-case jobs, at most eight concurrent jobs. Each cumulative
gate requires no missing/invalid cells; intermediate gates also reject stopped
cells. A failed gate prevents later stages. The smoke precedes all larger work.
The same life can contribute multiple incidents, so these are correlated
encounter tests rather than999 independent population trials.

The execution definition will pin the completed bank artifact ID, preparation
run and inner archive SHA; it cannot be dispatched before preparation finishes.
Cemetery owns the canonical bank/native evidence; Zoo owns aggregate reports
under `reports/saved-encounters/`. No main branch or accepted milestone changes
are part of creating or running this suite. Improvement/configuration comparison
claims need additional prespecified arms and are not inferred from this baseline.
