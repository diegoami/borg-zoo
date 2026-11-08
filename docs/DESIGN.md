# Design

The zoo answers one kind of question: *on the same seeds, how do these Borg
versions and configurations differ in survival and progress?* It owns the
catalogues, orchestration, the results store, the statistics and the site. It
owns no Borg code.

## Pieces

**Specimen.** Repository, full commit SHA, carried-fix count and label. Today
every specimen lives in better-borg-c's history:

| Specimen | Commit | Carries |
| --- | --- | --- |
| `pristine` | `e473720ed88a` | 0 (original C Borg, angband/angband) |
| `bbc-m1` | `d4bfdce9d478` | 2 |
| `bbc-m2` | `2675d198e4c3` | 7 |
| `bbc-m3` | `702f091f6ac0` | 34 |
| `bbc-m4` | `70993393a1c9` | 42 |

Carry counts are the length of `patches/series.json` at each commit.

**Harness.** better-borg-c's `tools/measure-native.py` and observer at a
pinned commit. For each specimen it exports the source with `git archive`,
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

**borg-rs specimens.** `rs-c` and `rs-r1` (named `rs-rust` in runs recorded before 2026-11-08) are a borg-rs commit built with
its own `harness/build.sh`: the C Borg and the Rust Borg in the same tree,
both behind borg-rs's headless `borgh` frontend (`zoo/borgrs.py`). Each run
mirrors `harness/run.sh`. The run's `borg.txt` is the checkout's
`harness/borg.txt` with the profile applied, and the outcome comes from
`summary.json`. The play hash is the hash of the key log, which is borg-rs's
own equivalence oracle, so identical play between `rs-c` and `rs-r1` is
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
runner compiles its private user path into the binary.

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
