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

`bench_sqlite.py` output:

```json
{
 "cells": 219795,
 "raw_record_bytes": 748914771,
 "load_s": 15.5,
 "index_s": 0.3,
 "db_bytes": 551854080,
 "queries": {
  "per-arm outcome summary (all runs)": {"ms": 40.8, "rows": 331},
  "per-class summary, one run": {"ms": 11.7, "rows": 9},
  "paired rescued/newly-killed, one run, two arms": {"ms": 20.3, "rows": 1},
  "per-seed history across all runs": {"ms": 0.3, "rows": 93},
  "runs sharing one exact configuration": {"ms": 0.0, "rows": 0},
  "fetch + inflate one full record": {"ms": 7.1, "rows": 1}
 }
}
```

`db_bytes` includes each full record gzipped on its own (294 MiB of it).
Without them the scalar index is 141 MiB, or 32 MiB gzipped. The
configuration query hit a cell with no `config_sha256` (22,029 cells have
none), so it returned no rows; this is a property of the data, not of the
query.

Other numbers on the [decision page](../README.md#measured-baseline-2026-11-15)
come from the commands above and from `gh run list -w pages.yml` and
`gh run list -w compare.yml`.
