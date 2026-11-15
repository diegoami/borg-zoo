# Response to the review of PR #119

The [independent review](https://github.com/diegoami/borg-zoo/pull/119)
(2026-11-15) covered `00abdc9..6469853` and returned **accept with specified
changes**. All nine findings were checked against the text and the pinned
sources, and all hold. The corrections are in this revision. Owner
decisions D1–D7 are unchanged.

| Finding | Correction | Where |
| --- | --- | --- |
| **F1 High.** Token equality is not an atomic acceptance; no authorised actor for claims | Coordinator jobs (zoo code only) do all dispatch, takeover and acceptance; runner jobs hold no credentials. The commit point is one conditional replace of the lease from `active(g, e)` to `done(g, e, attempt, hash)`, then a write-once acceptance receipt. Expired-but-uncontested results are accepted; takeover needs a passed deadline and a finished holder job; `done` is terminal; a crash between lease and receipt is reconciled from the lease | [Leases and acceptance](ARCHITECTURE.md#leases-and-acceptance), [actors](ARCHITECTURE.md#actors-and-permissions), invariant 5 |
| **F2 High.** Exports omit acceptance state | Statistics and resume read write-once receipts in the ledger, never leases. Exports list receipts before batches, which is coherent without pausing writers. Restore advances an epoch that every lease and attempt carries, so pre-restore workers cannot be accepted; the drill includes a paused old publisher | [Backup and restore](ARCHITECTURE.md#backup-and-restore), invariant 15 |
| **F3 High.** Equal effective settings, different input bytes | Split **settings** (semantic, effective values) from **configuration** (every original input file's hash, including the plan file and its contract version, plus the settings ID). Profile name and settings check move to the attempt. Unknown configurations of legacy records are tied to their attempt, never merged | [Entities](ARCHITECTURE.md#entities-and-identities) |
| **F4 High.** Two forks of one game share a life ID | New **work item** identity: execution, arm, start, origin (birth, checkpoint or scenario revision), continuation protocol, target horizon, repeat index. The expected manifest lists work items; a fork's life includes its parent checkpoint and protocol | Entities, invariant 3 |
| **F5 High.** Pins are not ordered with deletion | Every blob has a control record (`staged`, `live`, `deleting`, `deleted`). References, pins and deletion are conditional replaces on it; marking `deleting` is the commit point. Generation-suffixed keys are never reused; exports pin their blobs | [Retention, pins and deletion](ARCHITECTURE.md#retention-pins-and-deletion), invariant 14 |
| **F6 Medium.** Extending an arm's horizon looks incompatible | Caps and budgets leave the arm. A **gameplay contract** (boundary, calendar policy, forced options, state-format version) decides compatibility; a **horizon plan** with revisions holds targets, endpoints and budgets. A later extension is a new revision of the same arm | Entities, invariant 7 |
| **F7 Medium.** Raw trace hashes reject harmless checkpoint markers | Qualification compares a versioned **gameplay projection** (issued keys by decision index, game and Borg RNG, turn, depth, HP, outcome) without observer markers. It is tested both ways: an extra marker compares equal, an extra RNG draw does not | [RESUME.md, qualification](RESUME.md#qualifying-a-resume-as-faithful) |
| **F8 Medium.** Plan states may never be exercised | New criterion 6: every plan/controller state field must be non-empty at some passing checkpoint, using bounded fixtures where seeds do not reach it. Unexercised fields are unqualified, and resume refuses checkpoints that hold them. Qualification is per adapter, state format and plan schema | RESUME.md, criterion 6 |
| **F9 Medium.** The active Neo-original adapter was not audited | Audited at the newest measured triple (Borg and toolkit `967b28f5`, engine `b4af7034`): no save or resume; evidence is `commands.jsonl` checked against `playSha256`. Neo resume is deferred, with a defined import evidence level. New change request N2 for the fork's runner | [RESUME.md](RESUME.md#neo-original-and-neo-forks-kind-neo-original), PLAN tasks |

Other points from the review's coverage table, also corrected:

- **Late results** after `not_received` are stored as `late` and count only
  through a correction (invariant 3).
- **Conflicts across batches** are detected by the index, both records
  kept, neither used until corrected (invariant 2).
- **Reports** pin acceptance receipts and the corrections in force.
- **Cutover** drains running executions first; the link change from T0
  (PR #120) is recorded as already made.
- **M4** keeps exact resume disabled per adapter until M3 qualifies it.
- **Broad import** is described fairly: unknowns recorded, nothing guessed.
- **Units and prices:** GitHub's limit is 100 MiB; Backblaze is
  $6.95/TB-month; per-game coordination writes are costed (about $25–40 a
  year on R2); R2's conditional operations are documented; OIDC is
  documented for AWS and Google Cloud only.
- **Benchmark:** the paired query keeps finished games of one harness
  kind and is labelled a workload, not the zoo's statistics; the
  configuration query now hits a real configuration; "ten times the volume"
  is no longer claimed.

Estimates rose: M1 to 3–5 days and M2 to 3–4, about 18–30 days in all.
