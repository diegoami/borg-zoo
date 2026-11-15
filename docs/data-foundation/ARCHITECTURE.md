# Architecture of the shared data foundation

Proposal for borg-zoo#114. The [decision page](README.md) explains why this
design was chosen; this page says what it is. Names such as `life` or
`segment` are proposed schema names, not existing code.

## Use cases

| # | Who | Wants to | Needs from the foundation |
| --- | --- | --- | --- |
| U1 | Zoo reader | Compare two versions or configurations on the same seeds | Lives grouped by arm, paired by start, within one execution or with the differences shown |
| U2 | Zoo reader | Inspect what a game was actually configured with | Configuration bytes and effective settings by hash, a readable diff between arms |
| U3 | Zoo operator | Run 1,800 games to 100k, then extend them to 200k and 400k without replaying from birth | Sealed checkpoints, resume claims, segment lineage |
| U4 | Zoo reader | See survival and progress at 100k, 200k and later | Milestones per life, right-censoring, no double counting |
| U5 | Cemetery reader | Browse deaths by seed, race, class, build, cause, depth and evidence available | A case index over lives with a terminal death |
| U6 | Cemetery analyst | Replay a death from the last good checkpoint before it | The last sealed pre-death checkpoint plus a qualified resume method |
| U7 | Cemetery analyst | Try another build or setting from the same position | A fork with its own lineage that never counts as the original life |
| U8 | Anyone | Download a case or an experiment and work offline | A portable bundle: manifest and blobs, each verified by hash |
| U9 | Report author | Publish an analysis that can be traced and rebuilt | Reports as derived records over a hashed set of inputs |
| U10 | Owner | Find out why a run failed, stalled or timed out | Failures kept as first-class outcomes per segment, never turned into deaths |
| U11 | Later tools | Analyse or resume games without knowing the zoo's internals | Published schemas and identity rules, plus the bundle format |

## Entities and identities

Each record is canonical JSON: sorted keys, UTF-8, no insignificant
whitespace, a `schema` field such as `borg-data/life@1`. Its identity is the
SHA-256 of the canonical *identity tuple* named below, not of the whole
record, so a record's identity never depends on fields added later. Hashes
are written `sha256:<hex>`.

```mermaid
erDiagram
    EXPERIMENT_SNAPSHOT ||--o{ ARM : "declares"
    BUILD ||--o{ ARM : ""
    CONFIGURATION ||--o{ ARM : ""
    SETTINGS |o--o{ CONFIGURATION : "resolves to"
    GAMEPLAY_CONTRACT ||--o{ ARM : ""
    ARM ||--o{ HORIZON_PLAN : "revised by"
    EXPERIMENT_SNAPSHOT ||--o{ EXECUTION : "dispatched as"
    EXECUTION ||--|{ WORK_ITEM : "expects"
    ARM ||--o{ LIFE : "plays"
    START ||--o{ LIFE : "starts"
    LIFE ||--|{ SEGMENT : "ordered"
    WORK_ITEM ||--o{ ATTEMPT : "tried by"
    SEGMENT ||--o{ WORK_ITEM : "scheduled as"
    SEGMENT ||--o| ACCEPTANCE : "accepted by"
    ATTEMPT ||--o{ CHECKPOINT : "produces"
    CHECKPOINT ||--o{ SEGMENT : "resumed by"
    CHECKPOINT ||--o{ LIFE : "forked into"
    ATTEMPT ||--o{ OBSERVATION : "records"
    BLOB }o--o{ ATTEMPT : "evidence"
    BLOB }o--o{ CHECKPOINT : "state"
    REPORT }o--o{ ACCEPTANCE : "reads"
    RECORD ||--o| CORRECTION : "superseded by"
```

| Entity | Identity tuple | Holds |
| --- | --- | --- |
| **Blob** | SHA-256 of the original bytes | Compressed bytes, original size, media type, compression. One blob can serve many records. Stored under a generation-suffixed key ([blob control](#retention-pins-and-deletion)) |
| **Build** | Source repository and full commit, dirty-input digest, harness repository and commit, runner hash, instrumentation version, binary hash, game-data digest, compiler and flags, platform | All build provenance; the build tarball as a blob when kept |
| **Settings** | Adapter kind and the canonical effective settings, defaults included | A semantic equivalence class. Two configurations with the same settings play the same Borg settings, whatever their files look like. There is no settings record when the effective settings are unknown |
| **Configuration** | Adapter kind; the sorted (role, SHA-256) of every original input file (`borg.txt`, the plan file and its plan-contract version, birth options); the settings ID, or `unknown`. A legacy record with neither file bytes nor settings gets `unknown` plus its source attempt's identity, so unrelated unknowns are never merged | The applied inputs: what a game was actually given. Two plan files with the same scalar flags are different configurations. The profile name, the requested profile and how the settings were checked belong to the attempt, not here |
| **Gameplay contract** | Stop boundary (`exact` or `after-key`), calendar policy (real clock or a frozen date), ordinary-play options the runner forces (no cheat death, no respawn), adapter checkpoint state-format version | What must stay equal for a game to continue as the same game. Caps, wall and stall limits are deliberately not part of it |
| **Start** | Engine family, seed as the engine reads it, birth contract (rule, race, class, point buy, birth options) | What makes two lives "the same seed". C and Neo starts never compare equal |
| **Experiment snapshot** | Hash of the experiment file plus every catalogue file it resolves through | The frozen question: arms, suites, endpoints, `prespecified` text |
| **Arm** | Experiment snapshot that created it, build, configuration, gameplay contract | What one column of a comparison means. It has no cap: horizons live in the horizon plan |
| **Horizon plan** | Arm and revision number | Target horizons (for example 100k, then 200k and 400k), endpoints and prespecified text, wall and stall budgets per segment. Extending an arm to a horizon nobody planned is a new revision that names the reason; earlier revisions and their endpoints stay as they were |
| **Execution** | Producer (repository), workflow run ID and run attempt, or a local run ID | The dispatch: its **expected manifest** (the sorted work-item IDs and their hash, closed before any game runs), runner image, date, zoo commit, epoch |
| **Work item** | Execution, arm, start, origin (`birth`, or a checkpoint ID, or a cemetery scenario-revision ID), continuation protocol (`from-birth`, `exact`, `fresh-borg`), target horizon, repeat index | One expected piece of play. Two forks of one game from its 100k and 200k checkpoints in one execution are two work items, and so are two repeats |
| **Life** | Original: arm, start, and the work-item ID of its first segment. Fork: the fork's arm, the parent checkpoint, the continuation protocol, and the fork's first work-item ID | One independent game. Terminal outcome, lineage kind (`original`, `fork`) |
| **Segment** | Life and its starting point (birth, or a checkpoint ID) | The span from that point to the next accepted checkpoint or the end of the game |
| **Attempt** | Work item, lease generation, epoch, job coordinates (execution, shard, job attempt) | Segment-local outcome, wall time, decisions, exit status, evidence blobs, profile name and settings check. Retries are attempts, never new lives |
| **Acceptance** | Segment | Write-once receipt naming the accepted attempt, its record hash, lease generation and epoch. **The only thing statistics and resume eligibility read** ([protocol](#leases-and-acceptance)) |
| **Checkpoint** | Life, cumulative engine turn, producing attempt | Manifest: game save, Borg state, Borg RNG, game RNG, plan/controller state, calendar, build, configuration and gameplay-contract IDs, each file by blob hash. State `sealed` or `fresh-borg-only` |
| **Observation** | Attempt, cumulative turn, kind | Milestones (level, depth, gold, later net worth) at fixed turns, depth marks, stall blocks |
| **Report** | Analysis name and version, hash of the sorted input set, endpoint definitions | The input set lists acceptance receipts and the corrections applied, each with its hash. The output is a blob. A report is never an input to statistics |
| **Correction** | The corrected record's ID and a correction ordinal | `supersedes`, reason, author, the replacement record |

Cemetery entities sit on top and point down: an *episode* names a life, an
attempt and a turn range; a *scenario revision* names a checkpoint and its
continuation mode; a cemetery *source attempt* is a foundation attempt ID.
That fixes PR #2's finding R4 (source identity collisions) by construction,
because the execution and attempt coordinates are already in the attempt's
identity. A cemetery trial of another build from a scenario is a work item
whose origin is that scenario revision.

### Mapping from today's records

| Today | Becomes |
| --- | --- |
| `results/<experiment>/<run>/meta.json` | Experiment snapshot, execution, and one horizon plan per arm with the suite's cap |
| One `cells.jsonl` line | A work item, a life, its segment from birth, one attempt and an acceptance receipt (`imported`); observations from `milestones`, `first_turn_at_depth`, `stall`; evidence hashes become blob references (bytes missing unless salvaged) |
| `specimen`, `specimen_ref`, `binary_sha256`, `runner_sha256`, `harness_commit`, `compiler` | Build |
| `config_sha256` and `effective_settings` | Configuration and settings. A missing `config_sha256` gives an `unknown` configuration tied to that attempt, never a guessed one |
| `profile`, `profile_sha256`, `profile_applied` | Attempt fields |
| `boundary`, `calendar` | Gameplay contract (boundary), attempt (calendar observed) |
| `suite`, `seed`, `birth`, `race`, `class` | Start |
| `outcome`, `cause`, `final`, `wall_seconds` | The attempt's outcome; also the life's terminal outcome when the life has one segment |

## Invariants

Each invariant gets a test in the milestone that implements it
([PLAN.md](PLAN.md)). The failure sequences in the
[review of PR #119](https://github.com/diegoami/borg-zoo/pull/119) are
among those tests.

1. **Append-only.** No ledger object is ever overwritten or deleted by
   normal operation. Blobs are deleted only by the retention protocol below.
   Corrections are new records that name what they supersede; readers show
   the correction chain, and the original stays retrievable.
2. **Write-once identity.** A batch, commit marker, checkpoint or acceptance
   receipt is written by create-if-absent. Identical bytes are a no-op;
   different bytes are a conflict that stops the job. Records inside
   different batches can still claim one identity with different payloads
   (two publishers, a bug). The index detects this, keeps both, marks the
   identity `conflicted`, and uses neither in statistics until a correction
   resolves it. Nothing is replaced.
3. **Every expected work item is accounted for.** The expected manifest is
   closed before play. Finalising an execution writes an explicit
   `not_received` attempt for each work item without an accepted attempt.
   That is a harness failure, never a death and never dropped. A real result
   that arrives after finalisation is stored as a `late` attempt. It counts
   only through a correction that supersedes the `not_received` record, so
   the index never counts both.
4. **One life, one count.** Statistics count lives, never segments,
   attempts, checkpoints, work items or forks. A resumed segment extends its
   life. A fork is a new life with `lineage: fork` and is excluded from the
   parent arm's statistics.
5. **One accepted attempt per segment.** Acceptance is the write-once
   receipt of the [acceptance protocol](#leases-and-acceptance). Statistics
   and resume eligibility read receipts, never leases. Other attempts stay
   visible as `superseded`, `late` or `failed`, with their evidence.
6. **A checkpoint is usable only when sealed.** Sealing requires every blob
   in its manifest to be stored, referenced through the blob protocol and
   its hash verified on read-back. Resume refuses anything else.
7. **Resume is refused when incompatible.** Build, configuration, gameplay
   contract and adapter state-format version must equal the checkpoint's.
   Anything else is a fork with its own arm. **Horizons and budgets are not
   compatibility conditions:** extending an arm to a later horizon is a new
   horizon-plan revision of the same arm, and its lives continue.
8. **Turns are cumulative.** Engine turns count from birth across segments.
   Segment-local decisions, wall time and Borg restarts are separate fields.
9. **Survival is right-censored.** "Alive at H" needs accepted segments
   covering birth to at least H with no death before it. A life whose
   accepted segments stop short of H is `not_reached` at H, not alive and
   not dead.
10. **Failures stay failures.** Stalls, wall timeouts, crashes, harness
    failures, configuration errors and lost workers are outcomes of the
    attempt. A life whose last segment failed is `incomplete` at later
    horizons, and the failure is shown.
11. **Unknown stays unknown.** Missing provenance, settings or evidence is
    stored as `unknown` or `unavailable` with a reason. Imported records are
    labelled `imported` with their evidence level, and nothing is
    reconstructed by guessing.
12. **Derived data is rebuildable.** The index, the site, report caches and
    bundles can all be deleted and rebuilt from the ledger and blobs.
13. **Execution conditions are recorded.** Calendar, runner image and
    compiler belong to every attempt. Comparing arms across executions
    shows these differences, as zoo rule 7 requires today.
14. **References and deletion are ordered.** A pin or a new reference to a
    blob either succeeds before the blob is marked for deletion, and then
    prevents it, or fails visibly. A deleted generation is never reused.
15. **Stale workers are fenced.** Every lease and attempt carries the
    epoch. After a restore the epoch advances, and nothing from an earlier
    epoch can be accepted.

## Storage layout

One S3-compatible bucket, with prefixes having different rules:

```text
blobs/sha256/<2 hex>/<64 hex>/g<N>.<zst|gz|raw>  one key per generation, never reused
ledger/<kind>/<execution-id>/<batch>.jsonl.gz     write-once record batches
ledger/<kind>/<execution-id>/<batch>.commit       write-once commit marker, written last
ledger/checkpoints/<checkpoint-id>.json           write-once, written when sealed
ledger/receipts/<segment-id>.json                 write-once acceptance receipts
control/epoch.json                                conditional replace
control/leases/<work-item-id>.json                conditional replace
control/blobs/<hash>.json                         conditional replace, one per blob
index/<generation>/zoo.sqlite.gz, *.parquet       derived, replaceable
site/                                             derived static site
exports/<date>/                                   portable snapshots (see Backup)
```

- Records are batched per (execution, shard, attempt), so one file holds
  hundreds to thousands of records and compresses about 12× (measured).
- A batch is visible only once its `.commit` object exists. The commit
  lists the batch hash, record count and every blob it references. Readers
  ignore batches without a commit marker.
- Blobs are compressed with zstd or gzip (settled in the M2 benchmark).
  Identity is the hash of the original bytes; the index maps each hash to
  its live key.
- Git holds code, catalogue, schemas, the frozen legacy `results` branch and
  small reviewed fixtures. It no longer holds new results.

## Protocols

All protocols rely on two storage operations: **create-if-absent** and
**replace-if-unchanged** (an ETag or generation precondition). Amazon S3
(`If-None-Match`, `If-Match`), Google Cloud Storage (generation
preconditions) and Cloudflare R2 document both. No provider has been
conformance-tested yet (tasks T1, T3). There is no transaction across two
objects, so every protocol below makes a single conditional write its
commit point. A local filesystem backend implements the same two
operations (`O_EXCL` create, rename under a lock) for tests and offline use.

### Actors and permissions

| Actor | Runs | Can write |
| --- | --- | --- |
| **Runner jobs** | Borg code, including candidate code from other projects | Nothing in the bucket. They return results as Actions artifacts |
| **Coordinator jobs**: `plan`/`dispatch`, `publish`/`finalize`, `reconcile` | Zoo code only | `blobs/`, `ledger/`, `control/`; no delete permission |
| **Index job** | Zoo code only, one concurrency group | `index/`, `site/` |
| **Retention job** | Zoo code only, dry-run by default | Deletes blob generations, through the blob protocol |

All claiming, acceptance and pinning happen in coordinator jobs, never in
runner jobs.

### Ingesting a zoo execution

1. **plan** writes the execution record with its closed expected manifest,
   create-if-absent, so a re-run of the same workflow attempt is a no-op. It
   then creates a lease for each work item ([below](#leases-and-acceptance)).
2. **Runner jobs** play their games and flush each finished game to local
   JSONL immediately (zoo rule 13). They upload batches and evidence as
   artifacts even when cancelled.
3. **publish**, for each runner artifact: registers and uploads blobs
   through the [blob protocol](#retention-pins-and-deletion), writes the
   batch, then its commit marker, then runs acceptance for each attempt.
   Publishing the same artifact twice is a no-op. A publish that dies midway
   leaves staged blobs without a commit, which the orphan sweep collects.
4. **finalize** writes `not_received` attempts for work items without an
   accepted attempt (invariant 3), and marks the execution closed.
5. **index** reads receipts and commit markers newer than its last
   generation, writes a new generation and builds the site from it. It is
   rebuildable from scratch.

Collectors of different executions write disjoint keys, so they do not race.

### Leases and acceptance

```text
control/leases/<work-item-id>.json
  {state: active|done|void, generation, epoch, holder, deadline, accepted?}
```

1. **Dispatch.** A coordinator creates the lease with `generation = 1`,
   `state = active`, the current epoch, the holder (workflow run, job
   attempt, shard) and a deadline equal to the runner job's timeout plus a
   margin. Runner jobs cannot outlive their timeout, so no renewal is
   needed.
2. **Takeover.** A coordinator may move an `active` lease to a new holder,
   by replace-if-unchanged with `generation + 1`, only if its deadline has
   passed **and** GitHub reports the holder's job finished. A `void` lease
   (after a restore) can be re-dispatched the same way. A `done` lease is
   terminal and never taken over.
3. **Commit point.** After an attempt's batch is committed, publish reads
   the lease and replaces it, conditional on that read's ETag, from
   `active(generation g, epoch e)` to `done(g, e, accepted: attempt ID and
   record hash)`. This succeeds only if the attempt carries the same `g` and
   `e`.
   - An **expired but uncontested** lease is still accepted: the deadline
     only permits takeover. Game results do not depend on the lease clock;
     the runner's own wall limit is an outcome.
   - If a **takeover happened** between the read and the write, the ETag
     no longer matches, and the attempt is recorded `superseded`.
   - If the lease is **already `done`** with this attempt, the step is a
     no-op; with another attempt, this one is `superseded` and an alert is
     raised.
4. **Receipt.** Publish then writes `ledger/receipts/<segment-id>.json`
   create-if-absent with the same content as the lease's `accepted` field.
   If it crashes between steps 3 and 4, any later publish or the
   `reconcile` job finds a `done` lease without a receipt and writes it from
   the lease. Re-writing an identical receipt is a no-op.
5. When the accepted attempt has a sealed checkpoint at the target turn,
   the next segment's work items become eligible.

Clock policy: deadlines are compared on the coordinator's clock, and a
takeover also needs the holder's job to be finished according to GitHub, so
clock skew cannot create two live holders. Worker loss is lease expiry;
retrying a crash is a new attempt with a new generation. Neither creates a
life.

### Publishing a checkpoint

1. The runner stops play at a command boundary at or after the target turn
   and writes the save, Borg state and RNG state *without* advancing the
   game ([RESUME.md](RESUME.md)).
2. Publish uploads each file through the blob protocol, verifies its hash
   by reading it back, and acquires a reference for the checkpoint.
3. It writes `ledger/checkpoints/<id>.json` create-if-absent, listing every
   blob, the state-format version, and the build, configuration and
   gameplay-contract IDs.
4. A checkpoint missing required state, for example Borg memory on an
   adapter that cannot save it, is written as `fresh-borg-only`. Resume
   refuses it as an exact continuation; a fork can start from it, labelled
   as one.

### Retention, pins and deletion

Every blob has a control record, created when it is first uploaded. Blobs
of a class kept forever become `live` and are never selected for deletion,
but an upload that is never referenced is still swept as an orphan.

```text
control/blobs/<hash>.json
  {state: staged|live|deleting|deleted, generation, refs_version, pins, staged_at}
```

- **Upload:** create the record as `staged` (or, if it is `deleted`, move it
  to `staged` with `generation + 1`), then upload to that generation's key.
- **Reference or pin:** replace-if-unchanged from `staged` or `live` to
  `live` with `refs_version + 1` (and the pin added). Only after this
  succeeds is the batch committed, the checkpoint sealed or the pin
  reported. If the record is `deleting`, the operation fails visibly; the
  caller re-uploads once it is `deleted`, or reports the evidence as
  unavailable.
- **Delete:** the retention job replaces `live` (unpinned, past retention)
  or `staged` (older than the grace period) with `deleting`, conditional on
  the version it read. That is the commit point: any reference or pin that
  started earlier either landed first, so the condition fails, or will fail
  on `deleting`. The job then deletes exactly that generation's key, moves
  the record to `deleted`, and writes a deletion receipt to the ledger.
  Generation keys are never reused.

Pins are ledger records (`pin {object, owner, reason}`) and unpins are
corrections, so retention decisions are auditable. Exports hold pins on
every blob in their manifest until they expire.

| Class | Default | Notes |
| --- | --- | --- |
| Ledger records, commit markers, receipts, corrections | Forever | Small: about 285 bytes per game, compressed |
| Configuration bytes, build manifests | Forever | Deduplicated by hash |
| Sealed checkpoints of lives in an active long-run arm | Until the arm is closed, then the last two per life | Owner can pin more |
| Last sealed checkpoint before a death, and the terminal save | Forever (cemetery) | The basis of U6 |
| Raw logs and traces of deaths, stalls and failures | Forever, compressed | About 190 KB per game measured; 38% of games today |
| Raw logs and traces of survivors | 90 days, unless pinned | Same as today's artifact retention |
| Build tarballs | Until no sealed checkpoint references the build, then 90 days | A checkpoint without its build cannot be resumed |
| Staged blobs never referenced | 7 days | Orphan sweep |
| Index generations, site, report caches | Last 3 generations | Rebuildable |

### Corrections

A correction is a ledger record `{supersedes: <record id>, reason, by,
replacement}`. The index applies the latest correction when computing
statistics and shows the chain on the record's page. Correcting a correction
is allowed; deleting one is not.

### Reports

A report job takes an explicit input set (an execution, an arm, a list of
lives), resolves it to acceptance receipts and the corrections in force,
writes those IDs and hashes with the analysis name and version and the
endpoint definitions, then stores the output as a blob. The same inputs and
version produce the same report identity. A report built from records that
were later corrected says so.

## Access and security

- **Public read** of `blobs/`, committed `ledger/`, `index/` and `site/`
  (decision D6).
- **Writes** follow the [actors table](#actors-and-permissions), with a
  repository secret or, where the vendor supports it, GitHub OIDC
  federation. GitHub documents OIDC for AWS and Google Cloud; other
  S3-compatible vendors need a scoped secret (T1).
- **Jobs that run Borg code get no credentials.** This also covers
  candidate code supplied by other projects.

## Backup and restore

- The bucket's object versioning or retention lock, where the vendor offers
  one, protects against a misused token.
- **Monthly portable export** to a second location: all acceptance
  receipts, then all commit markers and batches, then all checkpoint
  records, listed in that order. Because batches are committed before their
  receipts, every listed receipt finds its batch, so the export is coherent
  without stopping writers. It includes a manifest of the live blob
  generations it references, each pinned for the export's lifetime. Leases
  are not exported: `done` leases are reconstructible from receipts, and
  `active` ones are void after a restore.
- **Restore:** into a new bucket, or in place after voiding every non-`done`
  lease. First advance `control/epoch.json`. Every lease and acceptance
  carries the epoch, so a worker or publisher from before the restore cannot
  be accepted: its conditional write fails or its epoch is stale, and its
  attempt is `superseded`. Then rebuild the index from receipts and
  batches, and re-dispatch the void work items.
- **Restore drill** (M2 acceptance): restore an export into an empty bucket
  and compare the statistics with the live index. Restore while a pre-restore
  publisher is paused, and show that its result is superseded. Show that a
  checkpoint whose blob was removed is reported `unavailable`, never
  resumable.

## Cost estimate

Volumes from the [baseline](README.md#measured-baseline-2026-11-15),
projected to a year at about the current pace (2 to 3 million games). These
are list prices as published for 2025–26. Check them again before choosing a
vendor (task T1).

| Item | Year-one volume |
| --- | --- |
| Ledger | 0.6–0.9 GB compressed |
| Raw evidence | Evidence-retaining runs produced 4.75 GiB in nine days (about 190 KB per game). Deaths are 32% of games and failures, stalls and timeouts 6%, so keeping those forever and survivors for 90 days is about 75–100 GB in year one |
| Checkpoints | Per long-run arm, 1,800 lives × 4 checkpoints × 0.1–1 MB = 0.7–7 GB (Borg-state size unknown, see [RESUME.md](RESUME.md)) |
| Writes | About 1 batch per 1,000 games; per game a lease, its `done` update and a receipt (3 writes, so 6–9 million a year: roughly $25–40 a year at R2's listed $4.50 per million after the free tier); plus 2–3 per retained blob (control record, upload, reference) |
| Reads | Index and site files, served as static objects |

| Option | Rough monthly cost at about 100 GB |
| --- | --- |
| Cloudflare R2 | 10 GB free, then $0.015/GB-month, no egress charge: about $1–2 for storage, plus $2–4 a month for the per-game writes above |
| Backblaze B2 | $6.95/TB-month (listed 2026-11-15), free egress up to 3× stored: under $1 |
| Google Cloud Storage or Amazon S3 | About $0.02/GB-month plus internet egress at roughly $0.09–0.12/GB: $1–2 storage, more if large downloads are popular |
| Firestore (option C) | Free tier of 50k reads and 20k writes a day. A 9,000-game experiment written as one document per game uses about half the daily writes; with segments, attempts and observations as their own documents it exceeds them. Beyond the free tier writes cost about $0.18 per 100k; with three or more documents per game that is roughly $5–20 a year. Live dashboard reads cost per document read, so views must be precomputed. Storage needs the Blaze plan |
| Managed PostgreSQL (option D) | Free tiers hold about 0.5 GB and some suspend when idle; paid plans start around $5–25 a month |

Every option is cheap at this volume. Operational effort and fit with the
invariants matter more.
