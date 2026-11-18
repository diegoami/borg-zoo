# Deaths in reborn-heal-class-pilot (borg-zoo#225)

Run [44173139346](https://github.com/diegoami/borg-zoo/actions/runs/44173139346), specimen `4.2.6-reborn-rust-main-a8ac685a`. A reading aid written by `python3 -m zoo.death_report`, not a cemetery entry or a causal diagnosis.

15 deaths in 90 games, 7 distinct dying games. Replayed locally from the run's own build artifact, arms `reborn-487-ctl`, `reborn-487-heal`: every replayed play hash matches CI.

| Game | Dies in | Killed by | Char level | Dungeon level | Game turn | Keys |
|---|---|---|---|---|---|---|
| [Ranger Human 226104090](#ranger-226104090-2d2c9198) | `reborn-487-ctl`, `reborn-487-digger` | a soldier | 7 | 3 (max 3) | 54290 | 10429 |
| [Rogue Half-Elf 1381972077](#rogue-1381972077-8c4cf442) | `reborn-487-ctl`, `reborn-487-digger` | a giant white mouse | 2 | 1 (max 1) | 14193 | 1850 |
| [Blackguard Human 1472012981](#blackguard-1472012981-c0b5fd56) | `reborn-487-ctl`, `reborn-487-digger` | poison | 7 | 1 (max 3) | 43400 | 5842 |
| [Mage Human 1548306106](#mage-1548306106-15f1d78b) | `reborn-487-ctl`, `reborn-487-digger` | a giant white mouse | 4 | 1 (max 1) | 34660 | 3261 |
| [Necromancer Human 300036923](#necromancer-300036923-a1b9a3c8) | `reborn-487-heal`, `reborn-487-both`, `reborn-487-speedres` | a small kobold | 2 | 1 (max 1) | 5824 | 556 |
| [Druid Half-Elf 934061548](#druid-934061548-f53c443e) | `reborn-487-heal` | a soldier | 3 | 2 (max 2) | 35851 | 4957 |
| [Priest Human 1569794094](#priest-1569794094-5b24ad51) | `reborn-487-heal`, `reborn-487-both`, `reborn-487-speedres` | Fang, Farmer Maggot's Dog | 2 | 1 (max 1) | 8760 | 624 |

## Observations

All five arms were replayed (90 games), and every play hash matches CI. Gold is from each game's `town-transactions.jsonl`, averaged per game. Observations, not diagnoses:

| arm | deaths /18 | mean max CL | mean max DL | healing | escape | oil | ammo | armour | weapons | digger | unknown kinds | detect/map scrolls | Shovels bought | rubble removed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ctl | 4 | 5.94 | 2.50 | 166 | 70 | 57 | 32 | 29 | 25 | 44 | 271 | 85 | 12 | 57 |
| digger | 4 | 5.83 | 2.28 | 227 | 80 | 66 | 33 | 53 | 25 | 18 | 283 | 158 | 5 | 44 |
| heal | 3 | 5.78 | 2.39 | 113 | 89 | 50 | 96 | 61 | 0 | 62 | 260 | 177 | 17 | 65 |
| both (shipped) | 2 | 5.89 | 2.67 | 133 | 92 | 62 | 116 | 62 | 0 | 18 | 325 | 159 | 5 | 64 |
| speedres | 2 | 5.89 | 2.72 | 127 | 99 | 62 | 99 | 68 | 0 | 18 | 325 | 167 | 5 | 55 |

- **The shipped healing settings cut healing spend.** It falls from 166-227 to 113-133 gold per game. The gold goes to ammunition (32 → 96-116) and armour (29 → 61-68) instead.
- **The digger gate works.** Shovels bought fall from 12-17 to 5 per arm. Rubble removed doesn't fall with them (44-65 per arm).
- **No arm with the shipped healing bought a weapon.** Weapons are 0 gold per game in heal, both and speedres, against 25 in ctl and digger. That is #487's original complaint, still open.
- **The largest category in every arm is unknown kinds** (flavoured potions, staves): 260-325 gold per game.
- **Deaths:** 4, 4, 3, 2 and 2. The shipped healing changes every game. Against ctl it rescues 4 and newly kills 2-3: a Necromancer (CL2, small kobold) and a Priest (CL2, Fang) die in all three shipped-healing arms, and the Druid also dies in `heal`. `speedres` plays like `both` in outcome; the real-HP reserve changes little at this size.
- No arm's dead character carried Cure potions, except the CL2 Priest killed by Fang, with 4 left.

## Handover: working on these deaths in the Borg's repository

For a session in diegoami/borg-reborn-rs that changes parameters or code against these deaths. That repository owns the Borg; the zoo only measures, and any change is measured here later as a new specimen.

- **Build:** `diegoami/borg-reborn-rs` at `a8ac685a2c90b412971fedd90d98b783b7f70380` (zoo specimen `4.2.6-reborn-rust-main-a8ac685a`): `BORG_IMPL=rust harness/build.sh`, or the run's CI artifact: `gh run download 44173139346 -R diegoami/borg-zoo -n build-4.2.6-reborn-rust-main-a8ac685a`.
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
| [Ranger 226104090](#ranger-226104090-2d2c9198) | 226104090 | 0 (Human) | 7 | `reborn-487-ctl` | `2d2c9198d0600a64` |
| [Rogue 1381972077](#rogue-1381972077-8c4cf442) | 1381972077 | 1 (Half-Elf) | 6 | `reborn-487-ctl` | `8c4cf4426fe2b695` |
| [Blackguard 1472012981](#blackguard-1472012981-c0b5fd56) | 1472012981 | 0 (Human) | 8 | `reborn-487-ctl` | `c0b5fd569280377a` |
| [Mage 1548306106](#mage-1548306106-15f1d78b) | 1548306106 | 0 (Human) | 1 | `reborn-487-ctl` | `15f1d78bc97c44a0` |
| [Necromancer 300036923](#necromancer-300036923-a1b9a3c8) | 300036923 | 0 (Human) | 4 | `reborn-487-heal` | `a1b9a3c8834b1acc` |
| [Druid 934061548](#druid-934061548-f53c443e) | 934061548 | 1 (Half-Elf) | 2 | `reborn-487-heal` | `f53c443e0f445341` |
| [Priest 1569794094](#priest-1569794094-5b24ad51) | 1569794094 | 0 (Human) | 3 | `reborn-487-heal` | `5b24ad51bfc93d7e` |

In borg-zoo, `python3 -m zoo.death_report --experiment experiments/reborn-heal-class-pilot.json --run 44173139346` replays and checks them all. After a change: a PR in the Borg's repository, then ask the borg-zoo session for a new specimen at the merged commit and a pilot (or verysmall) of the same arms.

<a id="ranger-226104090-2d2c9198"></a>
## Ranger Human 226104090: a soldier

- Dies in: `reborn-487-ctl`, `reborn-487-digger`, the same game (play `2d2c9198d0600a64`).
- Same start elsewhere: `reborn-487-heal` turn_cap, `reborn-487-both` turn_cap, `reborn-487-speedres` turn_cap.
- Last state line: `54290 153,9 d3/3 hp-4/71 sp7/7 f5279 au184 xp175 lv7 t2:1,9:10 o5:2256,12:5000 p503493f54e6998db eb3f259212c5e8b53 r08ee9afe362a4c74`

- Cure potions quaffed: 17; Phase Door read: 10; Unknown potions quaffed: 0; Healing (outmatched) notes: 11; Potion of Speed quaffed: 0; Failed teleports: 8; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Human Ranger, Level 7/7
Exp: 475  Gold: 184  Turn: 54290
Killed on level: 3 (max. 3) by a soldier
```

**Character Equipment**

```
a) Main Gauche (1d5) (+0,+0)
b) Short Bow (x2) (+0,+0)
f) Wooden Torch (2256 turns)
g) Robe [2,+0]
i) Cloak [1,+0]
m) Wicker Shield [2,+0]
n) Hard Leather Cap [2,+0]
o) Set of Leather Gloves [1,+0]
p) Pair of Leather Sandals [1,+0]
```

**Character Quiver**

```
a) 40 Arrows (1d4) (+0,+0)
b) 11 Arrows (1d4) (+0,+0)
```

**Character Inventory**

```
a) 2 Books of Nature Magics [Lesser Charms]
b) 12 Rations of Food
c) 4 Potions of Boldness
d) 4 Scrolls titled "tendiae sus"
e) 2 Scrolls titled "lacips jus"
f) 2 Wooden Torches (5000 turns)
g) Hard Leather Cap [2,+0]
```

**Home Inventory (page 1)**

```
a) a Handful of Dried Fruits
b) a Wooden Torch (2857 turns)
c) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
7801 39730 0 # Trip: descend via stairs (plan 4): below-plan(2 < 4)
8420 42386 0 # Trip: descend via search (plan 4): below-plan(3 < 4)
8721 44674 0 # Trip: descend via stairs (plan 4): below-plan(2 < 4)
8871 45386 0 # Trip: descend via search (plan 4): below-plan(3 < 4)
9929 51314 0 # Trip: descend via stairs (plan 4): below-plan(2 < 4)
10108 52809 0 # Trip: descend via search (plan 4): below-plan(3 < 4)
10383 54164 0 # Trip: ascend via stairs (plan 2): unprepared(depth 3 > prepared 2)
10386 54172 0 # Trip: ascend via search (plan 2): unprepared(depth 3 > prepared 2)
```

### Last 30 game messages

```
10385 54164 0 Something mumbles.
10385 54164 0 You are hit by something!
10388 54172 3 You fail to harm someone.
10388 54173 34 Someone hits you.
10391 54181 3 You fail to harm someone.
10391 54182 34 Someone hits you.
10394 54189 3 You fail to harm someone.
10394 54191 34 Someone hits you.
10397 54198 3 You fail to harm someone.
10397 54200 34 Someone hits you.
10400 54206 3 You fail to harm someone.
10400 54210 34 Someone hits you.
10403 54215 3 You fail to harm someone.
10406 54223 2 You hit someone.
10406 54228 34 Someone hits you.
10409 54232 2 You hit someone.
10412 54240 2 You hit someone.
10415 54249 2 You hit someone.
10415 54250 34 Someone hits you.
10418 54257 3 You miss someone.
10418 54260 34 Someone hits you.
10421 54266 3 You miss someone.
10421 54270 34 Someone hits you.
10424 54274 2 You hit someone.
10424 54280 34 Someone hits you.
10427 54283 2 You hit someone.
10427 54290 34 Someone hits you.
10427 54290 34 Someone hits you.
10427 54290 8 You die.
10428 54290 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
10425 54283 0 # Bored but unable to flow to up stairs.
10425 54283 0 # no up stairs found, going down
10425 54283 0 # heading up, not prep for current level: 2 cure)
10425 54283 0 # heading up (bored and unable to dive: 2 cure)
10425 54283 0 # Climbing (too deep: 2 cure)
10425 54283 0 # Looking for up stairs.  Going up.
10425 54283 0 # Bored but unable to flow to up stairs.
10425 54283 0 # no up stairs found, going down
10425 54283 0 # Boosting bravery (1) from 4 to 8!
10425 54283 0 # Fleeing and leaving the level. Brave Thinking.
10425 54283 0 # heading up, not prep for current level: 2 cure)
10425 54283 0 # heading up (bored and unable to dive: 2 cure)
10425 54283 0 # Climbing (too deep: 2 cure)
10425 54283 0 # Looking for up stairs.  Going up.
10425 54283 0 # Bored but unable to flow to up stairs.
10425 54283 0 # no up stairs found, going down
10425 54283 0 # Boosting bravery (2) from 4 to 284!
10425 54283 0 # Fleeing and leaving the level. Brave Thinking.
10425 54283 0 # heading up, not prep for current level: 2 cure)
10425 54283 0 # heading up (bored and unable to dive: 2 cure)
10425 54283 0 # Climbing (too deep: 2 cure)
10425 54283 0 # Looking for up stairs.  Going up.
10425 54283 0 # Bored but unable to flow to up stairs.
10425 54283 0 # no up stairs found, going down
10425 54283 0 # Boosting bravery (3) from 4 to 30000!
10425 54283 0 # Fleeing and leaving the level. Brave Thinking.
10425 54283 0 # Flowing toward kill at cost 1
10425 54283 0 # Walking into a 'apprentice' at (8,153)
10428 54290 0 # Aborting (death).
10428 54290 0 # Aborting (player died).
```

<a id="rogue-1381972077-8c4cf442"></a>
## Rogue Half-Elf 1381972077: a giant white mouse

- Dies in: `reborn-487-ctl`, `reborn-487-digger`, the same game (play `8c4cf4426fe2b695`).
- Same start elsewhere: `reborn-487-heal` turn_cap, `reborn-487-both` turn_cap, `reborn-487-speedres` turn_cap.
- Last state line: `14193 87,16 d1/1 hp-2/17 sp0/0 f7989 au7 xp24 lv2 t- o2:3822,5:5000 pce677f6f36ad76d5 eb46fece410dfef25 r08ee9afe362a4c74`

- Cure potions quaffed: 4; Phase Door read: 2; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 0; Failed teleports: 2; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Half-Elf Rogue, Level 2/2
Exp: 124  Gold: 7  Turn: 14193
Killed on level: 1 (max. 1) by a giant white mouse
```

**Character Equipment**

```
a) Dagger (1d4) (+0,+0)
f) Wooden Torch (3822 turns)
g) Soft Leather Armour [8,+0]
```

**Character Inventory**

```
a) Book of Magic Spells [First Spells]
b) 5 Rations of Food
c) 4 Potions of Boldness
d) Scroll titled "propio"
e) Scroll titled "per prolum sus"
f) Wooden Torch (5000 turns)
```

**Home Inventory (page 1)**

```
a) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
1000 6929 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1052 7159 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1189 8259 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1318 9380 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1452 10340 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1564 11686 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1638 12366 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1691 12836 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 30 game messages

```
1795 13857 3 You miss the small kobold.
1795 13859 34 The small kobold hits you.
1799 13867 3 You miss the small kobold.
1799 13867 3 You miss the small kobold.
1799 13870 34 The small kobold hits you.
1803 13877 3 You miss the small kobold.
1803 13877 2 You hit the small kobold.
1803 13881 34 The small kobold hits you.
1807 13887 2 You hit the small kobold.
1807 13887 2 You hit the small kobold.
1807 13887 6 You have slain the small kobold.
1819 14095 39 The giant white mouse bites you.
1822 14097 2 You hit the giant white mouse.
1822 14097 6 You have slain the giant white mouse.
1827 14122 2 You hit the giant white mouse.
1827 14122 6 You have slain the giant white mouse.
1831 14137 2 You hit the giant white mouse.
1831 14137 6 You have slain the giant white mouse.
1833 14149 39 The giant white mouse bites you.
1836 14152 2 You hit the giant white mouse.
1836 14152 6 You have slain the giant white mouse.
1838 14159 39 The giant white mouse bites you.
1841 14167 2 You hit the giant white mouse.
1841 14167 6 You have slain the giant white mouse.
1843 14176 39 The giant white mouse bites you.
1846 14182 2 You hit the giant white mouse.
1846 14182 6 You have slain the giant white mouse.
1848 14193 39 The giant white mouse bites you.
1848 14193 8 You die.
1849 14193 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
1842 14172 0 # heading up (bored and unable to dive: 30 hp)
1842 14172 0 # Looking for up stairs.  Going up.
1842 14172 0 # Bored but unable to flow to up stairs.
1842 14172 0 # Boosting bravery (2) from 2 to 68!
1842 14172 0 # Flowing toward up-stairs at cost 73
1842 14172 0 # Looking for stairs. Goal_less, brave.
1844 14182 0 # HIT_BY:The giant white mouse (+)
1844 14182 0 # Creating a monster 'giant white mouse' at (15,87), HP: 1, Index: 23
1844 14182 0 # HIT_BY:The giant white mouse (3)
1844 14182 0 # Loc:17,87 Dep:1 Lev:2 HP:0/17 SP:0/0 Danger:p=11
1844 14182 0 # Performing attack type 1 with value 21.
1844 14182 0 # Facing giant white mouse at (16,87) who has 2 Hit Points.
1844 14182 0 # Attacking with weapon 'Dagger (1d4) (+0,+0)'
1847 14187 0 # HIT:the giant white mouse (+)
1847 14187 0 # KILL:the giant white mouse (+)
1847 14187 0 # Forgetting a monster 'giant white mouse' at (16,87)
1847 14187 0 # HIT:the giant white mouse (2)
1847 14187 0 # KILL:the giant white mouse (2)
1847 14187 0 # Loc:17,87 Dep:1 Lev:2 HP:0/17 SP:0/0 Danger:p=5
1847 14187 0 # Fleeing and leaving the level. (Looking for any stair)
1847 14187 0 # Fleeing and leaving the level (Looking for Up Stair).
1847 14187 0 # Spent too long (120) on level, leaving.
1847 14187 0 # heading up (bored and unable to dive: 30 hp)
1847 14187 0 # Looking for up stairs.  Going up.
1847 14187 0 # Bored but unable to flow to up stairs.
1847 14187 0 # Boosting bravery (2) from 0 to 68!
1847 14187 0 # Flowing toward up-stairs at cost 72
1847 14187 0 # Looking for stairs. Goal_less, brave.
1849 14193 0 # Aborting (death).
1849 14193 0 # Aborting (player died).
```

<a id="blackguard-1472012981-c0b5fd56"></a>
## Blackguard Human 1472012981: poison

- Dies in: `reborn-487-ctl`, `reborn-487-digger`, the same game (play `c0b5fd569280377a`).
- Same start elsewhere: `reborn-487-heal` turn_cap, `reborn-487-both` turn_cap, `reborn-487-speedres` turn_cap.
- Last state line: `43400 24,33 d1/3 hp-1/58 sp3/7 f5369 au165 xp153 lv7 t7:13 o4:772,8:5000 p7e8e7761a5c85816 ef88c4e6308f55178 r08ee9afe362a4c74`

- Cure potions quaffed: 7; Phase Door read: 2; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 0; Failed teleports: 20; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Human Blackguard, Level 7/7
Exp: 453  Gold: 165  Turn: 43400
Killed on level: 1 (max. 3) by poison
```

**Character Equipment**

```
a) Dagger (1d4) (+7,+2)
b) Sling (x2) (+0,+0)
f) Wooden Torch (772 turns)
g) Robe [2,+0]
i) Cloak [1,+0]
m) Leather Shield [8,+0]
```

**Character Inventory**

```
a) 3 Necromantic Tomes [Into the Shadows]
b) 9 Rations of Food
c) 4 Potions of Boldness
d) Shimmering Potion
e) Teal Potion
f) Wooden Torch (5000 turns)
g) Tulwar (2d4) (+0,+0)
```

**Home Inventory (page 1)**

```
a) a Wooden Torch (5000 turns)
b) a Wicker Shield [2,+0] {cursed}
```

### Last trip decisions

```
4635 33050 0 # Trip: descend via search (plan 4): below-plan(2 < 4)
4786 34448 0 # Trip: descend via search (plan 4): below-plan(2 < 4)
4957 36613 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
5197 38710 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
5395 40377 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
5435 40645 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
5592 41784 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
5762 43071 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
```

### Last 30 game messages

```
5782 43106 2 You hit the apprentice.
5782 43111 35 The white jelly touches you.
5783 43111 56 You are more poisoned!
5783 43114 34 The apprentice hits you.
5784 43116 35 The white jelly touches you.
5784 43116 56 You are more poisoned!
5788 43116 2 You hit the apprentice.
5788 43116 4 The apprentice flees in terror!
5788 43121 35 The white jelly touches you.
5789 43121 56 You are more poisoned!
5792 43125 2 You hit the white jelly.
5792 43126 35 The white jelly touches you.
5792 43126 56 You are more poisoned!
5793 43131 35 The white jelly touches you.
5793 43131 56 You are more poisoned!
5797 43133 2 You hit the white jelly.
5797 43133 6 You have destroyed the white jelly.
5801 43170 53 You no longer feel berserk.
5815 43292 78 You enter a maze of up staircases.
5816 43292 0 This seems a tame, sheltered place.
5820 43312 29 You enter a maze of down staircases.
5821 43312 0 This seems a tame, sheltered place.
5827 43352 78 You enter a maze of up staircases.
5828 43352 0 This seems a tame, sheltered place.
5832 43372 29 You enter a maze of down staircases.
5833 43372 0 This seems a tame, sheltered place.
5837 43392 78 You enter a maze of up staircases.
5838 43392 0 This seems a tame, sheltered place.
5840 43400 8 You die.
5841 43400 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
5829 43352 0 # Flowing toward dark-2 at cost 3
5830 43362 0 # Flowing toward down-stairs at cost 1
5830 43362 0 # Desperate for Stairs (four)
5831 43372 0 # Standing on dn-stairs
5834 43372 0 # FEELING_DANGER:8 (+)
5834 43372 0 # FEELING_DANGER:8 (1)
5834 43372 0 # Standing on up-stairs
5834 43372 0 # Leaving (bleeding/poison)
5834 43372 0 # Fleeing (bleeding/poison)
5834 43372 0 # Fleeing and leaving the level. (Looking for any stair)
5834 43372 0 # Flowing toward up-stairs at cost 0
5834 43372 0 # Fleeing and leaving the level (Looking for Up Stair).
5834 43372 0 # Flowing toward up-stairs at cost 0
5834 43372 0 # Flowing toward dark-2 at cost 3
5835 43382 0 # Flowing toward up-stairs at cost 1
5835 43382 0 # Desperate for Stairs (one)
5836 43392 0 # Standing on up-stairs
5836 43392 0 # Leaving via up stairs.
5839 43392 0 # FEELING_DANGER:8 (+)
5839 43392 0 # FEELING_DANGER:8 (1)
5839 43392 0 # Standing on dn-stairs
5839 43392 0 # Leaving (bleeding/poison)
5839 43392 0 # Fleeing (bleeding/poison)
5839 43392 0 # Fleeing and leaving the level. (Looking for any stair)
5839 43392 0 # Flowing toward down-stairs at cost 0
5839 43392 0 # Fleeing and leaving the level (Looking for Up Stair).
5839 43392 0 # Flowing toward down-stairs at cost 0
5839 43392 0 # Flowing toward dark-2 at cost 3
5841 43400 0 # Aborting (death).
5841 43400 0 # Aborting (player died).
```

<a id="mage-1548306106-15f1d78b"></a>
## Mage Human 1548306106: a giant white mouse

- Dies in: `reborn-487-ctl`, `reborn-487-digger`, the same game (play `15f1d78bc97c44a0`).
- Same start elsewhere: `reborn-487-heal` turn_cap, `reborn-487-both` turn_cap, `reborn-487-speedres` turn_cap.
- Last state line: `34660 48,11 d1/1 hp-2/21 sp0/7 f5939 au119 xp55 lv4 t3:6 o2:2883,4:4563 pae5eeb8a37a224a7 e098d867857c77dc5 r08ee9afe362a4c74`

- Cure potions quaffed: 4; Phase Door read: 7; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 0; Failed teleports: 7; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Human Mage, Level 4/4
Exp: 155  Gold: 119  Turn: 34660
Killed on level: 1 (max. 1) by a giant white mouse
```

**Character Equipment**

```
a) Dagger (1d4) (+4,+2)
f) Wooden Torch (4563 turns)
g) Robe [2,+0]
```

**Character Inventory**

```
a) Book of Magic Spells [First Spells]
b) 8 Rations of Food
c) 7 Flasks of oil
d) 3 Scrolls of Detect Invisible
e) Scroll titled "crio irgat mio"
f) Wooden Torch (2883 turns)
g) Rapier (1d6) (+0,+0)
```

**Home Inventory (page 1)**

```
a) a Potion of Berserk Strength
b) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
1650 19853 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2010 23170 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2187 25201 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2371 27571 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2420 28001 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2542 28971 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2573 29201 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2668 30011 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 30 game messages

```
3224 34555 39 The giant white mouse bites you.
3225 34561 39 The giant white mouse bites you.
3228 34565 2 You hit the giant white mouse.
3228 34565 6 You have slain the giant white mouse.
3228 34571 39 The giant white mouse bites you.
3231 34575 0 The giant white mouse misses you.
3231 34581 39 The giant white mouse bites you.
3234 34585 3 You miss the giant white mouse.
3234 34585 39 The giant white mouse bites you.
3234 34591 39 The giant white mouse bites you.
3237 34601 39 The giant white mouse bites you.
3237 34601 39 The giant white mouse bites you.
3240 34605 2 You hit the giant white mouse.
3240 34605 6 You have slain the giant white mouse.
3240 34611 39 The giant white mouse bites you.
3244 34615 2 You hit the giant white mouse.
3244 34615 6 You have slain the giant white mouse.
3244 34615 39 The giant white mouse bites you.
3245 34621 39 The giant white mouse bites you.
3247 34627 39 The giant white mouse bites you.
3250 34635 2 You hit the giant white mouse.
3250 34635 6 You have slain the giant white mouse.
3250 34635 39 The giant white mouse bites you.
3255 34645 0 You do not have enough mana to cast this spell.
3257 34645 0 You faint from the effort!
3257 34645 58 You are paralysed!
3257 34650 39 The giant white mouse bites you.
3258 34660 39 The giant white mouse bites you.
3258 34660 8 You die.
3260 34660 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
3246 34625 0 # Loc:12,55 Dep:1 Lev:4 HP:5/21 SP:0/7 Danger:p=10
3246 34625 0 # Retreating to 12,56 (distance 1) via 12,56 (10 > 0)
3248 34635 0 # HIT_BY:The giant white mouse (+)
3248 34635 0 # Tracking a monster 'giant white mouse' at (12,55) from (12,54)
3248 34635 0 # Creating a monster 'giant white mouse' at (12,57), HP: 2, Index: 23
3248 34635 0 # HIT_BY:The giant white mouse (3)
3248 34635 0 # There was a monster 'giant white mouse' at (11,54)
3248 34635 0 # Forgetting a monster 'giant white mouse' at (11,54)
3248 34635 0 # Possibility of being surrounded (monsters/safegrids)(2/0)
3248 34635 0 # Loc:12,56 Dep:1 Lev:4 HP:3/21 SP:0/7 Danger:p=10
3248 34635 0 # Performing attack type 1 with value 13.
3248 34635 0 # Facing giant white mouse at (12,57) who has 2 Hit Points.
3248 34635 0 # Attacking with weapon 'Dagger (1d4) (+4,+2)'
3252 34645 0 # HIT:the giant white mouse (+)
3252 34645 0 # KILL:the giant white mouse (+)
3252 34645 0 # HIT_BY:The giant white mouse (+)
3252 34645 0 # Forgetting a monster 'giant white mouse' at (12,57)
3252 34645 0 # Tracking a monster 'giant white mouse' at (12,57) from (11,61)
3252 34645 0 # Creating a monster 'giant white mouse' at (12,55), HP: 2, Index: 23
3252 34645 0 # HIT:the giant white mouse (2)
3252 34645 0 # KILL:the giant white mouse (2)
3252 34645 0 # HIT_BY:The giant white mouse (3)
3252 34645 0 # There was a monster 'giant white mouse' at (12,55)
3252 34645 0 # Forgetting a monster 'giant white mouse' at (12,55)
3252 34645 0 # Possibility of being surrounded (monsters/safegrids)(2/1)
3252 34645 0 # Loc:12,56 Dep:1 Lev:4 HP:1/21 SP:0/7 Danger:p=15
3252 34645 0 # Casting Phase Door (0,3).
3252 34645 0 # Danger Level 1.3  Critical Attempt
3260 34660 0 # Aborting (death).
3260 34660 0 # Aborting (player died).
```

<a id="necromancer-300036923-a1b9a3c8"></a>
## Necromancer Human 300036923: a small kobold

- Dies in: `reborn-487-heal`, `reborn-487-both`, `reborn-487-speedres`, the same game (play `a1b9a3c8834b1acc`).
- Same start elsewhere: `reborn-487-ctl` turn_cap, `reborn-487-digger` turn_cap.
- Last state line: `5824 143,24 d1/1 hp-2/19 sp4/4 f8419 au6 xp10 lv2 t3:2,9:8 o- p91ae08696b59e83b ef45f8eba99899246 r08ee9afe362a4c74`

- Cure potions quaffed: 0; Phase Door read: 2; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 0; Failed teleports: 0; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Human Necromancer, Level 2/2
Exp: 110  Gold: 6  Turn: 5824
Killed on level: 1 (max. 1) by a small kobold
```

**Character Equipment**

```
a) Main Gauche (1d5) (+0,+0)
```

**Character Inventory**

```
a) Necromantic Tome [Into the Shadows]
b) 5 Rations of Food
c) 10 Flasks of oil
d) 4 Potions of Cure Light Wounds
e) Scroll of Word of Recall
```

**Home Inventory (page 1)**

```
a) 2 Potions of Cure Serious Wounds
b) a Potion of Berserk Strength
```

### Where it splits from the control `reborn-487-ctl` (game turn 121)

```
12 91 0 # Flowing toward Alchemy Shop at cost 3
14 111 0 # Entering a '4' shop
15 111 0 # Town plan executing action 1 at shop 4 slot 3
19 111 0 You bought an Azure Potion for 80 gold.
19 111 0 You have a Potion of Berserk Strength (c).
23 121 0 # Buying Potions of Berserk Strength {unseen}.
23 121 0 # Flowing toward General Store at cost 24
31 201 0 The village idiot wakes up.
32 201 0 # PAIN:The village idiot (+)
32 201 0 # PAIN:The village idiot (2)
32 201 0 # Performing attack type 1 with value 1.
32 201 0 # Facing village idiot at (12,36) who has 10 Hit Points.
```

Control at the same point:

```
23 121 0 # Re-entering a shop
24 121 0 # Town plan executing action 1 at shop 4 slot 1
28 121 0 You bought an Indigo Potion for 70 gold.
28 121 0 You have a Potion of Cure Serious Wounds (c).
32 121 0 # Buying Potions of Cure Serious Wounds {unseen}.
32 121 0 # Flowing toward General Store at cost 24
```

### Last trip decisions

```
292 1647 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
358 2207 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
520 5517 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 30 game messages

```
433 2567 0 Target Selected.
438 2567 7 Welcome to level 2.
438 2567 0 You can learn 1 more ritual.
438 2567 6 The giant white centipede dies.
443 2577 9 You have learned the ritual of Sense Invisible.
463 3787 0 You failed to concentrate hard enough!
495 5317 78 You enter a maze of up staircases.
500 5337 29 You enter a maze of down staircases.
501 5337 0 This seems a quiet, peaceful place.
545 5763 47 The floating eye gazes at you.
545 5763 58 You are paralysed!
545 5772 47 The floating eye gazes at you.
546 5774 0 The small kobold wakes up.
546 5781 47 The floating eye gazes at you.
547 5781 0 You resist the effects!
547 5784 34 The small kobold hits you.
548 5784 76 You have been stunned.
548 5790 47 The floating eye gazes at you.
549 5794 34 The small kobold hits you.
549 5799 47 The floating eye gazes at you.
550 5800 53 You can move again.
550 5804 34 The small kobold hits you.
551 5808 47 The floating eye gazes at you.
551 5808 58 You are paralysed!
552 5814 34 The small kobold hits you.
552 5817 47 The floating eye gazes at you.
553 5817 0 You resist the effects!
553 5824 34 The small kobold hits you.
554 5824 8 You die.
555 5824 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
498 5327 0 # Creating a monster 'village idiot' at (12,19), HP: 8, Index: 7
498 5327 0 # Removing Regional Fear (12,19) because of a LOS village idiot
498 5327 0 # Nothing to sell in town (leaving).
498 5327 0 # Flowing toward down-stairs at cost 1
499 5337 0 # Standing on dn-stairs
502 5337 0 # FEELING_DANGER:9 (+)
502 5337 0 # FEELING_DANGER:9 (1)
502 5337 0 # Standing on up-stairs
502 5337 0 # Flowing toward dark-2 at cost 2
504 5357 0 # Flowing toward dark-2 at cost 2
506 5377 0 # Flowing toward dark-2 at cost 2
507 5387 0 # Flowing toward dark-3 at cost 1
507 5387 0 # Opening a door
509 5407 0 # Flowing toward dark-2 at cost 2
511 5427 0 # Flowing toward dark-2 at cost 2
513 5447 0 # Flowing toward dark-2 at cost 2
515 5467 0 # Flowing toward dark-2 at cost 2
517 5487 0 # Flowing toward dark-2 at cost 2
519 5507 0 # Flowing toward dark-3 at cost 2
520 5517 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
520 5517 0 # Flowing toward dark-4 at cost 11
531 5627 0 # Flowing toward dark-2 at cost 2
533 5647 0 # Flowing toward dark-2 at cost 2
535 5667 0 # Flowing toward dark-2 at cost 2
537 5687 0 # Flowing toward dark-2 at cost 2
539 5707 0 # Flowing toward dark-2 at cost 2
541 5727 0 # Flowing toward dark-2 at cost 2
543 5747 0 # Flowing toward dark-2 at cost 2
555 5824 0 # Aborting (death).
555 5824 0 # Aborting (player died).
```

<a id="druid-934061548-f53c443e"></a>
## Druid Half-Elf 934061548: a soldier

- Dies in: `reborn-487-heal`, the same game (play `f53c443e0f445341`).
- Same start elsewhere: `reborn-487-ctl` turn_cap, `reborn-487-digger` turn_cap, `reborn-487-both` turn_cap, `reborn-487-speedres` turn_cap.
- Last state line: `35851 184,9 d2/2 hp-2/30 sp0/5 f6719 au171 xp49 lv3 t- o1:3363,4:3878 p28e9fcabd3544c74 ef76dbdee69f442a0 r08ee9afe362a4c74`

- Cure potions quaffed: 13; Phase Door read: 12; Unknown potions quaffed: 0; Healing (outmatched) notes: 13; Potion of Speed quaffed: 0; Failed teleports: 3; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Half-Elf Druid, Level 3/3
Exp: 249  Gold: 171  Turn: 35851
Killed on level: 2 (max. 2) by a soldier
```

**Character Equipment**

```
a) Whip (1d3) (+0,+0)
b) Sling (x2) (+0,+0)
f) Wooden Torch (3363 turns)
g) Robe [2,+0]
i) Cloak [1,+0]
n) Hard Leather Cap [2,+0]
o) Set of Leather Gloves [1,+0]
```

**Character Quiver**

```
a) 15 Iron Shots (1d4) (+0,+0)
```

**Character Inventory**

```
a) Book of Nature Magics [Lesser Charms]
b) 2 Apples
c) 9 Rations of Food
d) Potion of Neutralize Poison
e) Potion of Boldness
f) Wooden Torch (3878 turns)
g) Shovel (1d2) (+0,+0)
```

**Home Inventory (page 1)**

```
a) an Apple
b) 19 Flasks of oil
c) a Potion of Cure Serious Wounds
d) a Wooden Torch (5000 turns)
```

### Where it splits from the control `reborn-487-ctl` (game turn 341)

```
46 331 0 # Tracking a monster 'scrawny cat' at (11,22) from (11,23)
46 331 0 # Entering a '4' shop
47 331 0 # Town plan executing action 1 at shop 4 slot 1
50 331 0 You bought a Cyan Potion for 70 gold.
50 331 0 You have a Potion of Cure Serious Wounds (c).
55 341 0 # Buying Potion of Cure Serious Wounds {unseen}.
55 341 0 # Flowing toward General Store at cost 34
56 351 0 # Tracking a monster 'scrawny cat' at (11,21) from (11,22)
56 351 0 # Tracking a monster 'scrawny cat' at (12,22) from (12,24)
57 361 0 # Tracking a monster 'scrawny cat' at (12,20) from (11,21)
57 361 0 # Tracking a monster 'scrawny cat' at (11,21) from (12,22)
57 361 0 # There was a monster 'filthy street urchin' at (14,30)
```

Control at the same point:

```
55 341 0 # Re-entering a shop
56 341 0 "You can use the 'I' command to inspect items and get details on them."
56 341 0 # Town plan executing action 1 at shop 4 slot 0
61 341 0 You bought 3 Metallic Purple Potions for 60 gold.
61 341 0 You have 3 Potions of Cure Light Wounds (c).
65 341 0 # Buying 3 x Potions of Cure Light Wounds {unseen}.
```

### Last trip decisions

```
2398 18876 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2651 20992 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3372 23338 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3715 24944 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3825 25865 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3962 26916 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
4213 29240 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
4601 34941 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
```

### Last 30 game messages

```
4931 35791 0 You feel much better.
4931 35791 0 You have no more Potions of Cure Light Wounds (d).
4931 35801 34 The acolyte hits you.
4932 35801 34 The soldier hits you.
4932 35801 34 The soldier hits you.
4935 35801 2 You hit the apprentice.
4935 35801 4 The apprentice flees in terror!
4935 35804 0 The apprentice blinks.
4936 35811 0 The acolyte magically starts closing wounds.
4936 35811 0 The acolyte looks REALLY healthy!
4937 35811 0 The soldier misses you.
4937 35811 0 The soldier misses you.
4941 35811 3 You miss the acolyte.
4941 35821 34 The acolyte hits you.
4941 35821 34 The soldier hits you.
4941 35821 34 The soldier hits you.
4945 35821 2 You hit the acolyte.
4945 35831 0 The acolyte magically starts closing wounds.
4945 35831 0 The acolyte looks REALLY healthy!
4946 35831 34 The soldier hits you.
4946 35831 34 The soldier hits you.
4950 35831 2 You hit the acolyte.
4950 35841 0 The acolyte tries to cast a spell, but fails.
4950 35841 34 The soldier hits you.
4951 35841 0 The soldier misses you.
4954 35841 2 You hit the acolyte.
4954 35851 34 The acolyte hits you.
4954 35851 34 The soldier hits you.
4954 35851 8 You die.
4956 35851 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
4943 35821 0 # HIT_BY:The soldier (3)
4943 35821 0 # HIT_BY:The soldier (3)
4943 35821 0 # Loc:9,184 Dep:2 Lev:3 HP:11/30 SP:0/5 Danger:p=73
4943 35821 0 # Performing attack type 1 with value 89.
4943 35821 0 # Facing acolyte at (9,185) who has 20 Hit Points.
4943 35821 0 # Attacking with weapon 'Whip (1d3) (+0,+0)'
4948 35831 0 # HIT:the acolyte (+)
4948 35831 0 # SPELL_064:The acolyte (+)
4948 35831 0 # HIT_BY:The soldier (+)
4948 35831 0 # HIT_BY:The soldier (+)
4948 35831 0 # HIT:the acolyte (2)
4948 35831 0 # SPELL_064:The acolyte (3)
4948 35831 0 # HIT_BY:The soldier (3)
4948 35831 0 # HIT_BY:The soldier (3)
4948 35831 0 # Loc:9,184 Dep:2 Lev:3 HP:7/30 SP:0/5 Danger:p=73
4948 35831 0 # Performing attack type 1 with value 89.
4948 35831 0 # Facing acolyte at (9,185) who has 20 Hit Points.
4948 35831 0 # Attacking with weapon 'Whip (1d3) (+0,+0)'
4952 35841 0 # HIT:the acolyte (+)
4952 35841 0 # HIT_BY:The soldier (+)
4952 35841 0 # MISS_BY:The soldier (+)
4952 35841 0 # HIT:the acolyte (2)
4952 35841 0 # HIT_BY:The soldier (3)
4952 35841 0 # MISS_BY:The soldier (3)
4952 35841 0 # Loc:9,184 Dep:2 Lev:3 HP:3/30 SP:0/5 Danger:p=73
4952 35841 0 # Performing attack type 1 with value 89.
4952 35841 0 # Facing acolyte at (9,185) who has 18 Hit Points.
4952 35841 0 # Attacking with weapon 'Whip (1d3) (+0,+0)'
4956 35851 0 # Aborting (death).
4956 35851 0 # Aborting (player died).
```

<a id="priest-1569794094-5b24ad51"></a>
## Priest Human 1569794094: Fang, Farmer Maggot's Dog

- Dies in: `reborn-487-heal`, `reborn-487-both`, `reborn-487-speedres`, the same game (play `5b24ad51bfc93d7e`).
- Same start elsewhere: `reborn-487-ctl` turn_cap, `reborn-487-digger` turn_cap.
- Last state line: `8760 75,33 d1/1 hp-4/20 sp0/4 f8429 au3 xp10 lv2 t- o2:4409,4:5000 pffec860338b93c6b eb88258f248fe5239 r08ee9afe362a4c74`

- Cure potions quaffed: 3; Phase Door read: 1; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 0; Failed teleports: 2; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Human Priest, Level 2/2
Exp: 110  Gold: 3  Turn: 8760
Killed on level: 1 (max. 1) by Fang, Farmer Maggot's Dog
```

**Character Equipment**

```
a) Mace (2d4) (+0,+0)
f) Wooden Torch (4409 turns)
o) Set of Leather Gloves [1,+0]
```

**Character Inventory**

```
a) Holy Book of Prayers [Novice's Handbook]
b) 5 Rations of Food
c) Copper Speckled Potion
d) Wooden Torch (5000 turns)
e) Dagger (1d4) (+0,+0)
```

**Home Inventory (page 1)**

```
a) a Potion of Cure Light Wounds
b) a Wooden Torch (5000 turns)
```

### Where it splits from the control `reborn-487-ctl` (game turn 661)

```
74 561 0 You bought 3 Rations of Food for 9 gold.
74 561 0 You have 5 Rations of Food (b).
78 571 0 # Buying 3 x Rations of Food.
78 571 0 # Flowing toward Alchemy Shop at cost 10
87 661 0 # Entering a '4' shop
88 661 0 # Town plan executing action 1 at shop 4 slot 0
92 661 86 Agreed!
92 661 0 You bought a Metallic Green Potion for 20 gold.
92 661 0 You have a Potion of Cure Light Wounds (c).
96 671 0 # Buying Potions of Cure Light Wounds {unseen}.
96 671 0 # Flowing toward Home at cost 28
99 701 0 # There was a monster 'mean-looking mercenary' at (16,39)
```

Control at the same point:

```
93 661 86 Agreed!
93 661 0 You bought 2 Metallic Green Potions for 40 gold.
93 661 0 You have 2 Potions of Cure Light Wounds (c).
97 671 0 # Buying 2 x Potions of Cure Light Wounds {unseen}.
97 671 0 # Re-entering a shop
98 671 0 # Town plan executing action 1 at shop 4 slot 7
```

### Last trip decisions

```
231 2511 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
319 4211 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
513 7055 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 30 game messages

```
562 7295 6 You have slain the small kobold.
568 7350 53 The prayer has expired.
574 7450 25 You feel yourself yanked upwards!
584 8261 0 You failed to concentrate hard enough!
586 8271 29 You enter a maze of down staircases.
587 8271 0 This seems a tame, sheltered place.
587 8271 0 You have found a secret door.
591 8675 0 The fruit bat wakes up.
600 8701 2 You hit the fruit bat.
600 8701 6 You have slain the fruit bat.
600 8701 7 Welcome to level 2.
600 8701 0 You can learn 1 more prayer.
601 8705 0 You hear a door burst open!
601 8710 39 Fang, Farmer Maggot's Dog, bites you.
605 8711 0 You feel very good.
605 8711 0 You have no more Potions of Cure Serious Wounds (c).
605 8715 39 Fang, Farmer Maggot's Dog, bites you.
606 8720 39 Fang, Farmer Maggot's Dog, bites you.
609 8730 39 Fang, Farmer Maggot's Dog, bites you.
609 8730 77 You have been given a graze.
609 8730 53 You are no longer bleeding.
612 8740 39 Fang, Farmer Maggot's Dog, bites you.
615 8741 9 You have learned the prayer of Minor Healing.
615 8745 39 Fang, Farmer Maggot's Dog, bites you.
616 8750 39 Fang, Farmer Maggot's Dog, bites you.
620 8751 3 You miss Fang, Farmer Maggot's Dog.
620 8755 39 Fang, Farmer Maggot's Dog, bites you.
621 8760 39 Fang, Farmer Maggot's Dog, bites you.
622 8760 8 You die.
623 8760 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
603 8711 0 # Standing on up-stairs
603 8711 0 # Quaffing Potion of Cure Serious Wounds.
603 8711 0 # Healing Level 2.
608 8721 0 # HIT_BY:Fang, Farmer Maggot's Dog (+)
608 8721 0 # HIT_BY:Fang, Farmer Maggot's Dog (+)
608 8721 0 # HIT_BY:Fang, Farmer Maggot's Dog (3)
608 8721 0 # HIT_BY:Fang, Farmer Maggot's Dog (3)
608 8721 0 # Loc:33,73 Dep:1 Lev:2 HP:17/20 SP:0/4 Danger:p=8
608 8721 0 # Standing on up-stairs
608 8721 0 # Retreating to 33,74 (distance 1) via 33,74 (8 > 4)
611 8731 0 # HIT_BY:Fang, Farmer Maggot's Dog (+)
611 8731 0 # Tracking a monster 'Fang, Farmer Maggot's Dog' at (33,73) from (33,72)
611 8731 0 # HIT_BY:Fang, Farmer Maggot's Dog (3)
611 8731 0 # Loc:33,74 Dep:1 Lev:2 HP:13/20 SP:0/4 Danger:p=8
611 8731 0 # Retreating to 33,75 (distance 1) via 33,75 (8 > 4)
613 8741 0 # HIT_BY:Fang, Farmer Maggot's Dog (+)
613 8741 0 # Tracking a monster 'Fang, Farmer Maggot's Dog' at (33,74) from (33,73)
613 8741 0 # HIT_BY:Fang, Farmer Maggot's Dog (3)
613 8741 0 # Loc:33,75 Dep:1 Lev:2 HP:10/20 SP:0/4 Danger:p=8
613 8741 0 # Studying spell/prayer Detect Evil.
618 8751 0 # HIT_BY:Fang, Farmer Maggot's Dog (+)
618 8751 0 # HIT_BY:Fang, Farmer Maggot's Dog (+)
618 8751 0 # HIT_BY:Fang, Farmer Maggot's Dog (3)
618 8751 0 # HIT_BY:Fang, Farmer Maggot's Dog (3)
618 8751 0 # Loc:33,75 Dep:1 Lev:2 HP:4/20 SP:0/4 Danger:p=8
618 8751 0 # Performing attack type 1 with value 40.
618 8751 0 # Facing Fang, Farmer Maggot's Dog at (33,74) who has 25 Hit Points.
618 8751 0 # Attacking with weapon 'Mace (2d4) (+0,+0)'
623 8760 0 # Aborting (death).
623 8760 0 # Aborting (player died).
```
