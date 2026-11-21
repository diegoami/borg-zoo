# Deaths in reborn-main-default-verysmall (borg-zoo#543)

Run [44841145368](https://github.com/diegoami/borg-zoo/actions/runs/44841145368), specimen `4.2.6-reborn-rust-main-2801ba18`. A reading aid written by `python3 -m zoo.death_report`, not a cemetery entry or a causal diagnosis.

1 deaths in 45 games, 1 distinct dying games. Replayed locally from the run's own build artifact, arms `reborn-maindefault-shipped`: every replayed play hash matches CI.

| Game | Dies in | Killed by | Char level | Dungeon level | Game turn | Keys |
|---|---|---|---|---|---|---|
| [Rogue Elf 102088710](#rogue-102088710-e2024c6a) | `reborn-maindefault-shipped` | Fang, Farmer Maggot's Dog | 2 | 1 (max 1) | 13373 | 1840 |

## Observations

One death in 45 starts (`classes-1800-verysmall`, 100,000 turns, shipped settings of main 2801ba18, no overrides): an Elf Rogue, killed on DL1 at character level 2 by Fang, Farmer Maggot's Dog, at game turn 13,373 (1,388 player turns). Observations from the retained logs (`messages.log`, `town-transactions.jsonl`, `trace-core.jsonl`); no diagnosis.

**The game before the dog**
- The Rogue had been on DL1-and-town for 13,000 game turns without gaining a level past 2: 16 recorded trips ("Trip: continue via none (plan 1): at-plan"), 36 downward flows, and 36 "heading up (bored and unable to dive: Clevel < depth)" notes. It never reached DL2 (`max_depth` 1).
- Four town purchases, all in the first 850 game turns: 4 Rations of Food (12 gold), 4 Red Potions (80; the Cure Light Wounds), 21 Flasks of oil (63) and 3 Scrolls of Phase Door (45), leaving 1 gold.
- **All 21 flasks were thrown by game turn 9,943** (16 throws, the last at a rock lizard: "You have no more Flasks of oil"), 3,400 game turns before Fang. No re-buy: the Rogue had 1 gold until it picked up 81 shortly before dying.

**The fight (game turns 13,028 to 13,373)**
- Fang appeared at 14/14 HP (CL2, max HP 14, Dagger 1d4, Soft Leather Armour, no launcher, no flasks): "Scary guy on level", "Fleeing and leaving the level", "Flowing toward stairs at cost 14". The scary list has Fang up to CL 6 for a Rogue, so it was scary at CL2.
- Fang (speed +20, 25 HP) was adjacent within 3 thinks. The notes then say "Fight race: 1 attackers, 8.000 turns to kill, 4.208 damage/turn, HP 14: **not winning** (#759)", and, in the same think, "Phase rule (from escape 4.1 compromised): enemy adjacent but the fight is **not lost** (danger 12, HP 14): no Phase Door; other escapes, else fight". It attacked (attack type 1, melee, value 32): "Phase rule: attacked instead of a Phase Door". Eight melee attack decisions in all, and no throw (no oil).
- **"Refusing flight Recall: modelled contact exposure 138.86 HP during 34 world ticks, HP 14 (#758)"** on its first think and again on every think while Fang was in view (exposure 140 to 527 HP); later also "unmodelled spell/status risk from 1 reachable monsters". The Rogue carried one Scroll of Word of Recall and never read it.
- Healing and escape: **8 Cure Light Wounds quaffed** (the 4 bought plus 4 more found; the last "no more" at game turn 13,333) and **3 Phase Door read**: at HP 10/14 ("the fight looks lost (danger 12)"), at HP 8/14 ("escape 1 emergency", "68 scary landing grids of 100 (at most 75)" noted, read anyway) and at HP 6. Each Phase put Fang back adjacent within a few steps; a grey mold (3 HP, killed) and later a cutpurse (30 HP) and fruit bats joined.
- Death: HP 5/14 with a cutpurse and Fang adjacent, "Performing attack type 1" again, then "Fang bites you" twice and "You die" at HP -1.
- Left unused at death: **7 unidentified Scrolls titled "salae colemo"** (never read), one Scroll of Word of Recall, and an Apple, 5 Rations, a Robe and 3 Wooden Torches in the pack.

**Against the rest of the run:** the other 44 starts reach the cap alive (mean CL 6.20, DL 2.20 over all 45). This Rogue is the one start that sat at CL2 for the whole game (`max_level` 2).


## Handover: working on these deaths in the Borg's repository

For a session in diegoami/borg-reborn-rs that changes parameters or code against these deaths. That repository owns the Borg; the zoo only measures, and any change is measured here later as a new specimen.

- **Build:** `diegoami/borg-reborn-rs` at `2801ba188b1f46ddfdd32eeb7ae7c58330b0fd30` (zoo specimen `4.2.6-reborn-rust-main-2801ba18`): `BORG_IMPL=rust harness/build.sh`, or the run's CI artifact: `gh run download 44841145368 -R diegoami/borg-zoo -n build-4.2.6-reborn-rust-main-2801ba18`.
- **Settings:** each death's exact `user/borg.txt` is `evidence/<death>/borg.txt` (with its plan file, if the arm sets `borg_plan`, from the specimen's `harness/plans/`).
- **Evidence:** `evidence/<death>/`: inventory at death, last 300 log lines, trip decisions, summary.

Re-run one death from the built `game/` directory, with no `BORG_*` variables set and `OUT` holding `user/borg.txt` and empty `save/ archive/ panic/ scores/`:

```
env -u BORG_PROFILE -u BORG_CORE -u BORG_ERRAND -u BORG_PLAN TZ=UTC LANG=C.UTF-8 LC_ALL=C.UTF-8 \
  ./angband -mborgh -n -uBorg -duser=$OUT/user -dsave=$OUT/save -darchive=$OUT/archive -dpanic=$OUT/panic -dscores=$OUT/scores \
  -- -seed SEED -race R -class C -turns 100000 -keylog $OUT/keys.log -summary $OUT/summary.json -menu-letters \
  -exact-turns -statelog $OUT/state.log -msglog $OUT/messages.log
```

`sha256sum keys.log` must start with the play hash below, or it is not the same game.

| Death | Seed | -race | -class | Arm | Play sha256 |
|---|---|---|---|---|---|
| [Rogue 102088710](#rogue-102088710-e2024c6a) | 102088710 | 2 (Elf) | 6 | `reborn-maindefault-shipped` | `e2024c6a8d00bc88` |

In borg-zoo, `python3 -m zoo.death_report --experiment experiments/reborn-main-default-verysmall.json --run 44841145368` replays and checks them all. Where to look first (observations from the zoo, not yet diagnosed):
1. The same think holds two verdicts on one state: #759's fight race says "not winning" (8 turns to kill, HP 14) while the Phase rule says "the fight is not lost (danger 12, HP 14)" and attacks instead of reading Phase Door.
2. #758's flight Recall refusal on a Fang in view at HP 14 (modelled exposure 139-527 HP over 34 world ticks): what a read at the first sighting would have cost, since the stairs were at cost 14.
3. Why the Rogue stayed at CL2 on DL1 for 13,000 game turns ("bored and unable to dive: Clevel < depth"; #522's gates, #541), with its oil all thrown by game turn 9,943 and no gold to buy more.
4. Seven unread unknown scrolls at death.
After a change: a PR in the Borg's repository, then ask the borg-zoo session for a new specimen at the merged commit and a pilot (or verysmall) of the same arms.

<a id="rogue-102088710-e2024c6a"></a>
## Rogue Elf 102088710: Fang, Farmer Maggot's Dog

- Dies in: `reborn-maindefault-shipped`, the same game (play `e2024c6a8d00bc88`).
- Same start elsewhere: none.
- Last state line: `13373 103,11 d1/1 hp-1/14 sp0/0 f8469 au81 xp23 lv2 t- o3:3792,5:5000 p98626963746fd425 eb46fece410dfef25 r08ee9afe362a4c74`

- Cure potions quaffed: 8; Phase Door read: 3; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 0; Failed teleports: 0; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Elf Rogue, Level 2/2
Exp: 123  Gold: 81  Turn: 13373
Killed on level: 1 (max. 1) by Fang, Farmer Maggot's Dog
```

**Character Equipment**

```
a) Dagger (1d4) (+0,+0)
f) Wooden Torch (3792 turns)
g) Soft Leather Armour [8,+0]
```

**Character Inventory**

```
a) Apple
b) 5 Rations of Food
c) Scroll of Word of Recall
d) 7 Scrolls titled "salae colemo"
e) 3 Wooden Torches (5000 turns)
f) Robe [2,+2]
```

### Last trip decisions

```
925 5852 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1097 7382 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1213 8372 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1354 9433 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1400 9823 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1459 10183 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1568 11698 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1657 12528 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 30 game messages

```
1802 13293 39 Fang, Farmer Maggot's Dog, bites you.
1806 13293 0 You feel much better.
1806 13293 0 You have 2 Potions of Cure Light Wounds (c).
1806 13298 39 Fang, Farmer Maggot's Dog, bites you.
1807 13303 39 Fang, Farmer Maggot's Dog, bites you.
1811 13303 0 You feel much better.
1811 13303 0 You have a Potion of Cure Light Wounds (c).
1811 13308 39 Fang, Farmer Maggot's Dog, bites you.
1815 13313 3 You miss Fang, Farmer Maggot's Dog.
1815 13313 3 You miss Fang, Farmer Maggot's Dog.
1815 13318 39 Fang, Farmer Maggot's Dog, bites you.
1819 13323 2 You hit Fang, Farmer Maggot's Dog.
1819 13323 2 You hit Fang, Farmer Maggot's Dog.
1819 13328 39 Fang, Farmer Maggot's Dog, bites you.
1820 13333 39 Fang, Farmer Maggot's Dog, bites you.
1824 13333 0 You feel much better.
1824 13333 0 You have no more Potions of Cure Light Wounds (c).
1824 13343 39 Fang, Farmer Maggot's Dog, bites you.
1828 13343 3 You miss Fang, Farmer Maggot's Dog.
1828 13343 3 You miss Fang, Farmer Maggot's Dog.
1828 13348 39 Fang, Farmer Maggot's Dog, bites you.
1832 13353 2 You hit Fang, Farmer Maggot's Dog.
1832 13353 3 You miss Fang, Farmer Maggot's Dog.
1832 13363 39 Fang, Farmer Maggot's Dog, bites you.
1836 13363 2 You hit Fang, Farmer Maggot's Dog.
1836 13363 3 You miss Fang, Farmer Maggot's Dog.
1836 13368 39 Fang, Farmer Maggot's Dog, bites you.
1837 13373 39 Fang, Farmer Maggot's Dog, bites you.
1838 13373 8 You die.
1839 13373 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
1830 13353 0 # There was a monster 'cutpurse' at (11,106)
1830 13353 0 # Forgetting a monster 'cutpurse' at (11,106)
1830 13353 0 # Scary guy on level.
1830 13353 0 # Loc:11,103 Dep:1 Lev:2 HP:6/14 SP:0/0 Danger:p=12
1830 13353 0 # Fleeing and leaving the level. (scaryguy)
1830 13353 0 # Refusing flight Recall: unmodelled spell/status risk from 1 reachable monsters; modelled contact exposure 433.57 HP during 34 world ticks, HP 6 (#758)
1830 13353 0 # Adjacent to monster on Scaryguy Level.
1830 13353 0 # Performing attack type 1 with value 32.
1830 13353 0 # Facing Fang, Farmer Maggot's Dog at (11,104) who has 8 Hit Points.
1830 13353 0 # Attacking with weapon 'Dagger (1d4) (+0,+0)'
1834 13363 0 # HIT:Fang, Farmer Maggot's Dog (+)
1834 13363 0 # MISS:Fang, Farmer Maggot's Dog (+)
1834 13363 0 # HIT_BY:Fang, Farmer Maggot's Dog (+)
1834 13363 0 # Creating a monster 'cutpurse' at (11,106), HP: 30, Index: 37
1834 13363 0 # Removing Regional Fear (11,106) because of a LOS cutpurse
1834 13363 0 # HIT:Fang, Farmer Maggot's Dog (2)
1834 13363 0 # MISS:Fang, Farmer Maggot's Dog (2)
1834 13363 0 # HIT_BY:Fang, Farmer Maggot's Dog (3)
1834 13363 0 # There was a monster 'fruit bat' at (11,105)
1834 13363 0 # Forgetting a monster 'fruit bat' at (11,105)
1834 13363 0 # Scary guy on level.
1834 13363 0 # Loc:11,103 Dep:1 Lev:2 HP:5/14 SP:0/0 Danger:p=40
1834 13363 0 # Fleeing and leaving the level. (scaryguy)
1834 13363 0 # Refusing flight Recall: unmodelled spell/status risk from 2 reachable monsters; modelled contact exposure 474.79 HP during 34 world ticks, HP 5 (#758)
1834 13363 0 # Adjacent to monster on Scaryguy Level.
1834 13363 0 # Performing attack type 1 with value 32.
1834 13363 0 # Facing Fang, Farmer Maggot's Dog at (11,104) who has 6 Hit Points.
1834 13363 0 # Attacking with weapon 'Dagger (1d4) (+0,+0)'
1839 13373 0 # Aborting (death).
1839 13373 0 # Aborting (player died).
```
