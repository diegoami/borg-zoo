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
| [Specimens](catalogue/specimens.json) | A Borg version: the game and Borg source at a pinned commit. Today: the original C Borg (angband/angband `e473720`) and better-borg-c milestones 1–4 (2, 7, 34 and 42 carried fixes). |
| [Profiles](catalogue/profiles.json) | A configuration: the `borg.txt` settings a run uses. Every run checks the settings the Borg actually applied; one that did not take effect makes the run a `config_error`. |
| [Suites](catalogue/suites.json) | Frozen seed lists with a turn cap, time limits and a birth rule. |
| [Experiments](experiments/) | Specimens × profiles × suites, with a control arm for paired comparison. |
| Runner | [better-borg-c](https://github.com/diegoami/better-borg-c)'s native runner and observer, pinned in the specimens catalogue. The zoo calls it; it does not reimplement it. |
| Results | One JSON line per run on the [`results`](https://github.com/diegoami/borg-zoo/tree/results) branch, append-only, one directory per workflow run. |
| Site | Static tables built from the results branch: outcomes per arm, paired rescued/newly-killed counts, survival by turn, depth reached. |

## Running an experiment

On GitHub: **Actions → compare → Run workflow**, then choose the experiment
file. The workflow builds each specimen once, runs the cells in parallel
jobs, appends the results to the `results` branch and rebuilds the site.

A big experiment is better run one arm at a time: `python3 -m zoo arms
--experiment experiments/F.json` lists the arms (`SPECIMEN:PROFILE`), and
each is dispatched with the `arm` input. Every arm run keeps the experiment's
name as its tag and appends its own run to the `results` branch; the site
merges the arm runs of a tag into one experiment page and says where they
differ (date, harness commit, compiler). A timeout then costs one arm, not the
experiment.

**Smoke checks** (a milestone or head builds and plays) live in
[`smoke/`](smoke/), not in `experiments/`. **Actions → smoke → Run workflow**
runs one. The dashboard lists smoke runs, old and new, under its **Smoke** tab
and keeps them out of the comparisons.

Locally (under the shared validation lock if other sessions use this machine):

```sh
git clone https://github.com/diegoami/better-borg-c.git harness
git -C harness checkout "$(python3 -c 'import json;print(json.load(open("catalogue/specimens.json"))["harness"]["commit"])')"
python3 -m zoo build --specimen 4.2.6 --harness harness --out specimens/4.2.6
python3 -m zoo run --experiment experiments/milestones-smoke.json --specimen 4.2.6 \
  --build specimens/4.2.6 --harness harness --work work --out cells/4.2.6.jsonl
python3 -m zoo collect --experiment experiments/milestones-smoke.json --cells cells \
  --results results --run-id local-1
python3 -m zoo site --results results --out _site
```

Tests: `python3 -m unittest discover -s tests`.

## Reading the results

The tables are descriptive. Suites are small, intervals are wide, and the
primary endpoint is not yet fixed. "Goal" (alive at the cap having reached
dungeon level 5) is a placeholder until it is. Runs that stall, time out,
crash or fail in the harness are counted and shown, never relabelled as
deaths. Compare arms only within one workflow run: every arm then shares the
compiler, the machine type and the calendar date (the game's seasonal monster
selection depends on the date).

See [docs/DESIGN.md](docs/DESIGN.md) for the design and its open questions,
and [AGENTS.md](AGENTS.md) and [RULES.md](RULES.md) for working rules.
