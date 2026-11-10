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
pinned commit (`9ca98661` since 2026-11-10, the mode-cutoff restart of
borg-zoo#54, which is also specimen `4.2.6-bbc-9ca98661`'s ref; before that
`fc9d97cb` since 2026-11-08, and before that `8c23ec0d`, whose
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
- fixed birth only;
- the run stops after the first key at or past the cap (cell `"boundary":
  "after-key"`), unless the specimen declares `"exact_turns": true`, which
  passes `-exact-turns` and stops the run at the cap itself (`"boundary":
  "exact"`); existing specimens keep `after-key`, the flag is opt-in per
  specimen;
- no per-turn states, so no depth marks or survival by turn, unless the
  specimen declares `"depth_stream": true`, which passes `-statelog` and
  fills `first_turn_at_depth` and a `milestones` list (level, max depth and
  gold on hand at 25/50/75/100% of the cap) from it. The state log hashes
  gear rather than valuing it, so this is gold on hand, not a full net
  worth (inventory and equipment value) — see "Open questions" below.

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

**borg-reborn-rs specimens** (borg-zoo#30; also kind `borg-rs`, `zoo/borgrs.py`).
`4.2.6-reborn-rust`, `4.2.6-reborn-c-pristine` and `4.2.6-reborn-c-bbc-m7` are
borg-reborn-rs commits of the three arms its own GOALS plan compares: the
reborn Borg (a placeholder strategy until its M3; its results mean nothing
yet) and two C controls (the original Borg and better-borg-c M7's Borg)
built on borg-reborn-rs's own engine tree. `impl` selects `BORG_IMPL` as
usual; the two controls use borg-reborn-rs's own control overlay (`c-pristine`,
`c-bbc-m7`), opaque to the zoo. All three declare `exact_turns` and
`depth_stream`: borg-reborn-rs's `borgh` build supports both from this pin.
`4.2.6-reborn-c-pristine`'s keys are a prefix of `4.2.6-rs-m0-c`'s on borg-rs's
smoke suite, one key shorter: this specimen's `exact_turns` stops it exactly
at the cap, while `4.2.6-rs-m0-c`'s tree has no `-exact-turns` and stops one
key after it. Outcomes pair with `4.2.6-rs-m0-c`; play/trace hashes do not
match (checked directly, #39's milestone review on #32). `ref` is tag `m1`
(`fab7155`), 24 commits past the review merge this was first pinned to,
including Borg behaviour changes (e.g. never holding on a shop entrance).

Death evidence: the adapter keeps `keys.log` (and `summary.json`, never
deleted) for a `death` cell instead of discarding it, so a natural death
found by a zoo run can be recorded and verified against `play_sha256` in the
measured repository, per its own rules. Every other outcome's keys are
discarded as before.

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

**Mode profiles and the cutoff (borg-zoo#54).** A profile that names no
mode setting leaves every mode on the build's own default, and
`borg_munchkin_by_class` defaults to TRUE only from better-borg-c
`fd683ced` (PR 302, 2026-11-10) — so the same profile name plays a
different game on either side of that commit, and the observer cannot
catch it, because it only verifies named settings. Four profiles name the
modes explicitly: `normal` (all four mode flags off), `munchkin-class`
(the product default for Warrior/Druid/Ranger), `munchkin-on`, and
`lunal`. Every better-borg-c-kind specimen (and `angband-e473-original`)
declares which side of the cutoff it is on (`mode_side` in
`catalogue/specimens.json`; pre-catalogue run snapshots are resolved from
the commit set in `zoo/catalogue.py`). Three rules follow:

- `python -m zoo plan` rejects `default` (any profile that leaves the
  modes unnamed) in an experiment that touches a post-cutoff
  better-borg-c specimen, and rejects a profile naming
  `borg_munchkin_by_class` for a specimen that predates the setting
  (older builds ignore the unknown line; every cell would be a
  `config_error`). An experiment recorded before the cutoff keeps its
  arms under an explicit `"pre_cutoff": "<date and reason>"` note.
- Version pairings (`vs_version`) between specimens on opposite sides of
  the cutoff are not computed (`zoo/stats.py`).
- Run pages label pre-cutoff results (recorded before 2026-11-10, or
  marked `pre_cutoff`) and state the cutoff; the Detailed and Versions
  tabs carry a standing note. Existing results stay on the `results`
  branch untouched (append-only); the restarted experiments are
  `bbc-explicit-smoke` and `classes-explicit`, on
  `4.2.6-bbc-9ca98661`.

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
- `boundary`: `"exact"` if the run stopped at the cap itself (the
  better-borg-c observer; a borg-rs specimen with `exact_turns`), else
  `"after-key"` (borg-rs without the flag; Neo-original, which turns an
  after-cap death into `turn_cap`; Mandos, which stops at the first loop
  boundary at or after the cap). A survivor's final turn and depth are only
  comparable at an exact boundary (borg-reborn-rs#30's `tools/endpoint.py`
  refuses after-key survivors unless told otherwise);
- the first turn at each depth mark, and, from the same sampled states, a
  `milestones` list: character level and max depth at 25/50/75/100% of the
  cap (the last sampled state at or before that turn), so progress can be
  read at fixed points rather than only at the end. The better-borg-c
  observer logs no gold or item value, so there is no net-worth figure from
  it; a borg-rs specimen with `depth_stream` adds gold on hand at those same
  points (still not a full net worth — gear is hashed there, not valued;
  see "Open questions");
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
   from the results branch and deploys it. Deploys queue rather than cancel
   (`cancel-in-progress: false`): every collect dispatches one, so a
   cancel-on-progress rule races merges against dispatches and can end with
   the site older than `main` and no successful deploy to fall back on.

The build and run jobs place the build at the same absolute path, because the
runner compiles its private user path into the binary. Mandos jobs also set
up Node 22 and check out and install the Mandos commit (`source/`) in both
jobs.

**Look at the dashboard before shipping chart changes.** A chart can pass
every test and still be unreadable — the shape-coded exemplars chart shipped
that way (labels were the fix, and rendering it caught three labels that
silently failed to place). After any `zoo/landing.py` or `zoo/site.py`
change, build the site from the results branch, render the charts to images,
and actually read them:

```sh
git worktree add --detach /tmp/results origin/results
python3 -m zoo site --results /tmp/results/results --out /tmp/site
# extract a chart <svg> from /tmp/site/index.html (or classes/<Class>.html),
# inline the svg.scatter CSS rules with concrete colors, then:
uv run --with cairosvg python -c \
  "import cairosvg; cairosvg.svg2png(url='/tmp/chart.svg', write_to='/tmp/chart.png')"
```

The automated half of that look is
`test_the_exemplars_chart_never_overlaps_its_own_labels` (every plotted dot
gets a label, and no two labels overlap) plus
`test_a_smoke_scale_setup_never_becomes_a_dashboard_point`; they catch the
regressions, the render catches everything else.

## Statistics (`zoo/stats.py`)

**Per arm:**
- runs, finished runs and outcome counts;
- deaths and death rate, with a Wilson 95% interval;
- "goal" rate (alive at the cap having reached DL5, a placeholder) - still used
  by the Detailed tab's milestone cards, left unchanged;
- median maximum depth and level;
- median death turn;
- share alive at 25/50/75/100% of the cap;
- share reaching DL2/3/5/10, with the median turn;
- `milestone_table`: median level, max depth and (where logged) gold on hand
  at 25/50/75/100% of the cap, over finished runs that recorded it at that
  point (a death before it is excluded, not substituted with a worse
  value). Shown on the site as "Level, max depth and gold by engine turn"
  whenever at least one cell in the suite carries it.
- `progress_score`: median of max_depth + max_level per cell (including
  deaths - a death's reach still counts, unlike the DL5 goal rate), one
  number instead of two. Used on the Overview tab's exemplars card and its
  by-class/turn-snapshot grids in place of the DL5 goal rate, after the
  owner's call that "alive at cap, reached DL5" was a bad metric and should
  be a combined depth+level (and eventually net worth) figure (2026-11-09).
  `milestone_progress_score` is its sibling at each turn fraction, reusing
  `milestone_table`'s death-exclusion rule. Neither touches `arm_summary`'s
  own `goal_rate`/`DEPTH_GOAL`, which the Detailed tab still shows - a
  deliberately narrow change, not a redefinition of the site-wide metric.

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
job - but `compare.yml`'s own `run` job sets `timeout-minutes: 300` (5
hours), tighter than that ceiling. At a 200,000-turn cap (`classes-1800-200k`),
8 shards was not enough: 2 of 8 shards for one specimen ran out the clock and
came back as `harness_failure` for every cell they hadn't finished (run
42647082970, 2026-11-09). 16 shards on a same-sized rerun finished clean. **A
cap much above the usual 100,000 needs more shards than `shards=8`,
proportioned down from 300 minutes** - the vanilla specimen's own 8 shards
finished fine in the same window, so it's specific to how slowly a given
specimen's games end, not a fixed rule.

**A specimen whose own default already is the munchkin start by class makes
the `munchkin-wdr` profile a no-op on it.** First found on `4.2.6-bbc-m8`
(and its Rust twin `4.2.6-rs-m8`) during the #39 review - identical
play/trace hashes on 3/3 seeds - then independently rediscovered on
`4.2.6-bbc-munchkin-by-class` inside the `classes-200k-best` run (1,800
cells wasted at the 200k cap before the fix) and confirmed again, cheaply
this time via a 3-seed smoke check first, on M9 and M10. Every milestone
from M8 onward inherits that default unchanged, so **before adding a
`munchkin-wdr` arm for any of them, check with a cheap smoke run first** (as
`m9-m10-munchkin-smoke.json` does) rather than finding out at full scale.

## Open questions for the owner

1. **Primary endpoint:** turn T, depth D and level L for "early-game
   survival". The site's DL5 goal (`arm_summary`'s `goal_rate`) is still a
   placeholder on the Detailed tab. Resolved for the Overview tab's
   exemplars card: the owner called it a bad metric (2026-11-09) and it now
   uses `progress_score` (median depth + level, see Statistics above)
   there instead - money and equipment value are still open, tracked under
   question 9.
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
8. **Milestone tags: resolved, in use since M7.** better-borg-c tags every
   milestone now (`4.2.6-impact-vN`); M7 through M10 all carry a `tag`
   field in the catalogue alongside their pinned SHA.
9. **Net worth (inventory and equipment value), not just gold.** Level and
   max depth at turn milestones (`milestones`, `zoo/stats.py`'s
   `milestone_table`) are in, over every finished run, needing no upstream
   change. Gold on hand at those same points is in too, but only for a
   borg-rs specimen with `depth_stream` (today, the three `4.2.6-reborn-*`
   specimens): a partial proxy, not a net worth, since that log only hashes
   equipment and inventory, never values them. The better-borg-c observer
   logs no gold at all. A full net-worth figure needs an upstream change
   (value the gear at each sampled state) in whichever harness the owner
   wants it from; that is a change request to route to that harness's own
   repository, the same way borg-reborn-rs's was routed here (#30), not
   something the zoo can add on its own.
10. **A deep start for the Lunal arm.** The `lunal` profile is in the
    catalogue, but `borg_self_lunal` only enters the mode when the Borg is
    prepared for 15 levels deeper and has reached `maxdepth >= depth + 15`
    (`borg-think-dungeon.c`), which the zoo's suites (20k-400k turns) only
    rarely offer. Measuring it now would repeat the exact failure this
    issue fixes: an arm that never enters the mode, reading as neutral.
    Deferred until better-borg-c exposes a deep start the harness can
    drive (the runner has a `load` hook for a save file; the zoo's suites
    have no field for one yet), or a 400k+ run is shown to enter the mode
    reliably (check the trace for Lunal notes first, cheaply, before
    scheduling any classes-scale Lunal run).
