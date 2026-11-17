# Deaths in reborn-main-defaults-medium (borg-zoo#181)

Run [44072424588](https://github.com/diegoami/borg-zoo/actions/runs/44072424588), specimen `4.2.6-reborn-rust-main-fdaf18e5`. A reading aid written by `python3 -m zoo.deaths`, not a cemetery entry or a causal diagnosis.

22 deaths in 270 games, 22 distinct dying games. Replayed locally from the run's own build artifact, arms `reborn-shipped-defaults`: every replayed play hash matches CI.

| Game | Dies in | Killed by | Char level | Dungeon level | Game turn | Keys |
|---|---|---|---|---|---|---|
| [Rogue Elf 21863389](#rogue-21863389-88b50659) | `reborn-shipped-defaults` | Fang, Farmer Maggot's Dog | 2 | 1 (max 1) | 12784 | 2337 |
| [Priest Gnome 31959072](#priest-31959072-1cecde75) | `reborn-shipped-defaults` | a small kobold | 2 | 1 (max 2) | 25434 | 3380 |
| [Mage Half-Elf 136470996](#mage-136470996-bb83ada6) | `reborn-shipped-defaults` | a soldier | 2 | 1 (max 1) | 40705 | 4872 |
| [Priest Kobold 240655275](#priest-240655275-2c2baf38) | `reborn-shipped-defaults` | an apprentice | 2 | 1 (max 1) | 13532 | 1867 |
| [Necromancer Elf 303741412](#necromancer-303741412-667cb908) | `reborn-shipped-defaults` | a crow | 2 | 1 (max 1) | 42288 | 2923 |
| [Druid Half-Elf 460387443](#druid-460387443-21a4bc06) | `reborn-shipped-defaults` | a cave spider | 2 | 1 (max 1) | 25904 | 3710 |
| [Mage Human 461220874](#mage-461220874-b253da2b) | `reborn-shipped-defaults` | a grey mold | 1 | 1 (max 1) | 6592 | 1066 |
| [Druid Human 625213959](#druid-625213959-35272354) | `reborn-shipped-defaults` | Grip, Farmer Maggot's Dog | 2 | 1 (max 1) | 21932 | 2976 |
| [Necromancer Human 895240287](#necromancer-895240287-a3a93698) | `reborn-shipped-defaults` | Grip, Farmer Maggot's Dog | 2 | 1 (max 1) | 15601 | 2209 |
| [Priest Dunadan 1002239165](#priest-1002239165-0dfa3c82) | `reborn-shipped-defaults` | a white worm mass | 3 | 1 (max 2) | 54021 | 3444 |
| [Paladin Elf 1072421289](#paladin-1072421289-e3dd7aa3) | `reborn-shipped-defaults` | burning to a cinder in lava | 3 | 0 (max 1) | 81237 | 6445 |
| [Ranger High-Elf 1125613689](#ranger-1125613689-8d4ccad4) | `reborn-shipped-defaults` | Fang, Farmer Maggot's Dog | 1 | 1 (max 1) | 3212 | 861 |
| [Mage Elf 1158815282](#mage-1158815282-b030c02b) | `reborn-shipped-defaults` | a wild cat | 2 | 1 (max 2) | 14078 | 1881 |
| [Ranger Half-Elf 1222599014](#ranger-1222599014-cb17efbd) | `reborn-shipped-defaults` | poison | 4 | 1 (max 2) | 55480 | 10646 |
| [Mage Half-Orc 1263833284](#mage-1263833284-b139f8f5) | `reborn-shipped-defaults` | poison | 4 | 1 (max 1) | 35800 | 3750 |
| [Rogue Gnome 1496887118](#rogue-1496887118-409b6148) | `reborn-shipped-defaults` | poison | 1 | 0 (max 2) | 6110 | 1109 |
| [Warrior Dwarf 1597870353](#warrior-1597870353-020c8e41) | `reborn-shipped-defaults` | a giant white louse | 11 | 3 (max 3) | 89887 | 17068 |
| [Blackguard Gnome 1672393740](#blackguard-1672393740-fdf78440) | `reborn-shipped-defaults` | poison | 3 | 1 (max 1) | 11520 | 1770 |
| [Mage Human 1946087915](#mage-1946087915-7e4b7479) | `reborn-shipped-defaults` | a salamander | 1 | 1 (max 1) | 7299 | 1177 |
| [Blackguard Hobbit 1981269294](#blackguard-1981269294-a27f2412) | `reborn-shipped-defaults` | a cave spider | 4 | 2 (max 2) | 86576 | 5655 |
| [Mage Dunadan 2017596150](#mage-2017596150-1ebce90d) | `reborn-shipped-defaults` | a crow | 1 | 1 (max 1) | 13332 | 1520 |
| [Ranger Elf 2107852048](#ranger-2107852048-7ff5c21d) | `reborn-shipped-defaults` | Grip, Farmer Maggot's Dog | 1 | 1 (max 1) | 276 | 70 |

## Observations

All 270 games were replayed and every play hash matches CI. No game used an unknown item or read Deep Descent. These are observations from the logs, not diagnoses. The last column of each line is the same start on 193d9076 (the control of run 44065025814): 18 of these 22 starts lived there.

### The patterns

| Pattern | Deaths | Starts |
|---|---|---|
| Out of Cure Light Wounds at the end (the last one drunk shortly before death, or none carried) | 19 of 22 | all but Mage 2017596150 (2 left, quaffing at 5/11 HP while "Buying time waiting for Recall"), Paladin 1072421289 (lava, 5 left) and Ranger 2107852048 (none ever, died at turn 276) |
| Melee as the last action at low HP | 9 (7 of them while logging "Scary guy" or "Fleeing and leaving the level") | for example Druid 625213959 whipping Grip at 1/25 HP, Warrior 1597870353 at 0/145 HP against a louse swarm on DL3, Priest 1002239165 against a white worm mass at 0/24 |
| Flasks of oil carried at death (9 to 23) | 10 | 2 Druids, 4 Mages, 2 Necromancers, the Paladin and Rogue 1496887118. Some threw earlier, none threw in the last fight |
| Farmer Maggot's dogs (Grip, Fang) on DL1 at character level 1-2 | 5 | Druid 625213959, Necromancer 895240287, Rangers 1125613689 and 2107852048, Rogue 21863389 |
| Poison | 4 | Blackguard 1672393740 (yellow jelly, no Cure left), Mage 1263833284 (white worm mass), Ranger 1222599014 (shooting a white jelly while adjacent), Rogue 1496887118 (in town, see below) |
| Unknown potions or scrolls carried, which #473 forbids it to use | 9 | for example Druid 460387443 (5 potions), Blackguard 1981269294 (4 Gold Potions), Ranger 2107852048 (5 Muddy Potions and a scroll) |
| The "danger" estimate is small next to the HP left | many | for example `HP:1/25 Danger:p=8` (Druid 625213959), `HP:0/145 Danger:p=21` (Warrior 1597870353), `HP:3/16 Danger:p=12` (Necromancer 895240287) |

### Single deaths worth a look

- **Mages faint casting Phase Door with no mana.**
  - Mage 1158815282 and Mage 1263833284 log `Casting Phase Door (0,3)` and `Danger Level 1.3 Critical Attempt` with SP 0.
  - The game answers `You do not have enough mana`, `You faint from the effort!`, `You are paralysed!`.
  - Both die while paralysed: to a wild cat, and to poison from a white worm mass.
- **Rogue 1496887118 dies of poison in town.**
  - It was at character level 1 with a cursed Dagger and had drunk its last Cure Light Wounds.
  - Poisoned again, it was walking to the Alchemist (`Flowing toward Alchemy Shop`) with 25 gold, and died 18 steps away at turn 6,110.
- **Paladin 1072421289 dies in lava in the town.**
  - It was at full HP (33/33), carrying 5 Cure Light Wounds, a Cure Serious Wounds and a Word of Recall.
  - It looped on `Fleeing and leaving the level. Brave Thinking.`, `Not deep enough to recall` and `Boosting bravery … to 30000`.
  - Then `Twitchy!` (a random step) took it into lava at turn 81,237.
- **Priest 31959072 dies on the "going down" pendulum.**
  - At 3/14 HP: `no up stairs found, going down`, `Flowing toward down-stairs`, then `Walking into a 'small kobold'`, which killed it.
- **Ranger 2107852048 dies at game turn 276.**
  - It walked into Grip while `Flowing toward Scum item`. The same start also dies to Grip on 193d9076.
- **Ranger 1125613689 dies at turn 3,212.**
  - It was `Resting for Recall` with Fang adjacent.
- **Druid 460387443 fights with a Shovel (1d2).**
  - The pilot's Druid 102023799 did the same.

### Where to look first in borg-reborn-rs

1. **Spell casting without mana:** casting with SP below the spell's cost as a "critical attempt" (2 deaths by paralysis).
2. **The cornered fight:** melee while fleeing at very low HP, oil flasks not thrown, and danger estimates far below the HP left (9 deaths end in melee).
3. **Running out of Cure Light Wounds** (19 deaths). With #473, an unknown potion is no longer a fallback. Whether it buys or keeps enough Cure Light Wounds is the question.
4. **Town hazards:** the lava step from `Twitchy!`, and a poisoned level-1 character walking to the Alchemist with no cure.
5. **Farmer Maggot's dogs** at character level 1-2 (5 deaths).

## Handover: working on these deaths in the Borg's repository

For a session in diegoami/borg-reborn-rs that changes parameters or code against these deaths. That repository owns the Borg; the zoo only measures, and any change is measured here later as a new specimen.

- **Build:** `diegoami/borg-reborn-rs` at `fdaf18e52b402d9952f432109806b210cd2074ff` (zoo specimen `4.2.6-reborn-rust-main-fdaf18e5`): `BORG_IMPL=rust harness/build.sh`, or the run's CI artifact: `gh run download 44072424588 -R diegoami/borg-zoo -n build-4.2.6-reborn-rust-main-fdaf18e5`.
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
| [Rogue 21863389](#rogue-21863389-88b50659) | 21863389 | 2 (Elf) | 6 | `reborn-shipped-defaults` | `88b506590b8b3d22` |
| [Priest 31959072](#priest-31959072-1cecde75) | 31959072 | 4 (Gnome) | 3 | `reborn-shipped-defaults` | `1cecde75466d2889` |
| [Mage 136470996](#mage-136470996-bb83ada6) | 136470996 | 1 (Half-Elf) | 1 | `reborn-shipped-defaults` | `bb83ada6f0268622` |
| [Priest 240655275](#priest-240655275-2c2baf38) | 240655275 | 10 (Kobold) | 3 | `reborn-shipped-defaults` | `2c2baf38a7fa1c60` |
| [Necromancer 303741412](#necromancer-303741412-667cb908) | 303741412 | 2 (Elf) | 4 | `reborn-shipped-defaults` | `667cb908ccb90ae8` |
| [Druid 460387443](#druid-460387443-21a4bc06) | 460387443 | 1 (Half-Elf) | 2 | `reborn-shipped-defaults` | `21a4bc06efe2b089` |
| [Mage 461220874](#mage-461220874-b253da2b) | 461220874 | 0 (Human) | 1 | `reborn-shipped-defaults` | `b253da2bd62dc924` |
| [Druid 625213959](#druid-625213959-35272354) | 625213959 | 0 (Human) | 2 | `reborn-shipped-defaults` | `35272354584b763c` |
| [Necromancer 895240287](#necromancer-895240287-a3a93698) | 895240287 | 0 (Human) | 4 | `reborn-shipped-defaults` | `a3a93698a01fcf51` |
| [Priest 1002239165](#priest-1002239165-0dfa3c82) | 1002239165 | 8 (Dunadan) | 3 | `reborn-shipped-defaults` | `0dfa3c82c2984d70` |
| [Paladin 1072421289](#paladin-1072421289-e3dd7aa3) | 1072421289 | 2 (Elf) | 5 | `reborn-shipped-defaults` | `e3dd7aa3230f7275` |
| [Ranger 1125613689](#ranger-1125613689-8d4ccad4) | 1125613689 | 9 (High-Elf) | 7 | `reborn-shipped-defaults` | `8d4ccad45eaa4f93` |
| [Mage 1158815282](#mage-1158815282-b030c02b) | 1158815282 | 2 (Elf) | 1 | `reborn-shipped-defaults` | `b030c02b34248d5c` |
| [Ranger 1222599014](#ranger-1222599014-cb17efbd) | 1222599014 | 1 (Half-Elf) | 7 | `reborn-shipped-defaults` | `cb17efbdbda16b2a` |
| [Mage 1263833284](#mage-1263833284-b139f8f5) | 1263833284 | 6 (Half-Orc) | 1 | `reborn-shipped-defaults` | `b139f8f585b31618` |
| [Rogue 1496887118](#rogue-1496887118-409b6148) | 1496887118 | 4 (Gnome) | 6 | `reborn-shipped-defaults` | `409b61484245dc8d` |
| [Warrior 1597870353](#warrior-1597870353-020c8e41) | 1597870353 | 5 (Dwarf) | 0 | `reborn-shipped-defaults` | `020c8e41bcee030a` |
| [Blackguard 1672393740](#blackguard-1672393740-fdf78440) | 1672393740 | 4 (Gnome) | 8 | `reborn-shipped-defaults` | `fdf784400742bbde` |
| [Mage 1946087915](#mage-1946087915-7e4b7479) | 1946087915 | 0 (Human) | 1 | `reborn-shipped-defaults` | `7e4b7479707a8f67` |
| [Blackguard 1981269294](#blackguard-1981269294-a27f2412) | 1981269294 | 3 (Hobbit) | 8 | `reborn-shipped-defaults` | `a27f2412314d1229` |
| [Mage 2017596150](#mage-2017596150-1ebce90d) | 2017596150 | 8 (Dunadan) | 1 | `reborn-shipped-defaults` | `1ebce90db5a95802` |
| [Ranger 2107852048](#ranger-2107852048-7ff5c21d) | 2107852048 | 2 (Elf) | 7 | `reborn-shipped-defaults` | `7ff5c21df8e1f085` |

In borg-zoo, `python3 -m zoo.deaths --experiment experiments/reborn-main-defaults-medium.json --run 44072424588` replays and checks them all. After a change: a PR in the Borg's repository, then ask the borg-zoo session for a new specimen at the merged commit and a pilot (or verysmall) of the same arms.

<a id="rogue-21863389-88b50659"></a>
## Rogue Elf 21863389: Fang, Farmer Maggot's Dog

- Dies in: `reborn-shipped-defaults`, the same game (play `88b506590b8b3d22`).
- Same start elsewhere: none.
- Last state line: `12784 46,16 d1/1 hp-1/15 sp0/0 f8129 au113 xp18 lv2 t- o2:4483,7:5000 p79a3cbff5f0cc2c5 e17e086494852c877 r08ee9afe362a4c74`

- Cure potions quaffed: 4; Phase Door read: 3; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 0; Failed teleports: 2; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Elf Rogue, Level 2/2
Exp: 118  Gold: 113  Turn: 12784
Killed on level: 1 (max. 1) by Fang, Farmer Maggot's Dog
```

**Character Equipment**

```
a) Dagger (1d4) (+0,+0)
b) Sling (x2) (+0,+0)
f) Wooden Torch (4483 turns)
g) Soft Leather Armour [8,+0]
```

**Character Quiver**

```
a) 12 Iron Shots (1d4) (+0,+0)
```

**Character Inventory**

```
a) 7 Rations of Food
b) 4 Potions of Boldness
c) Wooden Torch (5000 turns)
```

**Home Inventory (page 1)**

```
a) 5 Flasks of oil
b) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
762 4516 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
920 4898 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1078 5845 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1166 6691 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1280 7144 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1799 9854 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1899 10714 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2099 11711 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 25 game messages

```
2289 12729 39 Fang, Farmer Maggot's Dog, bites you.
2289 12734 39 Fang, Farmer Maggot's Dog, bites you.
2294 12747 0 You feel much better.
2294 12747 0 You have no more Potions of Cure Light Wounds (b).
2294 12756 39 The wild dog bites you.
2298 12757 2 You hit the wild dog.
2298 12757 6 You have slain the wild dog.
2303 12762 0 Target Selected.
2307 12762 0 You have 14 Iron Shots (1d4) (+0,+0) (0).
2307 12764 39 Fang, Farmer Maggot's Dog, bites you.
2308 12769 39 Fang, Farmer Maggot's Dog, bites you.
2314 12772 0 Target Selected.
2318 12772 85 Your Iron Shot (1d4) (+0,+0) hits Fang, Farmer Maggot's Dog.
2318 12772 0 You have 13 Iron Shots (1d4) (+0,+0) (0).
2319 12772 0 Fang, Farmer Maggot's Dog, yelps in pain.
2320 12774 39 Fang, Farmer Maggot's Dog, bites you.
2321 12779 39 Fang, Farmer Maggot's Dog, bites you.
2327 12782 0 Target Selected.
2331 12782 85 Your Iron Shot (1d4) (+0,+0) hits Fang, Farmer Maggot's Dog.
2331 12782 0 You have 12 Iron Shots (1d4) (+0,+0) (0).
2332 12782 0 You feel something roll beneath your feet.
2333 12782 0 Fang, Farmer Maggot's Dog, writhes in agony.
2334 12784 39 Fang, Farmer Maggot's Dog, bites you.
2335 12784 8 You die.
2336 12784 0 Score not registered for borgs.
```

### Last 25 Borg notes

```
2310 12772 0 # Perhaps wall near targetted location (16,45)
2310 12772 0 # Guessing wall (16,46) near target (16,45)
2310 12772 0 # HIT_BY:Fang, Farmer Maggot's Dog (3)
2310 12772 0 # HIT_BY:Fang, Farmer Maggot's Dog (3)
2310 12772 0 # Scary guy on level.
2310 12772 0 # Loc:16,46 Dep:1 Lev:2 HP:7/15 SP:0/0 Danger:p=12
2310 12772 0 # Fleeing and leaving the level. (scaryguy)
2310 12772 0 # Performing attack type 3 with raw utility 33 and weighted utility 42.
2310 12772 0 # Targeting Fang, Farmer Maggot's Dog who has 9 Hit Points (16,45).
2310 12772 0 # Firing missile 'Iron Shots (1d4) (+0,+0)'
2323 12782 0 # PAIN:Fang, Farmer Maggot's Dog (+)
2323 12782 0 # HIT_BY:Fang, Farmer Maggot's Dog (+)
2323 12782 0 # HIT_BY:Fang, Farmer Maggot's Dog (+)
2323 12782 0 # PAIN:Fang, Farmer Maggot's Dog (2)
2323 12782 0 # HIT_BY:Fang, Farmer Maggot's Dog (3)
2323 12782 0 # HIT_BY:Fang, Farmer Maggot's Dog (3)
2323 12782 0 # There was an object '& Iron Shot~' at (44,16)
2323 12782 0 # Scary guy on level.
2323 12782 0 # Loc:16,46 Dep:1 Lev:2 HP:3/15 SP:0/0 Danger:p=12
2323 12782 0 # Fleeing and leaving the level. (scaryguy)
2323 12782 0 # Performing attack type 3 with raw utility 33 and weighted utility 42.
2323 12782 0 # Targeting Fang, Farmer Maggot's Dog who has 5 Hit Points (16,45).
2323 12782 0 # Firing missile 'Iron Shots (1d4) (+0,+0)'
2336 12784 0 # Aborting (death).
2336 12784 0 # Aborting (player died).
```

<a id="priest-31959072-1cecde75"></a>
## Priest Gnome 31959072: a small kobold

- Dies in: `reborn-shipped-defaults`, the same game (play `1cecde75466d2889`).
- Same start elsewhere: none.
- Last state line: `25434 110,38 d1/2 hp-2/14 sp1/4 f6759 au93 xp27 lv2 t9:2 o2:4305,4:3932,7:4809 p7c1b77a526cc75ef eb59f7d0d074aae80 r08ee9afe362a4c74`

- Cure potions quaffed: 3; Phase Door read: 3; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 0; Failed teleports: 2; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Gnome Priest, Level 2/2
Exp: 227  Gold: 93  Turn: 25434
Killed on level: 1 (max. 2) by a small kobold
```

**Character Equipment**

```
a) Mace (2d4) (+0,+0)
f) Wooden Torch of Brightness (4809 turns) <+1>
```

**Character Inventory**

```
a) Holy Book of Prayers [Novice's Handbook]
b) 13 Rations of Food
c) 3 Potions of Boldness
d) Purple Speckled Potion
e) 5 Scrolls of Treasure Detection
f) Wooden Torch (4305 turns)
g) Wooden Torch (3932 turns)
```

**Home Inventory (page 1)**

```
a) 2 Potions of Cure Light Wounds
b) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
1783 13296 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1944 14448 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2018 15008 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2362 17641 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2440 18332 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2579 19022 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2933 22003 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3086 23134 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 25 game messages

```
3332 25176 2 You hit the clear icky thing.
3332 25176 6 You have slain the clear icky thing.
3352 25356 2 You hit the small kobold.
3352 25356 4 The small kobold flees in terror!
3352 25361 34 The small kobold hits you.
3357 25366 0 You feel better.
3357 25370 34 The small kobold hits you.
3360 25376 0 You feel much better.
3360 25376 0 You have no more Potions of Cure Light Wounds (c).
3360 25379 34 The small kobold hits you.
3361 25379 76 You have been stunned.
3364 25386 2 You hit the small kobold.
3364 25389 34 The small kobold hits you.
3367 25396 0 You feel very good.
3367 25396 0 You have no more Potions of Cure Serious Wounds (c).
3367 25398 34 The small kobold hits you.
3371 25406 3 You miss the small kobold.
3371 25407 34 The small kobold hits you.
3371 25416 34 The small kobold hits you.
3375 25416 2 You hit the small kobold.
3375 25425 34 The small kobold hits you.
3378 25426 3 You fail to harm the small kobold.
3378 25434 34 The small kobold hits you.
3378 25434 8 You die.
3379 25434 0 Score not registered for borgs.
```

### Last 25 Borg notes

```
3373 25416 0 # Performing attack type 1 with value 17.
3373 25416 0 # Facing small kobold at (39,110) who has 1 Hit Points.
3373 25416 0 # Attacking with weapon 'Mace (2d4) (+0,+0)'
3376 25426 0 # HIT:the small kobold (+)
3376 25426 0 # HIT_BY:The small kobold (+)
3376 25426 0 # HIT:the small kobold (2)
3376 25426 0 # HIT_BY:The small kobold (3)
3376 25426 0 # Scary guy on level.
3376 25426 0 # Loc:38,110 Dep:1 Lev:2 HP:3/14 SP:1/4 Danger:p=10
3376 25426 0 # Fleeing and leaving the level. (scaryguy)
3376 25426 0 # Adjacent to monster on Scaryguy Level.
3376 25426 0 # Fleeing and leaving the level. (Looking for any stair)
3376 25426 0 # Fleeing and leaving the level (Looking for Up Stair).
3376 25426 0 # Spent too long (251) on level, leaving.
3376 25426 0 # heading up (bored and unable to dive: 30 hp)
3376 25426 0 # Looking for up stairs.  Going up.
3376 25426 0 # Bored but unable to flow to up stairs.
3376 25426 0 # no up stairs found, going down
3376 25426 0 # Boosting bravery (1) from 3 to 6!
3376 25426 0 # Bored, or recalling and fighting a monster on Scaryguy Level.
3376 25426 0 # Fleeing and leaving the level. Brave Thinking.
3376 25426 0 # Flowing toward down-stairs at cost 44
3376 25426 0 # Walking into a 'small kobold' at (39,110)
3379 25434 0 # Aborting (death).
3379 25434 0 # Aborting (player died).
```

<a id="mage-136470996-bb83ada6"></a>
## Mage Half-Elf 136470996: a soldier

- Dies in: `reborn-shipped-defaults`, the same game (play `bb83ada6f0268622`).
- Same start elsewhere: none.
- Last state line: `40705 23,19 d1/1 hp-3/17 sp0/4 f6529 au102 xp26 lv2 t- o2:3396,4:5000 pa764f23ecf707d8d e3eeb45dd1a305379 r08ee9afe362a4c74`

- Cure potions quaffed: 16; Phase Door read: 3; Unknown potions quaffed: 0; Healing (outmatched) notes: 4; Potion of Speed quaffed: 0; Failed teleports: 0; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Half-Elf Mage, Level 2/2
Exp: 126  Gold: 102  Turn: 40705
Killed on level: 1 (max. 1) by a soldier
```

**Character Equipment**

```
a) Rapier (1d6) (+0,+0)
b) Sling (x2) (+0,+0)
f) Wooden Torch (3396 turns)
m) Wicker Shield [2,+0]
```

**Character Quiver**

```
a) 21 Iron Shots (1d4) (+0,+0)
```

**Character Inventory**

```
a) 2 Books of Magic Spells [First Spells]
b) Handful of Dried Fruits
c) 10 Rations of Food
d) 3 Potions of Boldness
e) Green Potion
f) 2 Vermilion Potions
g) Wooden Torch (5000 turns)
```

**Home Inventory (page 1)**

```
a) 21 Flasks of oil
b) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
2546 22471 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2684 24381 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3198 28984 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3370 30335 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3407 30625 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
4333 36866 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
4378 37256 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
4711 40127 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 25 game messages

```
4848 40655 39 Fang, Farmer Maggot's Dog, bites you.
4852 40659 0 You feel much better.
4852 40659 0 You have 3 Potions of Cure Light Wounds (d).
4852 40660 39 Fang, Farmer Maggot's Dog, bites you.
4853 40665 34 The soldier hits you.
4853 40665 34 The soldier hits you.
4857 40669 0 You feel much better.
4857 40669 0 You have 2 Potions of Cure Light Wounds (d).
4857 40670 39 Fang, Farmer Maggot's Dog, bites you.
4858 40675 34 The soldier hits you.
4858 40675 34 The soldier hits you.
4859 40675 0 Fang, Farmer Maggot's Dog, misses you.
4862 40679 0 You feel much better.
4862 40679 0 You have a Potion of Cure Light Wounds (d).
4862 40680 0 Fang, Farmer Maggot's Dog, misses you.
4863 40685 34 The soldier hits you.
4863 40685 34 The soldier hits you.
4864 40685 39 Fang, Farmer Maggot's Dog, bites you.
4867 40689 0 You feel much better.
4867 40689 0 You have no more Potions of Cure Light Wounds (d).
4867 40695 34 The soldier hits you.
4868 40695 34 The soldier hits you.
4870 40705 34 The soldier hits you.
4870 40705 8 You die.
4871 40705 0 Score not registered for borgs.
```

### Last 25 Borg notes

```
4865 40689 0 # HIT_BY:The soldier (3)
4865 40689 0 # HIT_BY:The soldier (3)
4865 40689 0 # HIT_BY:Fang, Farmer Maggot's Dog (3)
4865 40689 0 # Fleeing level. Scumming Mode
4865 40689 0 # Scumming Mode.  Power Diving. 
4865 40689 0 # Scary guy on level.
4865 40689 0 # Loc:18,23 Dep:1 Lev:2 HP:1/17 SP:0/4 Danger:p=102
4865 40689 0 # Fleeing and leaving the level. (scaryguy)
4865 40689 0 # Quaffing Potion of Cure Light Wounds.
4865 40689 0 # Healing (outmatched).
4869 40699 0 # HIT_BY:The soldier (+)
4869 40699 0 # HIT_BY:The soldier (+)
4869 40699 0 # HIT_BY:The soldier (3)
4869 40699 0 # HIT_BY:The soldier (3)
4869 40699 0 # There was a monster 'Fang, Farmer Maggot's Dog' at (17,24)
4869 40699 0 # Forgetting a monster 'Fang, Farmer Maggot's Dog' at (17,24)
4869 40699 0 # Fleeing level. Scumming Mode
4869 40699 0 # Scumming Mode.  Power Diving. 
4869 40699 0 # Scary guy on level.
4869 40699 0 # Loc:18,23 Dep:1 Lev:2 HP:4/17 SP:0/4 Danger:p=84
4869 40699 0 # Fleeing and leaving the level. (scaryguy)
4869 40699 0 # Flowing toward up-stairs at cost 3
4869 40699 0 # Desperate for Stairs (three)
4871 40705 0 # Aborting (death).
4871 40705 0 # Aborting (player died).
```

<a id="priest-240655275-2c2baf38"></a>
## Priest Kobold 240655275: an apprentice

- Dies in: `reborn-shipped-defaults`, the same game (play `2c2baf38a7fa1c60`).
- Same start elsewhere: none.
- Last state line: `13532 79,37 d1/1 hp-3/18 sp3/4 f8649 au16 xp27 lv2 t- o2:4813,6:4621 pca69faffacfc6084 e72a1afcf0f6030e0 r08ee9afe362a4c74`

- Cure potions quaffed: 10; Phase Door read: 2; Unknown potions quaffed: 0; Healing (outmatched) notes: 1; Potion of Speed quaffed: 0; Failed teleports: 0; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Kobold Priest, Level 2/2
Exp: 127  Gold: 16  Turn: 13532
Killed on level: 1 (max. 1) by an apprentice
```

**Character Equipment**

```
a) Mace (2d4) (+0,+0)
f) Wooden Torch (4621 turns)
```

**Character Inventory**

```
a) Holy Book of Prayers [Novice's Handbook]
b) 7 Rations of Food
c) 5 Pints of Fine Wine
d) 3 Potions of Boldness
e) 5 Scrolls of Light
f) Wooden Torch (4813 turns)
```

**Home Inventory (page 1)**

```
a) 11 Flasks of oil
b) a Potion of Cure Light Wounds
c) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
506 4421 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
551 4801 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1102 8071 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1345 10154 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1678 12344 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 25 game messages

```
1834 13348 39 The crow bites you.
1834 13353 39 The crow bites you.
1834 13353 39 The crow bites you.
1838 13355 0 You feel much better.
1838 13355 53 You are no longer bleeding.
1838 13355 0 You have no more Potions of Cure Light Wounds (d).
1839 13358 39 The crow bites you.
1839 13358 39 The crow bites you.
1840 13363 39 The crow bites you.
1840 13363 39 The crow bites you.
1842 13373 39 The crow bites you.
1842 13373 39 The crow bites you.
1845 13375 3 You miss the crow.
1845 13378 39 The crow bites you.
1845 13378 0 The crow misses you.
1845 13383 39 The crow bites you.
1846 13383 39 The crow bites you.
1849 13385 2 You hit the crow.
1849 13385 4 The crow flees in terror!
1853 13395 0 You sense no evil creatures.
1863 13515 2 You hit the crow.
1863 13515 6 You have slain the crow.
1865 13532 34 The apprentice hits you.
1865 13532 8 You die.
1866 13532 0 Score not registered for borgs.
```

### Last 25 Borg notes

```
1860 13505 0 # Bored, or recalling and fighting a monster on Scaryguy Level.
1860 13505 0 # Flowing toward up-stairs at cost 39
1860 13505 0 # Looking for stairs. Goal_less, brave.
1861 13515 0 # Tracking a monster 'apprentice' at (36,81) from (36,82)
1861 13515 0 # Tracking a monster 'crow' at (36,78) from (34,79)
1861 13515 0 # Scary guy on level.
1861 13515 0 # Loc:37,78 Dep:1 Lev:2 HP:1/18 SP:3/4 Danger:p=131
1861 13515 0 # Fleeing and leaving the level. (scaryguy)
1861 13515 0 # Bored, or recalling and fighting a monster on Scaryguy Level.
1861 13515 0 # Bored, or recalling and fighting a monster on Scaryguy Level.
1861 13515 0 # Performing attack type 1 with value 33.
1861 13515 0 # Facing crow at (36,78) who has 2 Hit Points.
1861 13515 0 # Attacking with weapon 'Mace (2d4) (+0,+0)'
1864 13525 0 # HIT:the crow (+)
1864 13525 0 # KILL:the crow (+)
1864 13525 0 # Forgetting a monster 'crow' at (36,78)
1864 13525 0 # Tracking a monster 'apprentice' at (36,80) from (36,81)
1864 13525 0 # HIT:the crow (2)
1864 13525 0 # KILL:the crow (2)
1864 13525 0 # Scary guy on level.
1864 13525 0 # Loc:37,78 Dep:1 Lev:2 HP:1/18 SP:3/4 Danger:p=107
1864 13525 0 # Fleeing and leaving the level. (scaryguy)
1864 13525 0 # Bored, or recalling and fighting a monster on Scaryguy Level.
1866 13532 0 # Aborting (death).
1866 13532 0 # Aborting (player died).
```

<a id="necromancer-303741412-667cb908"></a>
## Necromancer Elf 303741412: a crow

- Dies in: `reborn-shipped-defaults`, the same game (play `667cb908ccb90ae8`).
- Same start elsewhere: none.
- Last state line: `42288 76,46 d1/1 hp-1/14 sp4/4 f5349 au52 xp19 lv2 t8:3 o- p2c3276bc1eb8b91b eaeab66549e7a5583 r08ee9afe362a4c74`

- Cure potions quaffed: 6; Phase Door read: 1; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 1; Failed teleports: 2; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Elf Necromancer, Level 2/2
Exp: 119  Gold: 52  Turn: 42288
Killed on level: 1 (max. 1) by a crow
```

**Character Equipment**

```
a) Main Gauche (1d5) (+0,+0)
i) Cloak [1,+0]
o) Set of Leather Gloves [1,+0]
p) Pair of Leather Sandals [1,+0]
```

**Character Inventory**

```
a) Necromantic Tome [Into the Shadows]
b) 5 Rations of Food
c) 17 Pints of Fine Wine
d) 17 Flasks of oil
e) 3 Potions of Boldness
f) 3 Scrolls of Phase Door
g) 2 Scrolls of Detect Invisible
```

**Home Inventory (page 1)**

```
a) an Apple
b) a Potion of Cure Light Wounds
```

### Last trip decisions

```
1685 13562 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1959 15564 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2179 17784 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2246 18894 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2529 39794 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2683 40834 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2732 41341 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2860 42140 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 25 game messages

```
2904 42251 0 You have a Potion of Cure Light Wounds (e).
2904 42255 39 The crow bites you.
2905 42255 39 The crow bites you.
2905 42260 39 The crow bites you.
2905 42260 39 The crow bites you.
2909 42261 0 You feel much better.
2909 42261 0 You have no more Potions of Cure Light Wounds (e).
2909 42264 39 The crow bites you.
2910 42264 39 The crow bites you.
2910 42269 39 The crow bites you.
2910 42269 39 The crow bites you.
2914 42271 0 You feel very good.
2914 42271 0 You have no more Potions of Cure Serious Wounds (e).
2914 42274 39 The crow bites you.
2915 42274 39 The crow bites you.
2915 42279 39 The crow bites you.
2915 42279 39 The crow bites you.
2919 42281 2 You hit the crow.
2919 42283 39 The crow bites you.
2919 42283 39 The crow bites you.
2919 42288 39 The crow bites you.
2920 42288 77 You have been given a graze.
2920 42288 39 The crow bites you.
2920 42288 8 You die.
2922 42288 0 Score not registered for borgs.
```

### Last 25 Borg notes

```
2912 42271 0 # Loc:46,76 Dep:1 Lev:2 HP:3/14 SP:4/4 Danger:p=12
2912 42271 0 # Quaffing Potion of Cure Serious Wounds.
2912 42271 0 # Healing Level 2.
2917 42281 0 # HIT_BY:The crow (+)
2917 42281 0 # HIT_BY:The crow (+)
2917 42281 0 # HIT_BY:The crow (+)
2917 42281 0 # HIT_BY:The crow (+)
2917 42281 0 # HIT_BY:The crow (3)
2917 42281 0 # HIT_BY:The crow (3)
2917 42281 0 # HIT_BY:The crow (3)
2917 42281 0 # HIT_BY:The crow (3)
2917 42281 0 # Loc:46,76 Dep:1 Lev:2 HP:6/14 SP:4/4 Danger:p=12
2917 42281 0 # No Phase. scary squares: 100
2917 42281 0 # No Phase. scary squares: 100
2917 42281 0 # No Phase. scary squares: 100
2917 42281 0 # No Phase. scary squares: 100
2917 42281 0 # No Phase. scary squares: 100
2917 42281 0 # No Phase. scary squares: 100
2917 42281 0 # No Phase. scary squares: 100
2917 42281 0 # No Phase. scary squares: 100
2917 42281 0 # Performing attack type 1 with value 19.
2917 42281 0 # Facing crow at (47,77) who has 9 Hit Points.
2917 42281 0 # Attacking with weapon 'Main Gauche (1d5) (+0,+0)'
2922 42288 0 # Aborting (death).
2922 42288 0 # Aborting (player died).
```

<a id="druid-460387443-21a4bc06"></a>
## Druid Half-Elf 460387443: a cave spider

- Dies in: `reborn-shipped-defaults`, the same game (play `21a4bc06efe2b089`).
- Same start elsewhere: none.
- Last state line: `25904 20,15 d1/1 hp-1/19 sp4/4 f7209 au94 xp27 lv2 t- o1:3880,10:5000 p16890fd8872f6b4d e2dfd01cd00497d9a r08ee9afe362a4c74`

- Cure potions quaffed: 8; Phase Door read: 7; Unknown potions quaffed: 0; Healing (outmatched) notes: 7; Potion of Speed quaffed: 0; Failed teleports: 0; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Half-Elf Druid, Level 2/2
Exp: 127  Gold: 94  Turn: 25904
Killed on level: 1 (max. 1) by a cave spider
```

**Character Equipment**

```
a) Shovel (1d2) (+0,+0)
f) Wooden Torch (3880 turns)
g) Robe [2,+2]
i) Cloak [1,+0]
n) Hard Leather Cap [2,+0]
o) Set of Leather Gloves [1,+0]
p) Pair of Leather Sandals [1,+0]
```

**Character Inventory**

```
a) Book of Nature Magics [Lesser Charms]
b) 5 Rations of Food
c) 13 Pints of Fine Wine
d) 16 Flasks of oil
e) 5 Potions of Boldness
f) Coagulated Crimson Potion
g) 4 Hazy Potions
i) Wooden Torch (5000 turns)
```

**Home Inventory (page 1)**

```
a) a Wooden Torch (4577 turns)
b) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
2145 16034 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2248 16734 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2535 18544 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2620 19204 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2722 19894 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2956 20825 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3155 22406 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3451 24444 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 25 game messages

```
3684 25834 4 The cave spider flees in terror!
3687 25844 2 You hit the cave spider.
3687 25845 39 The cave spider bites you.
3687 25849 39 The cave spider bites you.
3688 25854 39 The cave spider bites you.
3691 25854 0 You feel much better.
3691 25854 0 You have a Potion of Cure Light Wounds (e).
3691 25858 39 The cave spider bites you.
3692 25863 39 The cave spider bites you.
3695 25864 2 You hit the cave spider.
3695 25868 39 The cave spider bites you.
3695 25872 39 The cave spider bites you.
3699 25874 0 You feel much better.
3699 25874 0 You have no more Potions of Cure Light Wounds (e).
3699 25877 39 The cave spider bites you.
3700 25881 39 The cave spider bites you.
3703 25884 2 You hit the cave spider.
3703 25886 39 The cave spider bites you.
3703 25890 39 The cave spider bites you.
3707 25894 2 You hit the cave spider.
3707 25895 39 The cave spider bites you.
3707 25899 39 The cave spider bites you.
3708 25904 39 The cave spider bites you.
3708 25904 8 You die.
3709 25904 0 Score not registered for borgs.
```

### Last 25 Borg notes

```
3701 25884 0 # QUAKE:Somebody (+)
3701 25884 0 # QUAKE:Somebody (0)
3701 25884 0 # QUAKE:Somebody (0)
3701 25884 0 # Scary guy on level.
3701 25884 0 # Loc:15,20 Dep:1 Lev:2 HP:11/19 SP:4/4 Danger:p=35
3701 25884 0 # Fleeing and leaving the level. (scaryguy)
3701 25884 0 # Adjacent to monster on Scaryguy Level.
3701 25884 0 # Performing attack type 1 with value 56.
3701 25884 0 # Facing cave spider at (16,21) who has 4 Hit Points.
3701 25884 0 # Attacking with weapon 'Shovel (1d2) (+0,+0)'
3705 25894 0 # HIT:the cave spider (+)
3705 25894 0 # QUAKE:Somebody (+)
3705 25894 0 # QUAKE:Somebody (+)
3705 25894 0 # HIT:the cave spider (2)
3705 25894 0 # QUAKE:Somebody (0)
3705 25894 0 # QUAKE:Somebody (0)
3705 25894 0 # Scary guy on level.
3705 25894 0 # Loc:15,20 Dep:1 Lev:2 HP:7/19 SP:4/4 Danger:p=35
3705 25894 0 # Fleeing and leaving the level. (scaryguy)
3705 25894 0 # Adjacent to monster on Scaryguy Level.
3705 25894 0 # Performing attack type 1 with value 56.
3705 25894 0 # Facing cave spider at (16,21) who has 3 Hit Points.
3705 25894 0 # Attacking with weapon 'Shovel (1d2) (+0,+0)'
3709 25904 0 # Aborting (death).
3709 25904 0 # Aborting (player died).
```

<a id="mage-461220874-b253da2b"></a>
## Mage Human 461220874: a grey mold

- Dies in: `reborn-shipped-defaults`, the same game (play `b253da2bd62dc924`).
- Same start elsewhere: none.
- Last state line: `6592 134,36 d1/1 hp-3/10 sp2/2 f8959 au22 xp7 lv1 t- o2:4728,4:5000 pc2f06c1a062dbb97 ef229f96d20a8c3a0 r08ee9afe362a4c74`

- Cure potions quaffed: 7; Phase Door read: 0; Unknown potions quaffed: 0; Healing (outmatched) notes: 5; Potion of Speed quaffed: 0; Failed teleports: 1; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Human Mage, Level 1/1
Exp: 107  Gold: 22  Turn: 6592
Killed on level: 1 (max. 1) by a grey mold
```

**Character Equipment**

```
a) Rapier (1d6) (+0,+0)
f) Wooden Torch (4728 turns)
```

**Character Inventory**

```
a) Book of Magic Spells [First Spells]
b) 5 Rations of Food
c) 23 Flasks of oil
d) Potion of Cure Light Wounds
e) 5 Potions of Boldness
f) 3 Scrolls of Phase Door
g) Wooden Torch (5000 turns)
i) Shovel (1d2) (+0,+0)
```

**Home Inventory (page 1)**

```
a) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
570 2571 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
647 3281 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
907 5032 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 25 game messages

```
1005 5542 0 You have 24 Flasks of oil (c).
1005 5542 0 The Flask of oil breaks.
1011 5552 0 Target Selected.
1016 5552 85 Your Flask of oil hits the rock lizard.
1016 5552 6 The rock lizard dies.
1016 5552 0 You have 23 Flasks of oil (c).
1017 5552 0 The Flask of oil breaks.
1022 5665 0 You hear a door burst open!
1024 5672 78 You enter a maze of up staircases.
1031 6392 29 You enter a maze of down staircases.
1032 6392 0 This seems a tame, sheltered place.
1051 6565 49 The grey mold releases spores at you.
1051 6565 49 The grey mold releases spores at you.
1055 6572 0 You feel much better.
1055 6572 0 You have a Potion of Cure Light Wounds (d).
1055 6574 49 The grey mold releases spores at you.
1056 6574 49 The grey mold releases spores at you.
1060 6582 0 You feel much better.
1060 6582 0 You have no more Potions of Cure Light Wounds (d).
1060 6583 49 The grey mold releases spores at you.
1061 6583 49 The grey mold releases spores at you.
1062 6592 49 The grey mold releases spores at you.
1063 6592 49 The grey mold releases spores at you.
1064 6592 8 You die.
1065 6592 0 Score not registered for borgs.
```

### Last 25 Borg notes

```
1044 6502 0 # Flowing toward dark-3 at cost 3
1045 6512 0 # Creating a monster 'floating eye' at (37,146), HP: 11, Index: 27
1045 6512 0 # Removing Regional Fear (37,146) because of a LOS floating eye
1045 6512 0 # Flowing toward dark-3 at cost 3
1048 6542 0 # Flowing toward dark-1 at cost 1
1048 6542 0 # Opening a door
1050 6562 0 # Flowing toward dark-2 at cost 3
1053 6572 0 # HIT_BY:The grey mold (+)
1053 6572 0 # HIT_BY:The grey mold (+)
1053 6572 0 # Creating a monster 'grey mold' at (36,133), HP: 2, Index: 17
1053 6572 0 # Removing Regional Fear (36,133) because of a LOS grey mold
1053 6572 0 # HIT_BY:The grey mold (4)
1053 6572 0 # HIT_BY:The grey mold (4)
1053 6572 0 # Loc:36,134 Dep:1 Lev:1 HP:2/10 SP:2/2 Danger:p=16
1053 6572 0 # Quaffing Potions of Cure Light Wounds.
1053 6572 0 # Healing Level 1.
1058 6582 0 # HIT_BY:The grey mold (+)
1058 6582 0 # HIT_BY:The grey mold (+)
1058 6582 0 # HIT_BY:The grey mold (3)
1058 6582 0 # HIT_BY:The grey mold (3)
1058 6582 0 # Loc:36,134 Dep:1 Lev:1 HP:2/10 SP:2/2 Danger:p=16
1058 6582 0 # Quaffing Potion of Cure Light Wounds.
1058 6582 0 # Healing Level 1.
1065 6592 0 # Aborting (death).
1065 6592 0 # Aborting (player died).
```

<a id="druid-625213959-35272354"></a>
## Druid Human 625213959: Grip, Farmer Maggot's Dog

- Dies in: `reborn-shipped-defaults`, the same game (play `35272354584b763c`).
- Same start elsewhere: none.
- Last state line: `21932 75,17 d1/1 hp-3/25 sp4/4 f7509 au22 xp20 lv2 t- o5:5000,6:4410 pe2880b7195531c2b e43c2d50168259de0 r08ee9afe362a4c74`

- Cure potions quaffed: 7; Phase Door read: 3; Unknown potions quaffed: 0; Healing (outmatched) notes: 2; Potion of Speed quaffed: 0; Failed teleports: 5; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Human Druid, Level 2/2
Exp: 120  Gold: 22  Turn: 21932
Killed on level: 1 (max. 1) by Grip, Farmer Maggot's Dog
```

**Character Equipment**

```
a) Whip (1d3) (+0,+0)
f) Wooden Torch (4410 turns)
```

**Character Inventory**

```
a) Book of Nature Magics [Lesser Charms]
b) 5 Rations of Food
c) 22 Flasks of oil
d) 5 Potions of Boldness
e) Wooden Torch (5000 turns)
```

**Home Inventory (page 1)**

```
a) a Wooden Torch (4286 turns)
b) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
1815 12442 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2108 14482 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2146 14802 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2310 16792 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2382 17452 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2531 18762 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2674 19962 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2837 21452 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 25 game messages

```
2938 21852 39 Grip, Farmer Maggot's Dog, bites you.
2942 21852 0 You feel much better.
2942 21852 0 You have no more Potions of Cure Light Wounds (d).
2942 21857 39 Grip, Farmer Maggot's Dog, bites you.
2943 21862 39 Grip, Farmer Maggot's Dog, bites you.
2947 21862 2 You hit Grip, Farmer Maggot's Dog.
2947 21867 39 Grip, Farmer Maggot's Dog, bites you.
2947 21872 39 Grip, Farmer Maggot's Dog, bites you.
2951 21872 3 You miss Grip, Farmer Maggot's Dog.
2951 21877 39 Grip, Farmer Maggot's Dog, bites you.
2952 21882 39 Grip, Farmer Maggot's Dog, bites you.
2956 21882 2 You hit Grip, Farmer Maggot's Dog.
2956 21887 39 Grip, Farmer Maggot's Dog, bites you.
2956 21892 39 Grip, Farmer Maggot's Dog, bites you.
2960 21892 3 You miss Grip, Farmer Maggot's Dog.
2960 21897 0 Grip, Farmer Maggot's Dog, misses you.
2964 21902 3 You miss Grip, Farmer Maggot's Dog.
2964 21907 39 Grip, Farmer Maggot's Dog, bites you.
2968 21912 3 You miss Grip, Farmer Maggot's Dog.
2968 21922 39 Grip, Farmer Maggot's Dog, bites you.
2972 21922 3 You miss Grip, Farmer Maggot's Dog.
2972 21927 39 Grip, Farmer Maggot's Dog, bites you.
2973 21932 39 Grip, Farmer Maggot's Dog, bites you.
2974 21932 8 You die.
2975 21932 0 Score not registered for borgs.
```

### Last 25 Borg notes

```
2962 21902 0 # Performing attack type 1 with value 22.
2962 21902 0 # Facing Grip, Farmer Maggot's Dog at (17,76) who has 15 Hit Points.
2962 21902 0 # Attacking with weapon 'Whip (1d3) (+0,+0)'
2966 21912 0 # MISS:Grip, Farmer Maggot's Dog (+)
2966 21912 0 # HIT_BY:Grip, Farmer Maggot's Dog (+)
2966 21912 0 # MISS:Grip, Farmer Maggot's Dog (2)
2966 21912 0 # HIT_BY:Grip, Farmer Maggot's Dog (3)
2966 21912 0 # Scary guy on level.
2966 21912 0 # Loc:17,75 Dep:1 Lev:2 HP:3/25 SP:4/4 Danger:p=8
2966 21912 0 # Fleeing and leaving the level. (scaryguy)
2966 21912 0 # Performing attack type 1 with value 22.
2966 21912 0 # Facing Grip, Farmer Maggot's Dog at (17,76) who has 15 Hit Points.
2966 21912 0 # Attacking with weapon 'Whip (1d3) (+0,+0)'
2970 21922 0 # MISS:Grip, Farmer Maggot's Dog (+)
2970 21922 0 # HIT_BY:Grip, Farmer Maggot's Dog (+)
2970 21922 0 # MISS:Grip, Farmer Maggot's Dog (2)
2970 21922 0 # HIT_BY:Grip, Farmer Maggot's Dog (3)
2970 21922 0 # Scary guy on level.
2970 21922 0 # Loc:17,75 Dep:1 Lev:2 HP:1/25 SP:4/4 Danger:p=8
2970 21922 0 # Fleeing and leaving the level. (scaryguy)
2970 21922 0 # Performing attack type 1 with value 22.
2970 21922 0 # Facing Grip, Farmer Maggot's Dog at (17,76) who has 15 Hit Points.
2970 21922 0 # Attacking with weapon 'Whip (1d3) (+0,+0)'
2975 21932 0 # Aborting (death).
2975 21932 0 # Aborting (player died).
```

<a id="necromancer-895240287-a3a93698"></a>
## Necromancer Human 895240287: Grip, Farmer Maggot's Dog

- Dies in: `reborn-shipped-defaults`, the same game (play `a3a93698a01fcf51`).
- Same start elsewhere: none.
- Last state line: `15601 74,44 d1/1 hp-2/16 sp0/4 f7939 au8 xp12 lv2 t- o- pe11342566be7004f ef45f8eba99899246 r08ee9afe362a4c74`

- Cure potions quaffed: 5; Phase Door read: 3; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 0; Failed teleports: 0; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Human Necromancer, Level 2/2
Exp: 112  Gold: 8  Turn: 15601
Killed on level: 1 (max. 1) by Grip, Farmer Maggot's Dog
```

**Character Equipment**

```
a) Main Gauche (1d5) (+0,+0)
```

**Character Inventory**

```
a) Necromantic Tome [Into the Shadows]
b) Apple
c) 5 Rations of Food
d) 13 Pints of Fine Wine
e) 19 Flasks of oil
f) 5 Potions of Boldness
g) Scroll titled "flea lam sub"
```

### Last trip decisions

```
1359 8900 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1438 9420 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1559 10637 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1648 11351 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2077 15112 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 25 game messages

```
2154 15482 0 Target Selected.
2159 15482 0 Grip, Farmer Maggot's Dog, snarls with pain.
2159 15486 39 Grip, Farmer Maggot's Dog, bites you.
2160 15491 39 Grip, Farmer Maggot's Dog, bites you.
2164 15492 0 You feel much better.
2164 15492 0 You have a Potion of Cure Light Wounds (f).
2164 15496 39 Grip, Farmer Maggot's Dog, bites you.
2165 15501 39 Grip, Farmer Maggot's Dog, bites you.
2173 15512 0 Target Selected.
2178 15512 0 It yelps in pain.
2180 15531 39 Grip, Farmer Maggot's Dog, bites you.
2183 15532 0 You feel much better.
2183 15532 0 You have no more Potions of Cure Light Wounds (f).
2187 15571 39 Grip, Farmer Maggot's Dog, bites you.
2192 15572 0 Target Selected.
2197 15572 0 You failed to concentrate hard enough!
2197 15576 39 Grip, Farmer Maggot's Dog, bites you.
2198 15581 39 Grip, Farmer Maggot's Dog, bites you.
2202 15582 3 You miss Grip, Farmer Maggot's Dog.
2202 15586 39 Grip, Farmer Maggot's Dog, bites you.
2206 15592 2 You hit Grip, Farmer Maggot's Dog.
2206 15596 39 Grip, Farmer Maggot's Dog, bites you.
2206 15601 39 Grip, Farmer Maggot's Dog, bites you.
2207 15601 8 You die.
2208 15601 0 Score not registered for borgs.
```

### Last 25 Borg notes

```
2188 15572 0 # Targeting Grip, Farmer Maggot's Dog who has 12 Hit Points (44,75).
2188 15572 0 # Casting Nether Bolt (0,0).
2198 15581 0 # Normal failure.
2200 15582 0 # HIT_BY:Grip, Farmer Maggot's Dog (+)
2200 15582 0 # HIT_BY:Grip, Farmer Maggot's Dog (+)
2200 15582 0 # HIT_BY:Grip, Farmer Maggot's Dog (3)
2200 15582 0 # HIT_BY:Grip, Farmer Maggot's Dog (3)
2200 15582 0 # Scary guy on level.
2200 15582 0 # Loc:44,74 Dep:1 Lev:2 HP:6/16 SP:0/4 Danger:p=12
2200 15582 0 # Fleeing and leaving the level. (scaryguy)
2200 15582 0 # Performing attack type 1 with value 26.
2200 15582 0 # Facing Grip, Farmer Maggot's Dog at (44,75) who has 12 Hit Points.
2200 15582 0 # Attacking with weapon 'Main Gauche (1d5) (+0,+0)'
2204 15592 0 # MISS:Grip, Farmer Maggot's Dog (+)
2204 15592 0 # HIT_BY:Grip, Farmer Maggot's Dog (+)
2204 15592 0 # MISS:Grip, Farmer Maggot's Dog (2)
2204 15592 0 # HIT_BY:Grip, Farmer Maggot's Dog (3)
2204 15592 0 # Scary guy on level.
2204 15592 0 # Loc:44,74 Dep:1 Lev:2 HP:3/16 SP:0/4 Danger:p=12
2204 15592 0 # Fleeing and leaving the level. (scaryguy)
2204 15592 0 # Performing attack type 1 with value 26.
2204 15592 0 # Facing Grip, Farmer Maggot's Dog at (44,75) who has 12 Hit Points.
2204 15592 0 # Attacking with weapon 'Main Gauche (1d5) (+0,+0)'
2208 15601 0 # Aborting (death).
2208 15601 0 # Aborting (player died).
```

<a id="priest-1002239165-0dfa3c82"></a>
## Priest Dunadan 1002239165: a white worm mass

- Dies in: `reborn-shipped-defaults`, the same game (play `0dfa3c82c2984d70`).
- Same start elsewhere: none.
- Last state line: `54021 110,22 d1/2 hp-1/24 sp1/6 f3799 au23 xp51 lv3 t- o2:5000,4:2196 p2804ebbf37e022c8 e6033fa9364b48701 r08ee9afe362a4c74`

- Cure potions quaffed: 2; Phase Door read: 5; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 0; Failed teleports: 4; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Dunadan Priest, Level 3/3
Exp: 251  Gold: 23  Turn: 54021
Killed on level: 1 (max. 2) by a white worm mass
```

**Character Equipment**

```
a) Mace (2d4) (+0,+0)
f) Wooden Torch (2196 turns)
g) Robe [2,+0]
i) Cloak [1,+0]
```

**Character Inventory**

```
a) 4 Holy Books of Prayers [Novice's Handbook]
b) Handful of Dried Fruits
c) 5 Rations of Food
d) 9 Pints of Fine Wine
e) Potion of Boldness
f) Yellow Potion
g) Wooden Torch (5000 turns)
i) Robe [2,+0]
```

**Home Inventory (page 1)**

```
a) 2 Handfuls of Dried Fruits
b) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
1571 30117 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1892 34031 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2144 38733 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2225 40183 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2500 43234 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2669 44944 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2987 48889 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3426 53970 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 25 game messages

```
3396 53770 53 You are no longer poisoned.
3403 53839 44 The white worm mass crawls on you.
3403 53839 56 You are poisoned!
3406 53850 53 You are no longer poisoned.
3406 53859 44 The white worm mass crawls on you.
3406 53859 56 You are poisoned!
3410 53870 53 You are no longer poisoned.
3413 53899 44 The white worm mass crawls on you.
3413 53899 56 You are poisoned!
3416 53910 53 You are no longer poisoned.
3419 53939 44 The white worm mass crawls on you.
3419 53939 56 You are poisoned!
3422 53950 53 You are no longer poisoned.
3425 53960 2 You hit the white worm mass.
3428 53970 2 You hit the white worm mass.
3428 53970 6 You have destroyed the white worm mass.
3431 53980 2 You hit the white worm mass.
3434 53990 2 You hit the white worm mass.
3434 53990 6 You have destroyed the white worm mass.
3438 54010 2 You hit the white worm mass.
3438 54010 6 You have destroyed the white worm mass.
3441 54020 2 You hit the white worm mass.
3441 54021 44 The white worm mass crawls on you.
3441 54021 8 You die.
3443 54021 0 Score not registered for borgs.
```

### Last 25 Borg notes

```
3435 54000 0 # Forgetting a monster 'white worm mass' at (22,110)
3435 54000 0 # HIT:the white worm mass (2)
3435 54000 0 # KILL:the white worm mass (2)
3435 54000 0 # Fleeing and leaving the level. (Looking for any stair)
3435 54000 0 # Flowing toward down-stairs at cost 16
3436 54010 0 # Creating a monster 'white worm mass' at (23,111), HP: 9, Index: 26
3436 54010 0 # Removing Regional Fear (23,111) because of a LOS white worm mass
3436 54010 0 # Creating a monster 'white worm mass' at (22,111), HP: 7, Index: 26
3436 54010 0 # Removing Regional Fear (22,111) because of a LOS white worm mass
3436 54010 0 # Possibility of being surrounded (monsters/safegrids)(2/1)
3436 54010 0 # Loc:22,110 Dep:1 Lev:3 HP:0/24 SP:1/6 Danger:p=72
3436 54010 0 # Performing attack type 1 with value 39.
3436 54010 0 # Facing white worm mass at (22,111) who has 7 Hit Points.
3436 54010 0 # Attacking with weapon 'Mace (2d4) (+0,+0)'
3439 54020 0 # HIT:the white worm mass (+)
3439 54020 0 # KILL:the white worm mass (+)
3439 54020 0 # Forgetting a monster 'white worm mass' at (22,111)
3439 54020 0 # HIT:the white worm mass (2)
3439 54020 0 # KILL:the white worm mass (2)
3439 54020 0 # Loc:22,110 Dep:1 Lev:3 HP:0/24 SP:1/6 Danger:p=32
3439 54020 0 # Performing attack type 1 with value 39.
3439 54020 0 # Facing white worm mass at (23,111) who has 9 Hit Points.
3439 54020 0 # Attacking with weapon 'Mace (2d4) (+0,+0)'
3443 54021 0 # Aborting (death).
3443 54021 0 # Aborting (player died).
```

<a id="paladin-1072421289-e3dd7aa3"></a>
## Paladin Elf 1072421289: burning to a cinder in lava

- Dies in: `reborn-shipped-defaults`, the same game (play `e3dd7aa3230f7275`).
- Same start elsewhere: none.
- Last state line: `81237 42,5 d0/1 hp-152/33 sp3/3 f1579 au21 xp50 lv3 t- o3:658,14:5000 pe890f3d46f5da903 e79a0caef79be09c1 r08ee9afe362a4c74`

- Cure potions quaffed: 1; Phase Door read: 10; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 0; Failed teleports: 0; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Elf Paladin, Level 3/3
Exp: 150  Gold: 21  Turn: 81237
Killed on level: 0 (max. 1) by burning to a cinder in lava
```

**Character Equipment**

```
a) Main Gauche (1d5) (+0,+0)
f) Wooden Torch (658 turns)
g) Robe [2,+0]
i) Cloak [1,+0]
m) Leather Shield [8,+0]
n) Hard Leather Cap [2,+0]
o) Set of Leather Gloves [1,+0]
p) Pair of Leather Boots [2,+0]
```

**Character Inventory**

```
a) 2 Holy Books of Prayers [Novice's Handbook]
b) 5 Rations of Food
c) 2 Pints of Fine Wine
d) 10 Flasks of oil
e) 5 Potions of Cure Light Wounds
f) Potion of Cure Serious Wounds
g) 4 Potions of Boldness
i) Scroll of Magic Mapping
m) Scroll of Word of Recall
n) 2 Wooden Torches (5000 turns)
o) Shovel (1d2) (+0,+0)
```

**Home Inventory (page 1)**

```
a) a Handful of Dried Fruits
b) a Potion of Cure Serious Wounds
c) a Wooden Torch (3747 turns)
d) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
2807 19685 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2982 20730 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3096 21650 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3365 24523 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3715 31427 0 # Trip: descend via search (plan 2): below-plan(1 < 2)
3975 37555 0 # Trip: descend via search (plan 2): below-plan(1 < 2)
4355 42070 0 # Trip: descend via search (plan 2): below-plan(1 < 2)
5328 69807 0 # Trip: descend via search (plan 2): below-plan(1 < 2)
```

### Last 25 game messages

```
6086 77880 2 You hit the village idiot.
6086 77880 4 The village idiot flees in terror!
6089 77887 0 You dig in the rubble with your swap digger.
6092 77897 0 You dig in the rubble with your swap digger.
6093 77907 0 You dig in the rubble with your swap digger.
6094 77917 0 You dig in the rubble with your swap digger.
6095 77927 0 You dig in the rubble with your swap digger.
6096 77937 0 You have removed the rubble with your swap digger.
6107 78027 2 You hit the pitiful-looking beggar.
6107 78027 6 You have slain the pitiful-looking beggar.
6112 78045 2 You hit the village idiot.
6112 78045 4 The village idiot flees in terror!
6152 78422 2 You hit the village idiot.
6152 78422 4 The village idiot flees in terror!
6187 78750 2 You hit the village idiot.
6187 78750 6 You have slain the village idiot.
6213 79000 129 You are getting hungry.
6216 79007 17 That tastes great!  A fine vintage.
6216 79007 129 You are no longer hungry.
6216 79007 66 You feel bold.
6217 79007 0 You have 2 Pints of Fine Wine (c).
6297 79800 53 You no longer feel bold.
6443 81237 0 The lava burns you!
6443 81237 8 You die.
6444 81237 0 Score not registered for borgs.
```

### Last 25 Borg notes

```
6440 81227 0 # Boosting bravery (1) from 33 to 66!
6440 81227 0 # Fleeing and leaving the level. Brave Thinking.
6440 81227 0 # Not deep enough to recall
6440 81227 0 # Boosting bravery (2) from 33 to 132!
6440 81227 0 # Fleeing and leaving the level. Brave Thinking.
6440 81227 0 # Not deep enough to recall
6440 81227 0 # Boosting bravery (3) from 33 to 30000!
6440 81227 0 # Fleeing and leaving the level. Brave Thinking.
6440 81227 0 # Not deep enough to recall
6440 81227 0 # Twitchy!
6441 81237 0 # Fleeing and leaving the level. (Looking for any stair)
6441 81237 0 # Fleeing and leaving the level (Looking for Up Stair).
6441 81237 0 # Not deep enough to recall
6441 81237 0 # Boosting bravery (1) from 33 to 66!
6441 81237 0 # Fleeing and leaving the level. Brave Thinking.
6441 81237 0 # Not deep enough to recall
6441 81237 0 # Boosting bravery (2) from 33 to 132!
6441 81237 0 # Fleeing and leaving the level. Brave Thinking.
6441 81237 0 # Not deep enough to recall
6441 81237 0 # Boosting bravery (3) from 33 to 30000!
6441 81237 0 # Fleeing and leaving the level. Brave Thinking.
6441 81237 0 # Not deep enough to recall
6441 81237 0 # Twitchy!
6444 81237 0 # Aborting (death).
6444 81237 0 # Aborting (player died).
```

<a id="ranger-1125613689-8d4ccad4"></a>
## Ranger High-Elf 1125613689: Fang, Farmer Maggot's Dog

- Dies in: `reborn-shipped-defaults`, the same game (play `8d4ccad45eaa4f93`).
- Same start elsewhere: none.
- Last state line: `3212 139,13 d1/1 hp-4/15 sp0/0 f8879 au9 xp1 lv1 t- o3:4897 p8cda99677f71a865 e3a07bce3466c0eb2 r08ee9afe362a4c74`

- Cure potions quaffed: 2; Phase Door read: 1; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 0; Failed teleports: 0; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the High-Elf Ranger, Level 1/1
Exp: 101  Gold: 9  Turn: 3212
Killed on level: 1 (max. 1) by Fang, Farmer Maggot's Dog
```

**Character Equipment**

```
a) Main Gauche (1d5) (+0,+0)
b) Short Bow (x2) (+0,+0)
f) Wooden Torch (4897 turns)
```

**Character Quiver**

```
a) 40 Arrows (1d4) (+0,+0)
b) 9 Arrows (1d4) (+0,+0)
```

**Character Inventory**

```
a) 5 Rations of Food
b) 3 Potions of Boldness
```

### Last trip decisions

```
680 2443 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 25 game messages

```
803 3143 0 You feel much better.
803 3143 0 You have no more Potions of Cure Light Wounds (b).
803 3147 39 Fang, Farmer Maggot's Dog, bites you.
804 3152 39 Fang, Farmer Maggot's Dog, bites you.
807 3162 39 Fang, Farmer Maggot's Dog, bites you.
810 3163 2 You hit Fang, Farmer Maggot's Dog.
818 3179 2 You hit Fang, Farmer Maggot's Dog.
818 3182 39 Fang, Farmer Maggot's Dog, bites you.
823 3185 0 Target Selected.
828 3185 0 Target Selected.
832 3185 85 Your Arrow (1d4) (+0,+0) hits Fang, Farmer Maggot's Dog.
832 3185 0 You have 50 Arrows (1d4) (+0,+0) (1st 0).
833 3185 0 The Arrow breaks.
833 3185 0 Fang, Farmer Maggot's Dog, howls in pain.
834 3187 39 Fang, Farmer Maggot's Dog, bites you.
835 3192 0 Fang, Farmer Maggot's Dog, misses you.
841 3195 0 Target Selected.
846 3195 0 Target Selected.
850 3195 85 Your Arrow (1d4) (+0,+0) hits Fang, Farmer Maggot's Dog.
850 3195 0 You have 49 Arrows (1d4) (+0,+0) (1st 0).
851 3195 0 Fang, Farmer Maggot's Dog, yelps in pain.
852 3197 39 Fang, Farmer Maggot's Dog, bites you.
859 3212 39 Fang, Farmer Maggot's Dog, bites you.
859 3212 8 You die.
860 3212 0 Score not registered for borgs.
```

### Last 25 Borg notes

```
837 3195 0 # MISS_BY:Fang, Farmer Maggot's Dog (+)
837 3195 0 # Tracking a monster 'white harpy' at (6,146) from (7,145)
837 3195 0 # PAIN:Fang, Farmer Maggot's Dog (2)
837 3195 0 # HIT_BY:Fang, Farmer Maggot's Dog (3)
837 3195 0 # MISS_BY:Fang, Farmer Maggot's Dog (3)
837 3195 0 # Scary guy on level.
837 3195 0 # Loc:13,139 Dep:1 Lev:1 HP:2/15 SP:0/0 Danger:p=12
837 3195 0 # Fleeing and leaving the level. (scaryguy)
837 3195 0 # Bored, or recalling and fighting a monster on Scaryguy Level.
837 3195 0 # Performing attack type 3 with raw utility 33 and weighted utility 66.
837 3195 0 # Targeting Fang, Farmer Maggot's Dog who has 5 Hit Points (12,138).
837 3195 0 # Targeting Fang, Farmer Maggot's Dog who has 5 Hit Points (12,138).
837 3195 0 # Firing missile 'Arrows (1d4) (+0,+0)'
854 3205 0 # PAIN:Fang, Farmer Maggot's Dog (+)
854 3205 0 # HIT_BY:Fang, Farmer Maggot's Dog (+)
854 3205 0 # Tracking a monster 'white harpy' at (7,145) from (6,146)
854 3205 0 # Creating an object '& Arrow~' at (138,12)
854 3205 0 # PAIN:Fang, Farmer Maggot's Dog (2)
854 3205 0 # HIT_BY:Fang, Farmer Maggot's Dog (3)
854 3205 0 # There was a monster 'Fang, Farmer Maggot's Dog' at (12,138)
854 3205 0 # Forgetting a monster 'Fang, Farmer Maggot's Dog' at (12,138)
854 3205 0 # Scary guy on level.
854 3205 0 # Resting for Recall.
860 3212 0 # Aborting (death).
860 3212 0 # Aborting (player died).
```

<a id="mage-1158815282-b030c02b"></a>
## Mage Elf 1158815282: a wild cat

- Dies in: `reborn-shipped-defaults`, the same game (play `b030c02b34248d5c`).
- Same start elsewhere: none.
- Last state line: `14078 40,42 d1/2 hp-1/13 sp0/4 f7999 au16 xp20 lv2 t3:1 o2:4462,6:5000 p582706c276a87485 ef229f96d20a8c3a0 r08ee9afe362a4c74`

- Cure potions quaffed: 4; Phase Door read: 2; Unknown potions quaffed: 0; Healing (outmatched) notes: 3; Potion of Speed quaffed: 0; Failed teleports: 0; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Elf Mage, Level 2/2
Exp: 220  Gold: 16  Turn: 14078
Killed on level: 1 (max. 2) by a wild cat
```

**Character Equipment**

```
a) Rapier (1d6) (+0,+0)
f) Wooden Torch (4462 turns)
```

**Character Inventory**

```
a) 2 Books of Magic Spells [First Spells]
b) 5 Rations of Food
c) 18 Flasks of oil
d) 4 Potions of Boldness
e) Scroll of Detect Invisible
f) Wooden Torch (5000 turns)
```

**Home Inventory (page 1)**

```
a) an Apple
b) a Handful of Dried Fruits
c) a Potion of Heroism
d) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
856 5371 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1155 8023 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1325 9974 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1608 12302 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1785 13684 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 25 game messages

```
1854 13964 0 You have a Potion of Cure Light Wounds (d).
1854 13967 38 The wild cat claws you.
1855 13967 38 The wild cat claws you.
1855 13970 0 The clear icky thing wakes up.
1856 13972 38 The wild cat claws you.
1856 13972 38 The wild cat claws you.
1860 13974 0 You feel much better.
1860 13974 0 You have no more Potions of Cure Light Wounds (d).
1860 13978 38 The wild cat claws you.
1861 13978 38 The wild cat claws you.
1861 13980 35 The clear icky thing touches you.
1862 13983 38 The wild cat claws you.
1862 13983 38 The wild cat claws you.
1867 13984 0 You do not have enough mana to cast this spell.
1869 13984 0 You faint from the effort!
1869 13984 58 You are paralysed!
1869 13984 0 You have damaged your health!
1870 13990 53 You can move again.
1876 14014 0 You do not have enough mana to cast this spell.
1878 14014 0 You faint from the effort!
1878 14014 58 You are paralysed!
1878 14014 0 You have damaged your health!
1879 14078 38 The wild cat claws you.
1879 14078 8 You die.
1880 14078 0 Score not registered for borgs.
```

### Last 25 Borg notes

```
1864 13984 0 # Fleeing and leaving the level. (scaryguy)
1864 13984 0 # Casting Phase Door (0,3).
1864 13984 0 # Danger Level 1.3  Critical Attempt
1871 13994 0 # PAIN:You (+)
1871 13994 0 # Assuming player ghost (You) (a)
1871 13994 0 # Assuming player ghost (You) (a)
1871 13994 0 # Assuming player ghost (You) (a)
1871 13994 0 # PAIN:You (0)
1871 13994 0 # Scary guy on level.
1871 13994 0 # Fleeing and leaving the level. (scaryguy)
1871 13994 0 # Flowing toward up-stairs at cost 6
1871 13994 0 # Desperate for Stairs (three)
1872 14004 0 # Tracking a monster 'wild cat' at (43,32) from (39,32)
1872 14004 0 # Scary guy on level.
1872 14004 0 # Fleeing and leaving the level. (scaryguy)
1872 14004 0 # Flowing toward up-stairs at cost 5
1872 14004 0 # Desperate for Stairs (three)
1873 14014 0 # Tracking a monster 'wild cat' at (45,31) from (43,32)
1873 14014 0 # Scary guy on level.
1873 14014 0 # Loc:46,31 Dep:1 Lev:2 HP:0/13 SP:0/4 Danger:p=18
1873 14014 0 # Fleeing and leaving the level. (scaryguy)
1873 14014 0 # Casting Phase Door (0,3).
1873 14014 0 # Danger Level 1.3  Critical Attempt
1880 14078 0 # Aborting (death).
1880 14078 0 # Aborting (player died).
```

<a id="ranger-1222599014-cb17efbd"></a>
## Ranger Half-Elf 1222599014: poison

- Dies in: `reborn-shipped-defaults`, the same game (play `cb17efbdbda16b2a`).
- Same start elsewhere: none.
- Last state line: `55480 92,37 d1/2 hp-1/33 sp3/3 f4359 au735 xp64 lv4 t7:167 o3:453,8:5000 p7399e6951b95c1bb e568f0868ee243d09 r08ee9afe362a4c74`

- Cure potions quaffed: 9; Phase Door read: 17; Unknown potions quaffed: 0; Healing (outmatched) notes: 7; Potion of Speed quaffed: 0; Failed teleports: 2; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Half-Elf Ranger, Level 4/4
Exp: 264  Gold: 735  Turn: 55480
Killed on level: 1 (max. 2) by poison
```

**Character Equipment**

```
a) Main Gauche (1d5) (+0,+0)
b) Short Bow (x2) (+0,+0)
f) Wooden Torch (453 turns)
g) Robe [2,+5]
i) Cloak [1,+0]
m) Wicker Shield [2,+4]
o) Set of Leather Gloves [1,+0]
p) Pair of Leather Sandals [1,+0]
```

**Character Quiver**

```
a) 40 Arrows (1d4) (+0,+0)
b) 27 Arrows (1d4) (+0,+0)
```

**Character Inventory**

```
a) 2 Books of Nature Magics [Lesser Charms]
b) Handful of Dried Fruits
c) 7 Rations of Food
d) 17 Pints of Fine Wine
e) 6 Potions of Boldness
f) 3 Scrolls titled "ocor fauto sus"
g) 2 Wooden Torches (5000 turns)
```

**Home Inventory (page 1)**

```
a) a Handful of Dried Fruits
b) a Flask of oil
c) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
8271 42624 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
8363 43494 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
8542 44992 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
8871 46736 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
9002 47956 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
9145 49336 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
9385 51106 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
9491 51896 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
```

### Last 25 game messages

```
10574 55445 82 You have found 55 gold pieces worth of copper.
10580 55445 0 Target Selected.
10586 55445 0 Target Selected.
10590 55445 85 Your Arrow (1d4) (+0,+0) hits the white jelly.
10590 55445 0 You have 70 Arrows (1d4) (+0,+0) (1st 0).
10591 55445 0 The white jelly squelches.
10597 55454 0 Target Selected.
10603 55454 0 Target Selected.
10607 55454 85 Your Arrow (1d4) (+0,+0) hits the white jelly.
10607 55454 0 You have 69 Arrows (1d4) (+0,+0) (1st 0).
10608 55454 0 The Arrow breaks.
10608 55454 0 The white jelly squelches.
10615 55463 0 Target Selected.
10621 55463 0 Target Selected.
10625 55463 85 Your Arrow (1d4) (+0,+0) hits the white jelly.
10625 55463 0 You have 68 Arrows (1d4) (+0,+0) (1st 0).
10626 55463 0 The white jelly squelches.
10632 55472 0 Target Selected.
10638 55472 0 Target Selected.
10642 55472 85 Your Arrow (1d4) (+0,+0) hits the white jelly.
10642 55472 0 You have 67 Arrows (1d4) (+0,+0) (1st 0).
10643 55472 0 The Arrow breaks.
10643 55472 0 The white jelly jerks limply.
10644 55480 8 You die.
10645 55480 0 Score not registered for borgs.
```

### Last 25 Borg notes

```
10610 55463 0 # PAIN:The white jelly (+)
10610 55463 0 # Tracking a monster 'white icky thing' at (33,96) from (34,95)
10610 55463 0 # Creating an object '& Arrow~' at (90,37)
10610 55463 0 # PAIN:The white jelly (2)
10610 55463 0 # Scary guy on level.
10610 55463 0 # Fleeing and leaving the level. (scaryguy)
10610 55463 0 # Adjacent to monster on Scaryguy Level.
10610 55463 0 # Performing attack type 3 with raw utility 4 and weighted utility 8.
10610 55463 0 # Targeting white jelly who has 13 Hit Points (37,90).
10610 55463 0 # Targeting white jelly who has 13 Hit Points (37,90).
10610 55463 0 # Firing missile 'Arrows (1d4) (+0,+0)'
10627 55472 0 # PAIN:The white jelly (+)
10627 55472 0 # Creating an object '& Arrow~' at (90,37)
10627 55472 0 # PAIN:The white jelly (2)
10627 55472 0 # There was a monster 'white icky thing' at (33,96)
10627 55472 0 # Forgetting a monster 'white icky thing' at (33,96)
10627 55472 0 # Scary guy on level.
10627 55472 0 # Fleeing and leaving the level. (scaryguy)
10627 55472 0 # Adjacent to monster on Scaryguy Level.
10627 55472 0 # Performing attack type 3 with raw utility 4 and weighted utility 8.
10627 55472 0 # Targeting white jelly who has 7 Hit Points (37,90).
10627 55472 0 # Targeting white jelly who has 7 Hit Points (37,90).
10627 55472 0 # Firing missile 'Arrows (1d4) (+0,+0)'
10645 55480 0 # Aborting (death).
10645 55480 0 # Aborting (player died).
```

<a id="mage-1263833284-b139f8f5"></a>
## Mage Half-Orc 1263833284: poison

- Dies in: `reborn-shipped-defaults`, the same game (play `b139f8f585b31618`).
- Same start elsewhere: none.
- Last state line: `35800 117,22 d1/1 hp-1/30 sp0/7 f6529 au36 xp69 lv4 t3:3,7:8 o2:3389,6:3890 p635d1f29a4bd9f1a e9c5af7be54bbe5e6 r08ee9afe362a4c74`

- Cure potions quaffed: 11; Phase Door read: 2; Unknown potions quaffed: 0; Healing (outmatched) notes: 3; Potion of Speed quaffed: 0; Failed teleports: 0; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Half-Orc Mage, Level 4/4
Exp: 169  Gold: 36  Turn: 35800
Killed on level: 1 (max. 1) by poison
```

**Character Equipment**

```
a) Rapier (1d6) (+0,+0)
b) Sling (x2) (+4,+5)
f) Wooden Torch (3890 turns)
i) Cloak [1,+0]
```

**Character Inventory**

```
a) Book of Magic Spells [First Spells]
b) 5 Rations of Food
c) 13 Pints of Fine Wine
d) 5 Potions of Boldness
e) 2 Indigo Potions
f) Scroll of Light
g) Wooden Torch (3389 turns)
```

**Home Inventory (page 1)**

```
a) 6 Flasks of oil
b) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
1164 10132 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1355 11642 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1403 13062 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1624 14642 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1762 16882 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2013 20603 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2283 22854 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3360 34488 0 # Trip: descend via search (plan 2): below-plan(1 < 2)
```

### Last 25 game messages

```
3708 35658 6 You have destroyed the white worm mass.
3710 35670 44 The white worm mass crawls on you.
3710 35670 56 You are more poisoned!
3713 35678 2 You hit the white worm mass.
3716 35688 2 You hit the white worm mass.
3719 35698 2 You hit the white worm mass.
3719 35698 6 You have destroyed the white worm mass.
3722 35708 2 You hit the white worm mass.
3722 35710 53 You are no longer poisoned.
3725 35718 2 You hit the white worm mass.
3728 35728 2 You hit the white worm mass.
3728 35728 6 You have destroyed the white worm mass.
3732 35748 2 You hit the white worm mass.
3735 35758 2 You hit the white worm mass.
3739 35778 2 You hit the white worm mass.
3739 35780 44 The white worm mass crawls on you.
3739 35780 56 You are poisoned!
3744 35788 0 You do not have enough mana to cast this spell.
3746 35788 0 You faint from the effort!
3746 35788 58 You are paralysed!
3746 35788 0 You have damaged your health!
3747 35791 44 The white worm mass crawls on you.
3747 35791 56 You are more poisoned!
3748 35800 8 You die.
3749 35800 0 Score not registered for borgs.
```

### Last 25 Borg notes

```
3736 35768 0 # Fleeing and leaving the level. Brave Thinking.
3736 35768 0 # heading down (bored and spastic).
3736 35768 0 # Flowing toward spastic at cost 0
3736 35768 0 # Boosting bravery (2) from 5 to 124!
3736 35768 0 # Flowing toward up-stairs at cost 44
3736 35768 0 # Looking for stairs. Goal_less, brave.
3737 35778 0 # Creating a monster 'white worm mass' at (22,104), HP: 10, Index: 26
3737 35778 0 # Removing Regional Fear (22,104) because of a LOS white worm mass
3737 35778 0 # Scary guy on level.
3737 35778 0 # Loc:22,107 Dep:1 Lev:4 HP:5/31 SP:0/7 Danger:p=42
3737 35778 0 # Fleeing and leaving the level. (scaryguy)
3737 35778 0 # Performing attack type 1 with value 33.
3737 35778 0 # Facing white worm mass at (22,106) who has 4 Hit Points.
3737 35778 0 # Attacking with weapon 'Rapier (1d6) (+0,+0)'
3741 35788 0 # HIT:the white worm mass (+)
3741 35788 0 # HIT_BY:The white worm mass (+)
3741 35788 0 # HIT:the white worm mass (2)
3741 35788 0 # HIT_BY:The white worm mass (3)
3741 35788 0 # Scary guy on level.
3741 35788 0 # Loc:22,107 Dep:1 Lev:4 HP:2/31 SP:0/7 Danger:p=42
3741 35788 0 # Fleeing and leaving the level. (scaryguy)
3741 35788 0 # Casting Phase Door (0,3).
3741 35788 0 # Danger Level 1.3  Critical Attempt
3749 35800 0 # Aborting (death).
3749 35800 0 # Aborting (player died).
```

<a id="rogue-1496887118-409b6148"></a>
## Rogue Gnome 1496887118: poison

- Dies in: `reborn-shipped-defaults`, the same game (play `409b61484245dc8d`).
- Same start elsewhere: none.
- Last state line: `6110 21,9 d0/2 hp-1/12 sp0/0 f8689 au25 xp6 lv1 t7:5 o1:4858 pd450d829f817d81b e5a6e5d2d4e7c9fc8 r08ee9afe362a4c74`

- Cure potions quaffed: 3; Phase Door read: 0; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 0; Failed teleports: 0; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Gnome Rogue, Level 1/1
Exp: 206  Gold: 25  Turn: 6110
Killed on level: 0 (max. 2) by poison
```

**Character Equipment**

```
a) Dagger (1d4) (+0,+0) {cursed}
f) Wooden Torch (4858 turns)
g) Soft Leather Armour [8,+0]
m) Wicker Shield [2,+0]
```

**Character Inventory**

```
a) 5 Rations of Food
b) 4 Pints of Fine Wine
c) 9 Flasks of oil
d) 3 Potions of Boldness
e) 2 Scrolls of Phase Door
```

**Home Inventory (page 1)**

```
a) a Scroll of Blessing
b) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
693 3769 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
818 4338 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 25 game messages

```
1027 5661 0 This seems a quiet, peaceful place.
1029 5661 78 You enter a maze of up staircases.
1032 5661 29 You enter a maze of down staircases.
1033 5661 0 This seems a tame, sheltered place.
1035 5661 78 You enter a maze of up staircases.
1038 5661 29 You enter a maze of down staircases.
1039 5661 0 This seems a quiet, peaceful place.
1041 5661 78 You enter a maze of up staircases.
1044 5661 29 You enter a maze of down staircases.
1045 5661 0 This seems a tame, sheltered place.
1047 5661 78 You enter a maze of up staircases.
1050 5661 29 You enter a maze of down staircases.
1051 5661 0 This seems a tame, sheltered place.
1053 5661 78 You enter a maze of up staircases.
1059 5681 0 You feel much better.
1059 5681 0 You have 2 Potions of Cure Light Wounds (d).
1065 5721 0 You feel much better.
1065 5721 0 You have a Potion of Cure Light Wounds (d).
1071 5761 0 You feel much better.
1071 5761 0 You have no more Potions of Cure Light Wounds (d).
1071 5770 53 You are no longer poisoned.
1080 5871 0 You drop a Scroll of Blessing (f).
1093 5980 56 You are poisoned!
1107 6110 8 You die.
1108 6110 0 Score not registered for borgs.
```

### Last 25 Borg notes

```
1069 5761 0 # Quaffing Potion of Cure Light Wounds.
1069 5761 0 # Healing Level 1.
1073 5771 0 # Resting to recover HP/SP...
1076 5861 0 # Flowing toward Home at cost 2
1077 5871 0 # Entering a '7' shop
1078 5871 0 # Town plan executing action 5 at shop 7 slot 5
1078 5871 0 # Selling Scroll of Blessing
1083 5881 0 # Flowing toward Alchemy Shop at cost 40
1090 5951 0 # There was a monster 'village idiot' at (10,28)
1091 5961 0 # There was a monster 'village idiot' at (10,28)
1094 5981 0 # Flowing toward Alchemy Shop at cost 30
1095 5991 0 # Flowing toward Alchemy Shop at cost 29
1096 6001 0 # Flowing toward Alchemy Shop at cost 28
1097 6011 0 # Flowing toward Alchemy Shop at cost 27
1098 6021 0 # Flowing toward Alchemy Shop at cost 26
1099 6031 0 # Flowing toward Alchemy Shop at cost 25
1100 6041 0 # Flowing toward Alchemy Shop at cost 24
1101 6051 0 # Flowing toward Alchemy Shop at cost 23
1102 6061 0 # Flowing toward Alchemy Shop at cost 22
1103 6071 0 # Flowing toward Alchemy Shop at cost 21
1104 6081 0 # Flowing toward Alchemy Shop at cost 20
1105 6091 0 # Flowing toward Alchemy Shop at cost 19
1106 6101 0 # Flowing toward Alchemy Shop at cost 18
1108 6110 0 # Aborting (death).
1108 6110 0 # Aborting (player died).
```

<a id="warrior-1597870353-020c8e41"></a>
## Warrior Dwarf 1597870353: a giant white louse

- Dies in: `reborn-shipped-defaults`, the same game (play `020c8e41bcee030a`).
- Same start elsewhere: none.
- Last state line: `89887 107,9 d3/3 hp-1/145 sp0/0 f3019 au1276 xp677 lv11 t- o4:5000,5:1846 pb485c81a588f8a15 e0bf3576db0169ce0 r08ee9afe362a4c74`

- Cure potions quaffed: 21; Phase Door read: 10; Unknown potions quaffed: 0; Healing (outmatched) notes: 9; Potion of Speed quaffed: 0; Failed teleports: 0; Trip returns: 8; Trip returns followed by "going down": 4.

### Worn and carried at death

```
Borg the Dwarf Warrior, Level 11/11
Exp: 977  Gold: 1276  Turn: 89887
Killed on level: 3 (max. 3) by a giant white louse
```

**Character Equipment**

```
a) Dagger (1d4) (+1,+0)
c) Ring of Feather Falling
f) Wooden Torch (1846 turns)
g) Soft Leather Armour [8,+0]
i) Cloak [1,+0]
m) Wicker Shield [2,+0]
n) Hard Leather Cap [2,+0]
o) Set of Leather Gloves [1,+2]
p) Pair of Leather Boots [2,+0]
```

**Character Inventory**

```
a) 5 Rations of Food
b) 23 Pints of Fine Wine
c) 7 Potions of Boldness
d) Rusty Wand
e) 3 Wooden Torches (5000 turns)
f) Shovel (1d2) (+0,+0)
```

**Home Inventory (page 1)**

```
a) 2 Apples
b) 2 Handfuls of Dried Fruits
c) a Potion of Cure Serious Wounds
d) a Potion of Berserk Strength
e) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
9350 66931 0 # Trip: descend via stairs (plan 4): below-plan(1 < 4)
9528 68326 0 # Trip: descend via search (plan 4): below-plan(1 < 4)
9696 69464 0 # Trip: descend via stairs (plan 4): below-plan(1 < 4)
9736 69834 0 # Trip: descend via search (plan 4): below-plan(2 < 4)
10332 75066 0 # Trip: descend via stairs (plan 4): below-plan(1 < 4)
10533 76977 0 # Trip: descend via stairs (plan 4): below-plan(2 < 4)
10878 79667 0 # Trip: descend via search (plan 4): below-plan(3 < 4)
16767 89500 0 # Trip: ascend via stairs (plan 2): unprepared(depth 3 > prepared 2)
```

### Last 25 game messages

```
17037 89855 6 You have slain the giant white louse.
17040 89858 2 You hit the giant white louse.
17040 89858 6 You have slain the giant white louse.
17043 89860 2 You hit the giant white louse.
17043 89860 6 You have slain the giant white louse.
17045 89870 39 The giant white louse bites you.
17045 89872 39 The giant white louse bites you.
17048 89873 3 You miss the giant white louse.
17048 89873 2 You hit the giant white louse.
17048 89873 6 You have slain the giant white louse.
17052 89878 2 You hit the giant white louse.
17052 89878 6 You have slain the giant white louse.
17052 89881 39 The giant white louse bites you.
17056 89881 2 You hit the giant white louse.
17056 89881 6 You have slain the giant white louse.
17056 89882 39 The giant white louse bites you.
17060 89884 2 You hit the giant white louse.
17060 89884 6 You have slain the giant white louse.
17060 89886 39 The giant white louse bites you.
17064 89887 3 You miss the giant white louse.
17064 89887 2 You hit the giant white louse.
17064 89887 6 You have slain the giant white louse.
17065 89887 39 The giant white louse bites you.
17065 89887 8 You die.
17067 89887 0 Score not registered for borgs.
```

### Last 25 Borg notes

```
17062 89887 0 # Tracking a monster 'giant white louse' at (10,105) from (11,106)
17062 89887 0 # Tracking a monster 'giant white louse' at (13,105) from (14,105)
17062 89887 0 # Tracking a monster 'giant white louse' at (10,103) from (9,102)
17062 89887 0 # Tracking a monster 'giant white louse' at (10,102) from (11,103)
17062 89887 0 # Tracking a monster 'giant white louse' at (10,101) from (9,100)
17062 89887 0 # Tracking a monster 'giant white louse' at (10,100) from (9,101)
17062 89887 0 # Tracking a monster 'giant white louse' at (15,105) from (15,106)
17062 89887 0 # Tracking a monster 'giant white louse' at (11,106) from (12,106)
17062 89887 0 # Tracking a monster 'giant white louse' at (9,98) from (9,99)
17062 89887 0 # Tracking a monster 'giant white louse' at (14,94) from (14,93)
17062 89887 0 # Creating an object 'Phase Door' at (107,11)
17062 89887 0 # Creating a monster 'giant white louse' at (13,92), HP: 1, Index: 57
17062 89887 0 # Removing Regional Fear (13,92) because of a LOS giant white louse
17062 89887 0 # HIT:the giant white louse (2)
17062 89887 0 # KILL:the giant white louse (2)
17062 89887 0 # HIT_BY:The giant white louse (3)
17062 89887 0 # Possibility of being surrounded (monsters/safegrids)(11/1)
17062 89887 0 # Scary guy on level.
17062 89887 0 # Loc:9,107 Dep:3 Lev:11 HP:0/145 SP:0/0 Danger:p=21
17062 89887 0 # Fleeing and leaving the level. (scaryguy)
17062 89887 0 # Performing attack type 1 with raw utility 11 and weighted utility 19.
17062 89887 0 # Facing giant white louse at (10,106) who has 1 Hit Points.
17062 89887 0 # Attacking with weapon 'Dagger (1d4) (+1,+0)'
17067 89887 0 # Aborting (death).
17067 89887 0 # Aborting (player died).
```

<a id="blackguard-1672393740-fdf78440"></a>
## Blackguard Gnome 1672393740: poison

- Dies in: `reborn-shipped-defaults`, the same game (play `fdf784400742bbde`).
- Same start elsewhere: none.
- Last state line: `11520 136,11 d1/1 hp-1/25 sp3/4 f8149 au18 xp50 lv3 t7:7 o4:4121 p37da6cad4a933a8b e41446351dfc3bd2b r08ee9afe362a4c74`

- Cure potions quaffed: 3; Phase Door read: 1; Unknown potions quaffed: 0; Healing (outmatched) notes: 1; Potion of Speed quaffed: 0; Failed teleports: 1; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Gnome Blackguard, Level 3/3
Exp: 150  Gold: 18  Turn: 11520
Killed on level: 1 (max. 1) by poison
```

**Character Equipment**

```
a) Tulwar (2d4) (+0,+0)
f) Wooden Torch (4121 turns)
m) Leather Shield [8,+0]
```

**Character Inventory**

```
a) Necromantic Tome [Into the Shadows]
b) 5 Rations of Food
c) 3 Potions of Boldness
```

**Home Inventory (page 1)**

```
a) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
794 3922 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
930 4896 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
984 5366 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1050 5846 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1120 6486 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1262 7487 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1440 8917 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1673 10921 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 25 game messages

```
1719 11225 0 You have a Potion of Cure Light Wounds (c).
1719 11228 0 The yellow jelly drains your mana away.
1720 11228 0 The yellow jelly appears healthier.
1721 11233 35 The yellow jelly touches you.
1721 11233 56 You are more poisoned!
1725 11235 2 You hit the yellow jelly.
1725 11239 35 The yellow jelly touches you.
1725 11239 56 You are more poisoned!
1729 11244 2 You hit the yellow jelly.
1729 11244 0 The yellow jelly misses you.
1729 11250 35 The yellow jelly touches you.
1730 11250 56 You are more poisoned!
1733 11252 2 You hit the yellow jelly.
1733 11255 35 The yellow jelly touches you.
1733 11255 56 You are more poisoned!
1734 11261 35 The yellow jelly touches you.
1734 11261 56 You are more poisoned!
1738 11261 2 You get in a shield bash!
1738 11261 2 You hit the yellow jelly.
1738 11261 0 The yellow jelly is stunned.
1739 11261 6 You have destroyed the yellow jelly.
1742 11269 0 You feel much better.
1742 11269 0 You have no more Potions of Cure Light Wounds (c).
1768 11520 8 You die.
1769 11520 0 Score not registered for borgs.
```

### Last 25 Borg notes

```
1760 11449 0 # Fleeing and leaving the level (Looking for Up Stair).
1760 11449 0 # Flowing toward dark-3 at cost 3
1761 11459 0 # Fleeing and leaving the level. (Looking for any stair)
1761 11459 0 # Fleeing and leaving the level (Looking for Up Stair).
1761 11459 0 # Flowing toward dark-3 at cost 2
1762 11469 0 # Fleeing and leaving the level. (Looking for any stair)
1762 11469 0 # Fleeing and leaving the level (Looking for Up Stair).
1762 11469 0 # Flowing toward dark-3 at cost 2
1763 11479 0 # Fleeing and leaving the level. (Looking for any stair)
1763 11479 0 # Fleeing and leaving the level (Looking for Up Stair).
1763 11479 0 # Flowing toward dark-3 at cost 2
1764 11489 0 # Fleeing and leaving the level. (Looking for any stair)
1764 11489 0 # Fleeing and leaving the level (Looking for Up Stair).
1764 11489 0 # Flowing toward dark-3 at cost 2
1765 11499 0 # Fleeing and leaving the level. (Looking for any stair)
1765 11499 0 # Fleeing and leaving the level (Looking for Up Stair).
1765 11499 0 # Flowing toward dark-4 at cost 6
1766 11509 0 # Fleeing and leaving the level. (Looking for any stair)
1766 11509 0 # Fleeing and leaving the level (Looking for Up Stair).
1766 11509 0 # Flowing toward dark-3 at cost 5
1767 11519 0 # Fleeing and leaving the level. (Looking for any stair)
1767 11519 0 # Fleeing and leaving the level (Looking for Up Stair).
1767 11519 0 # Flowing toward dark-3 at cost 4
1769 11520 0 # Aborting (death).
1769 11520 0 # Aborting (player died).
```

<a id="mage-1946087915-7e4b7479"></a>
## Mage Human 1946087915: a salamander

- Dies in: `reborn-shipped-defaults`, the same game (play `7e4b7479707a8f67`).
- Same start elsewhere: none.
- Last state line: `7299 19,9 d1/1 hp-1/10 sp0/2 f8679 au29 xp9 lv1 t- o2:4792,6:5000 pf4b986fc31bf281b ef229f96d20a8c3a0 r08ee9afe362a4c74`

- Cure potions quaffed: 4; Phase Door read: 2; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 0; Failed teleports: 2; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Human Mage, Level 1/1
Exp: 109  Gold: 29  Turn: 7299
Killed on level: 1 (max. 1) by a salamander
```

**Character Equipment**

```
a) Rapier (1d6) (+0,+0)
f) Wooden Torch (4792 turns)
```

**Character Inventory**

```
a) Book of Magic Spells [First Spells]
b) 5 Rations of Food
c) 12 Pints of Fine Wine
d) 14 Flasks of oil
e) Wooden Torch (5000 turns)
```

**Home Inventory (page 1)**

```
a) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
938 5501 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 25 game messages

```
1152 7241 0 You have a Potion of Cure Light Wounds (e).
1152 7243 0 You are enveloped in flames!
1153 7243 39 The salamander bites you.
1153 7244 0 You are covered with frost!
1154 7244 40 The giant white centipede stings you.
1157 7251 0 You feel much better.
1157 7251 0 You have no more Potions of Cure Light Wounds (e).
1157 7253 44 The giant white centipede crawls on you.
1158 7253 0 You are covered with frost!
1159 7253 40 The giant white centipede stings you.
1159 7254 0 You are enveloped in flames!
1160 7254 39 The salamander bites you.
1163 7261 3 You miss the salamander.
1166 7271 3 You miss the salamander.
1169 7281 3 You miss the salamander.
1169 7288 0 You are enveloped in flames!
1169 7288 39 The salamander bites you.
1170 7290 44 The giant white centipede crawls on you.
1170 7290 0 You are covered with frost!
1171 7290 40 The giant white centipede stings you.
1174 7291 3 You miss the salamander.
1174 7299 0 You are enveloped in flames!
1174 7299 39 The salamander bites you.
1175 7299 8 You die.
1176 7299 0 Score not registered for borgs.
```

### Last 25 Borg notes

```
1164 7271 0 # Performing attack type 1 with value 19.
1164 7271 0 # Facing salamander at (10,19) who has 11 Hit Points.
1164 7271 0 # Attacking with weapon 'Rapier (1d6) (+0,+0)'
1167 7281 0 # MISS:the salamander (+)
1167 7281 0 # Tracking a monster 'salamander' at (10,20) from (10,19)
1167 7281 0 # Tracking a monster 'giant white centipede' at (10,19) from (9,18)
1167 7281 0 # MISS:the salamander (2)
1167 7281 0 # Loc:9,19 Dep:1 Lev:1 HP:6/10 SP:0/2 Danger:p=26
1167 7281 0 # Performing attack type 1 with value 19.
1167 7281 0 # Facing salamander at (10,20) who has 11 Hit Points.
1167 7281 0 # Attacking with weapon 'Rapier (1d6) (+0,+0)'
1172 7291 0 # MISS:the salamander (+)
1172 7291 0 # HIT_BY:The salamander (+)
1172 7291 0 # HIT_BY:The giant white centipede (+)
1172 7291 0 # HIT_BY:The giant white centipede (+)
1172 7291 0 # MISS:the salamander (2)
1172 7291 0 # HIT_BY:The salamander (3)
1172 7291 0 # HIT_BY:The giant white centipede (3)
1172 7291 0 # HIT_BY:The giant white centipede (3)
1172 7291 0 # Loc:9,19 Dep:1 Lev:1 HP:1/10 SP:0/2 Danger:p=26
1172 7291 0 # Performing attack type 1 with value 19.
1172 7291 0 # Facing salamander at (10,20) who has 11 Hit Points.
1172 7291 0 # Attacking with weapon 'Rapier (1d6) (+0,+0)'
1176 7299 0 # Aborting (death).
1176 7299 0 # Aborting (player died).
```

<a id="blackguard-1981269294-a27f2412"></a>
## Blackguard Hobbit 1981269294: a cave spider

- Dies in: `reborn-shipped-defaults`, the same game (play `a27f2412314d1229`).
- Same start elsewhere: none.
- Last state line: `86576 159,41 d2/2 hp-2/46 sp5/5 f2149 au0 xp78 lv4 t- o2:3952,5:2879,12:5000 pb160554671375664 e32c2603e93dfb863 r08ee9afe362a4c74`

- Cure potions quaffed: 6; Phase Door read: 5; Unknown potions quaffed: 0; Healing (outmatched) notes: 5; Potion of Speed quaffed: 0; Failed teleports: 0; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Hobbit Blackguard, Level 4/4
Exp: 278  Gold: 0  Turn: 86576
Killed on level: 2 (max. 2) by a cave spider
```

**Character Equipment**

```
a) Tulwar (2d4) (+0,+0)
f) Wooden Torch (3952 turns)
m) Leather Shield [8,-1]
```

**Character Inventory**

```
a) 2 Necromantic Tomes [Into the Shadows]
b) Handful of Dried Fruits
c) 5 Rations of Food
d) 4 Pints of Fine Wine
e) Potion of Neutralize Poison
f) 3 Potions of Boldness
g) 4 Gold Potions
i) Wooden Torch (2879 turns)
m) Wooden Torch (5000 turns)
n) Dagger (1d4) (+0,+0)
```

**Home Inventory (page 1)**

```
a) 3 Scrolls of Blessing
b) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
3113 20894 0 # Trip: descend via search (plan 2): below-plan(1 < 2)
3300 22424 0 # Trip: descend via search (plan 2): below-plan(1 < 2)
3660 26111 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
3968 28785 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
4093 29989 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
4620 76435 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
4941 79364 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
5452 85754 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
```

### Last 25 game messages

```
5631 86562 39 The cave spider bites you.
5635 86563 2 You hit the metallic green centipede.
5635 86563 4 The metallic green centipede flees in terror!
5636 86566 39 The cave spider bites you.
5636 86566 39 The cave spider bites you.
5637 86568 139 The shrieker mushroom patch (offscreen) makes a high-pitched shriek.
5638 86568 0 2 cave spiders look even faster!
5639 86568 0 The metallic green centipede starts moving faster.
5640 86568 0 The yellow mushroom patch (offscreen) looks even faster!
5641 86568 0 The metallic green centipede looks even faster!
5642 86568 0 The giant white mouse (offscreen) looks even faster!
5643 86568 0 The giant white mouse (offscreen) starts moving faster.
5644 86568 0 The giant white mouse starts moving faster.
5645 86569 39 The cave spider bites you.
5645 86570 0 The cave spider misses you.
5649 86571 2 You hit the cave spider.
5649 86571 4 The cave spider flees in terror!
5649 86572 39 The cave spider bites you.
5650 86576 44 The metallic green centipede crawls on you.
5650 86576 0 You are covered in acid!
5651 86576 0 Your Leather Shield is damaged!
5651 86576 40 The metallic green centipede stings you.
5652 86576 39 The cave spider bites you.
5652 86576 8 You die.
5654 86576 0 Score not registered for borgs.
```

### Last 25 Borg notes

```
5647 86571 0 # QUAKE:Somebody (0)
5647 86571 0 # SPELL_001:The shrieker mushroom patch (offscreen) (5)
5647 86571 0 # PAIN:2 cave spiders (0)
5647 86571 0 # PAIN:The metallic green centipede (2)
5647 86571 0 # PAIN:The yellow mushroom patch (offscreen) (0)
5647 86571 0 # PAIN:The metallic green centipede (2)
5647 86571 0 # PAIN:The giant white mouse (offscreen) (0)
5647 86571 0 # PAIN:The giant white mouse (offscreen) (0)
5647 86571 0 # PAIN:The giant white mouse (2)
5647 86571 0 # QUAKE:Somebody (0)
5647 86571 0 # QUAKE:Somebody (0)
5647 86571 0 # There was a monster 'giant white mouse' at (41,167)
5647 86571 0 # Forgetting a monster 'giant white mouse' at (41,167)
5647 86571 0 # Possibility of being surrounded (monsters/safegrids)(4/3)
5647 86571 0 # Scary guy on level.
5647 86571 0 # Loc:41,159 Dep:2 Lev:4 HP:8/46 SP:4/5 Danger:p=401
5647 86571 0 # Fleeing and leaving the level. (scaryguy)
5647 86571 0 # Adjacent to monster on Scaryguy Level.
5647 86571 0 # Adjacent to monster on Scaryguy Level.
5647 86571 0 # Adjacent to monster on Scaryguy Level.
5647 86571 0 # Performing attack type 1 with raw utility 49 and weighted utility 78.
5647 86571 0 # Facing cave spider at (42,158) who has 8 Hit Points.
5647 86571 0 # Attacking with weapon 'Tulwar (2d4) (+0,+0)'
5654 86576 0 # Aborting (death).
5654 86576 0 # Aborting (player died).
```

<a id="mage-2017596150-1ebce90d"></a>
## Mage Dunadan 2017596150: a crow

- Dies in: `reborn-shipped-defaults`, the same game (play `1ebce90db5a95802`).
- Same start elsewhere: none.
- Last state line: `13332 132,40 d1/1 hp-1/11 sp2/2 f7869 au21 xp5 lv1 t8:5 o2:4570,7:5000 pb3c7d5f3cb55c449 ecf071c0655f9675b r08ee9afe362a4c74`

- Cure potions quaffed: 2; Phase Door read: 2; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 0; Failed teleports: 1; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Dunadan Mage, Level 1/1
Exp: 105  Gold: 21  Turn: 13332
Killed on level: 1 (max. 1) by a crow
```

**Character Equipment**

```
a) Rapier (1d6) (+0,+0)
f) Wooden Torch (4570 turns)
m) Leather Shield [8,+0]
```

**Character Inventory**

```
a) Book of Magic Spells [First Spells]
b) 5 Rations of Food
c) 15 Flasks of oil
d) 2 Potions of Cure Light Wounds
e) 3 Potions of Boldness
f) Wooden Torch (5000 turns)
```

**Home Inventory (page 1)**

```
a) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
658 5111 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
744 6531 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
912 8332 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1273 11422 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1312 11752 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1376 12253 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1482 13184 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 25 game messages

```
1438 12844 125 You are wearing a Leather Shield [8,+0] (m).
1462 13074 78 You enter a maze of up staircases.
1465 13074 29 You enter a maze of down staircases.
1466 13074 0 This seems a tame, sheltered place.
1481 13174 0 You have a Scroll of Phase Door (f).
1487 13232 39 The crow bites you.
1487 13232 39 The crow bites you.
1492 13234 0 You have no more Scrolls of Phase Door (f).
1497 13244 0 The air about you becomes charged...
1497 13244 0 You have no more Scrolls of Word of Recall (f).
1511 13314 0 You feel much better.
1511 13314 0 You have 2 Potions of Cure Light Wounds (d).
1511 13316 39 The crow bites you.
1512 13316 39 The crow bites you.
1512 13321 39 The crow bites you.
1512 13321 39 The crow bites you.
1516 13324 0 You feel much better.
1516 13324 0 You have a Potion of Cure Light Wounds (d).
1516 13327 39 The crow bites you.
1517 13327 39 The crow bites you.
1517 13327 77 You have been given a graze.
1517 13332 39 The crow bites you.
1518 13332 39 The crow bites you.
1518 13332 8 You die.
1519 13332 0 Score not registered for borgs.
```

### Last 25 Borg notes

```
1488 13234 0 # Reading Scroll of Phase Door.
1488 13234 0 # Danger Level 1.
1493 13244 0 # Reading Scroll of Word of Recall.
1493 13244 0 # Fleeing the level (recall)
1500 13254 0 # Flowing toward up-stairs at cost 8
1500 13254 0 # Looking for stairs. Goal_less, Fleeing.
1504 13294 0 # Resting for Recall.
1509 13314 0 # Tracking a monster 'crow' at (40,133) from (43,137)
1509 13314 0 # Loc:40,132 Dep:1 Lev:1 HP:7/11 SP:2/2 Danger:p=18
1509 13314 0 # Leaving (failed to teleport)
1509 13314 0 # Quaffing Potions of Cure Light Wounds.
1509 13314 0 # Buying time waiting for Recall.(3)
1514 13324 0 # HIT_BY:The crow (+)
1514 13324 0 # HIT_BY:The crow (+)
1514 13324 0 # HIT_BY:The crow (+)
1514 13324 0 # HIT_BY:The crow (+)
1514 13324 0 # HIT_BY:The crow (3)
1514 13324 0 # HIT_BY:The crow (3)
1514 13324 0 # HIT_BY:The crow (3)
1514 13324 0 # HIT_BY:The crow (3)
1514 13324 0 # Loc:40,132 Dep:1 Lev:1 HP:5/11 SP:2/2 Danger:p=18
1514 13324 0 # Quaffing Potions of Cure Light Wounds.
1514 13324 0 # Buying time waiting for Recall.(3)
1519 13332 0 # Aborting (death).
1519 13332 0 # Aborting (player died).
```

<a id="ranger-2107852048-7ff5c21d"></a>
## Ranger Elf 2107852048: Grip, Farmer Maggot's Dog

- Dies in: `reborn-shipped-defaults`, the same game (play `7ff5c21df8e1f085`).
- Same start elsewhere: none.
- Last state line: `276 183,30 d1/1 hp-1/14 sp0/0 f8979 au130 xp0 lv1 t- o5:4991,7:5000,9:5000 pf9fe9c0da5792bf5 e3a07bce3466c0eb2 r08ee9afe362a4c74`

- Cure potions quaffed: 0; Phase Door read: 0; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 0; Failed teleports: 0; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Elf Ranger, Level 1/1
Exp: 100  Gold: 130  Turn: 276
Killed on level: 1 (max. 1) by Grip, Farmer Maggot's Dog
```

**Character Equipment**

```
a) Main Gauche (1d5) (+0,+0)
b) Short Bow (x2) (+0,+0)
f) Wooden Torch (4991 turns)
```

**Character Quiver**

```
a) 15 Arrows (1d4) (+0,+0)
```

**Character Inventory**

```
a) Book of Nature Magics [Lesser Charms]
b) Ration of Food
c) 5 Muddy Potions
d) Scroll of Word of Recall
e) Scroll titled "opolevus ubi"
f) Wooden Torch (5000 turns)
g) Wooden Torch (5000 turns) {??}
```

### Last 25 game messages

```
13 121 29 You enter a maze of down staircases.
14 121 0 This seems a quiet, peaceful place.
16 121 78 You enter a maze of up staircases.
25 181 29 You enter a maze of down staircases.
26 181 0 This seems a tame, sheltered place.
29 196 39 Grip, Farmer Maggot's Dog, bites you.
29 201 39 Grip, Farmer Maggot's Dog, bites you.
30 201 0 You have a Scroll titled "opolevus ubi" (d).
33 211 39 Grip, Farmer Maggot's Dog, bites you.
35 222 0 You have a Wooden Torch (5000 turns) {??} (f).
38 243 0 You have 5 Muddy Potions (c).
44 244 0 Target Selected.
48 244 85 Your Arrow (1d4) (+0,+0) hits Grip, Farmer Maggot's Dog.
48 244 0 You have 16 Arrows (1d4) (+0,+0) (0).
49 244 0 Grip, Farmer Maggot's Dog, snarls with pain.
56 254 0 Target Selected.
60 254 85 Your Arrow (1d4) (+0,+0) hits Grip, Farmer Maggot's Dog.
60 254 0 You have 15 Arrows (1d4) (+0,+0) (0).
61 254 0 Grip, Farmer Maggot's Dog, yelps in pain.
62 261 39 Grip, Farmer Maggot's Dog, bites you.
66 264 2 You hit Grip, Farmer Maggot's Dog.
68 276 39 Grip, Farmer Maggot's Dog, bites you.
68 276 8 You die.
69 276 0 You have a Wooden Torch of Brightness (5000 turns) <+1> (g).
69 276 0 Score not registered for borgs.
```

### Last 25 Borg notes

```
39 244 0 # Performing attack type 3 with raw utility 16 and weighted utility 32.
39 244 0 # Targeting Grip, Farmer Maggot's Dog who has 25 Hit Points (31,184).
39 244 0 # Firing missile 'Arrows (1d4) (+0,+0)'
51 254 0 # PAIN:Grip, Farmer Maggot's Dog (+)
51 254 0 # Creating an object '& Arrow~' at (184,31)
51 254 0 # PAIN:Grip, Farmer Maggot's Dog (2)
51 254 0 # Fleeing level. Scumming Mode
51 254 0 # Scary guy on level.
51 254 0 # Loc:29,182 Dep:1 Lev:1 HP:6/14 SP:0/0 Danger:p=4
51 254 0 # Fleeing and leaving the level. (scaryguy)
51 254 0 # Performing attack type 3 with raw utility 16 and weighted utility 32.
51 254 0 # Targeting Grip, Farmer Maggot's Dog who has 19 Hit Points (31,184).
51 254 0 # Firing missile 'Arrows (1d4) (+0,+0)'
64 264 0 # PAIN:Grip, Farmer Maggot's Dog (+)
64 264 0 # HIT_BY:Grip, Farmer Maggot's Dog (+)
64 264 0 # Tracking a monster 'Grip, Farmer Maggot's Dog' at (30,183) from (31,184)
64 264 0 # PAIN:Grip, Farmer Maggot's Dog (2)
64 264 0 # HIT_BY:Grip, Farmer Maggot's Dog (3)
64 264 0 # Flowing toward Scum item at cost 2
64 264 0 # Walking into a 'Grip, Farmer Maggot's Dog' at (30,183)
67 273 0 # HIT:Grip, Farmer Maggot's Dog (+)
67 273 0 # Tracking a monster 'Grip, Farmer Maggot's Dog' at (29,183) from (30,183)
67 273 0 # HIT:Grip, Farmer Maggot's Dog (2)
69 276 0 # Aborting (death).
69 276 0 # Aborting (player died).
```
