# Post-fix Neo experiments, seeded-v2

Owner requested the post-fix runs on2026-11-15. Acceptance:18assigned births,
all nine classes and cycled races,100000ticks. After acceptance is healthy,
queue the new1800-game suite at the same cap. Four jobs maximum, two processes
per job; all attempts and abnormal outcomes retained. This is a descriptive
Neo-only measurement, with no C parity or improvement claim.

Borg runtime is merged76f25aa, engine fork b4af703 (stock/kit order corrections).
The toolkit is separately pinned to the repository headless-report proposal
which records the actual engine Git repository. The explicit seeded-v2 profile
uses C recommended point buy, no-selling enabled, native-menu birth RNG order,
a game-stream Borg startup seed and the GCC14.2 coordinate adapter. Clock640
remains unpatched. Old rolled-birth/no-selling-off cohorts are not causal controls.

New frozen suites have fresh SHA256-derived seeds under new suite IDs. Neither
old suite definitions nor existing result records change. Default Borg settings
are unchanged; the birth/startup protocol is named explicitly in both specimen
and suite and a mismatch fails planning. Node26 runs Neo only; Mandos retains22.

Dispatch smoke/neo-merged-seeded-v2-18.json via the existing smoke workflow.
Only after its build and assigned-cell outcomes are checked, dispatch
experiments/neo-merged-seeded-v2-1800.json via compare,18shards. The collector
keeps raw attempts, cell JSON and site summaries under the new experiment/run ID.
The owner authorized this queue, not a recurring automatic experiment.
