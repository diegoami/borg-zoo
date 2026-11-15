# Remaining clock lead

A source-checked continuation lead is tracked at https://github.com/diegoami/neo-angband-tracker/issues/640 . C e473720 player-birth.c:447 sets turn1; Neo06a2321 session/game.ts:3863 starts turn0. The retained native Warrior303 STATE start record and Neo verified2-neo-303 birth record confirm those initial values.

The eleven successful comparisons check the explicitly listed birth/terrain/RNG fields, not clock, energy, monster state or entire-world equality. Both source loops gate world processing on turn modulo10 before incrementing the clock, so the next controlled replay must check the first world-processing/RNG step. This has not yet reproduced a post-startup RNG consequence or established that a default-clock change is the right correction. No clock patch or new cohort is claimed.
