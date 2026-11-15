# Plan: zoo and cemetery on the shared foundation

Part of the borg-zoo#114 proposal; see the [decision page](README.md). This
plan is for owner review. It authorises nothing: no account, no paid
provisioning, no cutover, no deletion, no new long cohort.

## Product redesign

### Zoo

| Area | Today | Proposed |
| --- | --- | --- |
| Ingestion | `collect` merges shard artifacts and pushes one directory to the `results` branch | `publish` writes blobs and record batches to the bucket idempotently; `finalize` records missing games explicitly; run jobs keep no credentials ([protocols](ARCHITECTURE.md#protocols)) |
| Site build | Reads every result ever recorded (2 min, 3 GiB); copies raw cells into Pages (991 MB) | Built from the derived index, adding only new batches. Raw records stay in the bucket and pages link to them |
| Versions, configurations | Catalogue labels plus the configuration-evidence reports | A page per build ID and per configuration ID, with the exact bytes, effective settings, and a diff between any two configurations |
| Experiment pages | Per workflow run, merged by tag | Per experiment snapshot. Executions are listed with the conditions that differ (date, runner image, harness, compiler), as rule 7 requires |
| Games | A row in a table | A life page: start, arm, segments, checkpoints, milestones, outcome, evidence available and its retention, links to cemetery case if it died |
| Long runs | A new experiment per cap, each replayed from birth | A **horizon ladder**: one arm, lives extended segment by segment. The page shows alive / dead / not reached / incomplete at each horizon, with resume status (claimed, sealed, pending, failed) |
| Reports | Hand-written report folders in `reports/` | Report records with their input set, analysis version and endpoints; rendered pages are a cache |
| Comparisons | Paired within one run, by harness kind and command-stream profile | Unchanged rules, computed from the index. A fork never pairs with its parent arm |

### Cemetery

| Area | Today | Proposed |
| --- | --- | --- |
| Cases | Directories `D0001…` in Git, with records and launchers | A case is a life whose terminal outcome is a death. Its ID is the foundation life ID; `D0007` becomes an alias |
| Browse | Registry pages and statistics in Git | A case index built from the zoo's index: seed, race, class, build, configuration, cause, depth, level, turn, and an **evidence column** (pre-death checkpoint, terminal save, logs, recording, Borg state), each marked available, unavailable or expired |
| Stalls and failures | Separate, sometimes mixed into runs | Listed as their own case types, never as deaths (issue requirement) |
| Evidence | Curated saves in Git, recordings as release assets, the rest in 90-day artifacts | Blobs in the bucket, with the retention rules for deaths ([retention](ARCHITECTURE.md#retention)). Git keeps tools and small reviewed fixtures |
| Replay | Saved-position benchmark with a fresh Borg; full recorder replays for two cases | Two labelled modes: fresh-Borg from the last pre-death checkpoint (available once C1 lands), and exact continuation through the recorded death (once the adapter passes [qualification](RESUME.md#qualifying-a-resume-as-faithful)). Diagnostic and counterfactual replays are forks |
| Downloads | Per-case launchers in Git, release bundles | A portable case bundle generated on demand: manifest, blobs, build reference and launchers, each verified by hash. Inspecting a bundle never runs its launchers |
| Analysis | Death analysis documents | Unchanged in purpose. Reports become report records, so a later analysis can say what it read |

### Relation to cemetery PR #2

[PR #2](https://github.com/diegoami/borg-cemetery/pull/2) proposes the
cemetery's encounter laboratory: episodes, scenario revisions, danger
qualification, studies and per-build assessments, on Firebase. This plan
keeps that domain model as the cemetery's own and changes what sits under
it:

- Source cases, attempts, builds, configurations, checkpoints and artifacts
  in PR #2 become **references to foundation entities**. The cemetery stops
  defining them separately, which removes a second identity scheme and
  answers PR #2's review finding R4.
- PR #2's study and assessment records, leases and pins are cemetery
  application state. They can live as cemetery ledger records in the same
  bucket. If the cemetery later needs multi-user workspaces with private
  data, it adds a service store (Firestore or PostgreSQL) over the same
  ledger, as the [recommendation](README.md#recommendation) describes.
- The Firebase backend section of PR #2 is then a cemetery-service option,
  not the shared foundation. That is owner decision D1.

## Cutover and salvage

### What exists

| Data | Volume | Quality | Expires |
| --- | --- | --- | --- |
| Zoo cell records (`results` branch) | 219,795 games, 107 runs | Outcome, seed, birth, build hashes and effective settings on most. 22,029 (10%) lack `config_sha256`. No segments or checkpoints | Never (Git) |
| Zoo raw evidence artifacts | 4.75 GiB, 22 runs, about 25,000 games with per-file hashes; 16,254 list a save | Saves exist, but no Borg memory. Some are *final* saves (dead or at the cap), not pre-death checkpoints | From **2027-02-06** |
| Zoo build artifacts | 2.7 GiB | Rebuildable from pinned source | 7 or 90 days |
| Cemetery dossiers D0001–D0007, scenarios S0001–S0003 | 13 MB in Git (deaths 2.9 MB, scenarios 2.2 MB, statistics 8 MB) | Curated, reviewed, some with saves, two with full recordings | Never |
| Cemetery recordings (release `recordings-2026-11-15`) | Two bundles | Replay-verified | Never |

### Options

| Option | Scope | Effort | Consequences |
| --- | --- | --- | --- |
| **Clean start** | Freeze `results` and the current site as read-only legacy. The new system starts with the first new execution | None beyond freezing | Dashboard history resets; old comparisons remain readable at a legacy path. Raw evidence expires on schedule |
| **Selective salvage** (recommended) | Clean start, plus: import cell records of runs with complete build and configuration hashes as `imported` lives (one segment, `evidence: hashes-only`); import the raw evidence of death cells from the 22 retained runs before 2027-02-06; import the cemetery's seven dossiers and two recordings as legacy cases with their aliases | 1–2 days | The new dashboard can show the existing comparisons, labelled as imported. Deaths from retained runs keep their final saves and logs for the cemetery. No checkpoint or resume claims for imported lives |
| **Broad migration** | Everything, including runs without configuration hashes, survivor evidence and reconstructed provenance | 5–10 days | Mostly incomplete records and guessed provenance, which invariant 11 forbids. Not recommended |

Salvage labels every imported record with its source path and Git or
artifact revision, and verifies every byte against the hash the original
record lists. Runs without configuration hashes are imported only if the
owner asks, labelled `configuration: unknown`.

### Concrete cutover steps

1. Freeze: stop `collect` writing to `results`; keep the branch untouched.
2. Snapshot the current site to a `legacy/` path or a separate Pages
   deployment.
3. Run salvage (if chosen) and verify hashes.
4. Switch `compare.yml` to `publish`/`finalize`/`index`; switch Pages to the
   index-built site.
5. Turn on retention and backups, and run a restore drill.

**Destructive or link-breaking actions.** Step 4 changes public URLs: raw
cell files no longer sit under `runs/` on Pages. Step 2 decides whether old
links keep working. Nothing here deletes `results`, cemetery records or
artifacts; artifacts expire on GitHub's schedule as they do today. Any later
deletion is a separate owner decision.

## Milestones

Estimates are focused working sessions of about a day. Each milestone ends
with a review pull request; the owner chooses and runs the reviewer.

| Milestone | Delivers | Acceptance | Estimate |
| --- | --- | --- | --- |
| **M0 Decisions and urgent fix** | Owner decisions D1–D7; T0 (Pages size); T1 (vendor check) | Pages deploy stays under 1 GB with the next large experiment; decisions recorded on #114 | 0.5–1 |
| **M1 Contracts** | Schemas `borg-data/*@1`; canonical JSON and identity functions; a local filesystem backend with create-if-absent and replace-if-unchanged; the invariant test suite | Tests for every [invariant](ARCHITECTURE.md#invariants): idempotent re-ingest, conflict on altered bytes, explicit missing games, corrections, no double counting across segments and forks, censoring at horizons | 2–3 |
| **M2 Storage prototype and benchmark** | S3 backend tested against a local MinIO and one bounded bucket on the chosen vendor (owner approval); ingest all existing cells ledger-only; index and site built from it | Ingest, index and site-build times and sizes against the baseline; killed-publish and duplicate-publish fault injection; restore drill from an export into an empty bucket; finalised decision page with measured numbers | 2–3 |
| **M3 Resume qualification** (mostly upstream) | Change requests C1, C2, R1, R2 routed by the owner; spike S1; the [qualification protocol](RESUME.md#qualifying-a-resume-as-faithful) on reborn, then on native C | A qualification report per adapter: exact continuation passes, or the missing state is listed and the adapter is fresh-Borg-only | 3–6 here, plus upstream work |
| **M4 Zoo on the foundation** | `publish`/`finalize`/`index` jobs in `compare.yml` and `smoke.yml`; site from the index; life, build and configuration pages; horizon ladder and resume queue behind a flag | One smoke experiment produces the same statistics through the old and the new path; an interrupted shard is published and finalised correctly; two concurrent executions publish without conflict | 3–4 |
| **M5 Cemetery on the foundation** | Case index, evidence column, pre-death checkpoint retention, case bundles; PR #2 rebased onto foundation IDs | A death from M4 appears as a case with its checkpoint and logs; its bundle downloads and verifies offline; a stall appears as a stall case, not a death | 3–5 |
| **M6 Cutover** | Steps 1–5 above; salvage if chosen; runbook | Legacy site reachable as decided; new site live; backup and restore exercised on production data | 1–2 |
| **M7 First long-run pilot** (owner-started only) | A small arm, for example 60 lives extended 100k → 200k → 300k by resume, on a qualified adapter | Ladder page correct; no life counted twice; every segment failure visible | Owner's call |

Total: about 15–25 working days in this repository, plus the upstream
resume work, which is the longest item and is not under the zoo's control.
M1, M2 and the C1/C2 requests can start in parallel. M4 needs M2. M5 needs
M4. M7 needs M3 and M4.

## Follow-up tasks

Each becomes an issue in the repository named, once the owner agrees.

| # | Repository | Task |
| --- | --- | --- |
| T0 | borg-zoo | Stop copying raw `cells.jsonl` into Pages (link to the `results` branch file or ship a gzipped copy). Independent of this redesign, and urgent |
| T1 | borg-zoo | Check current prices, free tiers, conditional-write semantics and OIDC support of the candidate vendors; record in the decision page |
| T2 | borg-zoo | Schemas and identity library (M1) |
| T3 | borg-zoo | Filesystem and S3 backends with conformance tests (M1, M2) |
| T4 | borg-zoo | Ledger ingest of the existing `results` branch; index and site from it (M2) |
| T5 | borg-zoo | `publish`, `finalize` and `index` jobs (M4) |
| T6 | borg-zoo | Life, build, configuration and horizon-ladder pages (M4) |
| T7 | borg-zoo | Resume executions: segment lists, leases, workers (M4, after M3) |
| T8 | borg-cemetery | Case index and evidence column over the foundation (M5) |
| T9 | borg-cemetery | Case bundle format and offline verification (M5) |
| T10 | borg-cemetery | Rebase PR #2's model on foundation IDs (M5) |
| T11 | borg-zoo | Salvage import and verification, before 2027-02-06 for raw evidence (M6) |
| C1–C4 | better-borg-c | Named checkpoints, resume entry point, Borg memory and RNG serialisation, frozen calendar ([RESUME.md](RESUME.md#what-is-missing-by-owner)) |
| R1–R2 | borg-reborn-rs | Rust Borg and plan state serialisation, checkpoint manifest; coordinate with #320 |
| N1 | Mandos | `zoo-run` checkpoints, when a Neo long run is planned |
| S1 | borg-zoo | Process-snapshot (CRIU) spike for the native C runner |

## Risks

| Risk | Effect | Mitigation |
| --- | --- | --- |
| Exact Borg-memory restore is large upstream work, especially for C | Long runs without replay from birth are delayed or limited to fresh-Borg forks | Reborn first; spike S1; fresh-Borg restart as a labelled protocol if the owner accepts it (D4) |
| Pages exceeds 1 GB before T0 lands | Site deploy fails | Do T0 first, before the next large experiment |
| Raw evidence expires (from 2027-02-06) | Saves and logs of existing deaths are lost | Decide D3 by January; run T11 early if salvage is chosen |
| Conditional-write semantics differ between vendors | Lease or idempotency bugs | Conformance tests in T3 run against each backend, including the filesystem one |
| Calendar dependence (24–26 December) | Resumes or comparisons that straddle that window differ | Record the calendar per attempt now; frozen calendar (C4, D5) for long runs |
| Two designs for the cemetery (this and PR #2) | Duplicate identity schemes | D1 decides; T10 rebases |
| Vendor account or token compromise | Data written or deleted | Prefix-scoped tokens without delete, versioning, monthly exports |
| Concurrent sessions on the owner's machine | Benchmarks and qualification disturb other work | Heavy local runs take `/tmp/angband-validation.lock` (rule 9) |

## Owner decisions

| # | Decision | Recommended |
| --- | --- | --- |
| D1 | The shared foundation is the base for both repositories, and PR #2's backend becomes a cemetery-service option on top of it | Yes |
| D2 | Storage: an S3-compatible bucket (which vendor, and whether a few dollars a month is acceptable), or Git only | A bucket; vendor after T1 |
| D3 | Cutover: clean start, selective salvage or broad migration | Selective salvage |
| D4 | Allow fresh-Borg restart as a separately labelled long-run protocol until exact resume is qualified | Owner's call; it measures something different |
| D5 | Frozen calendar for long runs (changes measurement conditions) | Yes, once C4 exists |
| D6 | Are saves and logs public, like the results today? | Public, unless a class needs privacy |
| D7 | Keep legacy URLs working (snapshot the current site), or let old `runs/` links break | Keep a legacy snapshot |
