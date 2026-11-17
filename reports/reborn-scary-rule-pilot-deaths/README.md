# Deaths in reborn-scary-rule-pilot (borg-zoo#227)

Run [44178676657](https://github.com/diegoami/borg-zoo/actions/runs/44178676657), specimen `4.2.6-reborn-rust-main-a8ac685a`. A reading aid written by `python3 -m zoo.death_report`, not a cemetery entry or a causal diagnosis.

9 deaths in 54 games, 7 distinct dying games. Replayed locally from the run's own build artifact, arms `reborn-scary-ctl`, `reborn-scary-named`: every replayed play hash matches CI.

| Game | Dies in | Killed by | Char level | Dungeon level | Game turn | Keys |
|---|---|---|---|---|---|---|
| [Druid Human 102023799](#druid-102023799-ffc98880) | `reborn-scary-ctl` | a clear icky thing | 1 | 1 (max 1) | 9986 | 1197 |
| [Necromancer Human 300036923](#necromancer-300036923-a1b9a3c8) | `reborn-scary-ctl`, `reborn-scary-damage60` | a small kobold | 2 | 1 (max 1) | 5824 | 556 |
| [Mage Human 1548306106](#mage-1548306106-ba273be3) | `reborn-scary-ctl` | a wild dog | 3 | 1 (max 1) | 31960 | 3268 |
| [Priest Human 1569794094](#priest-1569794094-5b24ad51) | `reborn-scary-ctl`, `reborn-scary-damage60` | Fang, Farmer Maggot's Dog | 2 | 1 (max 1) | 8760 | 624 |
| [Druid Human 102023799](#druid-102023799-b28ce8cc) | `reborn-scary-named` | poison | 6 | 2 (max 2) | 66650 | 7200 |
| [Ranger Human 226104090](#ranger-226104090-feeb5943) | `reborn-scary-named` | poison | 7 | 2 (max 3) | 92840 | 14441 |
| [Druid Half-Elf 934061548](#druid-934061548-b362eb29) | `reborn-scary-named` | an apprentice | 4 | 2 (max 3) | 40491 | 4224 |

## Observations

All three arms were replayed (54 games), and every play hash matches CI. Observations, not diagnoses:

| arm (named list, damage %) | deaths /18 | at CL1-3 | mean max CL | mean max DL | same play as ctl | vs ctl rescued / newly killed | `Scary guy on level.` notes | down-then-up bounces |
|---|---|---|---|---|---|---|---|---|
| ctl (0, 0): no rule | 4 | 4 | 5.56 | 2.56 | 18 | - | 0 | 472 |
| named (1, 0): C's list | 3 | 0 | 4.94 | 2.11 | 0 | 3 / 2 | 11,804 | 1,515 |
| damage60 (0, 60): shipped | 2 | 2 | 5.89 | 2.67 | 15 | 2 / 0 | 10 | 507 |

- **The damage rule at 60% almost never fires:** 10 `Scary guy` notes in 18 games, and 15 games identical to the no-rule control.
  - It saves 2: the CL1 Druid (clear icky thing) and the CL3 Mage (wild dog).
  - It does not save the CL2 Necromancer (small kobold) or the CL2 Priest (Fang), who die in both ctl and damage60.
- **The named list prevents every CL1-3 death.** Its 3 deaths are later: two Druids at CL4 and CL6 and a Ranger at CL7, two of them by poison.
  - The cost is 0.6-0.9 character levels and a shallower game.
  - It triples the level bouncing (1,515 against about 500).
- `damage60` replays #225's `both` arm exactly (18/18), since the settings are the same.

At 60% the damage rule rarely triggers early, because Fang or a small kobold cannot take 60% of a level-2 caster's HP in one turn. The named list catches them by name. Two directions follow: a lower damage threshold, or the data-file list (#228, borg-reborn-rs#527) with Necromancers and Druids in its frail-caster exception.

## Handover: working on these deaths in the Borg's repository

For a session in diegoami/borg-reborn-rs that changes parameters or code against these deaths. That repository owns the Borg; the zoo only measures, and any change is measured here later as a new specimen.

- **Build:** `diegoami/borg-reborn-rs` at `a8ac685a2c90b412971fedd90d98b783b7f70380` (zoo specimen `4.2.6-reborn-rust-main-a8ac685a`): `BORG_IMPL=rust harness/build.sh`, or the run's CI artifact: `gh run download 44178676657 -R diegoami/borg-zoo -n build-4.2.6-reborn-rust-main-a8ac685a`.
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
| [Druid 102023799](#druid-102023799-ffc98880) | 102023799 | 0 (Human) | 2 | `reborn-scary-ctl` | `ffc98880aad74164` |
| [Necromancer 300036923](#necromancer-300036923-a1b9a3c8) | 300036923 | 0 (Human) | 4 | `reborn-scary-ctl` | `a1b9a3c8834b1acc` |
| [Mage 1548306106](#mage-1548306106-ba273be3) | 1548306106 | 0 (Human) | 1 | `reborn-scary-ctl` | `ba273be336fbd8f7` |
| [Priest 1569794094](#priest-1569794094-5b24ad51) | 1569794094 | 0 (Human) | 3 | `reborn-scary-ctl` | `5b24ad51bfc93d7e` |
| [Druid 102023799](#druid-102023799-b28ce8cc) | 102023799 | 0 (Human) | 2 | `reborn-scary-named` | `b28ce8ccd5061b64` |
| [Ranger 226104090](#ranger-226104090-feeb5943) | 226104090 | 0 (Human) | 7 | `reborn-scary-named` | `feeb5943c4eb26c8` |
| [Druid 934061548](#druid-934061548-b362eb29) | 934061548 | 1 (Half-Elf) | 2 | `reborn-scary-named` | `b362eb29fac5c0ca` |

In borg-zoo, `python3 -m zoo.death_report --experiment experiments/reborn-scary-rule-pilot.json --run 44178676657` replays and checks them all. After a change: a PR in the Borg's repository, then ask the borg-zoo session for a new specimen at the merged commit and a pilot (or verysmall) of the same arms.

<a id="druid-102023799-ffc98880"></a>
## Druid Human 102023799: a clear icky thing

- Dies in: `reborn-scary-ctl`, the same game (play `ffc98880aad74164`).
- Same start elsewhere: `reborn-scary-named` death, `reborn-scary-damage60` turn_cap.
- Last state line: `9986 110,16 d1/1 hp-1/12 sp2/2 f8109 au8 xp3 lv1 t- o1:4223,7:5000 pc567363e23a418d9 e5ba0659ac95a4d70 r08ee9afe362a4c74`

- Cure potions quaffed: 1; Phase Door read: 4; Unknown potions quaffed: 0; Healing (outmatched) notes: 1; Potion of Speed quaffed: 0; Failed teleports: 0; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Human Druid, Level 1/1
Exp: 103  Gold: 8  Turn: 9986
Killed on level: 1 (max. 1) by a clear icky thing
```

**Character Equipment**

```
a) Whip (1d3) (+0,+0)
f) Wooden Torch (4223 turns)
```

**Character Inventory**

```
a) Book of Nature Magics [Lesser Charms]
b) 5 Rations of Food
c) 20 Flasks of oil
d) 5 Potions of Cure Light Wounds
e) 2 Scrolls of Phase Door
f) Wooden Torch (5000 turns)
```

**Home Inventory (page 1)**

```
a) a Potion of Berserk Strength
```

### Last trip decisions

```
444 2983 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
542 3763 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
605 4333 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
686 5064 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
755 5694 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
829 6374 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
931 7544 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
1000 8174 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 30 game messages

```
1100 9051 0 You have found a secret door.
1104 9061 28 You failed to pick the lock.
1105 9071 87 You have picked the lock.
1107 9086 35 Something touches you.
1111 9119 35 Something touches you.
1115 9141 35 Something touches you.
1119 9152 35 Something touches you.
1123 9164 35 Something touches you.
1127 9175 35 Something touches you.
1131 9452 35 Something touches you.
1135 9475 35 Something touches you.
1139 9486 35 Something touches you.
1143 9519 35 Something touches you.
1147 9586 35 Something touches you.
1151 9597 35 Something touches you.
1154 9601 0 You feel much better.
1154 9601 0 You have 5 Potions of Cure Light Wounds (d).
1154 9608 35 Something touches you.
1159 9619 35 Something touches you.
1163 9630 35 Something touches you.
1167 9786 35 Something touches you.
1171 9797 35 Something touches you.
1175 9830 35 Something touches you.
1179 9841 35 Something touches you.
1183 9875 35 Something touches you.
1187 9964 35 Something touches you.
1191 9975 35 Something touches you.
1195 9986 35 Something touches you.
1195 9986 8 You die.
1196 9986 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
1172 9801 0 # Invisible monster nearby.
1172 9801 0 # HIT_BY:Something (5)
1172 9801 0 # Resting to recover HP/SP...
1176 9831 0 # HIT_BY:Something (+)
1176 9831 0 # Invisible monster nearby.
1176 9831 0 # Invisible monster nearby.
1176 9831 0 # HIT_BY:Something (5)
1176 9831 0 # Resting to recover HP/SP...
1180 9841 0 # HIT_BY:Something (+)
1180 9841 0 # Invisible monster nearby.
1180 9841 0 # Invisible monster nearby.
1180 9841 0 # HIT_BY:Something (5)
1180 9841 0 # Resting to recover HP/SP...
1184 9881 0 # HIT_BY:Something (+)
1184 9881 0 # Invisible monster nearby.
1184 9881 0 # Invisible monster nearby.
1184 9881 0 # HIT_BY:Something (5)
1184 9881 0 # Resting to recover HP/SP...
1188 9971 0 # HIT_BY:Something (+)
1188 9971 0 # Invisible monster nearby.
1188 9971 0 # Invisible monster nearby.
1188 9971 0 # HIT_BY:Something (5)
1188 9971 0 # Resting to recover HP/SP...
1192 9981 0 # HIT_BY:Something (+)
1192 9981 0 # Invisible monster nearby.
1192 9981 0 # Invisible monster nearby.
1192 9981 0 # HIT_BY:Something (5)
1192 9981 0 # Resting to recover HP/SP...
1196 9986 0 # Aborting (death).
1196 9986 0 # Aborting (player died).
```

<a id="necromancer-300036923-a1b9a3c8"></a>
## Necromancer Human 300036923: a small kobold

- Dies in: `reborn-scary-ctl`, `reborn-scary-damage60`, the same game (play `a1b9a3c8834b1acc`).
- Same start elsewhere: `reborn-scary-named` turn_cap.
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

<a id="mage-1548306106-ba273be3"></a>
## Mage Human 1548306106: a wild dog

- Dies in: `reborn-scary-ctl`, the same game (play `ba273be336fbd8f7`).
- Same start elsewhere: `reborn-scary-named` turn_cap, `reborn-scary-damage60` turn_cap.
- Last state line: `31960 123,33 d1/1 hp-1/17 sp0/5 f6609 au9 xp41 lv3 t- o2:2698,4:5000 p0350ea65bd2755bd e790ea4c973313a24 r08ee9afe362a4c74`

- Cure potions quaffed: 8; Phase Door read: 7; Unknown potions quaffed: 0; Healing (outmatched) notes: 5; Potion of Speed quaffed: 0; Failed teleports: 8; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Human Mage, Level 3/3
Exp: 141  Gold: 9  Turn: 31960
Killed on level: 1 (max. 1) by a wild dog
```

**Character Equipment**

```
a) Rapier (1d6) (+0,+0)
f) Wooden Torch (2698 turns)
i) Cloak [1,+0]
```

**Character Inventory**

```
a) 2 Books of Magic Spells [First Spells]
b) 5 Rations of Food
c) 14 Flasks of oil
d) 4 Wooden Torches (5000 turns)
```

**Home Inventory (page 1)**

```
a) an Apple
b) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
2066 19762 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2226 21753 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2350 23033 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2609 25824 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2752 27164 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
2908 28644 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3071 30784 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
3142 31524 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
```

### Last 30 game messages

```
3226 31845 34 The apprentice hits you.
3226 31854 34 The apprentice hits you.
3230 31854 0 You feel much better.
3230 31854 0 You have 2 Potions of Cure Light Wounds (d).
3230 31863 34 The apprentice hits you.
3234 31864 2 You hit the apprentice.
3234 31864 6 You have slain the apprentice.
3234 31864 0 You feel something roll beneath your feet.
3235 31874 0 Grip, Farmer Maggot's Dog, misses you.
3238 31884 39 Grip, Farmer Maggot's Dog, bites you.
3241 31884 0 You feel much better.
3241 31884 0 You have a Potion of Cure Light Wounds (d).
3241 31889 39 Grip, Farmer Maggot's Dog, bites you.
3244 31904 39 Grip, Farmer Maggot's Dog, bites you.
3247 31904 0 You feel much better.
3247 31904 0 You have no more Potions of Cure Light Wounds (d).
3247 31909 39 Grip, Farmer Maggot's Dog, bites you.
3248 31914 0 Grip, Farmer Maggot's Dog, misses you.
3251 31924 39 Grip, Farmer Maggot's Dog, bites you.
3254 31924 2 You hit Grip, Farmer Maggot's Dog.
3257 31934 3 You miss Grip, Farmer Maggot's Dog.
3257 31944 39 Grip, Farmer Maggot's Dog, bites you.
3261 31944 2 You hit Grip, Farmer Maggot's Dog.
3261 31949 39 Grip, Farmer Maggot's Dog, bites you.
3261 31954 39 Grip, Farmer Maggot's Dog, bites you.
3265 31954 3 You miss Grip, Farmer Maggot's Dog.
3265 31959 39 Grip, Farmer Maggot's Dog, bites you.
3266 31960 39 The wild dog bites you.
3266 31960 8 You die.
3267 31960 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
3255 31934 0 # Tracking a monster 'Grip, Farmer Maggot's Dog' at (34,123) from (32,123)
3255 31934 0 # HIT:Grip, Farmer Maggot's Dog (2)
3255 31934 0 # Loc:33,123 Dep:1 Lev:3 HP:12/17 SP:0/5 Danger:p=12
3255 31934 0 # Performing attack type 1 with value 26.
3255 31934 0 # Facing Grip, Farmer Maggot's Dog at (34,123) who has 18 Hit Points.
3255 31934 0 # Attacking with weapon 'Rapier (1d6) (+0,+0)'
3259 31944 0 # MISS:Grip, Farmer Maggot's Dog (+)
3259 31944 0 # HIT_BY:Grip, Farmer Maggot's Dog (+)
3259 31944 0 # Tracking a monster 'Grip, Farmer Maggot's Dog' at (34,122) from (34,123)
3259 31944 0 # MISS:Grip, Farmer Maggot's Dog (2)
3259 31944 0 # HIT_BY:Grip, Farmer Maggot's Dog (3)
3259 31944 0 # Loc:33,123 Dep:1 Lev:3 HP:8/17 SP:0/5 Danger:p=12
3259 31944 0 # Performing attack type 1 with value 26.
3259 31944 0 # Facing Grip, Farmer Maggot's Dog at (34,122) who has 18 Hit Points.
3259 31944 0 # Attacking with weapon 'Rapier (1d6) (+0,+0)'
3263 31954 0 # HIT:Grip, Farmer Maggot's Dog (+)
3263 31954 0 # HIT_BY:Grip, Farmer Maggot's Dog (+)
3263 31954 0 # HIT_BY:Grip, Farmer Maggot's Dog (+)
3263 31954 0 # Tracking a monster 'wild dog' at (32,123) from (29,123)
3263 31954 0 # Creating a monster 'wild dog' at (29,123), HP: 3, Index: 29
3263 31954 0 # Removing Regional Fear (29,123) because of a LOS wild dog
3263 31954 0 # HIT:Grip, Farmer Maggot's Dog (2)
3263 31954 0 # HIT_BY:Grip, Farmer Maggot's Dog (3)
3263 31954 0 # HIT_BY:Grip, Farmer Maggot's Dog (3)
3263 31954 0 # Loc:33,123 Dep:1 Lev:3 HP:2/17 SP:0/5 Danger:p=16
3263 31954 0 # Performing attack type 1 with value 26.
3263 31954 0 # Facing Grip, Farmer Maggot's Dog at (34,122) who has 12 Hit Points.
3263 31954 0 # Attacking with weapon 'Rapier (1d6) (+0,+0)'
3267 31960 0 # Aborting (death).
3267 31960 0 # Aborting (player died).
```

<a id="priest-1569794094-5b24ad51"></a>
## Priest Human 1569794094: Fang, Farmer Maggot's Dog

- Dies in: `reborn-scary-ctl`, `reborn-scary-damage60`, the same game (play `5b24ad51bfc93d7e`).
- Same start elsewhere: `reborn-scary-named` turn_cap.
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

<a id="druid-102023799-b28ce8cc"></a>
## Druid Human 102023799: poison

- Dies in: `reborn-scary-named`, the same game (play `b28ce8ccd5061b64`).
- Same start elsewhere: `reborn-scary-ctl` death, `reborn-scary-damage60` turn_cap.
- Last state line: `66650 125,37 d2/2 hp-1/54 sp10/10 f3709 au481 xp105 lv6 t7:220 o9:5000,10:3931 p9748f3679e00546f e09a5fdcfe0975552 r08ee9afe362a4c74`

- Cure potions quaffed: 14; Phase Door read: 7; Unknown potions quaffed: 0; Healing (outmatched) notes: 0; Potion of Speed quaffed: 1; Failed teleports: 3; Trip returns: 6; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Human Druid, Level 6/6
Exp: 305  Gold: 481  Turn: 66650
Killed on level: 2 (max. 2) by poison
```

**Character Equipment**

```
a) Whip (1d3) (+0,+0)
b) Sling (x2) (+0,+0)
c) Ring of Feather Falling
f) Wooden Torch (3931 turns)
g) Robe [2,+0]
i) Cloak [1,+0]
m) Wicker Shield of Resist Fire [2,+3]
n) Metal Cap [3,+0]
o) Set of Leather Gloves [1,+0]
p) Pair of Leather Sandals [1,+3]
```

**Character Quiver**

```
a) 24 Iron Shots (1d4) (+0,+0)
```

**Character Inventory**

```
a) 2 Books of Nature Magics [Lesser Charms]
b) Necromantic Tome [Into the Shadows]
c) Apple
d) Handful of Dried Fruits
e) 11 Rations of Food
f) 2 Potions of Speed
g) 2 Potions of Boldness
i) 2 Vermilion Potions
m) 4 Light Blue Potions
n) Scroll of Treasure Detection
o) Scroll titled "im ma per"
p) Scroll titled "cus ino deme"
q) Titanium Wand
r) 2 Wooden Torches (5000 turns)
```

**Home Inventory (page 1)**

```
a) a Handful of Dried Fruits
b) a Potion of Heroism
c) a Potion of Berserk Strength
d) a Scroll of Blessing
e) a Wooden Torch (5000 turns)
```

### Where it splits from the control `reborn-scary-ctl` (game turn 1)

```
0 1 0 Initializing the Borg... (options)
0 1 0 Initializing the Borg... (various)
0 1 0 Initializing the Borg... done.
0 1 0 # Ready...
0 1 0 # Installing keypress hook
0 1 0 # Creating a monster 'squint-eyed rogue' at (11,46), HP: 10, Index: 10
0 1 0 # Scary guy on level.
0 1 0 # Leaving (Scary guy on level)
0 1 0 # Fleeing (Scary guy on level)
0 1 0 # Standing on dn-stairs
0 1 0 # Fleeing and leaving the level. (scaryguy)
1 1 29 You enter a maze of down staircases.
```

Control at the same point:

```
0 1 0 # Standing on dn-stairs
0 1 0 # Studying spell/prayer Detect Life.
3 1 9 You have learned the verse of Detect Life.
4 11 0 # Standing on dn-stairs
4 11 0 # Flowing toward Alchemy Shop at cost 7
6 31 0 # Creating a monster 'blubbering idiot' at (18,33), HP: 2, Index: 5
```

### Last trip decisions

```
4232 38260 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
4620 42413 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
4772 44163 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
5456 51861 0 # Trip: return via search (plan 2): unknown(5 >= 5)
6103 58925 0 # Trip: return via stairs (plan 2): unknown(5 >= 5)
6185 59896 0 # Trip: return via search (plan 2): unknown(5 >= 5)
6281 60676 0 # Trip: return via search (plan 2): unknown(5 >= 5)
7010 65837 0 # Trip: return via stairs (plan 2): unknown(5 >= 5)
```

### Last 30 game messages

```
7164 66536 35 The white jelly touches you.
7164 66536 56 You are more poisoned!
7168 66537 2 You hit the white jelly.
7168 66541 0 The white jelly misses you.
7168 66546 35 The white jelly touches you.
7169 66546 56 You are more poisoned!
7172 66547 2 You hit the white jelly.
7172 66551 35 The white jelly touches you.
7172 66551 56 You are more poisoned!
7173 66556 35 The white jelly touches you.
7173 66556 56 You are more poisoned!
7177 66557 2 You hit the white jelly.
7177 66561 0 The white jelly misses you.
7177 66566 35 The white jelly touches you.
7178 66566 56 You are more poisoned!
7181 66567 2 You hit the white jelly.
7181 66571 35 The white jelly touches you.
7181 66571 56 You are more poisoned!
7182 66576 35 The white jelly touches you.
7182 66576 56 You are more poisoned!
7186 66577 2 You hit the white jelly.
7186 66581 0 The white jelly misses you.
7186 66586 0 The white jelly misses you.
7190 66587 2 You hit the white jelly.
7190 66591 35 The white jelly touches you.
7190 66591 56 You are more poisoned!
7191 66596 0 The white jelly misses you.
7198 66650 8 You die.
7199 66650 0 You have a Wicker Shield of Resist Fire [2,+3] (m).
7199 66650 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
7192 66597 0 # Loc:37,131 Dep:2 Lev:6 HP:5/54 SP:10/10 Danger:p=2
7192 66597 0 # Fleeing and leaving the level. (Looking for any stair)
7192 66597 0 # Fleeing and leaving the level (Looking for Up Stair).
7192 66597 0 # Looking for up stairs.  Going up.
7192 66597 0 # Bored but unable to flow to up stairs.
7192 66597 0 # heading up (bored and unable to dive: 9 level)
7192 66597 0 # Looking for up stairs.  Going up.
7192 66597 0 # Bored but unable to flow to up stairs.
7192 66597 0 # Boosting bravery (1) from 5 to 10!
7192 66597 0 # Fleeing and leaving the level. Brave Thinking.
7192 66597 0 # Flowing toward up-stairs at cost 25
7192 66597 0 # Looking for stairs. Flee, brave.
7193 66607 0 # There was a monster 'white jelly' at (37,132)
7193 66607 0 # Fleeing and leaving the level. (Looking for any stair)
7193 66607 0 # Flowing toward up-stairs at cost 24
7193 66607 0 # Looking for stairs. Fleeing.
7194 66617 0 # Fleeing and leaving the level. (Looking for any stair)
7194 66617 0 # Flowing toward up-stairs at cost 23
7194 66617 0 # Looking for stairs. Fleeing.
7195 66627 0 # Fleeing and leaving the level. (Looking for any stair)
7195 66627 0 # Flowing toward up-stairs at cost 22
7195 66627 0 # Looking for stairs. Fleeing.
7196 66637 0 # Fleeing and leaving the level. (Looking for any stair)
7196 66637 0 # Flowing toward up-stairs at cost 21
7196 66637 0 # Looking for stairs. Fleeing.
7197 66647 0 # Fleeing and leaving the level. (Looking for any stair)
7197 66647 0 # Flowing toward up-stairs at cost 20
7197 66647 0 # Looking for stairs. Fleeing.
7199 66650 0 # Aborting (death).
7199 66650 0 # Aborting (player died).
```

<a id="ranger-226104090-feeb5943"></a>
## Ranger Human 226104090: poison

- Dies in: `reborn-scary-named`, the same game (play `feeb5943c4eb26c8`).
- Same start elsewhere: `reborn-scary-ctl` turn_cap, `reborn-scary-damage60` turn_cap.
- Last state line: `92840 96,22 d2/3 hp-1/71 sp7/7 f1919 au874 xp178 lv7 t7:3 o4:1035,12:5000 p72c8e15c824e035e e9564e21ddfa91a6c r08ee9afe362a4c74`

- Cure potions quaffed: 22; Phase Door read: 12; Unknown potions quaffed: 0; Healing (outmatched) notes: 5; Potion of Speed quaffed: 0; Failed teleports: 19; Trip returns: 9; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Human Ranger, Level 7/7
Exp: 478  Gold: 874  Turn: 92840
Killed on level: 2 (max. 3) by poison
```

**Character Equipment**

```
a) Main Gauche (1d5) (+0,+0)
b) Short Bow (x2) (+0,+0)
f) Wooden Torch (1035 turns)
i) Cloak [1,+4]
m) Small Metal Shield [5,+0]
o) Set of Leather Gloves of Free Action [1,+4]
p) Pair of Leather Sandals [1,+4]
```

**Character Inventory**

```
a) 2 Books of Nature Magics [Lesser Charms]
b) 4 Apples
c) Handful of Dried Fruits
d) 16 Rations of Food
e) 3 Potions of Boldness
f) 5 Orange Potions
g) 5 Vermilion Potions
i) 2 Scrolls titled "tendiae sus"
m) Scroll titled "cressum nio"
n) Scroll titled "forsum ves"
o) Platinum Wand
p) 2 Wooden Torches (5000 turns)
q) Pair of Leather Sandals [1,+0]
r) Dagger (1d4) (+0,+0)
s) 2 Slings (x2) (+0,+0)
```

**Home Inventory (page 1)**

```
a) a Handful of Dried Fruits
b) a Potion of Cure Light Wounds
c) a Potion of Berserk Strength
d) 2 Scrolls of Blessing
e) a Wooden Torch (5000 turns)
```

### Where it splits from the control `reborn-scary-ctl` (game turn 280)

```
16 120 0 # Entering a '3' shop
17 120 0 # Town plan executing action 3 at shop 3 slot 0
17 120 0 # Selling Book of Nature Magics [Lesser Charms]
20 120 0 You had a Book of Nature Magics [Lesser Charms] (a).
26 130 0 # Flowing toward Home at cost 26
41 280 0 # Creating a monster 'squint-eyed rogue' at (16,25), HP: 8, Index: 10
41 280 0 # Scary guy on level.
41 280 0 # Leaving (Scary guy on level)
41 280 0 # Fleeing (Scary guy on level)
41 280 0 # Fleeing and leaving the level. (scaryguy)
41 280 0 # Fleeing and leaving the level. (Looking for any stair)
41 280 0 # Flowing toward stairs at cost 13
```

Control at the same point:

```
41 280 0 # Flowing toward Home at cost 11
42 290 0 # There was a monster 'squint-eyed rogue' at (16,25)
43 300 0 # There was a monster 'squint-eyed rogue' at (16,25)
44 310 0 # There was a monster 'squint-eyed rogue' at (16,25)
46 330 0 # There was a monster 'squint-eyed rogue' at (16,25)
51 380 0 # Entering a '7' shop
```

### Last trip decisions

```
12771 77669 0 # Trip: return via search (plan 2): unknown(5 >= 5)
13082 80719 0 # Trip: return via search (plan 2): unknown(5 >= 5)
13410 83833 0 # Trip: return via search (plan 2): unknown(5 >= 5)
13862 88052 0 # Trip: return via stairs (plan 4): unknown(5 >= 5)
13969 88934 0 # Trip: return via search (plan 4): unknown(5 >= 5)
14269 91578 0 # Trip: return via stairs (plan 4): unknown(5 >= 5)
14337 91980 0 # Trip: return via search (plan 4): unknown(6 >= 5)
14382 92280 0 # Trip: return via search (plan 2): unknown(6 >= 5)
```

### Last 30 game messages

```
14334 91971 35 The white jelly touches you.
14334 91971 56 You are more poisoned!
14334 91976 35 The white jelly touches you.
14335 91976 56 You are more poisoned!
14335 91980 82 You have found 100 gold pieces worth of copper.
14338 91981 35 The white jelly touches you.
14338 91981 56 You are more poisoned!
14338 91986 35 The white jelly touches you.
14339 91986 56 You are more poisoned!
14342 91990 0 You feel much better.
14342 91990 0 You have 2 Potions of Cure Light Wounds (e).
14342 91991 35 The white jelly touches you.
14343 91991 56 You are more poisoned!
14343 91996 35 The white jelly touches you.
14344 91996 56 You are more poisoned!
14346 92001 35 The white jelly touches you.
14346 92001 56 You are more poisoned!
14346 92006 35 The white jelly touches you.
14347 92006 56 You are more poisoned!
14360 92110 0 You feel much better.
14360 92110 0 You have a Potion of Cure Light Wounds (e).
14376 92260 0 You fall into a spiked pit!
14376 92260 0 You are impaled!
14376 92260 77 You have been given a light cut.
14380 92270 0 You feel much better.
14380 92270 53 You are no longer bleeding.
14380 92270 0 You have no more Potions of Cure Light Wounds (e).
14439 92840 8 You die.
14440 92840 0 You have a Set of Leather Gloves of Free Action [1,+4] (o).
14440 92840 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
14429 92750 0 # Flowing toward down-stairs at cost 34
14430 92760 0 # Fleeing and leaving the level. (Looking for any stair)
14430 92760 0 # Fleeing and leaving the level (Looking for Up Stair).
14430 92760 0 # Flowing toward down-stairs at cost 35
14431 92770 0 # Fleeing and leaving the level. (Looking for any stair)
14431 92770 0 # Fleeing and leaving the level (Looking for Up Stair).
14431 92770 0 # Flowing toward down-stairs at cost 36
14432 92780 0 # Fleeing and leaving the level. (Looking for any stair)
14432 92780 0 # Fleeing and leaving the level (Looking for Up Stair).
14432 92780 0 # Flowing toward down-stairs at cost 37
14433 92790 0 # Fleeing and leaving the level. (Looking for any stair)
14433 92790 0 # Fleeing and leaving the level (Looking for Up Stair).
14433 92790 0 # Flowing toward down-stairs at cost 38
14434 92800 0 # Fleeing and leaving the level. (Looking for any stair)
14434 92800 0 # Fleeing and leaving the level (Looking for Up Stair).
14434 92800 0 # Flowing toward down-stairs at cost 39
14435 92810 0 # Fleeing and leaving the level. (Looking for any stair)
14435 92810 0 # Fleeing and leaving the level (Looking for Up Stair).
14435 92810 0 # Flowing toward down-stairs at cost 40
14436 92820 0 # Fleeing and leaving the level. (Looking for any stair)
14436 92820 0 # Fleeing and leaving the level (Looking for Up Stair).
14436 92820 0 # Flowing toward down-stairs at cost 44
14437 92830 0 # Fleeing and leaving the level. (Looking for any stair)
14437 92830 0 # Fleeing and leaving the level (Looking for Up Stair).
14437 92830 0 # Flowing toward down-stairs at cost 45
14438 92840 0 # Fleeing and leaving the level. (Looking for any stair)
14438 92840 0 # Fleeing and leaving the level (Looking for Up Stair).
14438 92840 0 # Flowing toward down-stairs at cost 46
14440 92840 0 # Aborting (death).
14440 92840 0 # Aborting (player died).
```

<a id="druid-934061548-b362eb29"></a>
## Druid Half-Elf 934061548: an apprentice

- Dies in: `reborn-scary-named`, the same game (play `b362eb29fac5c0ca`).
- Same start elsewhere: `reborn-scary-ctl` turn_cap, `reborn-scary-damage60` turn_cap.
- Last state line: `40491 26,40 d2/3 hp-4/36 sp2/7 f5859 au302 xp79 lv4 t4:1,5:3 o1:5000,5:1371 p3c7ed004ca26865a ea0b6e2f6cfb63f04 r08ee9afe362a4c74`

- Cure potions quaffed: 9; Phase Door read: 7; Unknown potions quaffed: 0; Healing (outmatched) notes: 3; Potion of Speed quaffed: 0; Failed teleports: 2; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Half-Elf Druid, Level 4/4
Exp: 379  Gold: 302  Turn: 40491
Killed on level: 2 (max. 3) by an apprentice
```

**Character Equipment**

```
a) Whip (1d3) (+0,+0)
f) Wooden Torch of Brightness (1371 turns) <+1>
i) Cloak [1,+0]
```

**Character Inventory**

```
a) 2 Books of Nature Magics [Lesser Charms]
b) Apple
c) 2 Handfuls of Dried Fruits
d) 5 Rations of Food
e) 6 Flasks of oil
f) Scroll titled "aminus teo"
g) Wooden Torch (5000 turns)
```

**Home Inventory (page 1)**

```
a) a Handful of Dried Fruits
b) a Potion of Cure Serious Wounds
c) a Wooden Torch (4969 turns)
d) a Wooden Torch (5000 turns)
```

### Where it splits from the control `reborn-scary-ctl` (game turn 61)

```
6 11 0 You re-arrange your pack.
7 11 0 You combine some items in your pack.
7 11 125 You were holding a Wooden Torch (5000 turns) (d).
9 21 0 # Standing on dn-stairs
9 21 0 # Flowing toward Home at cost 24
13 61 0 # Creating a monster 'squint-eyed rogue' at (12,49), HP: 8, Index: 10
13 61 0 # Scary guy on level.
13 61 0 # Leaving (Scary guy on level)
13 61 0 # Fleeing (Scary guy on level)
13 61 0 # Fleeing and leaving the level. (scaryguy)
13 61 0 # Fleeing and leaving the level. (Looking for any stair)
13 61 0 # Flowing toward stairs at cost 4
```

Control at the same point:

```
13 61 0 # Flowing toward Home at cost 20
15 81 0 # Creating a monster 'filthy street urchin' at (14,30), HP: 3, Index: 1
16 91 0 # Creating a monster 'filthy street urchin' at (14,31), HP: 3, Index: 1
24 171 0 # Creating a monster 'filthy street urchin' at (15,31), HP: 3, Index: 1
24 171 0 # Creating a monster 'filthy street urchin' at (16,31), HP: 3, Index: 1
24 171 0 # There was a monster 'filthy street urchin' at (14,30)
```

### Last trip decisions

```
2445 20128 0 # Trip: descend via search (plan 2): below-plan(1 < 2)
2646 21828 0 # Trip: descend via search (plan 2): below-plan(1 < 2)
2679 22158 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
2829 24228 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
3271 29971 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
3391 31111 0 # Trip: descend via stairs (plan 2): below-plan(1 < 2)
3627 35272 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
4007 39852 0 # Trip: continue via none (plan 2): at-plan(2 = 2)
```

### Last 30 game messages

```
4198 40412 0 You are confused.
4198 40412 0 You spin around.
4198 40414 34 The apprentice hits you.
4198 40417 0 The acolyte tries to cast a spell, but fails.
4202 40422 0 You are confused.
4202 40422 2 You hit the apprentice.
4202 40425 34 The apprentice hits you.
4202 40426 0 The acolyte magically starts closing wounds.
4203 40426 0 The acolyte looks REALLY healthy!
4207 40432 0 You are confused.
4207 40432 0 You spin around.
4207 40436 34 The apprentice hits you.
4207 40436 34 The acolyte hits you.
4208 40440 53 You are no longer confused.
4211 40442 2 You hit the acolyte.
4211 40445 34 The acolyte hits you.
4211 40447 34 The apprentice hits you.
4214 40452 3 You miss the acolyte.
4214 40454 140 The acolyte conjures up scary horrors.
4214 40454 57 You are terrified!
4215 40458 0 The apprentice conjures up weird things.
4215 40458 55 You are confused!
4216 40461 0 The metallic green centipede wakes up.
4218 40463 34 The acolyte hits you.
4218 40469 34 The apprentice hits you.
4218 40472 0 The acolyte misses you.
4220 40480 34 The apprentice hits you.
4222 40491 34 The apprentice hits you.
4222 40491 8 You die.
4223 40491 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
4219 40472 0 # Bored, or recalling and fighting a monster on Scaryguy Level.
4219 40472 0 # Bored, or recalling and fighting a monster on Scaryguy Level.
4219 40472 0 # Bored, or recalling and fighting a monster on Scaryguy Level.
4219 40472 0 # Fleeing and leaving the level. Brave Thinking.
4219 40472 0 # Flowing toward down-stairs at cost 46
4221 40482 0 # HIT_BY:The apprentice (+)
4221 40482 0 # Monster opened door at 44,24.  That's scary.
4221 40482 0 # Tracking a monster 'acolyte' at (40,28) from (41,27)
4221 40482 0 # Tracking a monster 'metallic green centipede' at (38,20) from (38,18)
4221 40482 0 # HIT_BY:The apprentice (3)
4221 40482 0 # Scary guy on level.
4221 40482 0 # Loc:39,27 Dep:2 Lev:4 HP:0/36 SP:2/7 Danger:p=136
4221 40482 0 # Fleeing and leaving the level. (scaryguy)
4221 40482 0 # Bored, or recalling and fighting a monster on Scaryguy Level.
4221 40482 0 # Bored, or recalling and fighting a monster on Scaryguy Level.
4221 40482 0 # Bored, or recalling and fighting a monster on Scaryguy Level.
4221 40482 0 # Fleeing and leaving the level. (Looking for any stair)
4221 40482 0 # Fleeing and leaving the level (Looking for Up Stair).
4221 40482 0 # heading up (bored and unable to dive: 40 hp)
4221 40482 0 # Looking for up stairs.  Going up.
4221 40482 0 # Bored but unable to flow to up stairs.
4221 40482 0 # no up stairs found, going down
4221 40482 0 # Boosting bravery (2) from 0 to 144!
4221 40482 0 # Bored, or recalling and fighting a monster on Scaryguy Level.
4221 40482 0 # Bored, or recalling and fighting a monster on Scaryguy Level.
4221 40482 0 # Bored, or recalling and fighting a monster on Scaryguy Level.
4221 40482 0 # Fleeing and leaving the level. Brave Thinking.
4221 40482 0 # Flowing toward down-stairs at cost 45
4223 40491 0 # Aborting (death).
4223 40491 0 # Aborting (player died).
```
