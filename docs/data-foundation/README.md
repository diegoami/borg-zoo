# Shared data foundation for the zoo and the cemetery (borg-zoo#114)

Status: **proposal for owner review.** Nothing in it provisions a service,
opens a paid account, changes a running experiment, stops writing the
`results` branch, or deletes any record. Every such step is an owner decision
listed in the [plan](PLAN.md).

| Document | What it covers |
| --- | --- |
| This page | The decision: measured baseline, requirements, options, recommendation |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Use cases, entities and identities, invariants, storage layers and protocols |
| [RESUME.md](RESUME.md) | Checkpoint/resume: what each runner can do today, what is missing, how to prove a resume is faithful |
| [PLAN.md](PLAN.md) | Zoo and cemetery redesign, cutover and salvage options, milestones, tasks, risks, owner decisions |
| [baseline/](baseline/) | The script and numbers behind the baseline below |

The cemetery's own architecture proposal
([borg-cemetery PR #2](https://github.com/diegoami/borg-cemetery/pull/2),
head `ca7f62b`) is an input. Its encounter, scenario, study and assessment
model stays the cemetery's. This foundation sits underneath it: the games,
segments, checkpoints, builds, configurations and blobs that both
repositories point at. The [plan](PLAN.md#relation-to-cemetery-pr-2) says how
the two fit together.

## Measured baseline (2026-11-15)

Measured on the owner's machine against `results` at `d7b05dc5` and zoo
`main` at `a0f000c`. Reproduce with [baseline/](baseline/).

| Quantity | Value |
| --- | --- |
| Workflow runs on `results` | 107 runs, 93 experiments, 107 commits |
| Cells (games) | 219,795, recorded in about nine days (2026-11-07 to 11-15) |
| `results` tree, uncompressed | 775 MiB in 275 files; Git pack 89 MiB |
| Largest single file | `rs-pr85-full/43720870587-1/cells.jsonl`, **87.7 MB**: GitHub refuses files over 100 MB |
| All cells as one gzip stream | 60 MiB (12.4×, about 285 bytes per cell) |
| Same, gzipped one record at a time | 294 MiB: compress in batches, not per record |
| Site build (`python3 -m zoo site`) | **2 min 08 s, 3.0 GiB peak RSS** |
| Site output | **991 MB**, 987 MB of it copies of raw `cells.jsonl` under `runs/`. GitHub Pages documents a 1 GB limit for a published site |
| Pages workflow | 2.5–6 min per deploy (last 8), one per collect |
| Live Actions artifacts | 3,614 artifacts, about 9 GiB: raw evidence 4.75 GiB (22 workflow runs), builds 2.7 GiB, cells 72 MiB |
| Cells that list per-file evidence hashes | 25,382; 16,254 of them list a save file |
| Earliest raw-evidence expiry | **2027-02-06** (90-day retention); cells artifacts keep 30 days, builds 7 or 90 |
| Cells without `config_sha256` | 22,029 (10%), older runs |
| Outcomes | turn cap 61.9%, death 32.2%, harness failure 5.4% (11,798; 11,736 of them "no record collected" because a job failed or was cancelled, 11,700 in four runs), wall timeout, stall and crash 0.6% |
| Compare runs (last 100) | 90 success, 9 cancelled |

Indexing all 219,795 cells in SQLite (scalar fields plus a pointer to the full
record) took 15.5 s to load and 0.3 s to index. The scalar index is 141 MiB, or
32 MiB gzipped. The dashboard queries took:

| Query | Time |
| --- | --- |
| Outcome summary for every arm of every run (331 arms) | 41 ms |
| Per-class summary of the largest run | 12 ms |
| Paired rescued/newly-killed counts, two arms of one run | 20 ms |
| One seed's history across all runs | 0.3 ms |
| Fetch and decompress one full cell record | 7 ms |

### What the baseline says

1. **Query speed is not the problem.** A single-file embedded index answers
   every dashboard question in milliseconds at today's volume, and would at
   ten times it. A hosted query database is not justified by latency.
2. **The site is about to break.** It copies every raw cell file into Pages,
   so its size tracks the whole results branch. One more large experiment
   takes it past 1 GB. This needs a fix now, independent of this redesign
   (task T0 in the [plan](PLAN.md)).
3. **Single files are near GitHub's 100 MB limit.** A 9,000-cell run with
   evidence hashes is already 88 MB.
4. **Raw evidence and saves are not durable.** Saves, logs and traces exist
   only as Actions artifacts that expire after 7 to 90 days. Nothing can be
   resumed or investigated after that.
5. **Every rebuild reads everything.** The site build is linear in all
   results ever recorded: 2 minutes and 3 GiB now.
6. **Concurrent collectors race.** `collect` pushes to one branch with no
   retry, so two experiments finishing together can fail one push.
7. **There is no claim or lease primitive.** Resuming 1,800 games over many
   jobs needs one, and the current store cannot provide it.

## Requirements

Ranked by what the owner asked for and what the baseline shows.

- **R1 Durable blobs.** Saves, Borg state, logs and traces kept by content
  hash, beyond Actions expiry, with explicit retention.
- **R2 Atomic checkpoints and resume claims.** A checkpoint can be used only
  after every blob it needs is stored and verified. One worker at a time
  holds a segment, and a stale worker cannot overwrite a newer result.
- **R3 Append-only, idempotent ingestion.** Re-running a collect writes
  nothing new. Different bytes under an existing identity are refused.
  Missing attempts are recorded explicitly.
- **R4 Lives, not rows.** One identity per game, with ordered segments and
  checkpoints and one terminal outcome. A life is never counted twice.
- **R5 Exact identity.** Builds, configurations (bytes and effective
  settings) and experiment snapshots are hashed and immutable.
- **R6 Public read without login.** Reports and evidence stay readable
  without an account. Writes come from trusted jobs only.
- **R7 Bounded build time.** The site and reports are built from an index,
  not by reading every record.
- **R8 Portability.** The whole store can be exported in an open format and
  rebuilt elsewhere, with no lock-in to one vendor's query language.
- **R9 Low operating effort and cost.** One owner, no on-call. Free or a few
  dollars a month at the measured volume.

## Options compared

| | A. Git only, restructured | B. Object-storage ledger + derived index | C. Firestore + Cloud Storage | D. Managed PostgreSQL + object storage |
| --- | --- | --- | --- | --- |
| Authoritative metadata | Small compressed records sharded in Git | Immutable record batches in a bucket | Firestore documents | PostgreSQL rows |
| Blobs | Release assets | Same bucket, by content hash | Cloud Storage for Firebase | Bucket |
| R1 durable blobs | Weak: release assets are mutable and a release holds a limited number of assets | Yes; versioning or object lock | Yes; needs the Blaze (billing) plan | Yes |
| R2 atomic checkpoint, claims | Refs as compare-and-swap through the API: works, but awkward and rate-limited | Conditional create/replace (`If-None-Match`, `If-Match` or generation match; vendor support to confirm in T1) | Transactions, but no transaction spans Firestore and Storage | Transactions, unique constraints, `SKIP LOCKED` queues |
| R3, R4, R5 invariants | Application code | Application code; deterministic keys make them simple | Application code ([PR #2](https://github.com/diegoami/borg-cemetery/pull/2) says so) | Mostly the schema |
| R6 public read | Yes | Yes: a public bucket or CDN serving the index and site | Rules or an API; live reads cost per document | Needs an API or static exports |
| R7 analytics | Derived index | Derived index (SQLite/Parquet) | No aggregate joins; exports needed for paired statistics | SQL; still export for the static site |
| R8 portability | Full | Full: S3 API, JSONL, Parquet/SQLite | Export format is Firestore-specific | `pg_dump`, but needs a server to read it |
| R9 effort | None new, but fighting Git limits | One bucket, one write token | Google project, billing, rules, indexes, Cloud Run | A database to keep up, migrations, connection secrets |
| Fit for cemetery multi-user workspaces | Poor | Adequate for one owner; add a service later if needed | Good (Auth, per-workspace rules) | Good with an API |

Firebase Realtime Database is not a candidate: it is a single JSON tree
without compound queries, as PR #2 also concludes.

**Cost is not the deciding factor.** At the measured volume every option is
free or a few dollars a month (see the
[cost estimate](ARCHITECTURE.md#cost-estimate)). The list prices there come
from published price sheets; check them again before choosing a vendor (task
T1).

## Recommendation

**Option B: an immutable ledger and content-addressed blobs in one
S3-compatible bucket, plus a derived SQLite/Parquet index rebuilt from it.**
Git keeps code, catalogue, schemas and small reviewed fixtures. The `results`
branch is frozen as read-only legacy at cutover.

- It meets R1 to R3 with two primitives that Amazon S3 and Google Cloud
  Storage document (others to confirm): write-once objects and conditional
  replace. These give idempotent
  ingestion, atomic checkpoint publication and fenced resume leases
  ([protocols](ARCHITECTURE.md#protocols)).
- The index is disposable. Losing it costs one rebuild, measured at seconds
  today.
- Public read is a bucket or CDN path. Nobody needs an account to view a
  report.
- The S3 API means the vendor can change by copying the bucket.
- The storage contract is the same for the zoo, the cemetery and any later
  tool: the [entity model](ARCHITECTURE.md#entities-and-identities) does not
  depend on the backend.

**When to add a database.** Add PostgreSQL (D), not Firestore, as a
*derived* service store if any of these is measured: lease contention
between resume workers that conditional writes cannot keep up with, a
cemetery that must serve several users with private workspaces, or
interactive queries the static index cannot answer. The ledger stays the
authority, so adding one is not a migration. Firestore (C) stays a
reasonable choice for the cemetery's multi-user service layer if the owner
prefers its Auth and managed operation. It is a poor fit for the zoo's paired
statistics, which need joins over hundreds of thousands of games.

**If the owner wants no external account,** Option A works for metadata at
this scale: the compressed ledger is about 285 bytes per game. It does not
meet R1 or R2 well. Long-run resume would stay limited to saves kept in
release assets, and claims would use Git refs.

**What a database does not solve.** Faithful resume needs runner support
that does not exist yet in any adapter: Borg memory and Borg RNG are not
saved by the native C runner, borg-rs/reborn or Mandos. That work is
separate from the storage choice and is the main schedule risk
([RESUME.md](RESUME.md)).
