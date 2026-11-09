# Recorded-life analysis: original C and Neo Borgs

Start with the [plain-language maintainer handoff](MAINTAINER-HANDOFF.md) for the consequence, one-life reproduction and browser recipe.

The full run is complete: **C: 619 deaths / 1,181 caps; Neo: 1,450 deaths / 311 caps / 35 controller-watchdog stalls / 4 wall timeouts**. All 3,600 planned records and all 28,798 recorded raw files are verified. The [immutable collected data and death index](https://github.com/diegoami/borg-zoo/tree/dc0a348aab6f8b3169fa52118fd32e247e7a781f/results/originals-20261108-classes-1800/42534228784-1) remain the source evidence. This report separates a directly established port omission from broader mechanisms whose causal effects have not been measured.

**The strongest concrete finding is lost spellbook protection.** Original C [checks whether the current character can browse the book before selecting a thrown object](https://github.com/angband/angband/blob/e473720ed88a0f0c7ca66815cef3000eb4a38bc3/src/borg/borg-fight-attack.c#L2294-L2300). Official Neo Borg [only excludes MAGIC_BOOK and PRAYER_BOOK](https://github.com/neostryder/neo-angband-mod-borg/blob/014c810466ec7ac0b9b7a83416e075238c72edd0/src/fight/attack.ts#L1206-L1214). Nature and Shadow books remain eligible, even for their own caster. This differs from the measured original C source; it is not a C gameplay improvement being requested of the faithful port.

Across all Neo records, 351 lives issued a throw targeting a starting-book handle. Explicit Core projectile messages confirm throwing an own-realm book in **at least 320 lives**: 143 Druids, 171 Blackguards, four Necromancers and two Rangers. Complete C notes contain zero own-realm-book throws. The confirmed Neo subset contains 240 deaths, 76 caps, two watchdog stalls and two wall timeouts. Those counts establish occurrence, not the number of deaths a correction would prevent. A future parity correction must reproduce C's class-browsability predicate, not simply forbid every book type.

**Retail procurement is almost absent in this Neo profile.** Native C has retail-buy notes in 1,798 lives; 1,389 have such a note by tick 1,000, and 1,798 by tick 10,000. Retained C game messages independently confirm purchases in at least 1,137 lives, but native message history is bounded, so that is a lower bound. Neo issued one retail-buy intent and its complete message stream confirms one purchase, a ration at tick 17,119. It has zero buy intents before tick 10,000 and zero before the first descent intent. This is not 'never shops': one purchase and one sale really happened. Only 11 terminal Neo records contain any nonempty known store stock; an empty record does not prove no visit. Existing deferred port-tracker [#56](https://github.com/diegoami/neo-angband-borg-mod-tracker/issues/56), [#57](https://github.com/diegoami/neo-angband-borg-mod-tracker/issues/57) and [#58](https://github.com/diegoami/neo-angband-borg-mod-tracker/issues/58) are relevant leads, not newly created tasks.

The recorded inventories are consistent with a resource gap. At death, named healing/antidote items appear in 332/619 C dumps versus 151/1,450 Neo snapshots. Named phase/teleport/speed consumables appear in 103 C death dumps and zero Neo terminal inventories. Unidentified Neo items may have those effects; C dump inventory is recorded Borg observation, not a freshly loaded save. Resource absence is a plausible risk contributor, not a measured causal share. The surviving Neo controls also commonly survive without buying anything.

**The deaths concentrate very early and around specific hazards.** Neo has 934 deaths before tick 10,000 versus 216 C deaths; 1,368 Neo deaths occur on DL1 versus 472 C deaths. Creatures declared NEVER_MOVE in the respective pinned content kill 321 Neo characters versus 48 C characters; Maggot's dogs kill 238 versus 114; poison kills 131 versus 29. A declared immobile killer is not automatically an avoidable encounter. These are descriptive counts from different games, not paired outcomes or proof that every discrepancy is a port bug.

### Representative traces and surviving references

All records were audited before selecting cases. For each of the three largest cause groups above, the Neo death is the lower median death tick, with numeric seed breaking ties. The Neo cap reference matches class/race when available, then minimizes initial-HP difference, birth-stat-vector distance and seed. C cap references match class/race and initial HP where possible. They are reference examples, not matched worlds. The immobile group has no surviving Kobold Druid: its only Neo Druid cap is a stronger Half-Troll and is explicitly a class-only fallback.

- **Immobile median: Kobold Druid 483514869**, floating-eye death at tick 5,025. Born with 10 HP and one Nature book, it studies/casts Detect Life, then throws that book at a crow at tick 220. The Core confirms the hit; no book remains and no further cast occurs. At the end it repeatedly requests northward movement into an adjacent visible eye, becomes repeatedly paralysed and dies. The final recorded map has an open corridor to the south, but paralysis prevents action for much of the terminal window. Its Half-Troll Druid cap reference **100579143** also issues a starting-book throw and finishes without the book, yet survives to level 6 and tick 100,004. That is a counterexample to any deterministic 'book loss means death' claim. The C Kobold Druid reference **164026340** keeps its own Nature books, buys supplies, notices a floating eye early, and survives; different world and other setup differences remain.
- **Dog median: Half-Elf Warrior 1255090136**, Fang death at tick 5,441. It starts with 19 HP, reads its Recall scroll at 5,368, and dies 73 ticks later while retreating/being bitten, before recall completes. No retail purchase or identified healing/instant-escape consumable is recorded. The nearby-stat, same-race/class Neo cap **522091966** also has no retail purchase, demonstrating that the missing procurement is not sufficient by itself to force a death. C reference **182815350** survives with recorded healing supplies.
- **Poison median: Elf Warrior 1593777953**, death at tick 12,600. The full life has no quaff intent. It repeatedly acquires poison from a white worm mass, walks while warnings accumulate, and dies with a Berserk potion and unidentified potions, not a recorded known antidote. It used its Recall scroll much earlier and returned to town at 3,950, then re-entered without buying supplies. Same-race/class, same-initial-HP Neo cap **767827692** survives without retail purchases too; its different encounters matter. C reference **91007333** survives with recorded cure/antidote stock and uses a Teleportation scroll when encountering a floating eye.
- **C failure reference 1872536818**, selected by the same median rule among C immobile-killer deaths, keeps attacking a silver jelly with last-noted HP 1/13 and dies. A Cure Light Wounds potion is printed in its dump. This shows that risky terminal combat exists in original C as well; the report does not claim C always avoids immobile monsters or always uses supplies optimally.

The [selection rules](case-selection.json), [case manifest and raw-artifact links](case-manifest.json), and [complete selected raw traces](selected-raw-traces.tgz) preserve these ten lives byte-for-byte. All copied files were rechecked. Native has full Borg notes and bounded retained messages, not raw key commands; Neo has complete intent/message/state streams. No game, repair or source proposal was added during this analysis.

### Important limits and method correction

Initial HP medians are 14 in both arms. 1,192 Neo starts equal the native median for their class/race; 979 of these die. Lower initial HP alone does not describe the gap, but other birth stats, gear and host differences remain uncontrolled. Native uses default point buy; Neo uses ordinary Core roller birth. C birth stats/gold/gear were not separately recorded, and birth_no_selling is true in C versus false in Neo.

The earlier first-descent timing comparison must not be used as 'time spent preparing in town'. Native's 861 median is a periodic-snapshot upper bound; timed location notes can miss brief earlier descents too (1,423 notes appear after an earlier positive maxDepth snapshot). Retail action timing above is directly recorded and does not rely on that claim. Native energy is cumulative energy spent; Neo energy is the current balance. Gate acceptance does not guarantee the Core action succeeded.

The 35 Neo stalls are original-controller watchdog releases: 15 casts and one study ending in 'You cannot see!', 11 repeated refusals, four rests and four tunnels. Game time can advance during a rest stop. Four wall timeouts remain unknown endpoints, with no terminal run.json/map. The measured toolkit is still `2668adc`; the separately versioned viewer is presentation only. No whole-game fidelity or causal attribution follows from mortality alone.

### Deaths by class (200 starts per arm)

| Class | C deaths | Neo deaths | Neo stalls | Neo wall timeouts |
| --- | ---: | ---: | ---: | ---: |
| Blackguard | 39 | 114 | 4 | 2 |
| Druid | 141 | 199 | 0 | 0 |
| Mage | 62 | 170 | 12 | 0 |
| Necromancer | 66 | 181 | 16 | 1 |
| Paladin | 37 | 167 | 2 | 0 |
| Priest | 48 | 133 | 1 | 0 |
| Ranger | 86 | 185 | 0 | 0 |
| Rogue | 76 | 182 | 0 | 0 |
| Warrior | 64 | 119 | 0 | 1 |

## Confidence and next source lane

| Finding | Confidence and boundary | Next review lane |
| --- | --- | --- |
| Browsable-book protection differs from C | High: original source predicate and real book projectile messages agree. Mortality benefit of a correction is unmeasured. | Faithful Neo Borg port; use class-browsability semantics, including off-realm controls. |
| Retail procurement gap | High for recorded actions/messages; native confirmations are a lower bound. Birth wealth/gear are not symmetrically recorded. | Existing port #56/#57 and engine/known-stock contract review; no duplicate queue added. |
| Repeated closed-store exits | High for observed refusals; no browser reproduction or sole-cause attribution. | Existing deferred port #58 and host lifecycle cross-check. |
| Immobile-killer/paralysis concentration | High for cause counts and selected sequence; medium/low for any general policy explanation. Original C also fails in such encounters. | Compare danger/avoidance/escape inputs at a matching decision boundary before assigning port versus inherited C responsibility. |
| Poison and fast-dog deaths with limited known emergency stock | High for recorded inventory/messages; causal contribution of procurement, birth, encounter and policy differences remains unmeasured. | Port resource acquisition/caution first, with engine status/timing checks if inputs disagree. |
| Four wall timeouts | All four end with repeated accepted tunnel intents, no world-time progress and “You see nothing there to tunnel.” Available streams are preserved, but terminal state/maps are missing. They are not deaths. | Port recovery/target selection plus engine/adapter feature knowledge; attribution unproved. |

## Deaths by race

| Race | Starts per arm | C deaths | Neo deaths | Neo stalls | Neo timeouts |
| --- | ---: | ---: | ---: | ---: | ---: |
| Dunadan | 162 | 57 | 139 | 1 | 0 |
| Dwarf | 162 | 39 | 136 | 1 | 0 |
| Elf | 162 | 78 | 139 | 5 | 1 |
| Gnome | 162 | 58 | 132 | 5 | 0 |
| Half-Elf | 171 | 64 | 140 | 4 | 1 |
| Half-Orc | 162 | 49 | 125 | 1 | 2 |
| Half-Troll | 162 | 38 | 108 | 1 | 0 |
| High-Elf | 162 | 41 | 118 | 5 | 0 |
| Hobbit | 162 | 61 | 133 | 3 | 0 |
| Human | 171 | 82 | 157 | 3 | 0 |
| Kobold | 162 | 52 | 123 | 6 | 0 |

## Death tick distribution

| Engine ticks at death | C | Neo |
| --- | ---: | ---: |
| 0-999 | 7 | 144 |
| 1000-2499 | 23 | 232 |
| 2500-4999 | 74 | 277 |
| 5000-9999 | 112 | 281 |
| 10000-24999 | 171 | 270 |
| 25000-49999 | 111 | 150 |
| 50000-100000 | 121 | 96 |

The full depth/level distributions, class/race counts, birth-HP strata and coverage are in [summary.json](summary.json). See [METHOD.md](METHOD.md) for counter definitions, selection rules, source/build verification and reproduction. Raw run/build artifacts expire after 90 days; this bounded selected-trace bundle is retained in Git. These observations do not establish whole-game fidelity or a causal decomposition of the mortality difference.
