# C/Neo birth alignment and shared-seed pilot

The birth-policy mismatch is corrected in an **opt-in measurement profile**, and a small pilot verifies it. Equal integer seeds still do not generate matching worlds. The first RNG divergence has been measured, not inferred from mortality.

Tooling: [port PR94](https://github.com/diegoami/neo-angband-borg-mod-tracker/pull/94), head08f3d7b2b6b9d058ac7383f5e7fd3341bdc6fca8, stacked on host93; no gameplay source correction or merge. [Reproduction/tool contract](https://github.com/diegoami/neo-angband-borg-mod-tracker/blob/08f3d7b2b6b9d058ac7383f5e7fd3341bdc6fca8/tools/zoo/alignment/README.md). No upstream submission is added to the owner's separate eight-source-PR queue.

## Design and every attempt

Human births in all nine classes, seeds303–311, plus Human Warrior303 repeated in each engine. This is a local diagnostic pilot, not a survival experiment or a dispatched/frozen catalogue specimen. [Original plan](pilot-plan.json); [exact-cap follow-up plan](pilot-plan-exact.json). Each requested cap is2000 engine ticks. Heavy builds/replays/tests used flock /tmp/angband-validation.lock.

Pins: native C e473720ed88a0f0c7ca66815cef3000eb4a38bc3; native observer fc9d97cb46aa0aaa27773e5c83a41ec395d515fc; Neo engine06a2321ce30a414df20d1b20d486446e7688171c; Borg9c17cb0c582fe129008899491372787e91abdade; Node26.13.1. Read-only exported native instrumentation adds actual birth/gear/RNG evidence. X11 is disabled in favor of the headless test frontend. [Complete native source delta](native-source.patch), [source seal](native-source-seal.json) and build manifests retain compiler, binary, content and tool hashes.

Original pilot:10 C and10 Neo attempts, all turn caps. It revealed Neo's after-loop boundary can overshoot; Necromancer307 reaches2596 for a request of2000. That attempt is retained. Corrected pilot: reuse the same10 immutable native exact-stop records and run10 NEW Neo exact-tick records. **All20 corrected records end at exactly2000; all10 new Neo command streams preserve the original command prefix.** Birth counters start C at1 and Neo at0; these remain documented counter conventions, not a claim of identical elapsed actions or a mortality comparison.

Across both versions, preflights and controls, **38 completed play attempts** are retained in [the ledger](attempt-ledger.json), all capped; they are not38 independent seeds. This includes the initial Neo preflight before activation-option alignment, old/new default and probe controls, final review replays, and exact-cap preflight. Two earlier build failures (native graphical fallback; missing copied profile module) occurred before play; their logs remain in the work log, not counted as completed lives. The ordinary real-Core startup-only unit fixtures are tests, not benchmark lives. No large cohort was launched.

## Verified starting conditions

The profile explicitly matches native C recommended point buy and all46 Boolean option values. At activation it also matches C's pickup_always/pickup_inven settings (C borg-init.c:418/427), with a nearby FORK explanation in the measurement host. This is explicit profile configuration, not a silent policy change to the Borg. Historical/default no-profile behavior and frozen suites are unchanged.

| Check | Matched out of nine classes |
|---|---:|
| Requested and actual race/class |9|
| Natural stat vector |9|
| Initial HP/max HP |9|
| Initial SP/max SP |9|
| All46 initial Boolean options |9|
| All46 active Boolean options |9|
| Initial WELL pool/index |9|
| Full gear including quantities |0|
| Remaining starting gold |0|
| Raw town terrain/placement |0|

All15 birth options are included in the46, including no-selling=true, connected stairs=true and percent-damage=false. Numeric frontend preferences and every possible Borg configuration field are not comprehensively certified by this Boolean-options check. C's pack-slot sentinel12 (Human body.count) is normalized to Neo's -1; handles/inventory ordering are not treated as semantic identity. The raw observations are retained.

| Class | Natural stats STR/INT/WIS/DEX/CON | HP C/Neo | Gold C/Neo |
|---|---|---:|---:|
|Warrior|17/10/10/16/16|20/20|146/134|
|Mage|17/16/10/10/16|10/10|319/337|
|Druid|17/10/16/10/16|12/12|379/376|
|Priest|17/10/16/10/16|13/13|94/97|
|Necromancer|17/16/10/10/16|12/12|363/357|
|Paladin|17/10/15/12/15|17/17|289/295|
|Rogue|17/12/10/17/12|14/14|207/201|
|Ranger|17/10/13/16/13|15/15|118/133|
|Blackguard|17/12/10/17/12|18/18|133/139|

Starting gear differences observed here are random quantities/spares (food, torches and Ranger ammunition); matching items have matching recorded weight/dice/bonuses. For Warrior303, C has no spare torch while Neo has two, and gold is146 versus134. Both have stats17/10/10/16/16 and HP20. C starts at(22,3), Neo at(42,3); both towns are22×66 but their raw terrain differs. No quantitative similarity claim is made from common floor cells or numeric content IDs.

## Why the same seed diverges — confirmed seed303 trace

The initial32-word WELL pool and index agree. The differing inactive quick-seed register (C0, Neo303) is correctly excluded while quick=false. All captured C pool states for seed303 are found on the same TS main-generator sequence at the draw counts below. This is evidence against a raw-generator mismatch at these checkpoints, not an exhaustive RNG proof.

C [player-birth.c:1041,1078,1098,1109](https://github.com/angband/angband/blob/e473720ed88a0f0c7ca66815cef3000eb4a38bc3/src/player-birth.c#L1036) runs player_generate during initial/default setup, reset, race choice and class choice in this native harness path. Every call rolls age/height/weight and history ([C:1017–1026](https://github.com/angband/angband/blob/e473720ed88a0f0c7ca66815cef3000eb4a38bc3/src/player-birth.c#L1017)). C finally rolls HP at accept ([C:1236](https://github.com/angband/angband/blob/e473720ed88a0f0c7ca66815cef3000eb4a38bc3/src/player-birth.c#L1236)). The headless Neo host calls startGame directly; [generatePlayer:501–545](https://github.com/neostryder/neo-angband/blob/06a2321ce30a414df20d1b20d486446e7688171c/packages/core/src/player/birth.ts#L501) rolls HP FIRST, then one age/history pass. Point-buy stat generation itself consumes no RNG in either path.

| Stage | C raw main draws consumed | Neo raw main draws consumed |
|---|---:|---:|
| Seeded |0|0|
| Before HP roll |48|0|
| After HP roll |97|49|
| Before stores (after birth substeps) |97|61|
| World ready |31960|26284|

For this Human seed, each native age/height/weight pass uses5 draws and its history uses7. Four passes consume48 before HP; Neo's single pass follows HP. [Full state checkpoints and draw-count table](rng-counts-303.json). The sequence difference already exists before stores, outfit and town generation. Different later inputs can change rejection counts and generated content, so a constant integer offset is not a justified general seed translator. This does NOT establish that all later store/dungeon algorithms would agree under identical inputs; that remains a separate controlled test.

Borg-local RNG is a distinct later difference: C [borg-init.c:512–514](https://github.com/angband/angband/blob/e473720ed88a0f0c7ca66815cef3000eb4a38bc3/src/borg/borg-init.c#L512) takes another game draw at activation; seed303's private seed is71118219. The TS plugin's default is0x00c0ffee (12648430). This profile does not change that policy or forge either engine's RNG state. Aligning numeric initial seeds alone does not match both streams and their positions.

## Exact-cap correction and meaningful controls

Native observer calls measure_tick immediately after incrementing turn. Original Neo tools check the cap only after runGameLoop returns; long rests can cross it internally. [Core loop.ts:747](https://github.com/neostryder/neo-angband/blob/06a2321ce30a414df20d1b20d486446e7688171c/packages/core/src/game/loop.ts#L747) is the matching increment boundary. PR94's opt-in bundle instrumentation calls a measurement-only hook there, unwinds only the isolated run at the requested cap, and records boundary/guaranteedExact. It does not edit the pinned Core tree, change RNG, disturb the player or add actions. The build refuses a missing/ambiguous hook site.

Fail-before/pass-after case: Necromancer307 reaches2596 with the after-loop observer and exactly2000 with the new observer. All10 exact-cap runs preserve their previous command prefix. The default no-profile run retains its old command hash even in a bundle containing the inactive hook. [Exact-cap controls](exact-cap-controls.json).

Same-engine controls: repeated C birth/RNG checkpoints/final states agree; repeated Neo births and command hashes agree. Initial probe-on/probe-off aligned hashes agree; old/new no-profile hash agrees. [Controls](control-results.json), [review follow-up](final-review-control.json), [complete comparison](pilot-review-exact.json).

Validation: four actual-native-fixture/real-Core profile tests, including the old rolled/no-selling mismatch as a negative control; four real message-host tests;112 zoo tests including active-versus-inactive RNG register and inventory normalization counterexamples; normal TypeScript typecheck; actual20 corrected cap records. These are diagnostic checks, not a new claim that the whole Borg test suite was locally rerun. Hosted required CI on PR94 is reported separately.

## What is and is not fixed

Fixed in proposed tooling: explicit point-buy/birth options; verified starting-stat/HP/SP/Boolean-option records; timeout-resilient birth evidence; exact requested tick stop for the new profile. Old results remain append-only and distinguishable. No full-sized rerun, merge, upstream post or gameplay strategy correction occurred.

Unresolved: matching accepted stochastic birth/world states and Borg-local RNG startup; first-dungeon alignment; every race/class combination; equality of later generators under controlled inputs; engine blindness-ordering and earlier death mechanisms. This pilot does not establish why the large historical mortality gap exists or how much birth/options contributed. Do not present20 short alive caps as a survival improvement.

Next controlled step, before another cohort: define an accepted-birth state/continuation contract or drive equivalent birth UI paths, then compare pre-store, post-store and first-dungeon semantic checkpoints. Use common-state C/TS micro-scenarios to test individual decisions independently. Do not silently pad random draws, change the Borg seed, or call unequal worlds seed-paired. Independent cohorts remain possible after explicit methodology, but the current task authorized only this small pilot.

## Reproduction and evidence

Use the tooling README linked above, the two local pilot plans and `tools/report-birth-alignment.py --work WORK --plan PLAN --out REPORT`. For exact-cap runs build with `--alignment-probes true --exact-tick-cap true` and run with `--birth-profile c-point-buy-v1`. The native harness remains clean at its pin; only isolated exported trees carry the disclosed observer. Build hashes differ across compiler/path/formatting follow-ups; final review replay and command-prefix controls, not a false byte-identical bundle claim, verify behavior.

[Raw attempts](raw-attempts.tgz) include every played preflight/control and both pilot versions. [Per-file bytes/SHA256](raw-manifest.json) and SHA256.json seal the evidence. Canonical source/content/build pins are in the manifests. Some local scripts/paths in run records name this workspace; recreate equivalent fresh paths using the public pins, never the owner's lab. No C save interchange or complete native-controller parity is claimed.
