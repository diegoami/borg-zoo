# Deaths in reborn-main-defaults-pilot (borg-zoo#181)

Run [44071581589](https://github.com/diegoami/borg-zoo/actions/runs/44071581589), specimen `4.2.6-reborn-rust-main-fdaf18e5`. A reading aid written by `python3 -m zoo.deaths`, not a cemetery entry or a causal diagnosis.

3 deaths in 18 games, 3 distinct dying games. Replayed locally from the run's own build artifact, arms `reborn-shipped-defaults`: every replayed play hash matches CI.

| Game | Dies in | Killed by | Char level | Dungeon level | Game turn | Keys |
|---|---|---|---|---|---|---|
| [Druid Human 102023799](#druid-102023799-466c0175) | `reborn-shipped-defaults` | a rock lizard | 2 | 1 (max 1) | 33735 | 4174 |
| [Necromancer Human 300036923](#necromancer-300036923-00a4c65b) | `reborn-shipped-defaults` | a wild cat | 1 | 1 (max 1) | 12328 | 1586 |
| [Blackguard Half-Elf 888896726](#blackguard-888896726-ce316fc0) | `reborn-shipped-defaults` | a crow | 3 | 2 (max 2) | 54455 | 5478 |

## Observations

Gate checks on all 18 replayed games (every play hash matches CI):

- **No unknown-item use:** there are no `# Quaffing/Reading/Eating unknown` notes in any game.
- **No Deep Descent read:** scrolls of Deep Descent were picked up or discarded, never read (#473).
- **Trip returns and descents:** 31 `Trip: return` decisions and 210 `no up stairs found, going down` notes over 15 of the 18 games. The heaviest are Rogue 1502695781 (82, as in the issue) and Warrior 1085222502 (43, with 19 trip returns).

Each death:

- **Blackguard 888896726 (crow, DL2, character level 3):**
  - At 14/32 HP it stayed adjacent and meleed Grip, Farmer Maggot's Dog with its Tulwar while two crows and the dog bit it. It died 7 game turns later.
  - It carried two unknown scroll kinds (4 + 2), which #473 forbids it to read, and an unidentified Iron Rod.
  - It had a Sling with 2 Iron Shots equipped.
  - It had no Cure Light Wounds and no Phase Door.
- **Druid 102023799 (rock lizard, DL1, character level 2, turn 33,735):**
  - Its weapon was a Shovel (1d2).
  - It meleed a rock lizard at 0/25 HP with a wild dog also biting.
  - It carried 14 Flasks of oil and 5 unknown potions (2 Metallic Red, 3 Light Blue) that it may not use.
  - Its SP were 4/4, unspent.
- **Necromancer 300036923 (wild cat, DL1, character level 1, turn 12,328):**
  - It ran out of Cure Light Wounds, then meleed the wild cat with a Main Gauche at 5/12 HP.
  - It carried 24 Flasks of oil, none thrown in the fight.
  - It was still level 1 after 12,000 game turns.

Shared with run 44054277431's deaths: a cornered Borg fights in melee with throwables, a launcher or spell points unused. Unknown items are now never used, so an unknown potion can no longer be a last resort, but neither can it help. Observations only.

## Handover: working on these deaths in the Borg's repository

For a session in diegoami/borg-reborn-rs that changes parameters or code against these deaths. That repository owns the Borg; the zoo only measures, and any change is measured here later as a new specimen.

- **Build:** `diegoami/borg-reborn-rs` at `fdaf18e52b402d9952f432109806b210cd2074ff` (zoo specimen `4.2.6-reborn-rust-main-fdaf18e5`): `BORG_IMPL=rust harness/build.sh`, or the run's CI artifact: `gh run download 44071581589 -R diegoami/borg-zoo -n build-4.2.6-reborn-rust-main-fdaf18e5`.
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
| [Druid 102023799](#druid-102023799-466c0175) | 102023799 | 0 (Human) | 2 | `reborn-shipped-defaults` | `466c01755aa66df8` |
| [Necromancer 300036923](#necromancer-300036923-00a4c65b) | 300036923 | 0 (Human) | 4 | `reborn-shipped-defaults` | `00a4c65ba210248c` |
| [Blackguard 888896726](#blackguard-888896726-ce316fc0) | 888896726 | 1 (Half-Elf) | 8 | `reborn-shipped-defaults` | `ce316fc045c41e4e` |

In borg-zoo, `python3 -m zoo.deaths --experiment experiments/reborn-main-defaults-pilot.json --run 44071581589` replays and checks them all. After a change: a PR in the Borg's repository, then ask the borg-zoo session for a new specimen at the merged commit and a pilot (or verysmall) of the same arms.

<a id="druid-102023799-466c0175"></a>
## Druid Human 102023799: a rock lizard

- Dies in: `reborn-shipped-defaults`, the same game (play `466c01755aa66df8`).
- Same start elsewhere: none.
- Last state line: `33735 107,45 d1/1 hp-1/25 sp4/4 f6129 au9 xp20 lv2 t- o1:2568,5:5000 p05c62283d77a016b e5cf0f735475f2df0 r08ee9afe362a4c74`

- Cure potions quaffed: 5; Phase Door read: 7; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 0; Failed teleports: 0; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Human Druid, Level 2/2
Exp: 120  Gold: 9  Turn: 33735
Killed on level: 1 (max. 1) by a rock lizard
```

**Character Equipment**

```
a) Shovel (1d2) (+0,+0)
f) Wooden Torch (2568 turns)
```

**Character Inventory**

```
a) Book of Nature Magics [Lesser Charms]
b) 5 Rations of Food
c) 6 Pints of Fine Wine
d) 14 Flasks of oil
e) Potion of Boldness
f) 2 Metallic Red Potions
g) 3 Light Blue Potions
i) Scroll of Detect Invisible
m) Wooden Torch (5000 turns)
```

**Home Inventory (page 1)**

```
a) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
2392 17102 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2485 17832 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2644 19413 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2697 19883 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2855 20864 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3003 22035 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3895 31681 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3954 32142 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 30 game messages

```
4136 33623 2 You hit the wild dog.
4136 33630 39 The wild dog bites you.
4139 33633 2 You hit the wild dog.
4139 33633 4 The wild dog flees in terror!
4139 33641 39 The wild dog bites you.
4143 33643 2 You hit the wild dog.
4143 33643 4 The wild dog flees in terror!
4145 33654 39 The wild dog bites you.
4148 33663 2 You hit the wild dog.
4148 33665 39 The wild dog bites you.
4150 33680 39 The rock lizard bites you.
4153 33683 2 You hit the wild dog.
4153 33687 39 The wild dog bites you.
4153 33689 39 The rock lizard bites you.
4156 33693 2 You hit the rock lizard.
4156 33698 39 The wild dog bites you.
4156 33699 39 The rock lizard bites you.
4160 33703 2 You hit the rock lizard.
4160 33708 39 The rock lizard bites you.
4160 33710 39 The wild dog bites you.
4164 33713 2 You hit the rock lizard.
4164 33717 39 The rock lizard bites you.
4164 33721 39 The wild dog bites you.
4168 33723 2 You hit the rock lizard.
4168 33726 39 The rock lizard bites you.
4168 33732 39 The wild dog bites you.
4172 33733 2 You hit the rock lizard.
4172 33735 39 The rock lizard bites you.
4172 33735 8 You die.
4173 33735 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
4166 33723 0 # Tracking a monster 'wild dog' at (41,107) from (41,106)
4166 33723 0 # HIT:the rock lizard (2)
4166 33723 0 # HIT_BY:The rock lizard (3)
4166 33723 0 # HIT_BY:The wild dog (3)
4166 33723 0 # Scary guy on level.
4166 33723 0 # Loc:45,107 Dep:1 Lev:2 HP:2/25 SP:4/4 Danger:p=4
4166 33723 0 # Fleeing and leaving the level. (scaryguy)
4166 33723 0 # Adjacent to monster on Scaryguy Level.
4166 33723 0 # Adjacent to monster on Scaryguy Level.
4166 33723 0 # Adjacent to monster on Scaryguy Level.
4166 33723 0 # Performing attack type 1 with value 4.
4166 33723 0 # Facing rock lizard at (46,107) who has 8 Hit Points.
4166 33723 0 # Attacking with weapon 'Shovel (1d2) (+0,+0)'
4170 33733 0 # HIT:the rock lizard (+)
4170 33733 0 # HIT_BY:The rock lizard (+)
4170 33733 0 # HIT_BY:The wild dog (+)
4170 33733 0 # HIT:the rock lizard (2)
4170 33733 0 # HIT_BY:The rock lizard (3)
4170 33733 0 # HIT_BY:The wild dog (3)
4170 33733 0 # Scary guy on level.
4170 33733 0 # Loc:45,107 Dep:1 Lev:2 HP:0/25 SP:4/4 Danger:p=4
4170 33733 0 # Fleeing and leaving the level. (scaryguy)
4170 33733 0 # Adjacent to monster on Scaryguy Level.
4170 33733 0 # Adjacent to monster on Scaryguy Level.
4170 33733 0 # Adjacent to monster on Scaryguy Level.
4170 33733 0 # Performing attack type 1 with value 4.
4170 33733 0 # Facing rock lizard at (46,107) who has 7 Hit Points.
4170 33733 0 # Attacking with weapon 'Shovel (1d2) (+0,+0)'
4173 33735 0 # Aborting (death).
4173 33735 0 # Aborting (player died).
```

<a id="necromancer-300036923-00a4c65b"></a>
## Necromancer Human 300036923: a wild cat

- Dies in: `reborn-shipped-defaults`, the same game (play `00a4c65ba210248c`).
- Same start elsewhere: none.
- Last state line: `12328 45,45 d1/1 hp-2/12 sp2/2 f8269 au10 xp4 lv1 t- o- p68494096aa8903d7 ef45f8eba99899246 r08ee9afe362a4c74`

- Cure potions quaffed: 5; Phase Door read: 3; Unknown potions quaffed: 0; Healing (outmatched) notes: 2; Potion of Speed quaffed: 0; Failed teleports: 1; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Human Necromancer, Level 1/1
Exp: 104  Gold: 10  Turn: 12328
Killed on level: 1 (max. 1) by a wild cat
```

**Character Equipment**

```
a) Main Gauche (1d5) (+0,+0)
```

**Character Inventory**

```
a) Necromantic Tome [Into the Shadows]
b) 5 Rations of Food
c) 14 Pints of Fine Wine
d) 24 Flasks of oil
e) 2 Potions of Boldness
```

### Last trip decisions

```
1242 9605 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1441 11291 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1487 11691 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 30 game messages

```
1560 12271 38 The wild cat claws you.
1560 12271 38 The wild cat claws you.
1564 12271 0 You feel much better.
1564 12271 0 You have 2 Potions of Cure Light Wounds (e).
1564 12275 38 The wild cat claws you.
1565 12275 0 The wild cat misses you.
1565 12280 38 The wild cat claws you.
1565 12280 38 The wild cat claws you.
1568 12290 38 The wild cat claws you.
1568 12290 38 The wild cat claws you.
1571 12291 0 You feel much better.
1571 12291 0 You have a Potion of Cure Light Wounds (e).
1571 12294 38 The wild cat claws you.
1572 12294 0 The wild cat misses you.
1572 12299 38 The wild cat claws you.
1572 12299 38 The wild cat claws you.
1575 12309 38 The wild cat claws you.
1575 12309 38 The wild cat claws you.
1578 12311 0 You feel much better.
1578 12311 0 You have no more Potions of Cure Light Wounds (e).
1578 12313 38 The wild cat claws you.
1579 12313 38 The wild cat claws you.
1579 12318 38 The wild cat claws you.
1580 12318 38 The wild cat claws you.
1583 12321 2 You hit the wild cat.
1583 12323 38 The wild cat claws you.
1583 12323 38 The wild cat claws you.
1583 12328 38 The wild cat claws you.
1584 12328 8 You die.
1585 12328 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
1574 12301 0 # Scary guy on level.
1574 12301 0 # Loc:44,46 Dep:1 Lev:1 HP:6/12 SP:2/2 Danger:p=18
1574 12301 0 # Fleeing and leaving the level. (scaryguy)
1574 12301 0 # Backing up to 45,45 (18 > 6)
1576 12311 0 # HIT_BY:The wild cat (+)
1576 12311 0 # HIT_BY:The wild cat (+)
1576 12311 0 # Tracking a monster 'wild cat' at (44,46) from (43,47)
1576 12311 0 # HIT_BY:The wild cat (3)
1576 12311 0 # HIT_BY:The wild cat (3)
1576 12311 0 # Scary guy on level.
1576 12311 0 # Loc:45,45 Dep:1 Lev:1 HP:2/12 SP:2/2 Danger:p=18
1576 12311 0 # Quaffing Potion of Cure Light Wounds.
1576 12311 0 # Healing Level 1.
1581 12321 0 # HIT_BY:The wild cat (+)
1581 12321 0 # HIT_BY:The wild cat (+)
1581 12321 0 # HIT_BY:The wild cat (+)
1581 12321 0 # HIT_BY:The wild cat (+)
1581 12321 0 # HIT_BY:The wild cat (3)
1581 12321 0 # HIT_BY:The wild cat (3)
1581 12321 0 # HIT_BY:The wild cat (3)
1581 12321 0 # HIT_BY:The wild cat (3)
1581 12321 0 # Scary guy on level.
1581 12321 0 # Loc:45,45 Dep:1 Lev:1 HP:5/12 SP:2/2 Danger:p=18
1581 12321 0 # Fleeing and leaving the level. (scaryguy)
1581 12321 0 # Adjacent to monster on Scaryguy Level.
1581 12321 0 # Performing attack type 1 with value 31.
1581 12321 0 # Facing wild cat at (44,46) who has 9 Hit Points.
1581 12321 0 # Attacking with weapon 'Main Gauche (1d5) (+0,+0)'
1585 12328 0 # Aborting (death).
1585 12328 0 # Aborting (player died).
```

<a id="blackguard-888896726-ce316fc0"></a>
## Blackguard Half-Elf 888896726: a crow

- Dies in: `reborn-shipped-defaults`, the same game (play `ce316fc045c41e4e`).
- Same start elsewhere: none.
- Last state line: `54455 87,52 d2/2 hp-1/32 sp4/4 f4459 au21 xp49 lv3 t- o2:5000,3:4990 pe976ad083b1f764e e59bb9327bec91ed1 r08ee9afe362a4c74`

- Cure potions quaffed: 9; Phase Door read: 3; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 0; Failed teleports: 1; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Half-Elf Blackguard, Level 3/3
Exp: 249  Gold: 21  Turn: 54455
Killed on level: 2 (max. 2) by a crow
```

**Character Equipment**

```
a) Tulwar (2d4) (+0,+0)
b) Sling (x2) (+0,+0)
f) Wooden Torch (4990 turns)
g) Robe [2,+0]
i) Cloak [1,+0]
m) Leather Shield [8,+0]
o) Set of Leather Gloves [1,+0]
```

**Character Quiver**

```
a) 2 Iron Shots (1d4) (+0,+0)
```

**Character Inventory**

```
a) Necromantic Tome [Into the Shadows]
b) 5 Rations of Food
c) 16 Pints of Fine Wine
d) Potion of Neutralize Poison
e) 4 Scrolls of Blessing
f) 4 Scrolls titled "valmus"
g) 2 Scrolls titled "navita abeo"
i) Iron Rod
m) 2 Wooden Torches (5000 turns)
n) Dagger (1d4) (+0,+0)
```

**Home Inventory (page 1)**

```
a) a Handful of Dried Fruits
b) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
3669 24548 0 # Trip: descend via search (plan 2): below-plan(1 < 2)
3693 24788 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
3768 25478 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
3999 27209 0 # Trip: descend via search (plan 2): below-plan(1 < 2)
4222 29035 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
4709 33282 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
4912 35053 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
5009 35656 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
```

### Last 30 game messages

```
5454 54417 39 The crow bites you.
5455 54418 0 Grip, Farmer Maggot's Dog, misses you.
5458 54421 3 You miss Grip, Farmer Maggot's Dog.
5458 54422 0 The crow misses you.
5458 54422 39 The crow bites you.
5459 54423 39 Grip, Farmer Maggot's Dog, bites you.
5459 54427 0 The crow misses you.
5460 54427 39 The crow bites you.
5463 54430 0 You feel much better.
5463 54430 0 You have no more Potions of Cure Light Wounds (d).
5463 54431 39 The crow bites you.
5464 54431 39 The crow bites you.
5464 54436 0 The crow misses you.
5464 54436 39 The crow bites you.
5465 54438 0 Grip, Farmer Maggot's Dog, misses you.
5468 54440 2 You hit Grip, Farmer Maggot's Dog.
5468 54441 39 The crow bites you.
5468 54441 0 The crow misses you.
5469 54443 39 Grip, Farmer Maggot's Dog, bites you.
5469 54446 39 The crow bites you.
5470 54446 39 The crow bites you.
5470 54448 39 Grip, Farmer Maggot's Dog, bites you.
5474 54448 2 You hit Grip, Farmer Maggot's Dog.
5474 54450 39 The crow bites you.
5474 54450 39 The crow bites you.
5475 54453 39 Grip, Farmer Maggot's Dog, bites you.
5475 54455 39 The crow bites you.
5476 54455 39 The crow bites you.
5476 54455 8 You die.
5477 54455 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
5466 54440 0 # Scary guy on level.
5466 54440 0 # Loc:52,87 Dep:2 Lev:3 HP:26/32 SP:4/4 Danger:p=28
5466 54440 0 # Fleeing and leaving the level. (scaryguy)
5466 54440 0 # Adjacent to monster on Scaryguy Level.
5466 54440 0 # Performing attack type 1 with raw utility 46 and weighted utility 73.
5466 54440 0 # Facing Grip, Farmer Maggot's Dog at (53,87) who has 18 Hit Points.
5466 54440 0 # Attacking with weapon 'Tulwar (2d4) (+0,+0)'
5472 54448 0 # HIT:Grip, Farmer Maggot's Dog (+)
5472 54448 0 # HIT_BY:The crow (+)
5472 54448 0 # MISS_BY:The crow (+)
5472 54448 0 # HIT_BY:Grip, Farmer Maggot's Dog (+)
5472 54448 0 # HIT_BY:The crow (+)
5472 54448 0 # HIT_BY:The crow (+)
5472 54448 0 # HIT_BY:Grip, Farmer Maggot's Dog (+)
5472 54448 0 # HIT:Grip, Farmer Maggot's Dog (2)
5472 54448 0 # HIT_BY:The crow (3)
5472 54448 0 # MISS_BY:The crow (3)
5472 54448 0 # HIT_BY:Grip, Farmer Maggot's Dog (3)
5472 54448 0 # HIT_BY:The crow (3)
5472 54448 0 # HIT_BY:The crow (3)
5472 54448 0 # HIT_BY:Grip, Farmer Maggot's Dog (3)
5472 54448 0 # Scary guy on level.
5472 54448 0 # Loc:52,87 Dep:2 Lev:3 HP:14/32 SP:4/4 Danger:p=28
5472 54448 0 # Fleeing and leaving the level. (scaryguy)
5472 54448 0 # Adjacent to monster on Scaryguy Level.
5472 54448 0 # Performing attack type 1 with raw utility 46 and weighted utility 73.
5472 54448 0 # Facing Grip, Farmer Maggot's Dog at (53,87) who has 11 Hit Points.
5472 54448 0 # Attacking with weapon 'Tulwar (2d4) (+0,+0)'
5477 54455 0 # Aborting (death).
5477 54455 0 # Aborting (player died).
```
