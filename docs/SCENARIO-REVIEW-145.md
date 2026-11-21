# PR #145 review response

Historical PR review and retained cloud receipts. See [SCENARIO-DISPATCH](SCENARIO-DISPATCH.md) for workflow instructions.

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
   Cloud execution, collection and the isolated archive/site preview passed at [43914778367](https://github.com/diegoami/borg-zoo/actions/runs/43914778367)
   on runtime/workflow head `f8fe7197a3fa045ed0e4cc35d96e1276d2282535`.
   Subsequent evidence-only commits do not change those implementation bytes.
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

## Cloud-discovered correction and validation

The first cloud run [43913538368](https://github.com/diegoami/borg-zoo/actions/runs/43913538368)
built both targets, but relative output/profile paths were resolved from the
source checkout after the harness changed cwd. All 2/2 cells were retained as
harness failures, not deaths/survivals. The original comparison is preserved in
[the failed cloud packet](../reports/scenarios/cemetery-warrior-two-pushids-smoke/cloud-43913538368-1/README.md).

Output paths are now made absolute before adapter execution. A relative-path
regression covers it; its fixture's profile digest is consistent with the bytes
it writes. Collection independently revalidated the original caster receipts
without replaying those games. The separate pinned-Cemetery integration check
passes locally and in the cloud execution jobs.

Final local suite: 196 tests, one optional integration skip; that integration
was also run explicitly and passed. All 22 focused scenario tests pass. Site
build, workflow YAML, archive shell syntax and whitespace checks pass.

Cloud execution exposed an additional failure-path issue: downstream previews
were skipped after a failed run job despite successful collection. Preview and
manual archive now explicitly use always plus collection-success conditions, so
partial failure reports can still be rendered/archived. Production archival and
Pages dispatch remain manual and were not exercised against the public results
branch during PR validation. The same archive script is exercised against an
isolated real Git remote; no broader tier or population claim is implied.

## Retained corrected cloud evidence

[The corrected cloud packet](../reports/scenarios/cemetery-warrior-two-pushids-smoke/cloud-43914778367-1/README.md)
retains the original comparison from run 43914778367. All 2/2 Warrior cells
survived to the cap (5,002 actual engine ticks, 500 player turns, 334 Borg
decisions and 697 keys each). Both source builds, actual pinned-adapter tests,
artifact transfers, collection and isolated archive/site preview jobs passed.
Production archival was skipped as intended for a pull request. The downloaded
ZIP matches GitHub's artifact digest, and all retained receipt hashes match.

This is still a non-discriminating orchestration smoke. The failed predecessor
remains a separate invalid comparison, not a death or an extra independent life.
Evidence-only commits after the measured implementation leave runner/workflow
bytes unchanged; their normal CI checks are reported separately on the PR.
