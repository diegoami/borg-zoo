# Checkpoints and resume: adapter audit and qualification

Part of the borg-zoo#114 proposal. Storage can make a checkpoint durable and
claimable ([ARCHITECTURE.md](ARCHITECTURE.md#protocols)). Whether resuming it
plays the *same game* depends on the runner, and no runner can do that yet.
This page records what each adapter can do today, what is missing, and how
to prove a resume faithful rather than assume it from a save that loads.

## Three different things

| Mode | What is restored | Counts as |
| --- | --- | --- |
| **Exact continuation** | Game save and game RNG, *and* the Borg's memory, Borg RNG, plan/controller state and pending decisions, under the same build, configuration and calendar | The same life. Only allowed after qualification shows it plays exactly what an uninterrupted run plays |
| **Fresh-Borg restart** | Game save and game RNG; the Borg starts from scratch on the loaded position | A fork: a new life with `lineage: fork`, its own arm and execution contract. It can be a defined long-run protocol in its own right ("Borg restarted at 100k"), but it is never the same life and never pairs with an uninterrupted arm |
| **Prefix replay** | Re-run the recorded input from birth to the checkpoint | A verification oracle, not a way to save time. Rebuilding the Borg's memory needs the Borg to think through the whole prefix, which costs as much as playing it |

## What each adapter can do today

Read at the pins the zoo uses or at the repositories' current heads, as
noted. Every "unknown" is a question for the qualification below, not a
conclusion.

### Native C: better-borg-c runner and observer

Read at the zoo's harness pin `9ca98661` (and unchanged at better-borg-c
`7c942f70`).

| Need | Today |
| --- | --- |
| Save without disturbing play | Yes. `snapshot()` saves in a `fork()`ed child, so the live process never runs the save code (native saving compacts the monster list) |
| Checkpoints | `start.save` at birth, and `recent.save` every 1,000 game turns, **overwritten each time**. Only the latest survives a run |
| Save at a chosen turn | No. There is no 100k/200k checkpoint; only the rolling one |
| Load a save | `measure-native.py --load` (described as "diagnostic load; continuation reproducibility is not assumed"); `--play-turns` runs a bounded number of extra turns and writes `final.save` |
| Game RNG | The 4.2 save writes and reads the RNG (`wr_randomizer`, `rd_randomizer`). The observer seeds the RNG with `Rand_state_init(seed)` before the load. Whether the loaded state then replaces it is **unverified** |
| Borg memory | **Not saved.** The runner says so: "Native save restored; complete Borg memory is not serialized". The C Borg keeps its memory in many globals (tracked objects, monsters, item knowledge, danger caches, timers) |
| Borg RNG | `borg_rand_local` is logged in every state line but not saved. A fresh `borg_init` sets it with `randint1()` **from the game RNG**, so a fresh-Borg restart consumes a game RNG draw that an uninterrupted run would not |
| Calendar | System clock, recorded per run. `mon-make.c` allows seasonal monsters only on **24–26 December** (local time). A game that crosses that window plays differently depending on the wall-clock date |

### borg-rs and borg-reborn-rs: the `borgh` frontend

Read at borg-reborn-rs `ec9058d1` (`engine/frontend/main-borgh.c`,
`harness/run.sh`).

| Need | Today |
| --- | --- |
| Checkpoints | `-checkpoint-every N -checkpoint-dir DIR`: a save at the first game-command boundary at or after each multiple of N |
| Load | `-load FILE` (a living save), and `-keep-load-rng` to keep the save's RNG instead of reseeding. `check-extra-load.sh` checks in CI that a load replays the same keys as `save=NAME` |
| Stop exactly at a turn | `exact_turns` (the `-exact-turns` stop) |
| Final saves | `-save-living-on-stop`, `-save-on-stop`, `-save-final-state` |
| Calendar | `run.sh` fixes `TZ=UTC` and the locale; the date itself is the runner's clock |
| Rust Borg memory | Not restored. The Rust Borg's knowledge, world and danger types derive serde `Serialize` (used for traces), which suggests serialising its memory is feasible; no restore entry point was found |
| Plan state | The errands-plan proof of concept (borg-reborn-rs#305, PR #308) adds plan bytes, selected class and phase, cancellation and owner state, loop target and direction, town-detour state and pending decisions. All of these must be in the checkpoint ([comment on #114](https://github.com/diegoami/borg-zoo/issues/114)). The proof of concept refuses measured-harness plan runs until plan-aware identity exists |
| C Borg inside the reborn tree | Same as native C: no memory serialisation |

### Neo original and Neo forks: kind `neo-original`

The zoo's current Neo measurements (`zoo/neo_original.py`). Read at the
newest measured triple, specimen `neo-fork-76f25aa-seeded-v2`: Borg
`967b28f5`, engine diegoami/neo-angband-tracker `b4af7034`, toolkit
diegoami/neo-angband-borg-mod-tracker `967b28f5` (`tools/zoo/run.mjs`,
`session.ts`). Older specimens use the tracker's `tools/original-borg`
toolkit at `2668adc5`.

| Need | Today |
| --- | --- |
| Checkpoints, load, resume | None: the runner and session have no save, load or checkpoint path |
| Evidence per game | `commands.jsonl`, checked against the record's `playSha256`, plus `stdout.log` and `stderr.log`. Kept only in the raw-evidence artifact of evidence-retaining runs |
| Stop boundary | `after-key`; a death after the cap is recorded as `turn_cap` with `died_after_cap` |
| RNG | The alignment profile reads RNG state for observation only; Neo keeps a separate Borg RNG |
| Existing issues | Same engine seam as below (neo-angband-tracker#7, closed); nothing in the fork's toolkit |

Neo resume is **deferred**: no Neo long run is planned. Until then these
runs are ingested as lives with one segment from birth, evidence level
`commands` when `commands.jsonl` was retained and verified, otherwise
`hashes-only`, and checkpoints `unavailable`. Their identity is the
neo-original build triple (Borg, engine, toolkit), never Mandos's.

### Mandos: `tools/zoo-run.mjs`

A separate adapter (kind `mandos`). Read at better-borg (Mandos) `d32b69f`.

| Need | Today |
| --- | --- |
| Checkpoints, load | None in the `mandos/zoo-run@1` entry point |
| Controller RNG | `rng.snapshot()` exists and the controller captures it in memory |
| Engine save | Unknown in the headless profile; the Neo engine comes from npm |
| Borg memory | Plain TypeScript objects, with some `Set`s; serialisable in principle, nothing implemented in `zoo-run` |
| Existing issues | The engine seam that lets `ModSaves.load` resume a mod's controller was accepted upstream (neostryder/neo-angband PR #442) and imported; [neo-angband-tracker#7](https://github.com/diegoami/neo-angband-tracker/issues/7) is closed. Its Mandos adoption, [mandos#130](https://github.com/diegoami/mandos/issues/130), and the save-carrying stage ladder, [mandos#26](https://github.com/diegoami/mandos/issues/26), were **parked by the owner on 2026-11-06**. Whether that seam restores the Borg's memory, or only re-arms the controller, is not established here |

## What is missing, by owner

The zoo does not change Borgs (zoo rule 1). Each item below is a change
request, routed by the owner to the repository named.

As of 2026-11-15 **no issue exists for saving or restoring the C or Rust
Borg's memory.** [borg-reborn-rs#320](https://github.com/diegoami/borg-reborn-rs/issues/320)
lists it as part of its longer-run evaluation and points here. The Neo
issues are in the Mandos audit above.

| # | Repository | Change | Needed for |
| --- | --- | --- | --- |
| C1 | better-borg-c | Keep named checkpoints at requested turns (for example `--checkpoint-at 100000,200000`), not only the rolling `recent.save` | Any resume, fresh-Borg forks, cemetery pre-death checkpoints |
| C2 | better-borg-c | A resume entry point: load save and RNG, check that the RNG state after load equals the one recorded at the checkpoint, and report it | Fresh-Borg restart now; exact continuation later |
| C3 | better-borg-c | Serialise and restore the C Borg's memory and `borg_rand_local`, versioned. This is the large item: it touches most of `src/borg/` | Exact continuation of C specimens |
| C4 | better-borg-c | Optional frozen calendar (for example running under libfaketime, or an observer hook for `time()`), recorded in the build or execution contract | Resume across days; reproducibility around 24–26 December |
| R1 | borg-reborn-rs (and borg-rs if still measured) | Serialise and restore the Rust Borg's memory, plan and controller state, versioned; with a `-resume` that refuses a mismatched build, configuration or plan hash | Exact continuation of Rust specimens; plan-aware long runs (#320) |
| R2 | borg-reborn-rs | A checkpoint manifest naming every file written and its hash | Atomic publication |
| N1 | Mandos | Checkpoint and resume in `zoo-run` (engine save, controller and Borg state), building on the parked mandos#130 and #26 | Mandos long runs. Lowest priority: no Neo long run is planned, and that work is parked |
| N2 | neo-angband-borg-mod-tracker (toolkit `tools/zoo`) | Checkpoint and resume in the fork's runner, for the neo-original specimens | Neo-fork long runs. Deferred for the same reason |

**A shortcut to evaluate for C (spike S1).** A process-level snapshot, for
example CRIU, would restore the whole running game *and* Borg without
changing Borg code. That would make exact continuation correct by
construction. The open questions are whether it works on GitHub's hosted
runners (it needs elevated privileges), whether an image taken on one runner
restores on another (kernel and CPU features), its size, and its open trace
and log files. The spike runs a few seeds locally and on one runner. If it
passes, it can stand in for C3 for measurement purposes, labelled with its
own state-format version.

## Qualifying a resume as faithful

Run once per adapter and state-format version before any measured long run
uses resume. It is bounded and local first (under
`/tmp/angband-validation.lock`); it is not a cohort.

**Setup.** 20 seeds from a pilot suite, one build, one configuration, with
the frozen calendar if C4 exists. Every run logs its key stream and, at
every state sample, the game RNG state, Borg RNG, turn, depth and HP. The
native observer's `STATE` lines already carry the RNG fields.

| Run | What it does |
| --- | --- |
| A | Uninterrupted, from birth to horizon H3, with checkpoints turned off |
| A′ | Uninterrupted, with checkpoints at H1 and H2 written but play not stopped |
| B | Birth to H1, checkpoint, process exits; a new process resumes to H2, checkpoints and exits; a third resumes to H3 |
| F | Birth to H1, then a fresh-Borg restart from the H1 save, to H3 |

Start small (H = 10k, 20k, 30k turns), then 100k, 200k, 300k on the same 20
seeds.

**What is compared: the gameplay projection.** Raw traces differ for
harmless reasons: the native observer writes a `STATE checkpoint` line when
it saves, and a resumed process has its own start-up lines. So each run is
reduced to a canonical projection, hashed separately from the raw evidence
(which is kept unchanged):

- the sequence of keys or commands the Borg issued after birth, each with
  its decision index;
- at each decision, the game turn, the full game RNG state, the Borg RNG
  state, depth and HP;
- the outcome and final state.

Observer markers (checkpoint, start, process boundary) and wall-clock
fields are left out. Birth input is compared separately for runs that start
from birth. Records are aligned by decision index, not by line number. The
projection is versioned per adapter; its definition is part of the
qualification report.

The projection must still catch real changes, so it is tested both ways:
a trace that differs only by an extra checkpoint marker must compare equal,
and one with a single extra game-RNG draw must not.

**Pass criteria.**

1. **Checkpointing does not perturb play:** A and A′ have identical
   gameplay projections. This shows that writing a checkpoint adds no
   gameplay action and no RNG draw.
2. **Resume is exact:** B's projection equals A's. A mismatch is reported
   at the first divergent decision, with the turn and the state
   difference.
3. **Refusals work:** resuming with a different build, configuration, plan
   hash or state-format version is refused before play.
4. **Fresh-Borg restart is labelled correctly:** F is expected to differ
   from A. The report records where it first differs. It is stored as a
   fork, never as A's life.
5. **Storage round trip:** B's checkpoints go through the real publish,
   seal, claim and resolution protocols, including one injected worker loss
   (kill the holder, let the claim expire, take it over, resume from the
   same sealed checkpoint), and one checkpoint whose blob registration
   failed, which must never become usable.

6. **State coverage:** every field of the adapter's checkpoint state
   schema that the plan or controller can hold must have been **exercised**
   at some checkpoint of a passing B run. Each field has a typed predicate
   for what exercising it means: each meaningful value, including valid
   `false`, zero and enum values, and each transition the controller can be
   in the middle of. Generic truthiness does not count. For borg-reborn-rs with plans
   that means at least: each selected class and phase, a phase boundary,
   cancellation and owner state, both loop directions, a pending Recall or
   town recovery, and a pending decision. Random seeds may never reach some
   of these, so the qualification adds bounded fixtures: checkpoints chosen
   or started from saves where each state is live. The report lists each
   field as exercised or not. A field never exercised is **unqualified**,
   not passed, and resume refuses checkpoints taken while that field holds
   a value or transition that was not exercised.

Qualification applies to one adapter, one state-format version and one
plan/controller state schema. A new version of any of them needs a new
qualification.

If criterion 2 fails, the adapter offers only fresh-Borg restart, and the
qualification report lists exactly which state is missing. The zoo then
labels long runs on that adapter as forks, or waits for the change request.

## Recommended order

1. **borg-reborn-rs first.** It already has checkpoints at intervals, load
   with the save's RNG, exact stops and a CI load check. It needs R1 (Borg
   and plan state) for exact continuation, and it is where the owner wants
   long, plan-aware runs (#320).
2. **Native C next**, starting with C1 and C2, which are small and enough
   for fresh-Borg forks and cemetery pre-death checkpoints. Spike S1 (CRIU)
   decides whether C3 is needed before exact C long runs.
3. **Neo last** (N1 for Mandos, N2 for the neo-original fork runner), when a Neo long run is planned.

Until an adapter passes, the zoo can still run long games from birth as
today. If the owner approves the protocol (decision D4 in the
[plan](PLAN.md)), it can also run fresh-Borg restarts as separately
labelled arms.
