# Agent entry: borg-zoo

This session owns **diegoami/borg-zoo**: running seed suites across Borg
specimens and profiles, storing every run, and publishing comparisons. Read
[README](README.md), [RULES](RULES.md) and [docs/DESIGN.md](docs/DESIGN.md)
first. What the finished experiments showed, and what is still open, is in
[docs/FINDINGS.md](docs/FINDINGS.md). Update it when an experiment finishes.
[docs/OPEN-WORK.md](docs/OPEN-WORK.md) lists dispatch and replay traps, owner decisions and dated handovers.

```sh
git status --short
python3 -m unittest discover -s tests
for e in experiments/*.json smoke/*.json; do python3 -m zoo plan --experiment "$e"; done
gh run list -R diegoami/borg-zoo --limit 10
```

Related repositories, read only:

- [better-borg-c](https://github.com/diegoami/better-borg-c): the native C
  Borg with carried fixes, and the runner the zoo uses.
- [neo-angband-tracker](https://github.com/diegoami/neo-angband-tracker): the
  C Borg specification (`docs/c-borg/BORG_SPEC.md`), the tunable-Borg plan
  (`docs/c-borg/TUNABLE-BORG-PLAN.md`), findings and enhancement issues
  (#368–#371 quick gains, #376 experiment toolkit).
- [borg-rs](https://github.com/diegoami/borg-rs) and
  [borg-reborn-rs](https://github.com/diegoami/borg-reborn-rs): native
  headless specimens, including pinned source and engine identities in modern runs.

Adding a specimen, profile, suite or experiment is a catalogue change with a
pull request. Experiments are written as YAML in `definitions/` and generated
with `python3 -m zoo define` (RULES 15, `docs/DEFINE.md`); what can be asked
for is in `docs/PROFILES.md` (`/profiles`). Starting a large experiment is the owner's call. It costs no
money (standard runners are free for this public repository), but its shards share the owner's 20 concurrent Actions job slots with other
workflows and publish to the append-only results branch.
