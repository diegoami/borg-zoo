# Borg zoo

Seed-suite comparisons of Angband Borg versions and configurations, run
headless on GitHub Actions and published as statistics tables on
[GitHub Pages](https://diegoami.github.io/borg-zoo/).

The first question: **how does better-borg-c compare with the original C
Borg on the same seeds, at each of its milestones and under different
settings, with early-game survival first?**

## How it works

| Piece | What it is |
| --- | --- |
| [Specimens](catalogue/specimens.json) | A Borg version: the game and Borg source at a pinned commit. The catalogue includes the original C Borg, better-borg-c milestones, borg-rs and borg-reborn-rs builds, and Neo/Mandos lanes. |
| [Profiles](catalogue/profiles.json) | A configuration: the `borg.txt` settings a run uses. Validation is harness- and specimen-specific. Cells can carry the written configuration, native settings and a core resolution receipt. |
| [Suites](catalogue/suites.json) | Frozen seed lists with a turn cap, time limits and a birth rule. |
| [Experiments](experiments/) | Specimens × profiles × suites, with a control arm for paired comparison. |
| Runner | The specimen selects a runner. The [design](docs/DESIGN.md) describes the C observer, the Rust headless adapter and the Neo/Mandos adapters. |
| Results | One JSON line per cell on the [`results`](https://github.com/diegoami/borg-zoo/tree/results) branch, append-only, one directory per workflow run. |
| Site | Static tables built from the results branch: outcomes per arm, paired rescued/newly-killed counts, survival by turn, depth reached. |

## Running an experiment

Write or update the YAML definition and run `zoo define`, `zoo preflight` and
`zoo plan` before opening the catalogue PR. Start with a pilot and inspect its
gate before asking the owner to grow the study. See [DEFINE](docs/DEFINE.md)
and [RULES 11, 14–17](RULES.md).

After the PR merges successfully, dispatch `compare.yml` from `main`. Pass the
repository-relative JSON path as `experiment`, and size the shards from the
pilot and the account's runner budget. This example reruns an existing pilot:

```sh
python3 -m zoo preflight --experiment experiments/reborn-settings-receipt-pilot.json
python3 -m zoo plan --experiment experiments/reborn-settings-receipt-pilot.json --shards 3
gh workflow run compare.yml --ref main \
  -f experiment=experiments/reborn-settings-receipt-pilot.json -f shards=3
```

Check the run's build and cell outcomes, then look for
`results/EXPERIMENT/RUN_ID-ATTEMPT/` on the results branch. If collection fails
with `results -> results (fetch first)`, retry the failed jobs with
`gh run rerun RUN_ID --failed` and verify the new attempt was published.

For a single-arm diagnostic, `python3 -m zoo arms --experiment experiments/NAME.json`
lists the `SPECIMEN:PROFILE` values for the optional `arm` input. The site groups
separate arm runs by experiment name and shows their provenance. Dispatch
paired study arms together to preserve the shared run conditions.

**Smoke checks** (a milestone or head builds and plays) live in
[`smoke/`](smoke/), not in `experiments/`. **Actions → smoke → Run workflow**
runs one. The dashboard lists smoke runs, old and new, under its **Smoke** tab
and keeps them out of the comparisons.

Locally (under the shared validation lock if other sessions use this machine):

```sh
git clone https://github.com/diegoami/better-borg-c.git harness
git -C harness checkout "$(python3 -c 'import json;print(json.load(open("catalogue/specimens.json"))["harness"]["commit"])')"
python3 -m zoo build --specimen 4.2.6 --harness harness --out specimens/4.2.6
python3 -m zoo run --experiment smoke/milestones-smoke.json --specimen 4.2.6 \
  --build specimens/4.2.6 --harness harness --work work --out cells/4.2.6.jsonl
python3 -m zoo collect --experiment smoke/milestones-smoke.json --cells cells \
  --results results --run-id local-1
python3 -m zoo site --results results --out _site
```

Tests: `python3 -m unittest discover -s tests`.

## Deaths go to the cemetery

When cemetery bundles are enabled (the default), each natural death of a borg-rs or borg-reborn-rs cell is replayed once with
full logs. Its key stream is checked against the cell's, and the result is
uploaded as a death bundle in the run's `deaths-<specimen>-<shard>` artifacts
(90 days). borg-cemetery imports a run's deaths as replayable dossiers with
`python3 scripts/import_zoo_deaths.py --run RUN_ID`. See
[docs/CEMETERY-DEATHS.md](docs/CEMETERY-DEATHS.md) (#176).

## Cemetery scenarios

[Scenario dispatch](docs/SCENARIO-DISPATCH.md) compares exact pushids on an
immutable Cemetery bank, with separate synthetic reports and complete failure
denominators. The **Scenarios** tab lists scenario runs with their compared
versions, scenario counts, collected cells and paired outcomes. Each run links
to the full report and evidence; synthetic results stay separate from the
population comparisons.

[Balanced999 incidents](docs/BALANCED-INCIDENTS.md) prepares equal111-case
quotas for all nine classes and a bounded saved-state execution in Zoo.

## Reading the results

The Detailed tab lists experiments by the question they ask. Each run starts
with a short comparison brief: versions, settings, baseline, seed count and
turn cap. Background, study plans and exact settings expand on demand.
Reader-facing questions live in `zoo/briefs.py`; add one when introducing an
experiment. The recorded run supplies the conditions, including historical
ones.

The tables are descriptive. Suites are small, intervals are wide, and the
primary endpoint is not yet fixed. "Goal" (alive at the cap having reached
dungeon level 5) is a placeholder until it is. Runs that stall, time out,
crash or fail in the harness are counted and shown, never relabelled as
deaths. Compare arms only within one workflow run: every arm then shares the
compiler, the machine type and the calendar date (the game's seasonal monster
selection depends on the date).

A proposed redesign of storage, long-run resume and the cemetery, shared
with borg-cemetery, is in [docs/data-foundation/](docs/data-foundation/README.md)
(borg-zoo#114; for owner review, not yet adopted).

See [docs/DESIGN.md](docs/DESIGN.md) for the design and its open questions,
and [AGENTS.md](AGENTS.md) and [RULES.md](RULES.md) for working rules.
