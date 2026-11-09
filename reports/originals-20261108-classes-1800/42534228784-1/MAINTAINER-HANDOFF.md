# Maintainer handoff: own spellbooks are thrown away, and supplies are almost never bought

In this reproducible headless profile, the original Neo Borg can throw away the book its own caster needs. The clearest trace is a Kobold Druid that throws its only Nature spellbook at a crow at tick 220, never casts again, and later dies to a floating eye. The same source also almost never attempts to buy supplies. These are concrete recorded behaviours and a checked source difference, not a claim that we have measured what share of the mortality gap they cause.

**The first question for the Borg maintainer is small and specific:** should the throwing guard match C's class-browsability predicate? [Original C protects books this character can browse](https://github.com/angband/angband/blob/e473720ed88a0f0c7ca66815cef3000eb4a38bc3/src/borg/borg-fight-attack.c#L2294-L2300); [the measured Neo Borg only excludes MAGIC_BOOK and PRAYER_BOOK](https://github.com/neostryder/neo-angband-mod-borg/blob/014c810466ec7ac0b9b7a83416e075238c72edd0/src/fight/attack.ts#L1206-L1214). Nature and Shadow books remain throwable. A faithful correction would preserve the class-specific rule, rather than ban every book indiscriminately.

Across all 1,800 Neo starts, **351 lives issue a throw on a starting-book handle; explicit Core projectile messages confirm an own-realm book in at least 320 lives**. Those confirmed lives include 240 deaths and 76 caps, so losing a book is not deterministically fatal. Complete native C notes contain no own-realm-book throw. No gameplay correction has been made on these branches.

## Start with the recorded Druid

- **Seed:** `483514869`; **race/class:** Kobold Druid.
- It studies/casts Detect Life, then issues `throw(handle=5)` at tick 220. The Core says its Book of Nature Magics hits a crow.
- The book is absent afterward; only one cast occurs in the full life. It reaches level 2 with 3/3 SP but no book.
- The last map records a visible floating eye immediately north. Northward walk intents, repeated paralysis and gaze messages end in death at tick 5,025.
- The systematically selected surviving Druid is a stronger Half-Troll because no Kobold Druid cap exists. It also issues a starting-book throw and survives without the book. This is a reference, not a matched world or proof that retaining the book would prevent the selected death.

The [ten complete selected traces](selected-raw-traces.tgz) include this life as `cases/neo-5a9-original-483514869/`. The [case manifest](case-manifest.json) gives original artifact links and hashes; [selection rules](case-selection.json) show how all deaths and surviving references were chosen after auditing the full dataset.

## Browse first; no game build is needed

Python 3.10+, a normal browser, and authenticated GitHub CLI are enough to start inspecting the original records:

```sh
git clone https://github.com/diegoami/neo-angband-tracker.git neo-borg-tools
git -C neo-borg-tools checkout e1ad87d738118ef1565b8134f07115d44575e9df
cd neo-borg-tools
python3 tools/original-borg/browse.py --github-run 42534228784
```

This downloads compact catalogues, starts a loopback-only viewer and opens the browser. Filter for seed **483514869**, select it, then explicitly choose **Download raw shard**. Summary, Inventory, Final map and raw command/message/state panes display recorded evidence. The Neo map is a labelled projection of recorded terrain codes; it is not a screenshot or replay. [Viewer instructions](https://github.com/diegoami/neo-angband-tracker/blob/e1ad87d738118ef1565b8134f07115d44575e9df/tools/original-borg/browser/README.md) cover offline caches and hash checks.

To reproduce one life rather than just read it, use a separate measurement-tool checkout at `2668adc5ab3e2b6e194c2f1561e248b88850ea98`, fresh original engine/Borg checkouts at the pins below, and Node 22. After the documented frozen install and Core/content/SDK build:

```sh
node neo-measure/tools/original-borg/build.mjs   --engine-dir engine --borg-dir borg --out fresh-original-build
node neo-measure/tools/original-borg/run.mjs   --bundle fresh-original-build/bundle.mjs   --seed 483514869 --race Kobold --class Druid   --turns 100000 --out fresh-druid-record
```

[Full one-life setup](https://github.com/diegoami/neo-angband-tracker/blob/2668adc5ab3e2b6e194c2f1561e248b88850ea98/tools/original-borg/README.md) supplies the pinned source/build commands. A rerun is a diagnostic repeat, not an additional independent cohort life.

## What was run

[Workflow 42534228784](https://github.com/diegoami/borg-zoo/actions/runs/42534228784) completed 1,800 original C and 1,800 original Neo starts: nine classes, 200 each, with eleven races cycled. All 3,600 records and 28,798 raw files were independently checked. [Immutable collected records, manifest and 2,069-death index](https://github.com/diegoami/borg-zoo/tree/dc0a348aab6f8b3169fa52118fd32e247e7a781f/results/originals-20261108-classes-1800/42534228784-1).

| Outcome | Original C | Original Neo |
| --- | ---: | ---: |
| Death | 619 | 1,450 |
| Turn cap | 1,181 | 311 |
| Original-controller watchdog stall | 0 | 35 |
| Wall timeout | 0 | 4 |

The cap is 100,000 engine ticks, ten per normal-speed action. C stops exactly; Neo stops at a Core-loop boundary (largest observed overshoot 867 ticks). No post-cap death occurred. Stalls and timeouts are not deaths, and a watchdog stop need not freeze game time.

Runtime pins: **Angband `e473720`**, **Neo engine `5a9cab2`**, **Neo Borg `014c8104`**, measured Neo toolkit **`2668adc`**, native observer **`fc9d97c`**, Zoo measurement **`9cd7423`**. Full hashes and build qualifications are in [METHOD.md](METHOD.md). These are original-source gameplay implementations with explicit measurement instrumentation/host boundaries, not Mandos's carried gameplay corrections. Viewer revision `e1ad87d` is separately versioned presentation code.

C and Neo integer seeds generate different games. C uses default point buy; Neo uses ordinary Core roller birth. Initial HP medians are both 14, but other birth stats, gear, knowledge and host differences remain uncontrolled. Native messages are bounded retained history. These counts describe this profile, not a whole-game fidelity test or a causal mortality decomposition.

## Separate unresolved question: town procurement

By tick 10,000, 1,798 C lives have a retail-buy note; Neo has no buy intent in that window. Across the entire run, Neo issues/confirms **one retail purchase**, a ration at tick 17,119. Native retained messages independently confirm purchases in at least 1,137 lives. Notes/acceptance are not transaction success, and native history is bounded.

The practical question is whether the port's shop-coordinate initialization and observed-stock contract allow C's town planning to work. Existing deferred [port #56](https://github.com/diegoami/neo-angband-borg-mod-tracker/issues/56), [#57](https://github.com/diegoami/neo-angband-borg-mod-tracker/issues/57) and [#58](https://github.com/diegoami/neo-angband-borg-mod-tracker/issues/58) are leads; no duplicate task or repair was started here. Surviving Neo examples also buy nothing, so the data do not assign a causal death count to procurement.

## Branches and publication

| Repository/branch | PR/state | Purpose |
| --- | --- | --- |
| `neo-angband-tracker:task/original-borg-headless` | [#542](https://github.com/diegoami/neo-angband-tracker/pull/542), open proposal | One-life original Neo runner plus separately versioned local log browser. |
| `borg-zoo:task/pristine-originals-1800` | [#26](https://github.com/diegoami/borg-zoo/pull/26), merged at `9cd7423` | Frozen original-source suite, orchestration, all-attempt evidence retention and collector. |
| `borg-zoo:task/originals-42534228784-analysis` | [#28](https://github.com/diegoami/borg-zoo/pull/28), draft for review | This readable analysis, methods, receipts, all-record tables and selected full traces. |

These are **tooling and evidence branches; no gameplay fix is included**. All three PRs are in **our own forks**. The official Neo maintainer is not automatically notified by them, and no upstream gameplay-fix PR exists. The [full report](REPORT.md), [methods](METHOD.md), [all-record summary](summary.json) and [verification receipts](collector-verification.json) are already reviewable. A maintainer can start inspecting the selected life now without adopting a fix or running another large suite.

The proposed first upstream handoff is the Neo Borg mod repository for the specific book-protection omission, with the engine/tooling discussion linked separately. External posting is held for parent review of this wording. Open questions are the intended class-browsability guard, the shop/known-stock contract, and whether these host/birth choices represent the desired diagnostic profile. The broader combat and poison concentrations remain investigation leads with explicit confidence in the full report.
