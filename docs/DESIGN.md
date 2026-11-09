# Design

The zoo answers one kind of question: *on the same seeds, how do these Borg
versions and configurations differ in survival and progress?* It owns the
catalogues, orchestration, the results store, the statistics and the site. It
owns no Borg code.

## Pieces

**Specimen.** Repository, full commit SHA, carried-fix count and label. The
original C Borg and better-borg-c's milestones:

| Specimen | Commit | Carries |
| --- | --- | --- |
| `4.2.6` | `e473720ed88a` | 0 (original C Borg, angband/angband) |
| `4.2.6-bbc-m1` | `d4bfdce9d478` | 2 (tag `4.2.6-impact-v1`) |
| `4.2.6-bbc-m2` | `2675d198e4c3` | 7 (`4.2.6-impact-v2`) |
| `4.2.6-bbc-m3` | `702f091f6ac0` | 34 (`4.2.6-impact-v3`) |
| `4.2.6-bbc-m4` | `70993393a1c9` | 42 (`4.2.6-impact-v4`) |
| `4.2.6-bbc-m5` | `5384f12ed51e` | 50 (`4.2.6-impact-v5`) |
| `4.2.6-bbc-m6` | `b3c825c97c8a` | 63 (`4.2.6-impact-v6`) |
| `4.2.6-bbc-m7` | `3573d741e6dc` | 76 (`4.2.6-impact-v7`) |

Carry counts are the length of `patches/series.json` at each commit.

**Names.** A version's name starts with the engine version it is built on:
`4.2.6` is the original C Borg at the upstream pin, `4.2.6-bbc-mN` is
better-borg-c milestone N on it, `4.2.6-rs-mN` is the borg-rs Rust Borg
carrying the same fixes, and `4.2.6-rs-mN-c` is the C Borg of that borg-rs
tree. When the upstream pin moves to a new engine version, its versions get
new names and the old ones keep their results. Runs recorded before
2026-11-08 use the earlier names (`pristine`, `bbc-mN`, `rs-c`, `rs-mN`,
`rs-mN-c`, `rs-rust`); each version lists its earlier names under `formerly`
in `catalogue/specimens.json`.

Neo Angband versions start with `neo-b3`, for Neo Angband 1.23.0-beta.3, the
engine and content packages they run on: `neo-b3-mandos` is full Mandos,
`neo-b3-borg-<release>` an upstream Neo Borg release, and `neo-b3-api2-<lane>`
a Mandos measurement snapshot of one Borg source under the api2 adapter.

**Harness.** better-borg-c's `tools/measure-native.py` and observer at a
pinned commit (`fc9d97cb` since 2026-11-08; before that `8c23ec0d`, whose
watchdog could abort a run on a split UTF-8 character, better-borg-c#220). For each specimen it exports the source with `git archive`,
applies the observer instrumentation and builds a Debug binary with the test
frontend. For each cell it runs the binary on the seed with the turn cap and
records:
- the outcome class (death, turn cap, completion, stall, wall timeout, crash,
  harness failure);
- the cause of death;
- a state line every 100 Borg decisions (turn, depth, maximum depth, level,
  HP);
- the Borg settings in effect.

The zoo calls `prepare()` and `run()` as a library (`zoo/harness.py`).

**borg-rs specimens.** `4.2.6-rs-m0-c` and `4.2.6-rs-m0` are a borg-rs commit built with
its own `harness/build.sh`: the C Borg and the Rust Borg in the same tree,
both behind borg-rs's headless `borgh` frontend (`zoo/borgrs.py`). Each run
mirrors `harness/run.sh`. The run's `borg.txt` is the checkout's
`harness/borg.txt` with the profile applied, and the outcome comes from
`summary.json`. The play hash is the hash of the key log, which is borg-rs's
own equivalence oracle, so identical play between `4.2.6-rs-m0-c` and `4.2.6-rs-m0` is
the port's identity check at zoo scale.

Limits compared with the better-borg-c observer:
- no effective-settings line, so only the written `borg.txt` is checked;
- no per-turn states, so no depth marks or survival by turn;
- fixed birth only;
- the run stops after the first key at or past the cap.

Runs from different harnesses are not paired. Whether the same seed gives
the same game under the borgh frontend and under the better-borg-c observer
is not verified. In `rs-smoke` all six seed/profile runs reached the same
maximum depth and character level under both harnesses, which suggests it
might. Pairing stays off until key-level equality is shown; the observer
does not log keys.

Rust specimens follow better-borg-c's milestone numbers: `4.2.6-rs-m0` is the
port of the 4.2.6 C Borg, and `4.2.6-rs-m2` carries milestone 2's seven fixes
(there is no `4.2.6-rs-m1`). `4.2.6-rs-m2-c` is the C Borg of the same borg-rs tree, so
identical play between `4.2.6-rs-m2-c` and `4.2.6-rs-m2` is the M2 port's identity check.
The matching better-borg-c version for `4.2.6-rs-mN` is `4.2.6-bbc-mN`, or `4.2.6`
for M0.

**Mandos specimens** (`zoo/mandos.py`, kind `mandos`). A diegoami/mandos
commit that has the headless entry point `tools/zoo-run.mjs`
([interface](https://github.com/diegoami/mandos/blob/cca1293cb5ab02681b1c200dca2d0cb014c90381/docs/ZOO-HARNESS.md),
record schema `mandos/zoo-run@1`, mandos#213). Mandos is the Neo Angband
Borg mod, a TypeScript Borg on the Neo Angband engine from npm, not the C
game.
- **Never paired with C.** A Neo seed is a different game from a C seed,
  so Mandos runs are compared only with other Neo versions; the statistics
  pair only within one harness kind.
- **Build:** `pnpm install --frozen-lockfile` and `node tools/zoo-build.mjs`
  in an exact checkout, once per specimen. The build job keeps the bundle,
  whose SHA-256 must equal the one Mandos reported for that commit.
- **Run:** a fresh exact checkout, installed the same way, plays each cell
  as its own `zoo-run` process with that bundle, which checks source,
  bundle and content before play. Race and class are always passed
  explicitly: fixed birth is Human Warrior, assigned birth as the suite
  says. Mandos has no random first birth, so random-birth suites are
  rejected.
- **Settings:** only the nine controller flags apply (`borg_plays_risky`,
  the six `borg_worships_*`, `borg_self_scum` and `borg_munchkin_start`;
  `mandos.FLAGS`); a profile with any other setting, or the shipped base,
  is rejected before the run. The record's effective settings are checked
  against the profile.
- **Counters:** `turn` is Core game ticks, ten per normal-speed action, the
  same unit as the C game's turn counter (but not the same game). The cap
  stops at the first Core loop boundary at or after it, so a run can
  overshoot: one rest can run a thousand ticks past. The cell keeps
  requested and actual ticks. A death after the requested cap was alive at
  the cap, so it counts as a turn-cap run, with the death in
  `died_after_cap`. Decisions (issued commands), armed attempts and Core
  loop calls stay separate.
- **Outcomes:** `death`, `turn_cap`, `stalled`, `borg_stopped`,
  `decision_cap` and `harness_failure` are kept as they are; a wall
  timeout is the zoo's own. A missing or invalid record is a harness
  failure. None but `death` counts as a death.
- **Evidence:** the play hash is Mandos's `playSha256` over the issued
  command stream, checked against the file. Command streams, state streams
  and logs of runs without an endpoint are kept as workflow artifacts for
  30 days.
- **Local runs need Node 22 and a recent Corepack.** The Mandos tags pin
  `pnpm@12.16.1`. The Corepack bundled with Ubuntu's Node 22.22 can't start
  pnpm 12: it fails with `Cannot find module …/pnpm/12.16.1/bin/pnpm.cjs`.
  Actions' `setup-node` doesn't have this problem.
  - Locally, run a newer Corepack's `pnpm.js` under Node 22 (for example, a
    `pnpm` wrapper on `PATH` that execs `node <newer corepack>/dist/pnpm.js`),
    and keep Node 22 first on `PATH`.
  - Don't install two checkouts in parallel: two Corepack downloads into the
    same cache leave a broken pnpm directory.
- **Speed:** about 6× slower than the C Borg (a 100,000-tick run that
  survives took 549 s on one CPU in Mandos's measurement), so Mandos
  specimens get `wall_factor: 3` on the suite's wall limit.
- **Profiles and the api2 lanes** (mandos#215). Two tagged snapshots form
  the matched pair for comparing upstream with the port repairs:

  | Version | Tag | Snapshot | Borg source |
  |---|---|---|---|
  | `neo-b3-api2-upstream` | `v1.4.0-beta.4-upstream.a10655c3-zoo.1` | `45dee074` | official neostryder/neo-angband-mod-borg `a10655c3` |
  | `neo-b3-api2-port.2` | `v1.4.0-beta.4-port.2` | `ca659c51` | `a10655c3` plus the port repairs, clean producer `cc64c1cc` |

  Neither carries the C corrections. Both run the target's own `plugin.ts`
  through the same tools-only adapter and declare
  `controllerProfile=api2-plugin` and `commandStreamProfile=api2-intents-v1`.
  Each tag is resolved once to its commit in the catalogue.
  - The specimen declares both profiles. The build and every record must
    declare the same ones, and the record's commit must be the specimen's,
    or the run is a harness failure.
  - Each cell keeps `controller_profile`, `command_stream_profile` and the
    lane, plus the api2 counters: accepted commands, command-stream events
    and host reads.
  - Full Mandos at `cca1293c` declares no profile: it is the legacy
    `play-session` profile. Statistics pair runs, and compare play hashes,
    only within one harness kind and command-stream profile
    (`stats.pairing_class`). So the api2 lanes pair with each other, but
    not with full Mandos: a difference from full Mandos isn't attributed
    to the C corrections alone.
  - The headless profile uses Core's registered store transactions, not
    the browser's store modal. A UI item-choice prompt it can't answer
    ends the run as a harness failure, never as a death or a stall.
- **Pending lanes:** the release `v1.4.0-beta.4` (`48ee6e1c`) and
  `v1.4.0-beta.4-port.1` (`b076ffb5`) stay `pending`: neither has the
  entry point, and the api2 lanes are not substituted for them.

**Profile.** `borg.txt` lines, or with `"base": "shipped"`, the version's
own `src/borg/borg.txt` (formula section included) with named settings
overridden. The runner always adds
`borg_cheat_death = FALSE` and `borg_respawn_winners = FALSE`. After each run
the zoo compares the observer's `BORG_OPTIONS` line with the profile; any
difference turns the run into a `config_error`.

**Suite.** Seeds, cap, wall and stall limits, birth rule, and whether
checkpoint saves are kept. The birth rules:
- `fixed`: Human Warrior with default point buy, as in better-borg-c's
  cohorts;
- `random`: race and class chosen by the seeded game; observer only;
- `assigned`: each seed gets a race and class from the suite's
  `characters`. Classes are dealt in turn, and races cycle once per round of
  classes, so every class meets every race.

On the observer, the zoo gives the runner birth keys for the chosen race and
class. The birth menus select on a double tap: an item's letter moves the
cursor there, and the same letter again selects it. On borgh, the zoo passes
`-race` and `-class` indices with `-menu-letters`. Each run checks the
character actually played; a mismatch is a `config_error`.

**Seed sets.** Early suites list consecutive seeds. Later suites use a
`seed_rule` (`sha256-v1`): each seed is drawn deterministically from a hash of
the suite name and an index, spread over 1 to 2³¹−1. A rule suite skips any
seed that another suite already uses, so suites never overlap. Each suite
declares a role:
- `pilot`: sizing and exploration;
- `development`: screening, and choosing what to confirm;
- `confirmation`: prespecified tests only;
- `sealed`: untouched until the owner opens it for a final claim. The
  catalogue refuses an experiment on a sealed suite unless the experiment
  names that decision in `unsealed_by_owner`.

The current sets are `dev-2000`, `confirm-2000`, `deep-1000` (400,000 turns),
`random-1000` (race and class chosen by the seed) and `sealed-2000`.

**Cell.** (suite, specimen, profile, seed) → one JSON line (`borg-zoo/cell@1`).
The record holds:
- the outcome, cause and final state;
- the first turn at each depth mark;
- the wall time;
- the trace hash, and a play hash that leaves out the configuration lines, so
  identical play is detectable across profiles;
- the effective settings;
- the build identity: binary hash, compiler and platform;
- the calendar;
- for a run that did not finish, a `stall` block: the last engine turn, how
  many state records share it, the decision and energy deltas across them,
  level changes (a lower bound: state records are sampled every 100
  decisions) and depths seen, the most repeated Borg notes at that turn
  and the last 20 notes (borgh: keys). A heuristic `kind` labels it
  (`level_cycle`, `zero_energy_retry`, `energy_without_time`,
  `no_decisions`). The observer records no player position, so position
  changes are not available.

## Workflow (`.github/workflows/compare.yml`)

1. **plan**: expands the experiment into build and run matrices.
2. **build**: one job per specimen. It checks out the pinned harness with
   full history, builds, and tars the build so the binary stays executable.
3. **run**: one job per specimen shard, cells in parallel on the runner's
   cores.
4. **collect**: merges every shard. A missing cell is recorded as a harness
   failure, never dropped. The job writes `results/<experiment>/<run>/` to
   the `results` branch and dispatches the site build.
5. **pages** (`.github/workflows/pages.yml`): generates the static site
   from the results branch and deploys it.

The build and run jobs place the build at the same absolute path, because the
runner compiles its private user path into the binary. Mandos jobs also set
up Node 22 and check out and install the Mandos commit (`source/`) in both
jobs.

## Statistics (`zoo/stats.py`)

**Per arm:**
- runs, finished runs and outcome counts;
- deaths and death rate, with a Wilson 95% interval;
- "goal" rate (alive at the cap having reached DL5, a placeholder);
- median maximum depth and level;
- median death turn;
- share alive at 25/50/75/100% of the cap;
- share reaching DL2/3/5/10, with the median turn.

**Paired against the control arm, on seeds where both finished:**
- rescued, newly killed, both died, both lived;
- identical traces;
- an exact McNemar p for deaths and for the goal.

These are descriptive. They are not prespecified tests, unless an experiment
carries a `prespecified` field, written before its suite has any results and
shown on its page. `munchkin-confirm` is the first.

## Costs

Taken from better-borg-c's recorded run times. A 20,000-turn run takes
8–15 s; a 400,000-turn run takes 95–113 s; a 100,000-turn run is estimated at
30–45 s. These times are from the owner's machine; GitHub runners differ.

| Experiment | Cells | Rough CPU time |
| --- | --- | --- |
| `milestones-smoke` | 15 | minutes |
| `milestones-early` | 250 | 2–3 hours, spread over 20 jobs |
| `switches-early` | 900 | 8–11 hours, spread over 8 jobs (raise `shards`) |

Measured in Actions on 2026-11-08 and 9: Mandos api2 lanes at 100,000 ticks
take a median of 21–29 s per game, with a mean of 49 s and a maximum of
182 s (the Neo Borg dies early). `mandos-api2-classes-1800`, 3,600 games
with `shards=10` per lane, took 1 h 38 min from dispatch to collection. On
classes-1800 with `shards=4`, `classes-m7` (7,200 C games) took 2 h 44 min
and `classes-rs-m6` (9,000 games, borg-rs) took 38 min. The figures depend
on what else holds the queue.

Public repositories have no Actions minute charge on standard runners. The
limits that matter are 20 concurrent jobs, 256 matrix jobs and 6 hours per
job.

## Open questions for the owner

1. **Primary endpoint:** turn T, depth D and level L for "early-game
   survival". The site's DL5 goal is a placeholder.
2. **Birth rule:** fixed Human Warrior (comparable with better-borg-c's
   cohorts) or seed-chosen race and class (broader).
3. **Calendar:** today each run uses the runner's clock. Freezing the date
   (for example with libfaketime) would make runs comparable across days.
4. **Suite sizes:** after the pilot, size the comparisons from the observed
   death and discordance rates.
5. **New parameters:** restock depth (#370) and dive ratio (#371) enter as
   profiles once better-borg-c exposes them.
6. **Dynamic calculations need runner support.** With
   `borg_uses_dynamic_calcs = TRUE`, the Borg prints an extra start-up
   warning. That warning consumes one of the runner's fixed start-up keys,
   and the Borg aborts before its first decision. The `dynamic-calcs`
   profile is in the catalogue but blocked until better-borg-c's runner
   handles that start-up. The `shipped` profile (the version's own
   `borg.txt`, unchanged) was checked locally to play identically to
   `default`.
7. **Birth options** (connected stairs, force descend, no selling,
   randarts) are a second configuration axis. The runner uses the game's
   defaults, which the observer records: for example `birth_connect_stairs=1`
   and `birth_no_selling=1`. Varying them needs runner support too.
8. **Milestone tags:** if better-borg-c tags its milestones, specimens can
   name them instead of SHAs.
