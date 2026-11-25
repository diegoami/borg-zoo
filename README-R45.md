# Track R4.5 parity (borg-zoo#792)

The owner's receiving task: paired native / check / switch runs of the pinned
borg-reborn-rs harness suites, gated by `harness/check-r45-suite.py`.

- `.github/workflows/r45-parity.yml` — dispatch workflow: 3 arms × shards run
  the pinned `harness/suite.sh` per slice (native `24be987` shadow off;
  candidate `83e28cd` shadow check/switch), then a stage job merges each arm
  into the suite.sh layout, demonstrates failed-cell retention, and runs the
  checker from the `610aabe` pin.
- `zoo/r45_parity.py` — the staging helper (merge shards, rewrite the manifest
  to the canonical suite name/sha, union the `run_config.*` lines, write
  `DONE`; verify every cell's `run_exit`, the cell set, and the shadow files).
- Pinned constants (verified 2026-11-25 against both refs and the checker):
  borg.txt `dd21cc3e…`, smoke `ee385771…`, full `7c81c28c…`.
- Smoke pilot first (owner-authorized in #792); the 45-start `full` exit slice
  is requested on the pilot's evidence.
