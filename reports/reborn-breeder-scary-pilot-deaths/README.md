# Deaths in reborn-breeder-scary-pilot (borg-zoo#216)

Run [44147930313](https://github.com/diegoami/borg-zoo/actions/runs/44147930313), specimen `4.2.6-reborn-rust-main-233ef23e`. A reading aid written by `python3 -m zoo.death_report`, not a cemetery entry or a causal diagnosis.

11 deaths in 72 games, 7 distinct dying games. Replayed locally from the run's own build artifact, arms `reborn-503-both`, `reborn-503-ctl`, `reborn-503-nolist`: every replayed play hash matches CI.

| Game | Dies in | Killed by | Char level | Dungeon level | Game turn | Keys |
|---|---|---|---|---|---|---|
| [Mage Human 1548306106](#mage-1548306106-5d05128d) | `reborn-503-ctl`, `reborn-503-fight` | a giant white mouse | 4 | 1 (max 1) | 17969 | 2442 |
| [Ranger Human 226104090](#ranger-226104090-c98d373f) | `reborn-503-nolist` | poison | 7 | 2 (max 2) | 84990 | 14573 |
| [Druid Half-Elf 934061548](#druid-934061548-f83dbe73) | `reborn-503-nolist`, `reborn-503-both` | a kobold shaman | 6 | 2 (max 3) | 53617 | 6140 |
| [Rogue Half-Elf 1381972077](#rogue-1381972077-92023227) | `reborn-503-nolist` | a cutpurse | 6 | 2 (max 2) | 67528 | 8302 |
| [Priest Human 1569794094](#priest-1569794094-288f74e6) | `reborn-503-nolist`, `reborn-503-both` | a yellow jelly | 1 | 1 (max 1) | 5040 | 354 |
| [Necromancer Half-Elf 1574344917](#necromancer-1574344917-4917547d) | `reborn-503-nolist`, `reborn-503-both` | a kobold | 1 | 1 (max 1) | 8398 | 1349 |
| [Rogue Half-Elf 1381972077](#rogue-1381972077-44890862) | `reborn-503-both` | a crow | 6 | 2 (max 2) | 42447 | 5371 |

## Observations

All four arms were replayed, every one of the 72 play hashes matches CI, and the request's four sanity starts reproduce their local hashes in `both`. Observations, not diagnoses:

| Arm (breeder_fight, scary_named) | Deaths /18 | Mean max level | Mean max DL | `Scary guy on level.` notes | `Fleeing (breeder level)` | Down-then-up bounces | Breeder kills | Same play as ctl |
|---|---|---|---|---|---|---|---|---|
| ctl (0, 1) | 1 | 5.00 | 2.17 | 16,443 | 13 | 1,477 | 425 | 18 |
| fight (1, 1) | 1 | 5.00 | 2.17 | 14,646 | 9 | 1,419 | 93 | 8 |
| nolist (0, 0) | 5 | 5.67 | 2.28 | 0 | 16 | 453 | 38 | 0 |
| both (1, 0), shipped | 4 | 5.78 | 2.17 | 0 | 17 | 447 | 74 | 0 |

- **Turning the named scary list off is what changes play.**
  - Every game differs from ctl.
  - The `Scary guy on level.` notes disappear and down-then-up bounces fall by about two thirds.
  - Characters reach a higher level, but 4 to 5 die instead of 1.
- **The same four starts die in both list-off arms:** Druid 934061548 (kobold shaman, DL2, level 6), Rogue 1381972077 (DL2, level 6), Priest 1569794094 (yellow jelly) and Necromancer 1574344917 (kobold). The last two die at character level 1, against monsters on the old list. `nolist` also loses Ranger 226104090 (poison, level 7). Both list-off arms save Mage 1548306106, the only ctl and `fight` death (a giant white mouse).
- **The breeder stand alone (`fight`) changes 10 of 18 games but no outcome.** Breeder-flee notes drop from 13 to 9 and breeder kills from 425 to 93. Fighting early may keep swarms small, but that's unverified.
- **#510 adds no new notes.** `Fleeing (breeder level)` is the older C behaviour that the stand suppresses, so it still appears in ctl.

18 starts per arm cannot show which flags are better.

## Handover: working on these deaths in the Borg's repository

For a session in diegoami/borg-reborn-rs that changes parameters or code against these deaths. That repository owns the Borg; the zoo only measures, and any change is measured here later as a new specimen.

- **Build:** `diegoami/borg-reborn-rs` at `233ef23ebbbbebdbc75c8cc94b74edc5682606c5` (zoo specimen `4.2.6-reborn-rust-main-233ef23e`): `BORG_IMPL=rust harness/build.sh`, or the run's CI artifact: `gh run download 44147930313 -R diegoami/borg-zoo -n build-4.2.6-reborn-rust-main-233ef23e`.
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
| [Mage 1548306106](#mage-1548306106-5d05128d) | 1548306106 | 0 (Human) | 1 | `reborn-503-ctl` | `5d05128d16ac0526` |
| [Ranger 226104090](#ranger-226104090-c98d373f) | 226104090 | 0 (Human) | 7 | `reborn-503-nolist` | `c98d373f1354946b` |
| [Druid 934061548](#druid-934061548-f83dbe73) | 934061548 | 1 (Half-Elf) | 2 | `reborn-503-nolist` | `f83dbe738a300cd5` |
| [Rogue 1381972077](#rogue-1381972077-92023227) | 1381972077 | 1 (Half-Elf) | 6 | `reborn-503-nolist` | `92023227eea4b958` |
| [Priest 1569794094](#priest-1569794094-288f74e6) | 1569794094 | 0 (Human) | 3 | `reborn-503-nolist` | `288f74e6dc083fe8` |
| [Necromancer 1574344917](#necromancer-1574344917-4917547d) | 1574344917 | 1 (Half-Elf) | 4 | `reborn-503-nolist` | `4917547da83fcccd` |
| [Rogue 1381972077](#rogue-1381972077-44890862) | 1381972077 | 1 (Half-Elf) | 6 | `reborn-503-both` | `448908627645e626` |

In borg-zoo, `python3 -m zoo.death_report --experiment experiments/reborn-breeder-scary-pilot.json --run 44147930313` replays and checks them all. After a change: a PR in the Borg's repository, then ask the borg-zoo session for a new specimen at the merged commit and a pilot (or verysmall) of the same arms.

<a id="mage-1548306106-5d05128d"></a>
## Mage Human 1548306106: a giant white mouse

- Dies in: `reborn-503-ctl`, `reborn-503-fight`, the same game (play `5d05128d16ac0526`).
- Same start elsewhere: `reborn-503-nolist` turn_cap, `reborn-503-both` turn_cap.
- Last state line: `17969 151,30 d1/1 hp-1/20 sp0/7 f7709 au148 xp65 lv4 t3:8 o3:4409,5:5000,6:4545 p9c75627355579124 ef229f96d20a8c3a0 r08ee9afe362a4c74`

- Cure potions quaffed: 5; Phase Door read: 2; Unknown potions quaffed: 0; Healing (outmatched) notes: 2; Potion of Speed quaffed: 0; Failed teleports: 2; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Human Mage, Level 4/4
Exp: 165  Gold: 148  Turn: 17969
Killed on level: 1 (max. 1) by a giant white mouse
```

**Character Equipment**

```
a) Rapier (1d6) (+0,+0)
f) Wooden Torch (4545 turns)
```

**Character Inventory**

```
a) Book of Magic Spells [First Spells]
b) 2 Apples
c) 5 Rations of Food
d) Misty Potion
e) Black Potion
f) Scroll of Word of Recall
g) Scroll titled "adicto utius"
i) 2 Scrolls titled "arus plignas"
m) Wooden Torch (4409 turns)
n) Wooden Torch (5000 turns)
```

**Home Inventory (page 1)**

```
a) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
479 4291 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1207 8122 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1233 8322 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2416 17878 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 30 game messages

```
2382 17728 85 Your Flask of oil hits the giant white mouse.
2382 17728 6 The giant white mouse dies.
2383 17728 0 You have no more Flasks of oil (d).
2383 17728 0 The Flask of oil breaks.
2389 17758 2 You hit the giant white mouse.
2389 17758 6 You have slain the giant white mouse.
2389 17760 39 The giant white mouse bites you.
2396 17798 2 You hit the giant white mouse.
2396 17798 6 You have slain the giant white mouse.
2402 17818 0 Target Selected.
2407 17818 6 The giant white mouse dies.
2412 17848 2 You hit the giant white mouse.
2412 17848 4 The giant white mouse flees in terror!
2414 17859 39 The giant white mouse bites you.
2414 17868 39 The giant white mouse bites you.
2419 17888 2 You hit the giant white mouse.
2419 17888 6 You have slain the giant white mouse.
2422 17898 2 You hit the giant white mouse.
2422 17905 39 The giant white mouse bites you.
2426 17908 0 You do not have enough mana to cast this spell.
2428 17908 0 You faint from the effort!
2428 17908 58 You are paralysed!
2428 17908 0 You have damaged your health!
2429 17920 53 You can move again.
2437 17968 0 You do not have enough mana to cast this spell.
2439 17968 0 You faint from the effort!
2439 17968 58 You are paralysed!
2439 17969 39 The giant white mouse bites you.
2440 17969 8 You die.
2441 17969 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
2431 17938 0 # Fleeing and leaving the level (Looking for Up Stair).
2432 17948 0 # Creating a monster 'giant white mouse' at (26,161), HP: 2, Index: 23
2432 17948 0 # Removing Regional Fear (26,161) because of a LOS giant white mouse
2432 17948 0 # Fleeing level. Scumming Mode
2432 17948 0 # Scumming Mode.  Power Diving. 
2432 17948 0 # Scary guy on level.
2432 17948 0 # Fleeing and leaving the level. (scaryguy)
2432 17948 0 # Fleeing and leaving the level. (Looking for any stair)
2432 17948 0 # Fleeing and leaving the level (Looking for Up Stair).
2432 17948 0 # Flowing toward dark-1 at cost 2
2433 17958 0 # Tracking a monster 'giant white mouse' at (30,156) from (31,154)
2433 17958 0 # Fleeing level. Scumming Mode
2433 17958 0 # Scumming Mode.  Power Diving. 
2433 17958 0 # Scary guy on level.
2433 17958 0 # Fleeing and leaving the level. (scaryguy)
2433 17958 0 # Fleeing and leaving the level. (Looking for any stair)
2433 17958 0 # Fleeing and leaving the level (Looking for Up Stair).
2434 17968 0 # Tracking a monster 'giant white mouse' at (27,161) from (26,161)
2434 17968 0 # Tracking a monster 'giant white mouse' at (32,158) from (30,156)
2434 17968 0 # Creating a monster 'giant white mouse' at (26,161), HP: 2, Index: 23
2434 17968 0 # Removing Regional Fear (26,161) because of a LOS giant white mouse
2434 17968 0 # Fleeing level. Scumming Mode
2434 17968 0 # Scumming Mode.  Power Diving. 
2434 17968 0 # Scary guy on level.
2434 17968 0 # Loc:34,159 Dep:1 Lev:4 HP:1/20 SP:0/7 Danger:p=5
2434 17968 0 # Fleeing and leaving the level. (scaryguy)
2434 17968 0 # Casting Phase Door (0,3).
2434 17968 0 # Danger Level 1.3  Critical Attempt
2441 17969 0 # Aborting (death).
2441 17969 0 # Aborting (player died).
```

<a id="ranger-226104090-c98d373f"></a>
## Ranger Human 226104090: poison

- Dies in: `reborn-503-nolist`, the same game (play `c98d373f1354946b`).
- Same start elsewhere: `reborn-503-ctl` turn_cap, `reborn-503-fight` turn_cap, `reborn-503-both` turn_cap.
- Last state line: `84990 135,35 d2/2 hp-1/71 sp7/7 f2309 au319 xp149 lv7 t7:11 o7:5000,8:3765 pd79df305be6e09b3 e6061dcb6826589a2 r08ee9afe362a4c74`

- Cure potions quaffed: 18; Phase Door read: 9; Unknown potions quaffed: 0; Healing (outmatched) notes: 4; Potion of Speed quaffed: 0; Failed teleports: 15; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Human Ranger, Level 7/7
Exp: 349  Gold: 319  Turn: 84990
Killed on level: 2 (max. 2) by poison
```

**Character Equipment**

```
a) Main Gauche (1d5) (+0,+0)
b) Short Bow (x2) (+0,+0)
c) Ring of Feather Falling
f) Wooden Torch (3765 turns)
g) Robe [2,+0]
i) Cloak [1,+0]
m) Small Metal Shield [5,+0]
n) Hard Leather Cap [2,+0]
o) Set of Gauntlets [3,+0]
p) Pair of Leather Sandals [1,+4]
```

**Character Quiver**

```
a) 5 Arrows (1d4) (+0,+0)
```

**Character Inventory**

```
a) Book of Nature Magics [Lesser Charms]
b) 8 Rations of Food
c) Potion of Heroism
d) 3 Potions of Boldness
e) Purple Speckled Potion
f) Scroll of Treasure Detection
g) 3 Scrolls of Light
i) 3 Wooden Torches (5000 turns)
```

**Home Inventory (page 1)**

```
a) 3 Apples
b) a Handful of Dried Fruits
c) 2 Flasks of oil
d) a Potion of Cure Serious Wounds
e) 2 Potions of Boldness
f) a Wooden Torch (3798 turns)
g) a Wooden Torch (5000 turns)
```

### Where it splits from the control `reborn-503-ctl` (game turn 280)

```
16 120 0 # Entering a '3' shop
17 120 0 # Town plan executing action 3 at shop 3 slot 0
17 120 0 # Selling Book of Nature Magics [Lesser Charms]
20 120 0 You had a Book of Nature Magics [Lesser Charms] (a).
26 130 0 # Flowing toward Home at cost 26
41 280 0 # Creating a monster 'squint-eyed rogue' at (16,25), HP: 8, Index: 10
41 280 0 # Flowing toward Home at cost 11
42 290 0 # There was a monster 'squint-eyed rogue' at (16,25)
43 300 0 # There was a monster 'squint-eyed rogue' at (16,25)
44 310 0 # There was a monster 'squint-eyed rogue' at (16,25)
46 330 0 # There was a monster 'squint-eyed rogue' at (16,25)
51 380 0 # Entering a '7' shop
```

Control at the same point:

```
41 280 0 # Scary guy on level.
41 280 0 # Leaving (Scary guy on level)
41 280 0 # Fleeing (Scary guy on level)
41 280 0 # Fleeing and leaving the level. (scaryguy)
41 280 0 # Fleeing and leaving the level. (Looking for any stair)
41 280 0 # Flowing toward stairs at cost 13
```

### Last trip decisions

```
8746 56177 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
9699 59978 0 # Trip: descend via search (plan 2): below-plan(1 < 2)
10313 63031 0 # Trip: descend via search (plan 2): below-plan(1 < 2)
10356 63422 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
10714 65313 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
11245 68962 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
12204 73348 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
12861 76452 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
```

### Last 30 game messages

```
14497 84540 44 The white worm mass crawls on you.
14497 84540 56 You are poisoned!
14502 84547 0 Target Selected.
14506 84547 85 Your Arrow (1d4) (+0,+0) hits the white worm mass.
14506 84547 0 You have 6 Arrows (1d4) (+0,+0) (0).
14507 84547 0 The Arrow breaks.
14507 84547 0 The white worm mass cries out in pain.
14508 84554 44 The white worm mass crawls on you.
14509 84554 56 You are more poisoned!
14513 84580 44 The white worm mass crawls on you.
14513 84580 56 You are more poisoned!
14527 84710 53 You are no longer poisoned.
14531 84740 44 The white worm mass crawls on you.
14531 84740 56 You are poisoned!
14534 84760 44 The white worm mass crawls on you.
14534 84760 56 You are more poisoned!
14543 84840 44 The white worm mass crawls on you.
14543 84840 56 You are more poisoned!
14546 84860 44 The white worm mass crawls on you.
14546 84860 56 You are more poisoned!
14555 84940 44 The white worm mass crawls on you.
14555 84940 56 You are more poisoned!
14558 84960 44 The white worm mass crawls on you.
14558 84960 56 You are more poisoned!
14565 84985 0 Target Selected.
14569 84985 85 Your Arrow (1d4) (+0,+0) hits the white worm mass.
14569 84985 0 You have 5 Arrows (1d4) (+0,+0) (0).
14570 84985 0 The white worm mass grunts with pain.
14571 84990 8 You die.
14572 84990 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
14553 84925 0 # Retreating to 35,136 (distance 1) via 35,136 (32 > 1)
14554 84935 0 # There was a monster 'white worm mass' at (35,134)
14554 84935 0 # Forgetting a monster 'white worm mass' at (35,134)
14554 84935 0 # Flowing toward item at cost 3
14556 84945 0 # HIT_BY:The white worm mass (+)
14556 84945 0 # Creating a monster 'white worm mass' at (35,134), HP: 10, Index: 26
14556 84945 0 # Removing Regional Fear (35,134) because of a LOS white worm mass
14556 84945 0 # HIT_BY:The white worm mass (3)
14556 84945 0 # Loc:35,135 Dep:2 Lev:7 HP:6/71 SP:7/7 Danger:p=32
14556 84945 0 # Retreating to 35,136 (distance 1) via 35,136 (32 > 1)
14557 84955 0 # There was a monster 'white worm mass' at (35,134)
14557 84955 0 # Forgetting a monster 'white worm mass' at (35,134)
14557 84955 0 # Flowing toward item at cost 3
14559 84965 0 # HIT_BY:The white worm mass (+)
14559 84965 0 # Creating a monster 'white worm mass' at (35,134), HP: 10, Index: 26
14559 84965 0 # Removing Regional Fear (35,134) because of a LOS white worm mass
14559 84965 0 # HIT_BY:The white worm mass (3)
14559 84965 0 # Loc:35,135 Dep:2 Lev:7 HP:2/71 SP:7/7 Danger:p=32
14559 84965 0 # Backing up to 136,35 (32 > 1)
14560 84975 0 # There was a monster 'white worm mass' at (35,134)
14560 84975 0 # Forgetting a monster 'white worm mass' at (35,134)
14560 84975 0 # Flowing toward item at cost 3
14561 84985 0 # Creating a monster 'white worm mass' at (35,134), HP: 10, Index: 26
14561 84985 0 # Removing Regional Fear (35,134) because of a LOS white worm mass
14561 84985 0 # Loc:35,135 Dep:2 Lev:7 HP:0/71 SP:7/7 Danger:p=32
14561 84985 0 # Performing attack type 3 with raw utility 23 and weighted utility 46.
14561 84985 0 # Targeting white worm mass who has 10 Hit Points (35,134).
14561 84985 0 # Firing missile 'Arrows (1d4) (+0,+0)'
14572 84990 0 # Aborting (death).
14572 84990 0 # Aborting (player died).
```

<a id="druid-934061548-f83dbe73"></a>
## Druid Half-Elf 934061548: a kobold shaman

- Dies in: `reborn-503-nolist`, `reborn-503-both`, the same game (play `f83dbe738a300cd5`).
- Same start elsewhere: `reborn-503-ctl` turn_cap, `reborn-503-fight` turn_cap.
- Last state line: `53617 84,52 d2/3 hp-4/60 sp5/10 f4409 au80 xp133 lv6 t8:3 o1:1552,11:5000 p04c993d882d3ab95 eef9b3df494d67479 r08ee9afe362a4c74`

- Cure potions quaffed: 8; Phase Door read: 7; Unknown potions quaffed: 0; Healing (outmatched) notes: 5; Potion of Speed quaffed: 1; Failed teleports: 3; Trip returns: 5; Trip returns followed by "going down": 1.

### Worn and carried at death

```
Borg the Half-Elf Druid, Level 6/6
Exp: 433  Gold: 80  Turn: 53617
Killed on level: 2 (max. 3) by a kobold shaman
```

**Character Equipment**

```
a) Shovel (1d2) (+0,+0)
f) Wooden Torch (1552 turns)
g) Robe [2,+3]
i) Cloak [1,+0]
m) Small Metal Shield [5,+0]
n) Hard Leather Cap [2,+0]
o) Set of Leather Gloves [1,+0]
```

**Character Inventory**

```
a) Book of Nature Magics [Lesser Charms]
b) 2 Apples
c) Handful of Dried Fruits
d) 10 Rations of Food
e) Potion of Neutralize Poison
f) 6 Potions of Boldness
g) 5 Cloudy Potions
i) 3 Scrolls of Treasure Detection
m) 4 Scrolls of Detect Invisible
n) 5 Scrolls of Light
o) 2 Wooden Torches (5000 turns)
p) Wicker Shield [2,+0]
```

**Home Inventory (page 1)**

```
a) a Handful of Dried Fruits
b) 3 Scrolls of Blessing
c) a Wooden Torch (4705 turns)
d) a Wooden Torch (5000 turns)
```

### Where it splits from the control `reborn-503-ctl` (game turn 61)

```
6 11 0 You re-arrange your pack.
7 11 0 You combine some items in your pack.
7 11 125 You were holding a Wooden Torch (5000 turns) (d).
9 21 0 # Standing on dn-stairs
9 21 0 # Flowing toward Home at cost 24
13 61 0 # Creating a monster 'squint-eyed rogue' at (12,49), HP: 8, Index: 10
13 61 0 # Flowing toward Home at cost 20
15 81 0 # Creating a monster 'filthy street urchin' at (14,30), HP: 3, Index: 1
16 91 0 # Creating a monster 'filthy street urchin' at (14,31), HP: 3, Index: 1
24 171 0 # Creating a monster 'filthy street urchin' at (15,31), HP: 3, Index: 1
24 171 0 # Creating a monster 'filthy street urchin' at (16,31), HP: 3, Index: 1
24 171 0 # There was a monster 'filthy street urchin' at (14,30)
```

Control at the same point:

```
13 61 0 # Scary guy on level.
13 61 0 # Leaving (Scary guy on level)
13 61 0 # Fleeing (Scary guy on level)
13 61 0 # Fleeing and leaving the level. (scaryguy)
13 61 0 # Fleeing and leaving the level. (Looking for any stair)
13 61 0 # Flowing toward stairs at cost 4
```

### Last trip decisions

```
3534 31470 0 # Trip: return via search (plan 2): unknown(10 >= 5)
4545 40591 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
4777 43543 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
5024 45814 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
5269 48075 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
5425 49350 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
5663 51572 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
5718 52042 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
```

### Last 30 game messages

```
6107 53542 3 You miss the kobold shaman.
6107 53544 0 The kobold shaman misses you.
6107 53548 0 The small kobold misses you.
6111 53552 2 You hit the kobold shaman.
6111 53553 0 The kobold shaman magically starts closing wounds.
6112 53553 0 The kobold shaman looks REALLY healthy!
6113 53558 0 The small kobold misses you.
6113 53562 0 The kobold shaman conjures up weird things.
6114 53562 0 You retain your presence of mind.
6118 53562 2 You hit the kobold shaman.
6118 53568 34 The small kobold hits you.
6118 53571 0 The kobold shaman fires a magic missile.
6122 53572 2 You hit the kobold shaman.
6122 53578 0 The small kobold misses you.
6122 53580 0 The kobold shaman misses you.
6126 53582 2 You hit the kobold shaman.
6126 53588 34 The small kobold hits you.
6126 53590 0 The kobold shaman points at you and curses!
6127 53590 0 Your body tingles briefly.
6130 53592 2 You hit the kobold shaman.
6130 53598 34 The small kobold hits you.
6130 53599 0 The kobold shaman points at you and curses!
6134 53602 3 You miss the kobold shaman.
6134 53608 34 The small kobold hits you.
6134 53608 77 You have been given a graze.
6135 53608 34 The kobold shaman hits you.
6138 53612 2 You hit the kobold shaman.
6138 53617 34 The kobold shaman hits you.
6138 53617 8 You die.
6139 53617 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
6128 53592 0 # SPELL_044:The kobold shaman (+)
6128 53592 0 # HIT:the kobold shaman (2)
6128 53592 0 # HIT_BY:The small kobold (3)
6128 53592 0 # SPELL_044:The kobold shaman (3)
6128 53592 0 # Loc:52,84 Dep:2 Lev:6 HP:27/60 SP:5/10 Danger:p=629
6128 53592 0 # Performing attack type 1 with value 23.
6128 53592 0 # Facing kobold shaman at (52,83) who has 5 Hit Points.
6128 53592 0 # Attacking with weapon 'Shovel (1d2) (+0,+0)'
6132 53602 0 # HIT:the kobold shaman (+)
6132 53602 0 # HIT_BY:The small kobold (+)
6132 53602 0 # SPELL_044:The kobold shaman (+)
6132 53602 0 # HIT:the kobold shaman (2)
6132 53602 0 # HIT_BY:The small kobold (3)
6132 53602 0 # SPELL_044:The kobold shaman (3)
6132 53602 0 # Loc:52,84 Dep:2 Lev:6 HP:14/60 SP:5/10 Danger:p=635
6132 53602 0 # Performing attack type 1 with value 29.
6132 53602 0 # Facing kobold shaman at (52,83) who has 5 Hit Points.
6132 53602 0 # Attacking with weapon 'Shovel (1d2) (+0,+0)'
6136 53612 0 # MISS:the kobold shaman (+)
6136 53612 0 # HIT_BY:The small kobold (+)
6136 53612 0 # HIT_BY:The kobold shaman (+)
6136 53612 0 # MISS:the kobold shaman (2)
6136 53612 0 # HIT_BY:The small kobold (3)
6136 53612 0 # HIT_BY:The kobold shaman (3)
6136 53612 0 # Loc:52,84 Dep:2 Lev:6 HP:3/60 SP:5/10 Danger:p=635
6136 53612 0 # Performing attack type 1 with value 29.
6136 53612 0 # Facing kobold shaman at (52,83) who has 5 Hit Points.
6136 53612 0 # Attacking with weapon 'Shovel (1d2) (+0,+0)'
6139 53617 0 # Aborting (death).
6139 53617 0 # Aborting (player died).
```

<a id="rogue-1381972077-92023227"></a>
## Rogue Half-Elf 1381972077: a cutpurse

- Dies in: `reborn-503-nolist`, the same game (play `92023227eea4b958`).
- Same start elsewhere: `reborn-503-ctl` turn_cap, `reborn-503-fight` turn_cap, `reborn-503-both` death.
- Last state line: `67528 80,57 d2/2 hp-1/30 sp3/3 f3949 au1033 xp147 lv6 t- o4:5000,5:3617 p38f37927d67e224b ea9a0932519191874 r08ee9afe362a4c74`

- Cure potions quaffed: 17; Phase Door read: 12; Unknown potions quaffed: 0; Healing (outmatched) notes: 9; Potion of Speed quaffed: 0; Failed teleports: 9; Trip returns: 7; Trip returns followed by "going down": 1.

### Worn and carried at death

```
Borg the Half-Elf Rogue, Level 6/6
Exp: 347  Gold: 1033  Turn: 67528
Killed on level: 2 (max. 2) by a cutpurse
```

**Character Equipment**

```
a) Dagger (1d4) (+0,+0)
b) Sling (x2) (+0,+0)
c) Ring of Feather Falling
f) Wooden Torch (3617 turns)
g) Soft Leather Armour [8,+0]
m) Small Metal Shield [5,+0]
o) Set of Leather Gloves [1,+0]
```

**Character Inventory**

```
a) Apple
b) 2 Handfuls of Dried Fruits
c) 10 Rations of Food
d) Potion of Neutralize Poison
e) 5 Potions of Boldness
f) 6 Orange Speckled Potions
g) 3 Light Violet Potions
i) 3 Shimmering Potions
m) 3 Scrolls titled "propio"
n) Scroll titled "ditiosu cunuo"
o) 2 Wooden Torches (5000 turns)
p) Wicker Shield [2,+0]
q) Dagger (1d4) (+0,+0)
```

**Home Inventory (page 1)**

```
a) a Handful of Dried Fruits
b) a Potion of Cure Serious Wounds
c) a Potion of Heroism
d) a Wooden Torch (5000 turns)
e) a Robe [2,+3] {cursed}
```

### Where it splits from the control `reborn-503-ctl` (game turn 1526)

```
374 1506 0 # Flowing toward item at cost 4
376 1516 0 You feel that there is naught but cobwebs here.
377 1526 0 # FEELING_STUFF:10 (+)
377 1526 0 # Creating a monster 'giant white mouse' at (10,150), HP: 1, Index: 23
377 1526 0 # Removing Regional Fear (10,150) because of a LOS giant white mouse
377 1526 0 # FEELING_STUFF:10 (1)
377 1526 0 # Flowing toward item at cost 2
378 1536 0 # Walking onto and deleting a 'Blindness' at (11,142)
379 1546 0 You have a Vespertine Potion (f).
380 1547 0 # Flowing toward dark-3 at cost 4
384 1587 0 # Flowing toward dark-2 at cost 3
385 1597 0 # Flowing toward dark-3 at cost 4
```

Control at the same point:

```
377 1526 0 # Scary guy on level.
377 1526 0 # Leaving (Scary guy on level)
377 1526 0 # Fleeing (Scary guy on level)
377 1526 0 # Fleeing and leaving the level. (scaryguy)
377 1526 0 # Flowing toward up-stairs at cost 3
377 1526 0 # Desperate for Stairs (three)
```

### Last trip decisions

```
6517 51713 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
6685 53129 0 # Trip: return via search (plan 2): unknown(5 >= 5)
7020 56387 0 # Trip: return via stairs (plan 2): unknown(5 >= 5)
7327 59288 0 # Trip: return via search (plan 2): unknown(5 >= 5)
7368 59753 0 # Trip: return via search (plan 2): unknown(5 >= 5)
7700 62869 0 # Trip: return via stairs (plan 2): unknown(5 >= 5)
7785 63629 0 # Trip: return via search (plan 2): unknown(5 >= 5)
8226 67353 0 # Trip: return via stairs (plan 2): unknown(5 >= 5)
```

### Last 30 game messages

```
8282 67493 0 The soldier misses you.
8285 67493 2 You hit the soldier.
8285 67493 2 You hit the soldier.
8285 67498 34 The cutpurse hits you.
8285 67498 0 The cutpurse misses you.
8286 67498 0 The soldier misses you.
8286 67498 34 The soldier hits you.
8286 67503 34 The cutpurse hits you.
8287 67503 0 The cutpurse misses you.
8290 67503 0 You feel much better.
8290 67503 0 You have no more Potions of Cure Light Wounds (d).
8290 67504 34 The soldier hits you.
8291 67504 34 The soldier hits you.
8291 67508 34 The cutpurse hits you.
8291 67508 0 The cutpurse misses you.
8292 67509 0 The soldier misses you.
8292 67509 34 The soldier hits you.
8293 67513 34 The cutpurse hits you.
8293 67513 0 The cutpurse misses you.
8295 67520 34 The soldier hits you.
8295 67520 34 The soldier hits you.
8295 67523 0 The cutpurse misses you.
8295 67523 0 The cutpurse misses you.
8299 67523 2 You hit the soldier.
8299 67523 2 You hit the soldier.
8299 67525 34 The soldier hits you.
8299 67525 34 The soldier hits you.
8300 67528 34 The cutpurse hits you.
8300 67528 8 You die.
8301 67528 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
8294 67513 0 # MISS_BY:The soldier (+)
8294 67513 0 # HIT_BY:The soldier (+)
8294 67513 0 # HIT_BY:The cutpurse (+)
8294 67513 0 # MISS_BY:The cutpurse (+)
8294 67513 0 # HIT_BY:The soldier (3)
8294 67513 0 # HIT_BY:The soldier (3)
8294 67513 0 # HIT_BY:The cutpurse (3)
8294 67513 0 # MISS_BY:The cutpurse (3)
8294 67513 0 # MISS_BY:The soldier (3)
8294 67513 0 # HIT_BY:The soldier (3)
8294 67513 0 # HIT_BY:The cutpurse (3)
8294 67513 0 # MISS_BY:The cutpurse (3)
8294 67513 0 # Loc:57,81 Dep:2 Lev:6 HP:13/30 SP:3/3 Danger:p=88
8294 67513 0 # Backing up to 80,57 (88 > 12)
8297 67523 0 # HIT_BY:The soldier (+)
8297 67523 0 # HIT_BY:The soldier (+)
8297 67523 0 # MISS_BY:The cutpurse (+)
8297 67523 0 # MISS_BY:The cutpurse (+)
8297 67523 0 # Tracking a monster 'soldier' at (57,81) from (58,82)
8297 67523 0 # Tracking a monster 'cutpurse' at (58,81) from (57,82)
8297 67523 0 # HIT_BY:The soldier (3)
8297 67523 0 # HIT_BY:The soldier (3)
8297 67523 0 # MISS_BY:The cutpurse (3)
8297 67523 0 # MISS_BY:The cutpurse (3)
8297 67523 0 # Loc:57,80 Dep:2 Lev:6 HP:5/30 SP:3/3 Danger:p=88
8297 67523 0 # Performing attack type 1 with value 83.
8297 67523 0 # Facing soldier at (57,81) who has 14 Hit Points.
8297 67523 0 # Attacking with weapon 'Dagger (1d4) (+0,+0)'
8301 67528 0 # Aborting (death).
8301 67528 0 # Aborting (player died).
```

<a id="priest-1569794094-288f74e6"></a>
## Priest Human 1569794094: a yellow jelly

- Dies in: `reborn-503-nolist`, `reborn-503-both`, the same game (play `288f74e6dc083fe8`).
- Same start elsewhere: `reborn-503-ctl` turn_cap, `reborn-503-fight` turn_cap.
- Last state line: `5040 14,46 d1/1 hp-2/13 sp0/2 f8899 au3 xp5 lv1 t7:32 o2:4620,4:5000 p69d4c7f00486f34b e72a1afcf0f6030e0 r08ee9afe362a4c74`

- Cure potions quaffed: 4; Phase Door read: 1; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 0; Failed teleports: 1; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Human Priest, Level 1/1
Exp: 105  Gold: 3  Turn: 5040
Killed on level: 1 (max. 1) by a yellow jelly
```

**Character Equipment**

```
a) Mace (2d4) (+0,+0)
f) Wooden Torch (4620 turns)
```

**Character Inventory**

```
a) Holy Book of Prayers [Novice's Handbook]
b) 5 Rations of Food
c) Wooden Torch (5000 turns)
```

**Home Inventory (page 1)**

```
a) a Wooden Torch (5000 turns)
```

### Where it splits from the control `reborn-503-ctl` (game turn 421)

```
41 291 0 # KILL:the pitiful-looking beggar (+)
41 291 0 # Forgetting a monster 'pitiful-looking beggar' at (7,24)
41 291 0 # HIT:the pitiful-looking beggar (2)
41 291 0 # KILL:the pitiful-looking beggar (2)
54 421 0 # Creating a monster 'mean-looking mercenary' at (16,39), HP: 22, Index: 13
54 421 0 # Removing Regional Fear (16,39) because of a LOS mean-looking mercenary
54 421 0 # Flowing toward General Store at cost 15
55 431 0 # Creating a monster 'boil-covered wretch' at (17,38), HP: 4, Index: 6
55 431 0 # Removing Regional Fear (17,38) because of a LOS boil-covered wretch
55 431 0 # Flowing toward General Store at cost 14
56 441 0 # There was a monster 'mean-looking mercenary' at (16,39)
68 561 0 # Entering a '0' shop
```

Control at the same point:

```
54 421 0 # Scary guy on level.
54 421 0 # Leaving (Scary guy on level)
54 421 0 # Fleeing (Scary guy on level)
54 421 0 # Fleeing and leaving the level. (scaryguy)
54 421 0 # Fleeing and leaving the level. (Looking for any stair)
54 421 0 # Flowing toward stairs at cost 7
```

### Last trip decisions

```
219 2331 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
331 4981 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 30 game messages

```
283 3850 53 The prayer has expired.
311 4921 0 You have no more Scrolls of Phase Door (e).
316 4931 0 The air about you becomes charged...
316 4931 0 You have no more Scrolls of Word of Recall (e).
321 4941 0 You have a Potion of Cure Serious Wounds (d).
324 4951 0 You have no more Potions of Cure Serious Wounds (d).
327 4961 0 You have a Potion of Cure Light Wounds (c).
330 4971 0 You have no more Potions of Cure Light Wounds (c).
335 5001 2 You hit the yellow jelly.
335 5002 0 The yellow jelly misses you.
335 5007 0 The yellow jelly drains your mana away.
336 5007 0 The yellow jelly appears healthier.
340 5011 2 You hit the yellow jelly.
340 5011 35 The yellow jelly touches you.
340 5011 56 You are poisoned!
341 5016 35 The yellow jelly touches you.
341 5016 56 You are more poisoned!
341 5021 0 The yellow jelly drains your mana away.
342 5021 0 The yellow jelly appears healthier.
346 5021 2 You hit the yellow jelly.
346 5026 35 The yellow jelly touches you.
346 5026 56 You are more poisoned!
347 5031 35 The yellow jelly touches you.
347 5031 56 You are more poisoned!
351 5031 2 You hit the yellow jelly.
351 5035 35 The yellow jelly touches you.
351 5035 56 You are more poisoned!
352 5040 35 The yellow jelly touches you.
352 5040 8 You die.
353 5040 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
338 5011 0 # MISS_BY:The yellow jelly (3)
338 5011 0 # SPELL_041:The yellow jelly (3)
338 5011 0 # Loc:46,14 Dep:1 Lev:1 HP:13/13 SP:1/2 Danger:p=600
338 5011 0 # Performing attack type 1 with value 1004.
338 5011 0 # Facing yellow jelly at (45,13) who has 50 Hit Points.
338 5011 0 # Attacking with weapon 'Mace (2d4) (+0,+0)'
344 5021 0 # HIT:the yellow jelly (+)
344 5021 0 # HIT_BY:The yellow jelly (+)
344 5021 0 # HIT_BY:The yellow jelly (+)
344 5021 0 # SPELL_041:The yellow jelly (+)
344 5021 0 # HIT:the yellow jelly (2)
344 5021 0 # HIT_BY:The yellow jelly (3)
344 5021 0 # HIT_BY:The yellow jelly (3)
344 5021 0 # SPELL_041:The yellow jelly (3)
344 5021 0 # Loc:46,14 Dep:1 Lev:1 HP:8/13 SP:0/2 Danger:p=600
344 5021 0 # Performing attack type 1 with value 1004.
344 5021 0 # Facing yellow jelly at (45,13) who has 47 Hit Points.
344 5021 0 # Attacking with weapon 'Mace (2d4) (+0,+0)'
349 5031 0 # HIT:the yellow jelly (+)
349 5031 0 # HIT_BY:The yellow jelly (+)
349 5031 0 # HIT_BY:The yellow jelly (+)
349 5031 0 # HIT:the yellow jelly (2)
349 5031 0 # HIT_BY:The yellow jelly (3)
349 5031 0 # HIT_BY:The yellow jelly (3)
349 5031 0 # Loc:46,14 Dep:1 Lev:1 HP:4/13 SP:0/2 Danger:p=600
349 5031 0 # Performing attack type 1 with value 1004.
349 5031 0 # Facing yellow jelly at (45,13) who has 36 Hit Points.
349 5031 0 # Attacking with weapon 'Mace (2d4) (+0,+0)'
353 5040 0 # Aborting (death).
353 5040 0 # Aborting (player died).
```

<a id="necromancer-1574344917-4917547d"></a>
## Necromancer Half-Elf 1574344917: a kobold

- Dies in: `reborn-503-nolist`, `reborn-503-both`, the same game (play `4917547da83fcccd`).
- Same start elsewhere: `reborn-503-ctl` turn_cap, `reborn-503-fight` turn_cap.
- Last state line: `8398 102,46 d1/1 hp-4/12 sp0/2 f8769 au109 xp9 lv1 t- o- p77518f51f95616fb eb73d3a89e40731a7 r08ee9afe362a4c74`

- Cure potions quaffed: 6; Phase Door read: 3; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 0; Failed teleports: 2; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Half-Elf Necromancer, Level 1/1
Exp: 109  Gold: 109  Turn: 8398
Killed on level: 1 (max. 1) by a kobold
```

**Character Equipment**

```
a) Main Gauche (1d5) (+0,+0)
g) Robe [2,+0]
i) Cloak [1,+0]
```

**Character Inventory**

```
a) Necromantic Tome [Into the Shadows]
b) 5 Rations of Food
c) 21 Flasks of oil
d) Muddy Potion
e) Shovel (1d2) (+0,+0)
```

**Home Inventory (page 1)**

```
a) a Handful of Dried Fruits
b) a Potion of Berserk Strength
```

### Where it splits from the control `reborn-503-ctl` (game turn 2672)

```
535 2612 0 # Flowing toward dark-3 at cost 2
536 2622 0 # Flowing toward dark-2 at cost 2
538 2642 0 # Flowing toward dark-2 at cost 2
540 2662 0 # Flowing toward dark-3 at cost 2
541 2672 0 # Creating a monster 'giant white mouse' at (35,68), HP: 2, Index: 23
541 2672 0 # Removing Regional Fear (35,68) because of a LOS giant white mouse
541 2672 0 # Loc:33,67 Dep:1 Lev:1 HP:12/12 SP:2/2 Danger:p=6
541 2672 0 # Retreating to 32,67 (distance 1) via 32,67 (6 > 0)
542 2682 0 # There was a monster 'giant white mouse' at (35,68)
542 2682 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
542 2682 0 # Flowing toward dark-4 at cost 6
543 2692 0 # There was a monster 'giant white mouse' at (35,68)
```

Control at the same point:

```
541 2672 0 # Scary guy on level.
541 2672 0 # Leaving (Scary guy on level)
541 2672 0 # Fleeing (Scary guy on level)
541 2672 0 # Loc:33,67 Dep:1 Lev:1 HP:12/12 SP:2/2 Danger:p=6
541 2672 0 # Fleeing and leaving the level. (scaryguy)
541 2672 0 # Flowing toward up-stairs at cost 9
```

### Last trip decisions

```
398 1481 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
470 2022 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
542 2682 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
609 3292 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
667 3793 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1055 5102 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 30 game messages

```
1311 8291 0 You feel much better.
1311 8291 0 You have 5 Potions of Cure Light Wounds (d).
1311 8298 34 The kobold hits you.
1315 8301 0 You feel much better.
1315 8301 0 You have 4 Potions of Cure Light Wounds (d).
1315 8308 34 The kobold hits you.
1319 8311 0 You feel much better.
1319 8311 0 You have 3 Potions of Cure Light Wounds (d).
1319 8318 34 The kobold hits you.
1323 8321 2 You hit the kobold.
1323 8328 0 The kobold misses you.
1326 8331 2 You hit the kobold.
1326 8338 34 The kobold hits you.
1329 8340 0 You feel much better.
1329 8340 0 You have 2 Potions of Cure Light Wounds (d).
1329 8348 34 The kobold hits you.
1333 8350 0 You feel much better.
1333 8350 0 You have a Potion of Cure Light Wounds (d).
1333 8358 34 The kobold hits you.
1337 8360 0 You feel much better.
1337 8360 0 You have no more Potions of Cure Light Wounds (d).
1337 8368 34 The kobold hits you.
1341 8370 2 You hit the kobold.
1341 8378 34 The kobold hits you.
1344 8380 2 You hit the kobold.
1344 8388 34 The kobold hits you.
1347 8389 2 You hit the kobold.
1347 8398 34 The kobold hits you.
1347 8398 8 You die.
1348 8398 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
1331 8350 0 # Healing Level 1.
1335 8360 0 # HIT_BY:The kobold (+)
1335 8360 0 # HIT_BY:The kobold (3)
1335 8360 0 # Loc:46,102 Dep:1 Lev:1 HP:4/12 SP:0/2 Danger:p=16
1335 8360 0 # Quaffing Potion of Cure Light Wounds.
1335 8360 0 # Buying time waiting for Recall.(3)
1339 8370 0 # HIT_BY:The kobold (+)
1339 8370 0 # HIT_BY:The kobold (3)
1339 8370 0 # Loc:46,102 Dep:1 Lev:1 HP:8/12 SP:0/2 Danger:p=16
1339 8370 0 # Performing attack type 1 with value 25.
1339 8370 0 # Facing kobold at (45,102) who has 9 Hit Points.
1339 8370 0 # Attacking with weapon 'Main Gauche (1d5) (+0,+0)'
1342 8380 0 # HIT:the kobold (+)
1342 8380 0 # HIT_BY:The kobold (+)
1342 8380 0 # HIT:the kobold (2)
1342 8380 0 # HIT_BY:The kobold (3)
1342 8380 0 # Loc:46,102 Dep:1 Lev:1 HP:6/12 SP:0/2 Danger:p=16
1342 8380 0 # Performing attack type 1 with value 25.
1342 8380 0 # Facing kobold at (45,102) who has 9 Hit Points.
1342 8380 0 # Attacking with weapon 'Main Gauche (1d5) (+0,+0)'
1345 8389 0 # HIT:the kobold (+)
1345 8389 0 # HIT_BY:The kobold (+)
1345 8389 0 # HIT:the kobold (2)
1345 8389 0 # HIT_BY:The kobold (3)
1345 8389 0 # Loc:46,102 Dep:1 Lev:1 HP:2/12 SP:0/2 Danger:p=16
1345 8389 0 # Performing attack type 1 with value 25.
1345 8389 0 # Facing kobold at (45,102) who has 6 Hit Points.
1345 8389 0 # Attacking with weapon 'Main Gauche (1d5) (+0,+0)'
1348 8398 0 # Aborting (death).
1348 8398 0 # Aborting (player died).
```

<a id="rogue-1381972077-44890862"></a>
## Rogue Half-Elf 1381972077: a crow

- Dies in: `reborn-503-both`, the same game (play `448908627645e626`).
- Same start elsewhere: `reborn-503-ctl` turn_cap, `reborn-503-fight` turn_cap, `reborn-503-nolist` death.
- Last state line: `42447 108,9 d2/2 hp-1/30 sp2/3 f6459 au243 xp142 lv6 t9:5 o2:1125,5:5000 p17b82d0cd8e51051 ecc80b57486e56c72 r08ee9afe362a4c74`

- Cure potions quaffed: 17; Phase Door read: 8; Unknown potions quaffed: 0; Healing (outmatched) notes: 13; Potion of Speed quaffed: 0; Failed teleports: 1; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Half-Elf Rogue, Level 6/6
Exp: 342  Gold: 243  Turn: 42447
Killed on level: 2 (max. 2) by a crow
```

**Character Equipment**

```
a) Dagger (1d4) (+0,+0)
c) Ring of Feather Falling
f) Wooden Torch (1125 turns)
g) Soft Leather Armour [8,+0]
i) Cloak [1,+1]
m) Small Metal Shield [5,+0]
o) Set of Leather Gloves [1,+0]
```

**Character Inventory**

```
a) 10 Rations of Food
b) 5 Potions of Boldness
c) 6 Orange Speckled Potions
d) Light Violet Potion
e) 3 Scrolls titled "propio"
f) Scroll titled "ditiosu cunuo"
g) 3 Wooden Torches (5000 turns)
i) Wicker Shield [2,+0]
```

**Home Inventory (page 1)**

```
a) a Handful of Dried Fruits
b) a Potion of Cure Serious Wounds
c) a Potion of Heroism
d) a Wooden Torch (5000 turns)
e) a Robe [2,+3] {cursed}
```

### Where it splits from the control `reborn-503-ctl` (game turn 1526)

```
374 1506 0 # Flowing toward item at cost 4
376 1516 0 You feel that there is naught but cobwebs here.
377 1526 0 # FEELING_STUFF:10 (+)
377 1526 0 # Creating a monster 'giant white mouse' at (10,150), HP: 1, Index: 23
377 1526 0 # Removing Regional Fear (10,150) because of a LOS giant white mouse
377 1526 0 # FEELING_STUFF:10 (1)
377 1526 0 # Flowing toward item at cost 2
378 1536 0 # Walking onto and deleting a 'Blindness' at (11,142)
379 1546 0 You have a Vespertine Potion (f).
380 1547 0 # Flowing toward dark-3 at cost 4
384 1587 0 # Flowing toward dark-2 at cost 3
385 1597 0 # Flowing toward dark-3 at cost 4
```

Control at the same point:

```
377 1526 0 # Scary guy on level.
377 1526 0 # Leaving (Scary guy on level)
377 1526 0 # Fleeing (Scary guy on level)
377 1526 0 # Fleeing and leaving the level. (scaryguy)
377 1526 0 # Flowing toward up-stairs at cost 3
377 1526 0 # Desperate for Stairs (three)
```

### Last trip decisions

```
3816 28893 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3901 29656 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
4184 32488 0 # Trip: descend via search (plan 2): below-plan(1 < 2)
4250 33118 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
4524 35598 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
4709 37130 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
4959 39290 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
5123 40780 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
```

### Last 30 game messages

```
5352 42415 39 The crow bites you.
5352 42415 0 The crow misses you.
5352 42420 39 The crow bites you.
5353 42420 39 The crow bites you.
5356 42420 0 You feel much better.
5356 42420 0 You have no more Potions of Cure Light Wounds (b).
5356 42424 39 The crow bites you.
5357 42424 39 The crow bites you.
5357 42425 34 The soldier hits you.
5357 42425 34 The soldier hits you.
5358 42429 39 The crow bites you.
5358 42429 0 The crow misses you.
5361 42430 3 You fail to harm the soldier.
5361 42430 3 You fail to harm the soldier.
5361 42433 39 The crow bites you.
5362 42433 0 The crow misses you.
5362 42436 34 The soldier hits you.
5362 42436 34 The soldier hits you.
5363 42438 0 The crow misses you.
5363 42438 0 The crow misses you.
5363 42439 140 The acolyte conjures up scary horrors.
5364 42439 57 You are terrified!
5367 42440 53 You feel bolder now.
5367 42440 0 You have 4 Potions of Boldness (b).
5367 42442 0 The crow misses you.
5368 42442 39 The crow bites you.
5368 42447 0 The crow misses you.
5368 42447 39 The crow bites you.
5369 42447 8 You die.
5370 42447 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
5359 42430 0 # Creating an object 'copper' at (109,9)
5359 42430 0 # HIT_BY:The crow (3)
5359 42430 0 # HIT_BY:The crow (3)
5359 42430 0 # HIT_BY:The soldier (3)
5359 42430 0 # HIT_BY:The soldier (3)
5359 42430 0 # HIT_BY:The crow (3)
5359 42430 0 # MISS_BY:The crow (3)
5359 42430 0 # Possibility of being surrounded (monsters/safegrids)(3/0)
5359 42430 0 # Loc:9,108 Dep:2 Lev:6 HP:15/30 SP:2/3 Danger:p=180
5359 42430 0 # Performing attack type 1 with value 83.
5359 42430 0 # Facing soldier at (9,109) who has 11 Hit Points.
5359 42430 0 # Attacking with weapon 'Dagger (1d4) (+0,+0)'
5365 42440 0 # HIT_BY:The crow (+)
5365 42440 0 # MISS_BY:The crow (+)
5365 42440 0 # HIT_BY:The soldier (+)
5365 42440 0 # HIT_BY:The soldier (+)
5365 42440 0 # MISS_BY:The crow (+)
5365 42440 0 # MISS_BY:The crow (+)
5365 42440 0 # Creating an object 'copper' at (109,9)
5365 42440 0 # HIT_BY:The crow (3)
5365 42440 0 # MISS_BY:The crow (3)
5365 42440 0 # HIT_BY:The soldier (3)
5365 42440 0 # HIT_BY:The soldier (3)
5365 42440 0 # MISS_BY:The crow (3)
5365 42440 0 # MISS_BY:The crow (3)
5365 42440 0 # Possibility of being surrounded (monsters/safegrids)(3/0)
5365 42440 0 # Loc:9,108 Dep:2 Lev:6 HP:4/30 SP:2/3 Danger:p=180
5365 42440 0 # Quaffing Potions of Boldness.
5370 42447 0 # Aborting (death).
5370 42447 0 # Aborting (player died).
```
