# Zoo deaths in the cemetery (#176)

By default `compare.yml` attempts replay bundles for natural deaths.
The borg-rs adapter supports replay. The operator imports verified bundles
into [borg-cemetery](https://github.com/diegoami/borg-cemetery) with its
importer.

## In the run job

`compare.yml` passes `zoo run --deaths DIR` and the experiment can opt out.
The run writes each cell record first. For supported harnesses it then
replays each cell whose `outcome` is `death` once in the same job:

- The replay uses the same argv, `borg.txt` and plan, with `-msglog`,
  `-statelog` and `BORG_RUN_DIR` added (the core's decision trace and
  parameters). Ambient `BORG_*` variables are cleared, as for the cell. A cell
  that set the observation-only record streams (`BORG_TOWN_PLAN_RECORD`,
  `BORG_TRIP_RECORD`; retained-evidence and town-shadow cells only) gets them
  in the replay too, inside the bundle, and `config.txt` names them in
  `zoo_record_streams`. Every other cell sets neither, in play or replay.
- The replay's `keys.log` sha256 must equal the record's `play_sha256`.
  Otherwise the bundle is kept, marked `not_reproduced`, and the cemetery does
  not import it.
- The cell record is never changed. Bundles only add to the job's time: a death
  is played twice. On the local check (32 deaths of the `reborn-heal-pilot`
  shards) that took seconds per death. The worst case is a shard where every
  cell dies, which takes up to about twice its cells' play time. Size shards
  near the job timeout with that in mind.

`DIR/index.jsonl` is created before play, so a shard without deaths has an
empty index. A line is appended and flushed as each bundle finishes. A
cancelled or timed-out shard therefore still uploads an index for every bundle
it finished (RULES 13), and the cemetery lists any bundle directory that has
no index line. The index has one line per death, with `status` set to `reproduced`,
`not_reproduced`, `error` (the replay failed) or `unsupported` (a harness kind
other than borg-rs, which is listed and never dropped). Each bundle directory,
`DIR/<suite>/<specimen>/<profile>/<seed>/`, is the run directory that the
cemetery's `scripts/native/export-death.py` reads:

| File | What |
| --- | --- |
| `summary.json`, `keys.log`, `messages.log`, `state.log` | the replay's own output |
| `trace-core.jsonl`, `trace-core.lines` | the last 200 core thinks (what a dossier keeps); the full line count |
| `params-core.json` | the core's parameters |
| `user/borg.txt`, `user/<plan>`, `user/errands_plan.txt` | what the cell read; the plan again under the name the dossier keeps |
| `config.txt` | seed, race/class indices, cap, `borg_txt_sha256`, `zoo_*` provenance and the profile's `borg_*` settings, which the cemetery's `rerun-death.py` uses to rebuild `borg.txt` (see below) |
| `BUILD_ID` | the specimen build's identity (`git_rev`, `source_sha256`, ...) |
| `zoo-death.json` | the index entry plus the full cell record |

`config.txt` uses the format of the 58 zoo dossiers already in the cemetery.
A plan is `borg_errands_plan=user/NAME` with its hash in
`errands_plan_sha256`. Only the zoo path of the cemetery's `rerun-death.py`
(borg-cemetery#59, `zoo_plan`) reads that key. The older harness path reads
`borg_errands_plan_sha256` and cannot rerun a zoo cell in any case.

`compare.yml` uploads `DIR` as `deaths-<specimen>-<shard>`, kept 90 days,
whether or not `retain_evidence` is set. A death costs about 250 KB compressed.

This archive is separate from the raw attempt tarballs and the build
artifact used by `zoo.death_report`. See [DESIGN](DESIGN.md#evidence-and-collection)
for their paths and retention.

An experiment opts out with `cemetery_deaths: false` under `extra:` in its
definition.

## In the cemetery

```sh
python3 scripts/import_zoo_deaths.py --run RUN_ID
```

The script downloads the run's `deaths-*` artifacts and exports every
reproduced bundle as a `D-<sha256>` dossier. The README, REPLAY and
`build.sh`/`watch.sh`/`play.sh` launchers come with it, and the catalogue is
updated. It also writes a page for the run listing every death and every bundle
it did not import. A death the cemetery already has (same encounter family and
key stream) is a repeat and is not added again.
