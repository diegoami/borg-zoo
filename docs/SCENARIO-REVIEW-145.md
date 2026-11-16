# PR #145 review response

Response to the owner-supplied review of implementation head
`32beb4f1bd8cd1a9efcffedd4a0890da23314aef`. This updates the implementation
without accepting a milestone, merging another repository, or expanding tiers.

1. **Cloud path / unmerged dependency.** Added a separate frozen two-cell
   Warrior smoke using Cemetery `9b38f76f279bfa1f7e93588dc19e8a02f086cabd`,
   an ancestor of its main branch. The caster definition and original evidence
   are unchanged; their unmerged PR #26 pin is no longer the CI/default dependency.
   Relevant PR changes now trigger the fixed small smoke. Read-only execution,
   actual artifact upload/download/collection, an archive push against an isolated
   Git remote and site preview run before merge. Production results-branch and
   Pages dispatch remain manual; pre-merge CI does not publish those changes.
   Cloud results will be linked after the check finishes.
2. **Receipt trust and terminal consistency.** Collection now checks typed
   summary start/depth/build/one-way facts, configuration, process success and
   before/after binary hashes, and re-derives the terminal outcome before
   accepting death/survival/stopped labels. Rehashed contradictory summaries,
   altered labels and timeout receipts are rejected in tests. Documentation
   explicitly distinguishes unsigned receipt consistency from authenticity:
   coordinated forgery is not prevented, and raw stream hashes cannot be verified
   after their bytes expire. Cemetery's classifier remains the stream authority.
3. **Registry guard and separation test.** The check is a directory-existence
   check, not a sentinel file. The actual pinned Cemetery adapter sets
   `BORG_DEATH_RECORDS_DIR` to the attempt's `natural-registry-guard`; a mistakenly
   invoked natural exporter would create it. See the pinned adapter at
   [synthetic_suite.py](https://github.com/diegoami/borg-cemetery/blob/9b38f76f279bfa1f7e93588dc19e8a02f086cabd/scripts/synthetic_suite.py#L354).
   Retained this defensive check with an explanatory comment and a Zoo failure-path
   regression. A separate integration test calls the real pinned adapter with
   an isolated harness stub and proves its exporter destination is exactly the
   directory monitored by Zoo. The population separation test now includes an
   actual natural run alongside a synthetic comparison and verifies that only
   the unchanged natural cell enters `site.load_runs`.
4. **Duplicate target aliases.** Both preparation and frozen-plan validation
   require all target commits to be distinct. The A→X, B→X, C→Y definition is
   explicitly rejected by regression.
5. **Malformed reports.** Scenario-site generation catches bad report/schema/
   plan/render data, preserves valid reports and lists unavailable entries with
   reasons in the scenario index and `unavailable.json`. It does not erase or
   silently repair the original record. A good/bad report regression covers it.
6. **Budgets and job duration.** Each matrix target gets a derived job timeout:
   ten build minutes, three setup/upload minutes, plus all selected cell wall
   limits and their 15-second outer cleanup allowances, rounded up. The build
   step has its own ten-minute timeout. The reviewed two-cell work budget is
   unchanged; these limits do not authorize larger tiers.
7. **Helper/adapter tests.** Added real temporary-Git tests for clean/exact
   checkout, dirty/untracked rejection, runner digest verification before import,
   contained/symlink paths and engine-tree hash scope. Added applied-profile byte
   and effective-value mismatch cases, the exporter-directory failure case, an
   actual pinned-adapter integration check and an isolated archive push/overwrite
   test. No external clone/network is required by the ordinary unit suite; the
   smoke workflow supplies the exact Cemetery checkout for its integration test.
8. **Non-discriminating smoke.** Agreed: the original caster smoke establishes
   orchestration/configuration only. Intentional rescued/newly-killed transitions
   remain tested with controlled fixtures; no improvement claim or expanded
   experiment is added to seek a favorable outcome.
