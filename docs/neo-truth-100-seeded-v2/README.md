# Corrected Neo monster-truth run

The owner requested this new run after merging the three danger-cache/HP/retreat
repairs and the headless monster-truth correction tracked in
[port100](https://github.com/diegoami/neo-angband-borg-mod-tracker/issues/100).
It preserves the frozen seeded-v2 1800 assignments, point-buy/no-selling rules,
100000-tick cap, 600-second per-game watchdog, 36 shards, four simultaneous jobs
and two processes per job. Source and toolkit are pinned together in the new
specimen; the stock/kit engine remains b4af703. Clock640 remains unresolved.

The earlier cohort43670231534 remains immutable. Its source76f25aa did not
contain the three retreat/danger fixes and its host denied monster combat-data
reads. Do not describe it as the fully repaired Borg or compare its death rate
with native C as a faithful performance measurement. The new arm is a separate
run, with no claim of population improvement from selected replays.

A local six-case5000-tick pilot on source/toolkit c0414a0 (runtime-identical to
merged967b28f, whose later changes affect CI only) completed with a valid
bundle-identified monster-truth receipt in every run:

| Seed | Outcome | Turn |
| --- | --- | --- |
|350019725|cap|5000|
|557466218|grey mold death|1469|
|36984942|cap|5000|
|772054174|cap|5000|
|1957415190|cap|5000|
|1972606412|grey mushroom death|452|

These selected cases verify the corrected runtime and receipt path; they do not
estimate the full cohort's survival. The actual source/toolkit pin is merged967b28f5fe12c4974a6a793040f73246eb7d1200;
source CI43701712464 passed ordinary/exact-source1194 tests with no skips and
the additional real measurement-engine host gate before merge. All six pilot
births, options, Borg startup seeds and activation RNG states match the original
records exactly.
