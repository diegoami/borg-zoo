# Balanced999: completed baseline versus Zoo speed30 experiment

**Completed:1,998/1,998 valid cells,999 distinct saved scenarios,111 per class per setup.** No missing, invalid, stopped or wall-timeout cells.

[Full Zoo execution](https://github.com/diegoami/borg-zoo/actions/runs/44058010288) · [Archived compact JSON](https://github.com/diegoami/borg-zoo/blob/results/saved-incident-results/balanced999-baseline-vs-speed30/44058010288-1/comparison.json) · [Dashboard preview artifact](https://github.com/diegoami/borg-zoo/actions/runs/44058010288/artifacts/14316884028) · [Run one scenario](https://github.com/diegoami/borg-cemetery/blob/evidence/paired-smoke-validation/docs/RUN-A-SCENARIO.md)

Live dashboard presentation is prepared in [UI PR179](https://github.com/diegoami/borg-zoo/pull/179). Automatic approval review requires explicit owner approval for that specific main-branch merge. The experiment and archive are complete; the preview contains all999 individual scenario pages.

## Outcomes

| Setup | Death | Survival to horizon | Total |
|---|---:|---:|---:|
| Baseline reborn | 528 | 471 | 999 |
| Exact Zoo speed30 bundle | 291 | 708 | 999 |

Paired outcomes:315 rescued,78 newly killed,213 both died and393 both survived. “Rescued” means baseline death versus candidate survival to the finite horizon; it does not mean an eventual win.

| Class | Starts/setup | Baseline deaths | Speed30 deaths | Rescued | Newly killed | Start levels |
|---|---:|---:|---:|---:|---:|---|
| Warrior | 111 | 48 | 29 | 30 | 11 | 1–15 |
| Mage | 111 | 67 | 25 | 48 | 6 | 1–6 |
| Druid | 111 | 73 | 45 | 36 | 8 | 1–6 |
| Priest | 111 | 60 | 22 | 40 | 2 | 1–8 |
| Necromancer | 111 | 66 | 33 | 43 | 10 | 1–8 |
| Paladin | 111 | 53 | 32 | 30 | 9 | 1–8 |
| Rogue | 111 | 52 | 42 | 19 | 9 | 1–10 |
| Ranger | 111 | 58 | 35 | 37 | 14 | 1–6 |
| Blackguard | 111 | 51 | 28 | 32 | 9 | 1–10 |

## Builds and configuration

| Setup | Source commit | Core | Configuration |
|---|---|---|---|
| Baseline | `6d1bca10bc67d02150a1a717f111891976e98069` | reborn | Saved default numeric profile |
| Zoo speed30 | `193d9076747cd5c52e1fe1f6ea314570d8f3873a` | borg-rs | `4.2.6-reborn-rust-speed-fight` / `reborn-bundle-plan-speed30` |

The candidate uses the complete original Zoo profile, including healing, town/trip policy, class attack preferences and `errands_plan.txt`, plus attack speed fight danger tenths30. Native parameter values/origins and the loaded errands SHA were checked in every candidate cell. Classic settings without native readback are input-file verified.

The two setups differ in source, controller and configuration. Interpret the result as a descriptive comparison on this incident-selected bank. Isolating speed30 or making population claims needs separate controlled studies. Only2 starts had an identified Potion of Speed; unidentified inventory and later opportunities are separate from that screen.

## What the suite contains and how it ran

611 historical deaths and388 observed critical-HP recoveries from758 source lives, with178 equipment kind/slot combinations. Critical recovery requires actual damage to≤25% HP followed by observed recovery≥50%. Qualified counterfactual lethality remains unavailable. Shared-life encounters remain correlated.

All cases loaded original native saves with fresh Borg memory and saved engine RNG. Both setups used exact2,000-engine-turn horizons and5-second native wall budgets. Initial resources and baseline equipment/inventory were checked; candidate native pack/equipment/rune hashes had to match the observed baseline.

| Stage | Zoo run | Cumulative scenarios | Cumulative cells | Newly executed cells |
|---|---|---:|---:|---:|
| Smoke | [44046247609](https://github.com/diegoami/borg-zoo/actions/runs/44046247609) | 18 | 36 | 36 |
| Small | [44049067280](https://github.com/diegoami/borg-zoo/actions/runs/44049067280) | 90 | 180 | 144 |
| Medium | [44049683178](https://github.com/diegoami/borg-zoo/actions/runs/44049683178) | 360 | 720 | 540 |
| Big | [44054323639](https://github.com/diegoami/borg-zoo/actions/runs/44054323639) | 900 | 1800 | 1080 |
| Full | [44058010288](https://github.com/diegoami/borg-zoo/actions/runs/44058010288) | 999 | 1998 | 198 |

Each stage independently revalidated the parent receipts, reused the exact original compiled builds and played only new cases. No case was replayed between these formal tiers. Jobs were bounded at40 starts and eight concurrent jobs.

Sum of measured per-cell execution/receipt elapsed times:619.75s baseline and571.34s candidate,1191.09s total (about0.60s per cell). These sums exclude building, queues, artifact transfer, stage validation and publication; jobs run in parallel.

The initial validation run44045219309 is retained separately. It exposed the missing borg-rs observation stream, post-autosave input hashing and wrong candidate exporter pin. Corrected adapters preserved all108 key/state/message hashes across the repeated cloud smoke. All actual deaths, including the7 first-run candidate export failures, are retained/recovered explicitly in Cemetery. Repeats are not extra independent observations.

## Run one case with a specific Borg

[Cemetery’s executable guide](https://github.com/diegoami/borg-cemetery/blob/evidence/paired-smoke-validation/docs/RUN-A-SCENARIO.md) gives the exact source/tool/artifact setup and single-case command. It supports compatible `borg-reborn-rs` builds using the reborn or borg-rs controller. The guide is in Cemetery with the saves and native code; Zoo owns this comparison and dashboard presentation.

Example: level1 Druid `c2-r2-s1020000-i000` in bank shard000. Run `scripts/single_encounter.py` with the selected source commit/core and, for speed30, the retained complete borg.txt and errands file. The same executable binary and configuration were actually tested locally: key and state streams match the Zoo run; messages differ only in the diagnostic’s absolute run-root path and match after explicit normalization. Both raw hashes are retained.

Every dashboard case page provides its own ID, manifest, initial equipment/resources, outcomes, hashes and copyable commands. Native inputs/evidence and the single-case guide are canonical in [Cemetery PR65](https://github.com/diegoami/borg-cemetery/pull/65); the execution integration is [Zoo PR169](https://github.com/diegoami/borg-zoo/pull/169).
