# Deaths in reborn-casteroil-a87-pilot (borg-zoo#436)

Run [44607268031](https://github.com/diegoami/borg-zoo/actions/runs/44607268031), specimen `4.2.6-reborn-rust-main-a87b4c96`. A reading aid written by `python3 -m zoo.death_report`, not a cemetery entry or a causal diagnosis.

6 deaths in 80 games, 6 distinct dying games. Replayed locally from the run's own build artifact, arms `reborn-casteroil-a87-ctl`, `reborn-casteroil-a87-w_attack-200`: every replayed play hash matches CI.

| Game | Dies in | Killed by | Char level | Dungeon level | Game turn | Keys |
|---|---|---|---|---|---|---|
| [Druid Dunadan 1678303796](#druid-1678303796-47af613c) | `reborn-casteroil-a87-ctl` | poison | 5 | 1 (max 2) | 37330 | 5470 |
| [Druid Elf 1678765969](#druid-1678765969-6a641ef4) | `reborn-casteroil-a87-ctl` | a wild cat | 1 | 1 (max 1) | 6951 | 953 |
| [Druid Human 2109297965](#druid-2109297965-95e63194) | `reborn-casteroil-a87-w_attack-200` | poison | 7 | 1 (max 2) | 84230 | 10504 |
| [Mage Half-Elf 247597266](#mage-247597266-de81c8f9) | `reborn-casteroil-a87-ctl` | Grip, Farmer Maggot's Dog | 2 | 1 (max 2) | 11116 | 1346 |
| [Necromancer Gnome 1236782037](#necromancer-1236782037-1943e161) | `reborn-casteroil-a87-w_attack-200` | a soldier | 3 | 1 (max 2) | 50875 | 5549 |
| [Priest Human 1217781050](#priest-1217781050-da3e6b72) | `reborn-casteroil-a87-w_attack-200` | a small kobold | 5 | 2 (max 2) | 88202 | 6682 |

## Observations

Three deaths per arm, and each start dies in one arm only. The other arm of the same start reaches the cap. The last 300 lines of each death:

- **Druid 1678303796 (ctl; poison, CL5, DL1, turn 37,330).**
  - **The death:** it was poisoned again and again by a **white worm mass** while "Goal_less, Fleeing" toward the up stairs, backing up one square at a time.
  - **Unused:** 3 Potions of Cure Serious Wounds, 20 Flasks of oil, a Sling with 37 Iron Shots, and two unknown potions.
  - **In the tail:** no throw, no Phase Door, no cure.
- **Druid 1678765969 (ctl; wild cat, CL1, DL1, turn 6,951).**
  - **The death:** it was clawed down by a wild cat after quaffing one Cure Light Wounds ("Healing Level 1").
  - **What it did:** one Flask of oil thrown in the tail.
  - **Unused:** 23 Flasks of oil, 3 Cure Light Wounds and 7 Phase Door.
- **Druid 2109297965 (w_attack-200; poison, CL7, DL1, turn 84,230).**
  - **The death:** like the first Druid, it was poisoned 11 times by **white worm masses** ("Spent too long (1299) on level", "Bored but unable to flow to up stairs"). Phase Door is mentioned 15 times in the tail.
  - **Unused:** 17 Flasks of oil, 3 Cure Serious Wounds, and a Sling (+5,+5) with 48 Iron Shots.
- **Mage 247597266 (ctl; Grip, CL2, DL1, turn 11,116).**
  - **The death:** it fought Grip, with a small kobold alongside, using the sling and Magic Missile, and died at the dog's bite.
  - **Unused:** a Potion of Speed. It carried no Flasks of oil.
- **Necromancer 1236782037 (w_attack-200; soldier, CL3, DL1, turn 50,875).**
  - **The death:** stunned, it attacked an apprentice in melee with a Main Gauche ("You fail to harm the apprentice") while a soldier beat it to death.
  - **Unused:** 4 Flasks of oil, a Potion of Neutralize Poison and the last Cure Light Wounds.
- **Priest 1217781050 (w_attack-200; small kobold, CL5, DL2, turn 88,202).**
  - **The death:** it had **no light source equipped** ("restock light radius < 1"). It was "unable to flow to up stairs" and "exploring for them (rising)", then died to "Something hits you".
  - **Inventory:** no torch, no oil, no cure potions.

**Notes across the six deaths:**
- **Oil was carried and not used:** four of the six deaths carried Flasks of oil (4-23) or Cure Serious Wounds that weren't used at the end.
- **Worm masses:** two deaths, one in each arm, are long poisonings by white worm masses at CL5-7. These are breeders, which #632 and #656 (compiled in, shipped off) address.
- **The arm's own deaths come late:** w_attack-200's three deaths come at turns 50k-88k, later than ctl's CL1-2 deaths.

## Handover: working on these deaths in the Borg's repository

For a session in diegoami/borg-reborn-rs that changes parameters or code against these deaths. That repository owns the Borg; the zoo only measures, and any change is measured here later as a new specimen.

- **Build:** `diegoami/borg-reborn-rs` at `a87b4c96cff9cf636f95cbb9818526f22a025625` (zoo specimen `4.2.6-reborn-rust-main-a87b4c96`): `BORG_IMPL=rust harness/build.sh`, or the run's CI artifact: `gh run download 44607268031 -R diegoami/borg-zoo -n build-4.2.6-reborn-rust-main-a87b4c96`.
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
| [Druid 1678303796](#druid-1678303796-47af613c) | 1678303796 | 8 (Dunadan) | 2 | `reborn-casteroil-a87-ctl` | `47af613cdceac6c2` |
| [Druid 1678765969](#druid-1678765969-6a641ef4) | 1678765969 | 2 (Elf) | 2 | `reborn-casteroil-a87-ctl` | `6a641ef4c017dc03` |
| [Druid 2109297965](#druid-2109297965-95e63194) | 2109297965 | 0 (Human) | 2 | `reborn-casteroil-a87-w_attack-200` | `95e631948304dba8` |
| [Mage 247597266](#mage-247597266-de81c8f9) | 247597266 | 1 (Half-Elf) | 1 | `reborn-casteroil-a87-ctl` | `de81c8f99296159d` |
| [Necromancer 1236782037](#necromancer-1236782037-1943e161) | 1236782037 | 4 (Gnome) | 4 | `reborn-casteroil-a87-w_attack-200` | `1943e16195f6b185` |
| [Priest 1217781050](#priest-1217781050-da3e6b72) | 1217781050 | 0 (Human) | 3 | `reborn-casteroil-a87-w_attack-200` | `da3e6b720012ca56` |

In borg-zoo, `python3 -m zoo.death_report --experiment experiments/reborn-casteroil-a87-pilot.json --run 44607268031` replays and checks them all. After a change: a PR in the Borg's repository, then ask the borg-zoo session for a new specimen at the merged commit and a pilot (or verysmall) of the same arms.

<a id="druid-1678303796-47af613c"></a>
## Druid Dunadan 1678303796: poison

- Dies in: `reborn-casteroil-a87-ctl`, the same game (play `47af613cdceac6c2`).
- Same start elsewhere: `reborn-casteroil-a87-w_attack-200` turn_cap.
- Last state line: `37330 46,25 d1/2 hp-1/40 sp10/10 f6869 au0 xp104 lv5 t7:3 o1:5000,4:1659 p4d07c047efb302fa e5b90eb9a57a795e6 r08ee9afe362a4c74`

- Cure potions quaffed: 16; Phase Door read: 17; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 0; Failed teleports: 4; Trip returns: 1; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Dunadan Druid, Level 5/5
Exp: 304  Gold: 0  Turn: 37330
Killed on level: 1 (max. 2) by poison
```

**Character Equipment**

```
a) Whip (1d3) (+0,+0)
b) Sling (x2) (+0,+0)
f) Wooden Torch (1659 turns)
i) Cloak [1,+0]
m) Small Metal Shield [5,+0]
n) Hard Leather Cap [2,+0]
o) Set of Leather Gloves [1,+0]
p) Pair of Leather Boots [2,+0]
```

**Character Quiver**

```
a) 37 Iron Shots (1d4) (+0,+0)
```

**Character Inventory**

```
a) 2 Books of Nature Magics [Lesser Charms]
b) 10 Rations of Food
c) Grey Potion
d) Green Potion
e) 3 Scrolls of Treasure Detection
f) 2 Wooden Torches (5000 turns)
```

**Home Inventory (page 1)**

```
a) 20 Flasks of oil
b) 3 Potions of Cure Serious Wounds
c) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
2135 17848 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2247 18499 0 # Trip: descend via search (plan 2): below-plan(1 < 2)
2341 20061 0 # Trip: return via stairs (plan 2): unknown(3 >= 2)
2791 21763 0 # Trip: descend via search (plan 2): below-plan(1 < 2)
2871 22873 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
3022 25423 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
3180 26823 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
3262 27992 0 # Trip: descend via search (plan 2): below-plan(1 < 2)
```

### Last 30 game messages

```
5408 36940 56 You are poisoned!
5412 36950 53 You are no longer poisoned.
5412 36960 44 The white worm mass crawls on you.
5412 36960 56 You are poisoned!
5416 36970 53 You are no longer poisoned.
5416 36980 44 The white worm mass crawls on you.
5416 36980 56 You are poisoned!
5420 36990 53 You are no longer poisoned.
5431 37100 44 The white worm mass crawls on you.
5431 37100 56 You are poisoned!
5434 37110 53 You are no longer poisoned.
5434 37120 44 The white worm mass crawls on you.
5434 37120 56 You are poisoned!
5438 37130 53 You are no longer poisoned.
5441 37160 44 The white worm mass crawls on you.
5441 37160 56 You are poisoned!
5444 37170 53 You are no longer poisoned.
5447 37200 44 The white worm mass crawls on you.
5447 37200 56 You are poisoned!
5450 37210 53 You are no longer poisoned.
5450 37220 44 The white worm mass crawls on you.
5450 37220 56 You are poisoned!
5454 37230 53 You are no longer poisoned.
5461 37300 44 The white worm mass crawls on you.
5461 37300 56 You are poisoned!
5464 37310 53 You are no longer poisoned.
5464 37320 44 The white worm mass crawls on you.
5464 37320 56 You are poisoned!
5468 37330 8 You die.
5469 37330 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
5459 37280 0 # Creating a monster 'white worm mass' at (26,46), HP: 9, Index: 26
5459 37280 0 # Removing Regional Fear (26,46) because of a LOS white worm mass
5459 37280 0 # Loc:25,46 Dep:1 Lev:5 HP:6/40 SP:10/10 Danger:p=32
5459 37280 0 # Retreating to 24,46 (distance 1) via 24,46 (32 > 1)
5460 37290 0 # There was a monster 'white worm mass' at (26,46)
5460 37290 0 # Forgetting a monster 'white worm mass' at (26,46)
5460 37290 0 # Flowing toward up-stairs at cost 13
5460 37290 0 # Looking for stairs. Goal_less, Fleeing.
5462 37300 0 # HIT_BY:The white worm mass (+)
5462 37300 0 # Creating a monster 'white worm mass' at (26,46), HP: 11, Index: 26
5462 37300 0 # Removing Regional Fear (26,46) because of a LOS white worm mass
5462 37300 0 # HIT_BY:The white worm mass (3)
5462 37300 0 # Loc:25,46 Dep:1 Lev:5 HP:5/40 SP:10/10 Danger:p=32
5462 37300 0 # Retreating to 24,46 (distance 1) via 24,46 (32 > 1)
5463 37310 0 # There was a monster 'white worm mass' at (26,46)
5463 37310 0 # Forgetting a monster 'white worm mass' at (26,46)
5463 37310 0 # Flowing toward up-stairs at cost 13
5463 37310 0 # Looking for stairs. Goal_less, Fleeing.
5466 37320 0 # HIT_BY:The white worm mass (+)
5466 37320 0 # Creating a monster 'white worm mass' at (26,46), HP: 11, Index: 26
5466 37320 0 # Removing Regional Fear (26,46) because of a LOS white worm mass
5466 37320 0 # HIT_BY:The white worm mass (3)
5466 37320 0 # Loc:25,46 Dep:1 Lev:5 HP:1/40 SP:10/10 Danger:p=32
5466 37320 0 # Backing up to 46,24 (32 > 1)
5467 37330 0 # There was a monster 'white worm mass' at (26,46)
5467 37330 0 # Forgetting a monster 'white worm mass' at (26,46)
5467 37330 0 # Flowing toward up-stairs at cost 13
5467 37330 0 # Looking for stairs. Goal_less, Fleeing.
5469 37330 0 # Aborting (death).
5469 37330 0 # Aborting (player died).
```

<a id="druid-1678765969-6a641ef4"></a>
## Druid Elf 1678765969: a wild cat

- Dies in: `reborn-casteroil-a87-ctl`, the same game (play `6a641ef4c017dc03`).
- Same start elsewhere: `reborn-casteroil-a87-w_attack-200` turn_cap.
- Last state line: `6951 70,32 d1/1 hp-2/11 sp2/2 f8809 au9 xp10 lv1 t- o1:5000,4:4396 p8dcb8ac26cb623e0 e0e1ef622b1e04456 r08ee9afe362a4c74`

- Cure potions quaffed: 5; Phase Door read: 0; Unknown potions quaffed: 0; Healing (outmatched) notes: 1; Potion of Speed quaffed: 0; Failed teleports: 0; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Elf Druid, Level 1/1
Exp: 110  Gold: 9  Turn: 6951
Killed on level: 1 (max. 1) by a wild cat
```

**Character Equipment**

```
a) Whip (1d3) (+0,+0)
f) Wooden Torch (4396 turns)
i) Cloak [1,+0]
m) Wicker Shield [2,+0]
o) Set of Leather Gloves [1,+0]
```

**Character Inventory**

```
a) 2 Books of Nature Magics [Lesser Charms]
b) 8 Rations of Food
c) 23 Flasks of oil
d) 4 Potions of Cure Light Wounds
e) 7 Scrolls of Phase Door
f) Wooden Torch (5000 turns)
```

**Home Inventory (page 1)**

```
a) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
299 1684 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
356 2194 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
401 2574 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
471 3214 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
514 3584 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
575 4134 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
689 5114 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
827 6141 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 30 game messages

```
932 6911 0 You feel much better.
932 6911 0 You have 6 Potions of Cure Light Wounds (d).
932 6915 38 The wild cat claws you.
933 6915 38 The wild cat claws you.
933 6919 38 The wild cat claws you.
933 6919 38 The wild cat claws you.
937 6921 0 You feel much better.
937 6921 0 You have 5 Potions of Cure Light Wounds (d).
937 6924 38 The wild cat claws you.
938 6924 38 The wild cat claws you.
938 6928 38 The wild cat claws you.
938 6928 38 The wild cat claws you.
942 6931 0 You feel much better.
942 6931 0 You have 4 Potions of Cure Light Wounds (d).
942 6933 38 The wild cat claws you.
943 6933 38 The wild cat claws you.
943 6937 38 The wild cat claws you.
943 6937 77 You have been given a graze.
944 6937 38 The wild cat claws you.
944 6940 53 You are no longer bleeding.
948 6941 0 You feel much better.
948 6941 0 You have 3 Potions of Cure Light Wounds (d).
948 6942 38 The wild cat claws you.
949 6942 38 The wild cat claws you.
949 6946 38 The wild cat claws you.
949 6946 38 The wild cat claws you.
950 6951 38 The wild cat claws you.
950 6951 38 The wild cat claws you.
950 6951 8 You die.
952 6951 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
940 6931 0 # HIT_BY:The wild cat (3)
940 6931 0 # HIT_BY:The wild cat (3)
940 6931 0 # HIT_BY:The wild cat (3)
940 6931 0 # HIT_BY:The wild cat (3)
940 6931 0 # Scary guy on level.
940 6931 0 # Loc:32,70 Dep:1 Lev:1 HP:4/11 SP:2/2 Danger:p=18
940 6931 0 # Fleeing and leaving the level. (scaryguy)
940 6931 0 # Phase rule (from escape 1 emergency): enemy adjacent and the fight looks lost (danger 18, HP 4): the rule allows a Phase Door
940 6931 0 # Phase (escape 1 emergency): no, 100 scary landing grids of 100 (at most 75)
940 6931 0 # Phase (escape 2.2 after teleport): no, 100 scary landing grids of 100 (at most 50)
940 6931 0 # Phase (escape 3.1 danger): no, 100 scary landing grids of 100 (at most 25)
940 6931 0 # Phase (escape 3.3 danger fallback): no, 100 scary landing grids of 100 (at most 75)
940 6931 0 # Phase (escape 4.1 compromised): no, 100 scary landing grids of 100 (at most 20)
940 6931 0 # Phase (escape 5.1 low level): no, 100 scary landing grids of 100 (at most 20)
940 6931 0 # Quaffing Potions of Cure Light Wounds.
940 6931 0 # Healing (outmatched).
946 6941 0 # HIT_BY:The wild cat (+)
946 6941 0 # HIT_BY:The wild cat (+)
946 6941 0 # HIT_BY:The wild cat (+)
946 6941 0 # HIT_BY:The wild cat (+)
946 6941 0 # HIT_BY:The wild cat (3)
946 6941 0 # HIT_BY:The wild cat (3)
946 6941 0 # HIT_BY:The wild cat (3)
946 6941 0 # HIT_BY:The wild cat (3)
946 6941 0 # Scary guy on level.
946 6941 0 # Loc:32,70 Dep:1 Lev:1 HP:1/11 SP:2/2 Danger:p=18
946 6941 0 # Quaffing Potions of Cure Light Wounds.
946 6941 0 # Healing Level 1.
952 6951 0 # Aborting (death).
952 6951 0 # Aborting (player died).
```

<a id="druid-2109297965-95e63194"></a>
## Druid Human 2109297965: poison

- Dies in: `reborn-casteroil-a87-w_attack-200`, the same game (play `95e631948304dba8`).
- Same start elsewhere: `reborn-casteroil-a87-ctl` turn_cap.
- Last state line: `84230 173,22 d1/2 hp-1/67 sp12/12 f2879 au302 xp176 lv7 t7:4 o8:5000,9:2715,13:7500 p11222f5596fc26ab e405625ee3a273e31 r08ee9afe362a4c74`

- Cure potions quaffed: 23; Phase Door read: 8; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 0; Failed teleports: 8; Trip returns: 4; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Human Druid, Level 7/7
Exp: 376  Gold: 302  Turn: 84230
Killed on level: 1 (max. 2) by poison
```

**Character Equipment**

```
a) Whip (1d3) (+0,+0)
b) Sling (x2) (+5,+5)
c) Ring of Searching <+1>
d) Ring of Feather Falling
f) Wooden Torch (2715 turns)
g) Soft Leather Armour [8,+0]
i) Cloak [1,+0]
n) Metal Cap [3,+0]
o) Set of Gauntlets [3,+0]
```

**Character Quiver**

```
a) 40 Iron Shots (1d4) (+0,+0)
b) 8 Iron Shots (1d4) (+0,+0)
```

**Character Inventory**

```
a) 2 Books of Nature Magics [Lesser Charms]
b) 2 Apples
c) 5 Rations of Food
d) 2 Purple Potions
e) 6 Scrolls of Phase Door
f) 3 Wooden Torches (5000 turns)
g) Lantern (7500 turns)
```

**Home Inventory (page 1)**

```
a) an Apple
b) 17 Flasks of oil
c) 3 Potions of Cure Serious Wounds
d) a Potion of Boldness
e) 6 Scrolls of Detect Invisible
f) 2 Scrolls of Blessing
g) a Wooden Torch (5000 turns)
i) a Wooden Torch (4730 turns)
```

### Where it splits from the control `reborn-casteroil-a87-ctl` (game turn 731)

```
115 611 0 # Entering a '7' shop
116 611 0 # Town plan executing action 5 at shop 7 slot 3
116 611 0 # Selling Potion of Cure Serious Wounds
118 611 0 You drop a Potion of Cure Serious Wounds (d).
121 621 0 # Flowing toward General Store at cost 12
132 731 0 # Entering a '0' shop
133 731 0 # Town plan executing action 1 at shop 0 slot 5
139 731 86 Okay.
139 731 0 You bought 32 Flasks of oil for 96 gold.
139 731 0 You have 32 Flasks of oil (c).
143 741 0 # Buying 32 x Flasks of oil.
143 741 0 # Re-entering a shop
```

Control at the same point:

```
133 731 0 # Town plan executing action 1 at shop 0 slot 2
138 731 86 Okay.
138 731 0 You bought 2 Rations of Food for 6 gold.
138 731 0 You have 5 Rations of Food (b).
142 741 0 # Buying 2 x Rations of Food.
142 741 0 # Flowing toward Alchemy Shop at cost 27
```

### Last trip decisions

```
5552 50664 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
5804 53505 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
5870 54085 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
6318 59444 0 # Trip: return via search (plan 2): unknown(4 >= 2)
6390 60145 0 # Trip: return via stairs (plan 2): unknown(4 >= 2)
6753 62435 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
7053 65635 0 # Trip: descend via search (plan 2): below-plan(1 < 2)
7418 70917 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
```

### Last 30 game messages

```
10440 83824 2 You hit the white worm mass.
10440 83827 44 The white worm mass crawls on you.
10440 83827 56 You are more poisoned!
10444 83834 2 You hit the white worm mass.
10447 83844 2 You hit the white worm mass.
10447 83844 6 You have destroyed the white worm mass.
10451 83880 53 You are no longer poisoned.
10451 83881 44 The white worm mass crawls on you.
10451 83881 56 You are poisoned!
10455 83901 44 The white worm mass crawls on you.
10455 83901 56 You are more poisoned!
10460 83940 53 You are no longer poisoned.
10463 83961 44 The white worm mass crawls on you.
10463 83961 56 You are poisoned!
10466 83981 44 The white worm mass crawls on you.
10466 83981 56 You are more poisoned!
10469 84001 44 The white worm mass crawls on you.
10469 84001 56 You are more poisoned!
10475 84050 53 You are no longer poisoned.
10483 84121 44 The white worm mass crawls on you.
10483 84121 56 You are poisoned!
10486 84141 44 The white worm mass crawls on you.
10486 84141 56 You are more poisoned!
10489 84161 44 The white worm mass crawls on you.
10489 84161 56 You are more poisoned!
10492 84181 44 The white worm mass crawls on you.
10492 84181 56 You are more poisoned!
10497 84184 0 You have 6 Scrolls of Phase Door (e).
10502 84230 8 You die.
10503 84230 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
10500 84214 0 # Fleeing and leaving the level. (Looking for any stair)
10500 84214 0 # Fleeing and leaving the level (Looking for Up Stair).
10500 84214 0 # Spent too long (1298) on level, leaving.
10500 84214 0 # Looking for up stairs.  Going up.
10500 84214 0 # Bored but unable to flow to up stairs.
10500 84214 0 # Spent too long (1298) on level, leaving.
10500 84214 0 # Looking for up stairs.  Going up.
10500 84214 0 # Bored but unable to flow to up stairs.
10500 84214 0 # Boosting bravery (1) from 1 to 2!
10500 84214 0 # Fleeing and leaving the level. Brave Thinking.
10500 84214 0 # heading down (bored and spastic).
10500 84214 0 # Boosting bravery (2) from 1 to 268!
10500 84214 0 # Fleeing and leaving the level. Brave Thinking.
10500 84214 0 # Flowing toward up-stairs at cost 108
10500 84214 0 # Looking for stairs. Flee, brave.
10501 84224 0 # Fleeing and leaving the level. (Looking for any stair)
10501 84224 0 # Fleeing and leaving the level (Looking for Up Stair).
10501 84224 0 # Spent too long (1299) on level, leaving.
10501 84224 0 # Looking for up stairs.  Going up.
10501 84224 0 # Bored but unable to flow to up stairs.
10501 84224 0 # Spent too long (1299) on level, leaving.
10501 84224 0 # Looking for up stairs.  Going up.
10501 84224 0 # Bored but unable to flow to up stairs.
10501 84224 0 # Boosting bravery (2) from 0 to 268!
10501 84224 0 # Fleeing and leaving the level. Brave Thinking.
10501 84224 0 # Flowing toward up-stairs at cost 107
10501 84224 0 # Walking onto and deleting a '& Iron Shot~' at (22,173)
10501 84224 0 # Looking for stairs. Flee, brave.
10503 84230 0 # Aborting (death).
10503 84230 0 # Aborting (player died).
```

<a id="mage-247597266-de81c8f9"></a>
## Mage Half-Elf 247597266: Grip, Farmer Maggot's Dog

- Dies in: `reborn-casteroil-a87-ctl`, the same game (play `de81c8f99296159d`).
- Same start elsewhere: `reborn-casteroil-a87-w_attack-200` turn_cap.
- Last state line: `11116 96,22 d1/2 hp-2/13 sp1/4 f8679 au145 xp18 lv2 t0:26 o2:4021,4:5000 pa8b0a21347f0e77b e2196c7607ffe246a r08ee9afe362a4c74`

- Cure potions quaffed: 8; Phase Door read: 6; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 1; Failed teleports: 0; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Half-Elf Mage, Level 2/2
Exp: 218  Gold: 145  Turn: 11116
Killed on level: 1 (max. 2) by Grip, Farmer Maggot's Dog
```

**Character Equipment**

```
a) Rapier (1d6) (+0,+0)
b) Sling (x2) (+5,+4)
f) Wooden Torch (4021 turns)
p) Pair of Leather Sandals [1,+0]
```

**Character Quiver**

```
a) 16 Iron Shots (1d4) (+0,+0)
```

**Character Inventory**

```
a) Book of Magic Spells [First Spells]
b) 5 Rations of Food
c) Potion of Speed
d) 3 Wooden Torches (5000 turns)
```

**Home Inventory (page 1)**

```
a) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
291 1714 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
367 2414 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
674 5205 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1086 9286 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 30 game messages

```
1277 11079 0 You have a Potion of Cure Light Wounds (c).
1277 11081 34 The small kobold hits you.
1278 11081 39 Grip, Farmer Maggot's Dog, bites you.
1283 11084 0 Target Selected.
1287 11084 0 You have 20 Iron Shots (1d4) (+0,+0) (0).
1287 11086 39 Grip, Farmer Maggot's Dog, bites you.
1291 11089 0 You feel much better.
1291 11089 0 You have no more Potions of Cure Light Wounds (c).
1291 11091 39 Grip, Farmer Maggot's Dog, bites you.
1292 11092 34 The small kobold hits you.
1297 11094 0 Target Selected.
1301 11094 0 You have 19 Iron Shots (1d4) (+0,+0) (0).
1301 11096 39 Grip, Farmer Maggot's Dog, bites you.
1307 11099 0 Target Selected.
1311 11099 0 You have 18 Iron Shots (1d4) (+0,+0) (0).
1311 11101 39 Grip, Farmer Maggot's Dog, bites you.
1312 11103 0 The small kobold misses you.
1317 11104 0 Target Selected.
1321 11104 0 You have 17 Iron Shots (1d4) (+0,+0) (0).
1326 11109 0 Target Selected.
1330 11109 85 Your Iron Shot (1d4) (+0,+0) hits Grip, Farmer Maggot's Dog.
1330 11109 0 You have 16 Iron Shots (1d4) (+0,+0) (0).
1331 11109 0 Grip, Farmer Maggot's Dog, yelps in pain.
1332 11111 39 Grip, Farmer Maggot's Dog, bites you.
1333 11114 34 The small kobold hits you.
1338 11114 0 Target Selected.
1343 11114 0 Grip, Farmer Maggot's Dog, yelps in pain.
1343 11116 39 Grip, Farmer Maggot's Dog, bites you.
1344 11116 8 You die.
1345 11116 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
1313 11104 0 # MISS_BY:The small kobold (3)
1313 11104 0 # Possibility of being surrounded (monsters/safegrids)(2/0)
1313 11104 0 # Loc:22,96 Dep:1 Lev:2 HP:5/13 SP:2/4 Danger:p=9
1313 11104 0 # Performing attack type 3 with value 76.
1313 11104 0 # Targeting Grip, Farmer Maggot's Dog who has 25 Hit Points (22,97).
1313 11104 0 # Firing missile 'Iron Shots (1d4) (+0,+0)'
1322 11109 0 # Perhaps wall near targetted location (22,97)
1322 11109 0 # Guessing wall (22,96) near target (22,97)
1322 11109 0 # Creating an object '& Iron Shot~' at (97,22)
1322 11109 0 # Possibility of being surrounded (monsters/safegrids)(2/0)
1322 11109 0 # Loc:22,96 Dep:1 Lev:2 HP:5/13 SP:2/4 Danger:p=9
1322 11109 0 # Leaving (low hit-points)
1322 11109 0 # Fleeing (low hit-points)
1322 11109 0 # Performing attack type 3 with value 76.
1322 11109 0 # Targeting Grip, Farmer Maggot's Dog who has 25 Hit Points (22,97).
1322 11109 0 # Firing missile 'Iron Shots (1d4) (+0,+0)'
1334 11114 0 # PAIN:Grip, Farmer Maggot's Dog (+)
1334 11114 0 # HIT_BY:Grip, Farmer Maggot's Dog (+)
1334 11114 0 # HIT_BY:The small kobold (+)
1334 11114 0 # Creating an object '& Iron Shot~' at (97,22)
1334 11114 0 # PAIN:Grip, Farmer Maggot's Dog (2)
1334 11114 0 # HIT_BY:Grip, Farmer Maggot's Dog (3)
1334 11114 0 # HIT_BY:The small kobold (3)
1334 11114 0 # Possibility of being surrounded (monsters/safegrids)(2/0)
1334 11114 0 # Loc:22,96 Dep:1 Lev:2 HP:1/13 SP:2/4 Danger:p=9
1334 11114 0 # Performing attack type 4 with raw utility 46 and weighted utility 92.
1334 11114 0 # Targeting Grip, Farmer Maggot's Dog who has 13 Hit Points (22,97).
1334 11114 0 # Casting Magic Missile (0,0).
1345 11116 0 # Aborting (death).
1345 11116 0 # Aborting (player died).
```

<a id="necromancer-1236782037-1943e161"></a>
## Necromancer Gnome 1236782037: a soldier

- Dies in: `reborn-casteroil-a87-w_attack-200`, the same game (play `1943e16195f6b185`).
- Same start elsewhere: `reborn-casteroil-a87-ctl` turn_cap.
- Last state line: `50875 48,41 d1/2 hp-1/14 sp2/6 f5319 au179 xp53 lv3 t- o11:5000 pa8f2d30316ffbc6f e8674a8621d9c2dfe r08ee9afe362a4c74`

- Cure potions quaffed: 14; Phase Door read: 10; Unknown potions quaffed: 0; Healing (outmatched) notes: 12; Potion of Speed quaffed: 0; Failed teleports: 6; Trip returns: 4; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Gnome Necromancer, Level 3/3
Exp: 253  Gold: 179  Turn: 50875
Killed on level: 1 (max. 2) by a soldier
```

**Character Equipment**

```
a) Main Gauche (1d5) (+0,+0)
c) Ring of Feather Falling
g) Robe [2,+0]
i) Cloak [1,+0]
m) Wicker Shield [2,+0]
n) Hard Leather Cap [2,+0]
o) Set of Leather Gloves [1,+2]
```

**Character Inventory**

```
a) 2 Necromantic Tomes [Into the Shadows]
b) Book of Nature Magics [Lesser Charms]
c) Apple
d) 2 Handfuls of Dried Fruits
e) 6 Slime Molds
f) 2 Rations of Food
g) 4 Flasks of oil
i) Potion of Cure Light Wounds
m) Potion of Neutralize Poison
n) 2 Purple Potions
o) 4 Scrolls of Treasure Detection
p) 3 Scrolls titled "illa to detrus"
q) 2 Wooden Torches (5000 turns)
```

**Home Inventory (page 1)**

```
a) 2 Apples
b) a Handful of Dried Fruits
c) a Potion of Heroism
d) 2 Scrolls of Blessing
```

### Where it splits from the control `reborn-casteroil-a87-ctl` (game turn 651)

```
71 641 0 # Creating a monster 'village idiot' at (15,12), HP: 10, Index: 7
71 641 0 # Removing Regional Fear (15,12) because of a LOS village idiot
71 641 0 # Flowing toward Alchemy Shop at cost 2
72 651 0 # Entering a '4' shop
73 651 0 "Never go exploring without an escape option."
73 651 0 # Town plan executing action 1 at shop 4 slot 0
78 651 0 You bought 7 Cerulean Potions for 140 gold.
78 651 0 You have 7 Potions of Cure Light Wounds (c).
82 661 0 # Buying 7 x Potions of Cure Light Wounds {unseen}.
82 661 0 # Flowing toward General Store at cost 18
85 691 0 # There was a monster 'village idiot' at (15,12)
99 831 0 # Entering a '0' shop
```

Control at the same point:

```
78 651 0 You bought 9 Cerulean Potions for 180 gold.
78 651 0 You have 9 Potions of Cure Light Wounds (c).
82 661 0 # Buying 9 x Potions of Cure Light Wounds {unseen}.
82 661 0 # Flowing toward General Store at cost 18
85 691 0 # There was a monster 'village idiot' at (15,12)
99 831 0 # Entering a '0' shop
```

### Last trip decisions

```
2369 22539 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2522 23729 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2791 26320 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3368 30242 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3466 31153 0 # Trip: return via search (plan 1): unknown(2 >= 2)
4155 37656 0 # Trip: return via search (plan 1): unknown(2 >= 2)
4684 42858 0 # Trip: return via search (plan 1): unknown(2 >= 2)
5177 47578 0 # Trip: return via search (plan 1): unknown(2 >= 2)
```

### Last 30 game messages

```
5526 50825 0 You feel much better.
5526 50825 0 You have 4 Potions of Cure Light Wounds (i).
5526 50829 34 The soldier hits you.
5527 50829 34 The soldier hits you.
5527 50831 34 The apprentice hits you.
5530 50835 0 You feel much better.
5530 50835 0 You have 3 Potions of Cure Light Wounds (i).
5530 50838 34 The soldier hits you.
5531 50838 34 The soldier hits you.
5531 50838 76 You have been stunned.
5531 50842 34 The apprentice hits you.
5535 50845 0 You feel much better.
5535 50845 0 You have 2 Potions of Cure Light Wounds (i).
5535 50847 34 The soldier hits you.
5536 50847 34 The soldier hits you.
5536 50850 53 You are no longer stunned.
5536 50853 34 The apprentice hits you.
5540 50855 0 You feel much better.
5540 50855 0 You have a Potion of Cure Light Wounds (i).
5540 50857 0 The soldier misses you.
5541 50857 34 The soldier hits you.
5541 50864 34 The apprentice hits you.
5541 50864 76 You have been stunned.
5545 50865 3 You fail to harm the apprentice.
5545 50866 0 The soldier misses you.
5545 50866 34 The soldier hits you.
5546 50870 53 You are no longer stunned.
5546 50875 34 The soldier hits you.
5546 50875 8 You die.
5548 50875 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
5533 50845 0 # Quaffing Potions of Cure Light Wounds.
5533 50845 0 # Healing (outmatched).
5538 50855 0 # HIT_BY:The soldier (+)
5538 50855 0 # HIT_BY:The soldier (+)
5538 50855 0 # PAIN:You (+)
5538 50855 0 # HIT_BY:The apprentice (+)
5538 50855 0 # Assuming player ghost (You) (a)
5538 50855 0 # Assuming player ghost (You) (a)
5538 50855 0 # Tracking a monster 'apprentice' at (39,48) from (39,47)
5538 50855 0 # Assuming player ghost (You) (a)
5538 50855 0 # HIT_BY:The soldier (3)
5538 50855 0 # HIT_BY:The soldier (3)
5538 50855 0 # PAIN:You (0)
5538 50855 0 # HIT_BY:The apprentice (3)
5538 50855 0 # Loc:41,48 Dep:1 Lev:3 HP:6/14 SP:2/6 Danger:p=326
5538 50855 0 # Quaffing Potions of Cure Light Wounds.
5538 50855 0 # Healing (outmatched).
5543 50865 0 # MISS_BY:The soldier (+)
5543 50865 0 # HIT_BY:The soldier (+)
5543 50865 0 # HIT_BY:The apprentice (+)
5543 50865 0 # Tracking a monster 'apprentice' at (39,47) from (39,48)
5543 50865 0 # MISS_BY:The soldier (3)
5543 50865 0 # HIT_BY:The soldier (3)
5543 50865 0 # HIT_BY:The apprentice (3)
5543 50865 0 # Loc:41,48 Dep:1 Lev:3 HP:8/14 SP:2/6 Danger:p=326
5543 50865 0 # Performing attack type 1 with value 159.
5543 50865 0 # Facing apprentice at (40,47) who has 17 Hit Points.
5543 50865 0 # Attacking with weapon 'Main Gauche (1d5) (+0,+0)'
5548 50875 0 # Aborting (death).
5548 50875 0 # Aborting (player died).
```

<a id="priest-1217781050-da3e6b72"></a>
## Priest Human 1217781050: a small kobold

- Dies in: `reborn-casteroil-a87-w_attack-200`, the same game (play `da3e6b720012ca56`).
- Same start elsewhere: `reborn-casteroil-a87-ctl` turn_cap.
- Last state line: `88202 162,19 d2/2 hp-2/43 sp8/9 f2479 au70 xp92 lv5 t- o- paef1c4b967f60b7b ee200e93d4c075eda r08ee9afe362a4c74`

- Cure potions quaffed: 8; Phase Door read: 1; Unknown potions quaffed: 0; Healing (outmatched) notes: 4; Potion of Speed quaffed: 0; Failed teleports: 7; Trip returns: 33; Trip returns followed by "going down": 2.

### Worn and carried at death

```
Borg the Human Priest, Level 5/5
Exp: 292  Gold: 70  Turn: 88202
Killed on level: 2 (max. 2) by a small kobold
```

**Character Equipment**

```
a) Mace (2d4) (+0,+0)
g) Robe [2,+0]
o) Set of Leather Gloves [1,+0]
```

**Character Inventory**

```
a) 2 Holy Books of Prayers [Novice's Handbook]
b) 6 Rations of Food
c) 2 Azure Potions
d) Icky Green Potion
e) 3 Scrolls titled "todo pratepro"
```

**Home Inventory (page 1)**

```
a) a Wooden Torch (5000 turns)
```

### Where it splits from the control `reborn-casteroil-a87-ctl` (game turn 181)

```
30 171 0 # Entering a '0' shop
31 171 0 # Town plan executing action 1 at shop 0 slot 2
36 171 86 Fine.
36 171 0 You bought 4 Rations of Food for 12 gold.
36 171 0 You have 5 Rations of Food (b).
40 181 0 # Buying 4 x Rations of Food.
40 181 0 # Re-entering a shop
41 181 0 "Carry around extra copies of town spellbooks in case one gets burned."
41 181 0 # Town plan executing action 1 at shop 0 slot 4
47 181 86 Done!
47 181 0 You bought 14 Flasks of oil for 42 gold.
47 181 0 You have 14 Flasks of oil (c).
```

Control at the same point:

```
40 181 0 # Flowing toward Alchemy Shop at cost 7
46 241 0 # Entering a '4' shop
47 241 0 # Town plan executing action 1 at shop 4 slot 0
52 241 0 You bought 2 Crimson Potions for 40 gold.
52 241 0 You have 2 Potions of Cure Light Wounds (c).
56 251 0 # Buying 2 x Potions of Cure Light Wounds {unseen}.
```

### Last trip decisions

```
5640 71868 0 # Trip: return via stairs (plan 1): restock unknown(2 >= 2)
5653 71998 0 # Trip: return via search (plan 1): restock unknown(2 >= 2)
5654 72008 0 # Trip: return via stairs (plan 1): restock unknown(2 >= 2)
5707 73658 0 # Trip: return via search (plan 1): unknown(2 >= 2)
5862 76108 0 # Trip: return via search (plan 1): restock unknown(2 >= 2)
6049 78619 0 # Trip: return via search (plan 1): restock unknown(3 >= 2)
6491 86879 0 # Trip: ascend via search (plan 1): unprepared(depth 2 > prepared 1) unknown(3 >= 2)
6632 87869 0 # Trip: return via search (plan 1): restock unknown(3 >= 2)
```

### Last 30 game messages

```
6613 87769 0 You have no more Potions of Cure Serious Wounds (d).
6613 87777 34 Something hits you.
6617 87797 34 Something hits you.
6621 87827 34 Something hits you.
6623 87837 34 Something hits you.
6625 87847 34 Something hits you.
6628 87849 0 You feel much better.
6628 87849 0 You have a Potion of Cure Light Wounds (c).
6628 87857 34 Something hits you.
6629 87857 77 You have been given a graze.
6631 87867 34 Something hits you.
6633 87877 34 Something hits you.
6636 87879 0 You feel much better.
6636 87879 53 You are no longer bleeding.
6636 87879 0 You have no more Potions of Cure Light Wounds (c).
6637 87887 34 Something hits you.
6639 87897 34 Something hits you.
6641 87907 34 Something hits you.
6643 87909 16 You feel a wall blocking your way.
6643 87917 34 Something hits you.
6643 87917 77 You have been given a graze.
6649 87949 2 You hit something.
6651 87960 53 You are no longer bleeding.
6667 88109 16 You feel a wall blocking your way.
6669 88119 16 You feel a wall blocking your way.
6676 88184 34 Something hits you.
6678 88193 34 Something hits you.
6680 88202 34 Something hits you.
6680 88202 8 You die.
6681 88202 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
6679 88199 0 # Boosting bravery (1) from 3 to 6!
6679 88199 0 # Fleeing and leaving the level. Brave Thinking.
6679 88199 0 # heading up, not prep for current level: restock light radius < 1)
6679 88199 0 # heading up (bored and unable to dive: restock light radius < 1)
6679 88199 0 # Climbing (too deep: restock light radius < 1)
6679 88199 0 # returning to town to restock(too deep: restock light radius < 1)
6679 88199 0 # Looking for up stairs.  Going up.
6679 88199 0 # Bored but unable to flow to up stairs.
6679 88199 0 # no up stairs found, going down
6679 88199 0 # Boosting bravery (2) from 3 to 172!
6679 88199 0 # Fleeing and leaving the level. Brave Thinking.
6679 88199 0 # heading up, not prep for current level: restock light radius < 1)
6679 88199 0 # heading up (bored and unable to dive: restock light radius < 1)
6679 88199 0 # Climbing (too deep: restock light radius < 1)
6679 88199 0 # returning to town to restock(too deep: restock light radius < 1)
6679 88199 0 # Looking for up stairs.  Going up.
6679 88199 0 # Bored but unable to flow to up stairs.
6679 88199 0 # no up stairs found, exploring for them (rising)
6679 88199 0 # Boosting bravery (3) from 3 to 30000!
6679 88199 0 # Fleeing and leaving the level. Brave Thinking.
6679 88199 0 # heading up, not prep for current level: restock light radius < 1)
6679 88199 0 # heading up (bored and unable to dive: restock light radius < 1)
6679 88199 0 # Climbing (too deep: restock light radius < 1)
6679 88199 0 # returning to town to restock(too deep: restock light radius < 1)
6679 88199 0 # Looking for up stairs.  Going up.
6679 88199 0 # Bored but unable to flow to up stairs.
6679 88199 0 # no up stairs found, exploring for them (rising)
6679 88199 0 # Twitchy!
6681 88202 0 # Aborting (death).
6681 88202 0 # Aborting (player died).
```
