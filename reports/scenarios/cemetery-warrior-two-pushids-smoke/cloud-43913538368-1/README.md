# Initial cloud smoke: retained harness failures

[Actions run 43913538368](https://github.com/diegoami/borg-zoo/actions/runs/43913538368)
on Zoo `e7d9510d992988bc093ef28410e15cc9682148fb` built both exact runtimes,
but both launchers failed before gameplay because relative output/profile paths
were interpreted from the source checkout. The launcher reported a missing profile.

Collection retained all 2/2 expected cells as harness failures and the pair as
invalid. Neither became a death or survival. This record is retained unchanged
beside subsequent smoke evidence; it is not an independent natural-life sample.

`comparison.json` is the original cloud comparison artifact, downloaded after
collection. The original source/plan/binary receipts and failure reasons remain
in it. Artifact ZIP SHA-256: c746b16e11c75a9986b579f7cc8348099b9d504ef604e4aaf6061561f0424b78.

The path fix resolves the output directory before Cemetery changes cwd. A
regression uses a relative output path. The failed run also exposed that preview
jobs needed explicit always/collection-success conditions after execution failures;
that workflow condition is corrected separately. Production archival was skipped.
