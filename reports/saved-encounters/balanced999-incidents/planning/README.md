# Balanced999 Zoo execution plan

Status: planned; no games dispatched by this planning request.
Tracking: [Zoo #168](https://github.com/diegoami/borg-zoo/issues/168),
[implementation PR169](https://github.com/diegoami/borg-zoo/pull/169).

Use the completed [harvest43979480269](https://github.com/diegoami/borg-zoo/actions/runs/43979480269):
999 distinct saved starts,111 for every one of the nine classes,611 historical
deaths and388 observed critical-HP recoveries from758 source lives. There are
178 equipment kind/slot combinations. Near-death screening requires actual HP
loss to≤25% followed by recovery≥50%; counterfactual lethality is unavailable.

## Requested setups

| Setup | Exact source | Core | Configuration |
|---|---|---|---|
| Baseline | `6d1bca10bc67d02150a1a717f111891976e98069` | reborn | Saved default profile, hash checked per scenario |
| Zoo speed30 | `193d9076747cd5c52e1fe1f6ea314570d8f3873a` | borg-rs | `4.2.6-reborn-rust-speed-fight` / `reborn-bundle-plan-speed30` |

The speed30 reference is [Zoo43994684018](https://github.com/diegoami/borg-zoo/actions/runs/43994684018),
Zoo source45066abaed03d9b966c9860925e33c68c2144fd2. The complete profile is
frozen under `scenario-inputs/balanced999-speed30/`, including town/trip policy,
healing and class attack preferences. Its attack speed fight danger tenths is30.
The exact `errands_plan.txt` SHA is
`084bc3e8999697bd8edf7fd302ea75d65b50ef2714afdd3a47354a1f24137e87`.
The same literal plan bytes are retained with the profile snapshot.

Both setups play the same999 saves:1998 expected cells,111 per class per arm.
They differ in source, controller core and configuration. This compares the
complete setups; it cannot isolate the speed parameter's effect. Use the same
runner image/compiler/toolchain within the comparison, building each target once.

## Stages and gates

| Stage | Cumulative starts per class | Cumulative scenarios | Cumulative cells, both arms | New cells |
|---|---:|---:|---:|---:|
| Smoke | 2 | 18 | 36 | 36 |
| Small | 10 | 90 | 180 | 144 |
| Medium | 40 | 360 | 720 | 540 |
| Big | 100 | 900 | 1800 | 1080 |
| Full | 111 | 999 | 1998 | 198 |

Stages execute only newly added cases and report cumulative outcomes. Every
class is balanced at each boundary. Bound jobs at40 starts and eight concurrent
execution jobs. Smoke timings establish runtime estimates before expansion.
Each case starts from the same original save with fresh Borg memory and saved
engine RNG, at most2000 engine turns and5 native wall seconds. Treat wall
expiry, load errors, missing receipts and configuration failures as failures.

Before expansion, inspect exact source/build/process hashes, loaded save/state,
class/race/resources/equipment, parameter readbacks and core identity. For the
candidate, verify the loaded errands-file hash as well as the written input.
Classic settings with no native readback remain explicitly input-file verified.
All missing/invalid cells block a gate; stopped outcomes also block intermediate
expansion. A failed gate prevents further work. No automatic change to main or
milestone acceptance follows from a passed gate.

Report per-class and incident-type deaths/survival-to-horizon, and paired rescued,
newly killed, both died, both survived, stopped/inconclusive and invalid/missing.
Count every expected cell. Retain canonical gameplay evidence in Cemetery and
aggregate comparisons in Zoo. Shared-life encounters remain correlated; these
are not999 independent population samples. Where possible, report which cases
had usable Speed potions and whether they were drunk; many early starts may not.
No improvement claim follows from this single bank alone.

## Exact inputs and execution readiness

The original bank artifact is14289964111 from run43979480269.
Its outer ZIP SHA is
`0aba17ff59883d2d9990ecf69108a19b1d2a2ab312dfd4fff8b0c584d9d7da2d`;
the inner `balanced999-bank.tgz` SHA is
`186066b039ccc8451642cbcbd77e714c6615c20d99d0de4b18963289c5748cbf`.
Cemetery code pin: `b93a7fc8e6509a462f05e7c2652d6ebe34c625d7`.
Native tools pin: `1afd9423d7f8a1340eca9d74cff85443e769b1a9`.
The generated bank is a separately hashed artifact over that code checkout;
it is not claimed to be tracked in the b93a7fc8 commit. Its native validation
checked every case, input digest, class quota and unique saved state.

`baseline-plan.json` is the validated999-case baseline schedule.
`comparison-plan.json` freezes both setups, all999 paired identities, per-case
requested candidate borg.txt hashes and the cumulative1998-cell schedule.
Both documents carry content hashes. Their Zoo code commit is the planning
implementation pin; the following receipt commit retains those documents.

The baseline has a saved-state execution workflow. The candidate requires Zoo
integration of Cemetery's `scripts/scenario_config.py:run_configured` and its
borg-rs/configured receipt validation before it can be dispatched. Candidate
save compatibility, named parameters, loaded plan and runtime behavior must pass
the paired smoke. **The comparison plan is not yet a dispatchable experiment.**
Do not feed its definition to the ordinary natural-run compare route.

Definitions are `definitions/balanced999-incidents-execution.yaml` and
`definitions/balanced999-incidents-speed30-comparison.yaml`; generate/check them
with `python3 -m zoo define`. To recreate plans after unpacking the exact bank
into a clean detached Cemetery b93a7fc8 checkout and checking out baseline6d1bca10:

```sh
python3 -m zoo.incident_bank plan \
  --definition scenario-experiments/balanced999-incidents-execution.json \
  --bank /path/to/cemetery-b93 --source /path/to/reborn-6d1bca10 \
  --archive /path/to/balanced999-bank.tgz --out /fresh/path/baseline-plan.json
python3 -m zoo.incident_comparison \
  --definition scenario-experiments/balanced999-incidents-speed30-comparison.json \
  --baseline /fresh/path/baseline-plan.json --out /fresh/path/comparison-plan.json
```
