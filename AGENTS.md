# Agent entry: borg-zoo

This session owns **diegoami/borg-zoo**: running seed suites across Borg
specimens and profiles, storing every run, and publishing comparisons. Read
[README](README.md), [RULES](RULES.md) and [docs/DESIGN.md](docs/DESIGN.md)
first.

```sh
git status --short
python3 -m unittest discover -s tests
for e in experiments/*.json; do python3 -m zoo plan --experiment "$e"; done
gh run list -R diegoami/borg-zoo --limit 10
```

Related repositories, read only:

- [better-borg-c](https://github.com/diegoami/better-borg-c): the native C
  Borg with carried fixes, and the runner the zoo uses.
- [neo-angband-tracker](https://github.com/diegoami/neo-angband-tracker): the
  C Borg specification (`docs/c-borg/BORG_SPEC.md`), the tunable-Borg plan
  (`docs/c-borg/TUNABLE-BORG-PLAN.md`), findings and enhancement issues
  (#368–#371 quick gains, #376 experiment toolkit).
- [borg-rs](https://github.com/diegoami/borg-rs): a later specimen, once it can
  run the same suites.

Adding a specimen, profile, suite or experiment is a catalogue change with a
pull request. Starting a large experiment uses GitHub Actions minutes and is
the owner's call.
