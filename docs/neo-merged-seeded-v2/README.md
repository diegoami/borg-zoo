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
experiments/neo-merged-seeded-v2-1800.json via compare,36shards. The collector
keeps raw attempts, cell JSON and site summaries under the new experiment/run ID.
The owner authorized this queue, not a recurring automatic experiment.

## Wall-budget calibration

Acceptance43668428660 retained18records:10deaths,7wall timeouts and1tunnel
stall. Each timeout's last observation was alive and advancing at47537–72682
ticks; the120-second budget cut these short of100000. This is not evidence
that those characters died or that the engine hung. Repeat both original Warrior
timeout cases in a distinct subset suite at600seconds; keep the original suite
and results unchanged. Before its first dispatch, the unmeasured1800suite uses
600seconds and36shards (50games each). Worst-case per-job child time is
50*600/2=250minutes, within the existing300-minute job budget; fourjobs max.
The controlled repeat must finish before dispatching that cohort.

## Completed checks and queued cohort

- Acceptance [43668428660](https://github.com/diegoami/borg-zoo/actions/runs/43668428660):
  all18records retained,10deaths,7wall timeouts,1tunnel stall. The original
 120-second outcomes are preserved, not relabelled.
- Calibration [43669373189](https://github.com/diegoami/borg-zoo/actions/runs/43669373189):
  the Human Warrior completes with death at65338 in127seconds; the Half-Elf
  Warrior reaches100000alive in178seconds. Both are ordinary endpoints under
  the separately declared600-second budget. A local repeat also matches all5997
  commands of the original Human timeout trace before continuing to the same
  death turn, confirming the budget-censoring diagnosis.
- Cohort [43670231534](https://github.com/diegoami/borg-zoo/actions/runs/43670231534):
  dispatched on commit6fd7666,1800games/100000ticks,36shards, fourjobs maximum,
  two processes per job. Planning and build pass; game jobs have started.
  No final cohort result or improvement claim is available yet.

Small immutable JSON receipts are in `receipts/`; raw builds/cells/evidence are
retained on the linked Actions runs and the normal results branch. The independent
repository harness is [port PR96](https://github.com/diegoami/neo-angband-borg-mod-tracker/pull/96),
with a durable [report ledger](https://github.com/diegoami/neo-angband-borg-mod-tracker/issues/97).
Its18-game5000-tick CI smoke reports17caps/1death; it is a different suite from
this longer acceptance and must not be pooled with it.
