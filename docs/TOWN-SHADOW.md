# Town class-profile checks (#88)

**Question:** does each class receive the requested parameters, and do the
native parsed settings match every recorded shadow vector?

This is configuration validation, not class tuning. Seven profiles are
imported unchanged from borg-rs commit
`2439dd4ad6e1e629f99d0c2449dc975c91a68a7a`. The shared reference has no
class overrides. The validation probe changes Mage cash priority to 50,
Ranger future-Home discount to 750 and Blackguard risk to 1500. These values
are examples, not recommendations.

`smoke/town-class-shadow-smoke.json` prepares two fresh Human starts per
class, reference and probe, at 2,000 turns: 36 attempted games. Nothing is
dispatched by this change. The planner remains off (`borg_town_plan = 0`);
the observer records its hypothetical choices without executing them.

The new specimen opts into `town_shadow_records` and native effective-setting
verification. Such experiments must retain evidence, keep the planner off
and leave journey depth/duration automatic. Each cell gets its own
`town-plan.jsonl` path; inherited shared paths are discarded. Older specimens
retain their existing behaviour.

Every v5 row must be shadow mode 0 and have all 24 parameters equal to the
native `summary.json.effective_settings` vector (indices 45–68 in the pinned
`borg_h.rs`). Ordinary resolved profile settings are checked against that
same native summary. Missing or mismatched required fields produce
`config_error`; the observed game outcome is retained separately. An empty
stream is `not_observed`, not evidence that planning was exercised.

Raw records, their SHA-256 and the per-cell summary stay in retained evidence.
Only the compact summary and native vector enter `cells.jsonl`; the raw
snapshot stream does not. Results include `town-shadow.csv`. The run page
lists every attempted outcome, profile selection, config hash and native
vector, plus coverage for all nine classes, including zero-attempt classes.

Snapshot diagnostics use the same formulas as the pinned source's
`tools/town-plan/class_report.py`: planned spending is the sum of ranked
purchase costs; available gold is the post-urgent budget plus proposed sale
proceeds; retained gold is that amount minus the planned spending. Per-cell
medians describe snapshots, not independent trips. Supply copies and Home
dispositions are proposal counts. Actual purchases remain in the separate
native-receipt report supplied by #92.

Acceptance still needs a native run showing identical gameplay for matched
reference/probe starts. Unit tests cover the capture path, class routing,
parsed/vector mismatches, corrupt streams, retention and failure reporting;
they do not establish policy fitness or a live executor. Source-native
validation is documented in the borg-reborn-rs repository at the pinned commit
(`docs/validation/2026-11-14-town-class-profiles/README.md` there; it is not in this repository, whose
`docs/validation/town-evidence-20261114/` holds the canary receipt).

This work integrates #92's evidence-retention support. A later live outcome
study requires accepted upstream execution support and an owner-started
experiment; it is not enabled here.
