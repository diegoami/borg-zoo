# Experimental Neo parity-and-books arm

Owner requested a new Borg build and Zoo arm, smoke first, on2026-11-16.
The fork candidate is version1.4.0-beta.6.zoo.1, source
464a1555ca73cf662b522f020152faa9d1a2d465, [source PR113](https://github.com/diegoami/neo-angband-borg-mod-tracker/pull/113).
It combines the six Neo514–519 fixes from [integration112](https://github.com/diegoami/neo-angband-borg-mod-tracker/pull/112)
with the existing carried-book value correction509 (upstream113/fork104).
This is an experimental fork build, not an official upstream release or tag.
Source proposals and fork master are not merged by this experiment.

## Conditions

- Specimen:neo-b4-parity-books-v1.
- Source:464a1555ca73cf662b522f020152faa9d1a2d465.
- Engine:officiald27ed50f9e3b650a43cceda5a0c007d03cc321df, beta.4/API2.1.
- Toolkit:638979da690891c11da1c1e780631828953b03d7, beta.4 SDK build-path correction; message/truth/session bytes unchanged from967b28f.
- Explicit c-seeded-point-buy-v2 birth, no-selling, C native-menu startup seed,
  GCC coordinate-order adapter and exact tick cap.
- Existing default Borg profile; no class-specific tuning or mode change.
- All cells and raw command/message/state/run streams retained. Timeouts,
  stalls and harness/configuration failures stay separate from deaths.

The old book-corrected run43759670685 used engine forkb4af703 (beta.3) and
older source d6215a8. The current Borg requires API2.1, so the new engine is
the verified compatible beta.4 pin. Engine, Borg and calendar differences
must be disclosed; this is not a six-fix-only controlled comparison or a
population improvement claim. Clock issue neo-angband-tracker640 remains.
Old frozen suites and all old results remain unchanged.

## Sequential acceptance and dispatch

1. Source ordinary/exact-source1363-case gates, type/plugin and real truth-host
   checks must pass. Local91 focused book/parity/version checks and31 routing
   controls passed. The first exact-source attempt exposed a missing combat
   field in the imported book-test model;464a155 completes the fixture with
   the unarmed combat frame. Assertions, seeds and gameplay bytes are unchanged.
2. Run smoke/neo-b4-parity-books-smoke-18-v1.json:18fresh starts, two per class,
  5000ticks,600seconds, two shards, two processes/job, maximum four jobs.
3. Inspect all18endpoints, actual race/class/options/settings, source/engine/
   toolkit and bundle hashes, raw-file receipts and durable truth-use journals.
   Check book retention and class-appropriate casting. A natural death is a
   gameplay endpoint, not a build failure; no-cast alone does not condemn a
   late-learning class. Every abnormal endpoint needs explicit assessment.
4. Only after acceptance, dispatch experiments/neo-b4-parity-books-v1-1800.json.
   It reuses the existing frozen1800assignments (200/class),100000ticks,
  600seconds,36shards, two processes/job and four concurrent jobs. Each shard
   has50games; its worst-case child budget is250minutes below the300-minute
   job timeout. Do not start alongside another active experiment.

The full arm is authorized by this request but must not run alongside the
smoke or before its evidence is accepted. There is no recurring automation,
unattended source watcher, local game/cohort or consumer/lab deployment.
Acceptance and run IDs will be appended here after the smoke completes.

## First smoke build and corrected toolkit pin

[Smoke43861106244](https://github.com/diegoami/borg-zoo/actions/runs/43861106244)
stopped before any game ran. The old967b28f builder aliases the SDK root as a
file prefix and resolves backup-policy below index.js, which cannot load.
The already-tested638979d toolkit adds the explicit backup-policy alias and
anchors the SDK-root match. Its run/session/message-host/truth-host files
are byte-identical to967b28f. No gameplay, source, engine, seed or cap changes.
The failed run is preserved; acceptance needs a fresh smoke on the corrected
catalogue pin. Source464a155's full1363-test ordinary/exact-source gates and
production truth-host checks passed in run43860178921.

## Accepted smoke

[Corrected smoke43861787363](https://github.com/diegoami/borg-zoo/actions/runs/43861787363)
completed on immutable catalogue2de7975d6939bc6139874fa09a50071f2d186825:
18/18 exact5000-tick caps, zero deaths/stalls/timeouts/harness/config errors.
All18entered the dungeon; one Necromancer reached depth2. All108 inventoried
raw files and both archive checksums were verified, as were assigned births,
actual options/settings, source/engine/toolkit and durable truth-use receipts.
Bundle SHA256:7805b062c6b867dbf3967f75d9db34cd9e965ef963a0bff23d9a40fc76f8c1ac.
All16casters retain the starting book. Mage cast attempts6/7, Priest9/10,
Necromancer5/7; short Druid/Rogue/Ranger runs do not establish casting eligibility
or success. This is acceptance of the measurement, not a survival result.

Machine-readable receipt: [smoke-43861787363-acceptance.json](smoke-43861787363-acceptance.json).
Recheck downloaded artifacts with `python3 reports/neo-parity-books-v1/verify-smoke.py
--artifacts ARTIFACT_DIRECTORY --catalogue CATALOGUE_CHECKOUT --out OUTPUT.json`.
The script verifies identities/hashes and leaves outcome acceptance to review.
Source1363-case ordinary/exact-source gates and catalogue172unit/113plan checks
are green. The full arm is ready; dispatch must respect the no-overlap rule
and preserve the exact accepted source/engine/toolkit/configuration.
