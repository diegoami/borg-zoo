# C/Neo shared-seed startup continuation, v2

**The shared seeds now align at startup in all eleven bounded pilot pairs.**
The earlier suggestion that equivalent seeds could not be used was too broad.
The RNG kernel agrees; startup operations and engine ordering needed correction.
This is a local reproduction on one machine, not a survival comparison.

All eleven pairs match race/class, point-buy stats, initial HP/SP, gold, exact
inventory quantities and equipment, player placement, every1452 town terrain
cell, the active32-word main RNG pool/index, the Borg startup seed, and the
underlying main stream after that one startup-seed draw. See
[startup-comparison.json](startup-comparison.json). Both arms completed their
requested2000ticks in all eleven cases. Future decisions, monster state and
first-dungeon generation were not established equivalent by these checks.

Cases: Human Warrior303, Mage304, Druid305, Priest306, Necromancer307,
Paladin308, Rogue309, Ranger310, Blackguard311; Dwarf Warrior313 and
High-Elf Mage314. These are eleven initial-state checks, not a representative
sample for estimating survival.

## What caused the deviation

| Cause | Concrete effect | Correction |
| --- | --- | --- |
| Headless birth skipped native menu generations | Native seed303 reaches HP rolling after48 main draws; the old Neo host started at0 | v2 performs the four real age/history generations before HP and retains the accepted fields |
| Neo appends shop/home stock; C prepends | Seed303 first differs at shop0 maintenance pass1; different wares receive later iteration/deletion | [engine issue635 / PR638](https://github.com/diegoami/neo-angband-tracker/pull/638) |
| Neo retains starting-kit parse order; C prepends | Warrior303 had140 gold and different torch/food quantities instead of146 | [engine issue636 / PR639](https://github.com/diegoami/neo-angband-tracker/pull/639) |
| C leaves random `loc(x,y)` argument evaluation order unspecified | This GCC14.2 build draws Y before X; JavaScript draws X before Y, changing streamer geometry and resident placement | Explicit compiler-specific benchmark adapter; [attribution issue637](https://github.com/diegoami/neo-angband-tracker/issues/637) |
| TS Borg defaults to a constant private seed | Startup decisions cannot share C's private random stream even with matching worlds | v2 draws exactly one Borg seed from the game stream, as C does |

The store correction restores all156 per-owner/per-maintenance RNG checkpoints
for Warrior303. With both source corrections and both coordinate sites adapted,
Warrior303 starts at(22,3), with146gold and Borg seed71118219 in both engines.
The first coordinate-only attempt fixed town terrain but still left nine of
eleven active streams unequal; adapting resident-placement order resolves those
initial-stream differences too. These failed/intermediate attempts are retained.

This does **not** justify a universal seed offset. We now use the same seed
without an offset or copying native states. Later differences in game rules,
Borg decisions, data traversal, rejection loops or additional compiler-dependent
expressions can change subsequent draws. They must be located where they arise.
C's inactive quick RNG value differs from Neo's initialized dormant value;
at Borg startup C switches its global quick mode while Neo keeps a separate
private generator. The comparator explicitly compares the active main stream
and the private startup seed, rather than claiming byte equality of those
different representations.

## Pins and proposal separation

- Native C: `e473720ed88a0f0c7ca66815cef3000eb4a38bc3`.
- Native measurement tools: better-borg-c
  `fc9d97cb46aa0aaa27773e5c83a41ec395d515fc`; exported observation extension,
  GCC14.2.0 Debug, test frontend, X11 disabled. Native source delta and seals
  are included. No C source repository was edited or posted to.
- Measured Neo: `06a2321ce30a414df20d1b20d486446e7688171c`, with benchmark
  backports `8120673dd507efcaf990e6de004f79c73acc7f5e` and
  `18ee52eaa550aef7a2d10c822f6669cab57c6e7d`, published on the engine fork's
  `task/seed-continuation-measured` branch. Pack data stays at06a2321.
- Borg: `9c17cb0c582fe129008899491372787e91abdade`, unchanged.
- Final toolkit: [4015f0d](https://github.com/diegoami/neo-angband-borg-mod-tracker/commit/4015f0d),
  [PR95](https://github.com/diegoami/neo-angband-borg-mod-tracker/pull/95),
  stacked on the unchanged v1 birth/options PR94. Node26.
- Current-upstream engine proposals start independently at pristine
  `765f39976462c2d6e414ba88d44feb15ca28ceb8`: stock
  `2fd9b11373e20b97fd54ed9ba51d35f1ff64abf3`, outfit
  `be049ef65a34514de3c85e3ffa789d353e12ee7c`. They exclude session docs and
  are distinct from the older benchmark backports. No source merge/deployment
  is represented by this report.

Birth uses C recommended point buy, no-selling enabled and explicitly recorded
Boolean options from v1. v2 adds startup sequencing; the GCC coordinate adapter
is an additional explicit build option. Old frozen suites/results are unchanged.

## Validation and reproducibility

Toolkit: typecheck,1170tests in63files with no skips, plugin build check and
host controls pass. Four native menu RNG controls pass for Human, Dwarf,
High-Elf and invalid-race rejection. The initial control incorrectly compared
inactive quick-stream representations; its failure is retained, followed by
explicit checks of each representation and equality of the active pool/index.
An intentionally mismatched pair fails the startup comparator.

Current source stock proposal: Core/SDK/content builds;99store tests pass.
Parent source with the final tests retained gives4failures/95passes (three new
regressions plus the existing explicitly corrected native-order expectation).
Current outfit proposal: same builds;55bind/gear tests pass. Parent source
with the final tests retained gives2failures/53passes. Imported4.2.6 f308221
and current C42cd156 preserve both list-prepend behaviors. These are engine
port defects, not intentional departures from C.

Ordinary and `c-point-buy-v1`2000-tick command/message hashes match the parent
08f3d7b toolkit with the new startup hooks compiled but inactive; see
[unchanged-controls.json](unchanged-controls.json). A compiled GCC adapter
requires v2 and cannot silently affect those controls. The final build manifest
records both applied startup/compiler adapters.

With the built engine/Borg pins above and toolkit4015f0d:

```sh
flock /tmp/angband-validation.lock node tools/zoo/build.mjs \
  --engine-dir ENGINE --borg-dir BORG \
  --engine-pin 18ee52eaa550aef7a2d10c822f6669cab57c6e7d \
  --borg-pin 9c17cb0c582fe129008899491372787e91abdade \
  --alignment-probes true --exact-tick-cap true \
  --c-seed-startup true --c-gcc-coordinate-order true --out NEW_BUILD
flock /tmp/angband-validation.lock node tools/zoo/run.mjs \
  --bundle NEW_BUILD/bundle.mjs --birth-profile c-seeded-point-buy-v2 \
  --seed 303 --race Human --class Warrior --turns 2000 --out NEW_RUN
```

The toolkit's alignment README documents native build/run and comparator commands.
Extract `raw-attempts.tgz`, then run toolkit
`tools/zoo/alignment/compare-startup.mjs verification-pairs.json` from its root.
The archived manifest uses relative paths and explicitly normalizes native
body-slot sentinel12 to Neo pack slot-1. To replay the compiled Neo build,
extract `compiled-attempts.tgz` and use its `gcc-both-build/bundle.mjs` with the
archived composed pack. Compiled attempts before that build can share this pack
only after verifying their recorded content hashes; all measured source changes
are code-only. Native rebuilds require the separately pinned source archive,
recorded tools and included delta; the final driver has a formatting-only
follow-up to the measured driver hash, so do not relabel the old binary hash.

[attempt-ledger.json](attempt-ledger.json) counts all47local run attempts,
including the failed store-probe harness, the partial coordinate pilot and four
unchanged-behavior controls. They are not pooled into the final eleven pairs.
`raw-manifest.json`, `compiled-manifest.json`, per-build metadata, source patches,
logs and `SHA256.json` retain provenance. CI state is reported separately on the
proposal PRs; these local passes do not assert CI completion.

No new large cohort was launched. The outstanding survival gap has not been
explained away: the previous C/Neo survival totals remain uncontrolled for these
new settings and engine fixes, and this startup pilot cannot establish the
consequence of later engine or Borg differences.
