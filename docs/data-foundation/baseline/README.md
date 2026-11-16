# Baseline measurements (2026-11-15)

Inputs: `results` at `d7b05dc56d8ecafed394e34925333dd211ea32ea`, zoo `main`
at `a0f000c`, on the owner's machine (WSL2, Python 3, SQLite from the
standard library). No experiment was changed or dispatched.

```sh
git fetch origin results
git worktree add --detach /tmp/results origin/results

# Size and composition
git ls-tree -r --long origin/results | awk '{s+=$4; n++} END {print n, s}'
cat /tmp/results/results/*/*/cells.jsonl | wc -l
cat /tmp/results/results/*/*/cells.jsonl | gzip -6 | wc -c

# Site build time, memory and output size
/usr/bin/time -v python3 -m zoo site --results /tmp/results/results --out /tmp/site
du -sh /tmp/site /tmp/site/runs

# Embedded index: load every cell, time the dashboard queries
python3 -I docs/data-foundation/baseline/bench_sqlite.py /tmp/results/results /tmp/zoo.db

# Live Actions artifacts by kind
gh api -X GET repos/diegoami/borg-zoo/actions/artifacts -f per_page=100 --paginate \
  --jq '.artifacts[]|[.name,.size_in_bytes,.expires_at]|@tsv'
```

`bench_sqlite.py` output (revised after the PR #119 review: the paired query keeps only finished games of one harness kind, and the configuration query picks a cell that has a configuration hash):

```json
{
 "cells": 219795,
 "raw_record_bytes": 748914771,
 "load_s": 16.4,
 "index_s": 0.4,
 "db_bytes": 551854080,
 "queries": {
  "per-arm outcome summary (all runs)": {"ms": 46.0, "rows": 331},
  "per-class summary, one run": {"ms": 11.9, "rows": 9},
  "paired rescued/newly-killed, one run, two arms": {"ms": 22.3, "rows": 1},
  "per-seed history across all runs": {"ms": 0.3, "rows": 93},
  "runs sharing one exact configuration": {"ms": 15.5, "rows": 34},
  "fetch + inflate one full record": {"ms": 8.9, "rows": 1}
 }
}
```

`db_bytes` includes each full record gzipped on its own (294 MiB of it).
Without them the scalar index is 141 MiB, or 32 MiB gzipped. 22,029
cells have no `config_sha256`.

These are query workloads shaped like the dashboard's, not the zoo's
statistics: the paired query does not apply every pairing rule
(command-stream profile, mode cutoff). The independent review reproduced the
counts and sizes exactly, with times of 0.1–114 ms on its run; timings vary
with load. Volumes ten times larger were not tested.

Other numbers on the [decision page](../README.md#measured-baseline-2026-11-15)
come from the commands above and from `gh run list -w pages.yml` and
`gh run list -w compare.yml`.
