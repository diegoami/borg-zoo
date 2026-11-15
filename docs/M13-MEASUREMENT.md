# M13 measurement preparation (#87)

**Question:** do M13's nineteen additional fixes change survival and progress
when the starting policy stays the same?

The catalogue already pins C M13 to `9ccb2aaeebc56ad6aeb35b668f112f0f58b142f8`
(tag `4.2.6-impact-v13`). No specimen ref needs changing. This preparation
adds comparisons; it records no new findings and dispatches no runs.

| Definition | What it tests | Games |
| --- | --- | ---: |
| `smoke/m12-m13-modes-smoke.json` | M12 and M13 build and apply normal, class-rule and Lunal profiles on three seeds | 18 |
| `experiments/m12-m13-explicit.json` | M12 against M13, separately under normal and the class-specific start, all nine classes | 7,200 |
| Existing `experiments/classes-v13.json` | Starting policies against each other within M13 | 3,600 |

The full comparison is descriptive. It isolates the milestone package under
one settings profile, not each individual fix. Neither settings comparison
is the source-gated per-mode batch requested in #87.

## What the owner can schedule

1. After the catalogue PR is accepted, start the smoke check. Require both
   builds, all attempted cells counted, and no configuration/harness errors.
   Inspect actual mode entry and branch execution separately from parsing.
2. The owner can then start the full comparison, preferably one arm at a
   time. Its maximum concurrency is eight jobs, one process per job.
3. Read M13 against M12 within the same profile. A cross-profile comparison
   changes the starting policy as well. Separate arm dispatches retain the
   site's calendar/compiler/harness/platform differences warning.

```sh
python3 -m zoo plan --experiment smoke/m12-m13-modes-smoke.json
python3 -m zoo arms --experiment experiments/m12-m13-explicit.json
python3 -m zoo plan --experiment experiments/m12-m13-explicit.json
```

No survival gain is established by a smoke check. No fresh confirmation,
primary endpoint or accepted improvement claim is introduced here.

## The per-fix work still owed

The [inventory](measurement/m13-mode-debt.json) lists **38 numbered units
0100–0137, correction 0101a, and the official import**. The handoff's
“0100–0118 (18 units)” count is off by one: that inclusive range has 19;
0118 belongs to the v12 cycle. The inventory uses the pinned source ledger,
not that shorthand count. Its statuses concern the owed zoo batch; source
fixture results remain separate.

| Group | Requirement before a per-mode result |
| --- | --- |
| Shared-code fixes | Matched before/after source pins, intended mode entered, changed branch shown to execute |
| 0101 + 0101a | Measure the runtime-mode gate; a class/config flag is not the current runtime mode. Normal exploration never calls this take function |
| 0119 | Reach and exercise the late-depth glyph read |
| 0120 | Enter Lunal and receive a monster teleport; normal-only cannot exercise it |
| 0121 / 0122 | Supply the relevant dead-unique / shape-changed unique state; fresh startup is insufficient |
| 0123 | Supply a respawn fixture; fresh-start no-respawn suites cannot exercise it |
| 0124–0130 | Source-classified comments/unreachable cleanup; no behaviour arm required |
| 0136 + 0137 | Keep the vulnerability corrections together in the requested combined comparison |
| Official import | Same engine/content on both sides, varying only the imported Borg hunks; M11 versus M12 does not isolate them |

The profiles `normal`, `munchkin-class` and `lunal` configure play. They do
not make a fix apply only in normal play or only in Lunal play. The zoo
cannot create those runtime source gates under RULES 1. Where #87 requires
such variants, accepted pinned variants must come from better-borg-c.
There is no claim here that the available source fixtures replace cohort
measurements.

Lunal is **not yet exercised**, not neutral. The existing 100,000-turn
experiment description incorrectly called it unreachable by construction.
The source requires preparation 15 levels deeper and sufficient prior depth;
a cap alone does not prove the gate cannot open. A source-provided deep-start
fixture or retained entry/branch evidence is needed before sizing a Lunal
outcome comparison. The 20,000-turn frozen Warrior cohort's documented failure
to reach Lunal cannot be generalized to every class-suite run.

Equal hashes with a disabled change mean **not exercised**. Only a reached
changed branch with a measured unchanged outcome can support “neutral”.
#87 remains open until the owed reachable arms are actually measured and
their evidence is reviewed.

## Runner and source evidence

The harness is already pinned to `9ca98661`, not M10. Its runner and observer
are byte-identical at M13: the three Git blob identities are retained in
[the provenance receipt](measurement/m13-runner-provenance.json). Keeping the
harness pin avoids an unnecessary provenance change while the M13 specimen
supplies the new Borg source.

Pinned sources:

- [M13 ledger](https://github.com/diegoami/better-borg-c/blob/9ccb2aaeebc56ad6aeb35b668f112f0f58b142f8/patches/series.json)
- [M13 package](https://github.com/diegoami/better-borg-c/blob/cfcb6f13fad7e5392c0efc35f8bbe9d69d5087e8/docs/measurement/IMPACT-MILESTONE13.md) (published after the runtime pin; it is absent at `9ccb2aae`)
- [M12 import account](https://github.com/diegoami/better-borg-c/blob/9ccb2aaeebc56ad6aeb35b668f112f0f58b142f8/docs/measurement/IMPACT-MILESTONE12.md)
- [0101 runtime-gate corrections and reachability](https://github.com/diegoami/better-borg-c/blob/9ccb2aaeebc56ad6aeb35b668f112f0f58b142f8/docs/measurement/LUNALTAKE-73.md)
