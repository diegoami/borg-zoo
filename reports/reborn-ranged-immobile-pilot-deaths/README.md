# Deaths in reborn-ranged-immobile-pilot (borg-zoo#426)

Run [44599279288](https://github.com/diegoami/borg-zoo/actions/runs/44599279288), specimen `4.2.6-reborn-rust-main-0d8b61d7`. A reading aid written by `python3 -m zoo.death_report`, not a cemetery entry or a causal diagnosis.

1 deaths in 36 games, 1 distinct dying games. Replayed locally from the run's own build artifact, arms `reborn-rangedimmobile-ctl`, `reborn-rangedimmobile-step`: every replayed play hash matches CI.

| Game | Dies in | Killed by | Char level | Dungeon level | Game turn | Keys |
|---|---|---|---|---|---|---|
| [Blackguard Human 1472012981](#blackguard-1472012981-5c9ec409) | `reborn-rangedimmobile-step` | a yellow worm mass | 6 | 1 (max 1) | 4578 | 1118 |

## Observations

- **Blackguard 1472012981 (yellow worm mass, CL6, DL1, turn 4,578; step arm only, ctl reaches the cap).**
  - **Where the game splits from ctl:** at turn 2,791 the new rule acts as designed. Next to a grey mold at CL1 with 13 of 18 HP, it noted "Stepping away from immobile grey mold, ranged first (#646)" and threw a Flask of oil at it. Ctl at the same point flowed to the up stairs instead.
  - **The death, in a different game:** 1,800 turns later, at CL6, it fought a **yellow worm mass colony** while repeatedly confused. It counted 8-9 worm masses around it ("Possibility of being surrounded (8/3)"). At 2-3 of 46 HP it kept attacking ("attack type 1, utility 14"). Two swings went into the granite wall, and one was a spin.
  - **What it had and didn't use:**
    - two unknown Shimmering Potions;
    - no Cure Light Wounds left (3 quaffed);
    - no Flasks of oil left;
    - 6 of 6 spell points.
  - **Is the rule involved?** Worm masses move, so the immobile rule does not apply to them. Nothing in the last 300 lines is a "# Stepping away" or "# Not fixing Confusion" note. As in the local run (borg-cemetery#78, borg-reborn-rs#675), the death is on a path the rule opened earlier, not a choice it made at the end.

## Handover: working on these deaths in the Borg's repository

For a session in diegoami/borg-reborn-rs that changes parameters or code against these deaths. That repository owns the Borg; the zoo only measures, and any change is measured here later as a new specimen.

- **Build:** `diegoami/borg-reborn-rs` at `0d8b61d77992f2b4fc690d5eba0296b97d92b491` (zoo specimen `4.2.6-reborn-rust-main-0d8b61d7`): `BORG_IMPL=rust harness/build.sh`, or the run's CI artifact: `gh run download 44599279288 -R diegoami/borg-zoo -n build-4.2.6-reborn-rust-main-0d8b61d7`.
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
| [Blackguard 1472012981](#blackguard-1472012981-5c9ec409) | 1472012981 | 0 (Human) | 8 | `reborn-rangedimmobile-step` | `5c9ec40907282b5f` |

In borg-zoo, `python3 -m zoo.death_report --experiment experiments/reborn-ranged-immobile-pilot.json --run 44599279288` replays and checks them all. After a change: a PR in the Borg's repository, then ask the borg-zoo session for a new specimen at the merged commit and a pilot (or verysmall) of the same arms.

<a id="blackguard-1472012981-5c9ec409"></a>
## Blackguard Human 1472012981: a yellow worm mass

- Dies in: `reborn-rangedimmobile-step`, the same game (play `5c9ec40907282b5f`).
- Same start elsewhere: `reborn-rangedimmobile-ctl` turn_cap.
- Last state line: `4578 171,20 d1/1 hp-1/46 sp6/6 f8849 au151 xp136 lv6 t4:43 o4:4662 p10c6efccaf01b2cb e41446351dfc3bd2b r08ee9afe362a4c74`

- Cure potions quaffed: 3; Phase Door read: 2; Unknown potions quaffed: 0; Healing (outmatched) notes: 3; Potion of Speed quaffed: 0; Failed teleports: 2; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Human Blackguard, Level 6/6
Exp: 236  Gold: 151  Turn: 4578
Killed on level: 1 (max. 1) by a yellow worm mass
```

**Character Equipment**

```
a) Tulwar (2d4) (+0,+0)
f) Wooden Torch (4662 turns)
m) Leather Shield [8,+0]
```

**Character Inventory**

```
a) Necromantic Tome [Into the Shadows]
b) 5 Rations of Food
c) 2 Shimmering Potions
```

**Home Inventory (page 1)**

```
a) a Wooden Torch (5000 turns)
```

### Where it splits from the control `reborn-rangedimmobile-ctl` (game turn 2791)

```
381 2791 0 # HIT_BY:The grey mold (+)
381 2791 0 # Creating a monster 'grey mold' at (11,60), HP: 2, Index: 17
381 2791 0 # Removing Regional Fear (11,60) because of a LOS grey mold
381 2791 0 # HIT_BY:The grey mold (4)
381 2791 0 # HIT_BY:The grey mold (4)
381 2791 0 # Loc:11,61 Dep:1 Lev:1 HP:13/18 SP:0/1 Danger:p=16
381 2791 0 # Stepping away from immobile grey mold, ranged first (#646)
382 2801 0 # There was a monster 'grey mold' at (11,60)
382 2801 0 # Performing attack type 2 with value 4.
382 2801 0 # Targeting grey mold who has 2 Hit Points (11,60).
382 2801 0 # Throwing painful object 'Flasks of oil'
387 2801 0 Target Selected.
```

Control at the same point:

```
381 2791 0 # Flowing toward up-stairs at cost 2
381 2791 0 # Desperate for Stairs (two)
382 2801 0 # Flowing toward dark-3 at cost 4
383 2811 0 # There was a monster 'grey mold' at (11,60)
386 2841 0 # Flowing toward dark-2 at cost 3
387 2841 0 You hit a teleport trap!
```

### Last trip decisions

```
191 1557 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
315 2211 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
520 3362 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
586 3532 0 # Trip: descend via search (plan 2): below-plan(1 < 2)
```

### Last 30 game messages

```
1078 4488 0 The yellow worm mass is no longer confused.
1082 4492 3 You miss the yellow worm mass.
1082 4494 44 The yellow worm mass crawls on you.
1082 4494 150 You feel very clumsy.
1083 4495 49 The grey mushroom patch releases spores at you.
1083 4495 55 You are more confused!
1084 4500 44 The yellow worm mass crawls on you.
1087 4502 0 You are confused.
1087 4502 2 You hit the yellow worm mass.
1087 4502 6 You have destroyed the yellow worm mass.
1091 4512 0 You are confused.
1091 4512 2 You hit the yellow worm mass.
1091 4512 6 You have destroyed the yellow worm mass.
1092 4513 49 The grey mushroom patch releases spores at you.
1093 4513 55 You are more confused!
1096 4522 2 You hit the grey mushroom patch.
1096 4522 6 You have destroyed the grey mushroom patch.
1100 4532 0 You are confused.
1100 4532 0 You chip away futilely with your weapon at the granite wall.
1101 4534 44 The yellow worm mass crawls on you.
1105 4542 0 You are confused.
1105 4542 0 You spin around.
1108 4552 0 You are confused.
1108 4552 0 You chip away futilely with your weapon at the granite wall.
1112 4562 2 You hit the yellow worm mass.
1115 4572 2 You hit the yellow worm mass.
1115 4575 44 The yellow worm mass crawls on you.
1115 4578 44 The yellow worm mass crawls on you.
1116 4578 8 You die.
1117 4578 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
1106 4552 0 # Loc:20,171 Dep:1 Lev:6 HP:2/46 SP:5/6 Danger:p=18
1106 4552 0 # Performing attack type 1 with raw utility 14 and weighted utility 22.
1106 4552 0 # Facing yellow worm mass at (21,171) who has 18 Hit Points.
1106 4552 0 # Attacking with weapon 'Tulwar (2d4) (+0,+0)'
1110 4562 0 # Tracking a monster 'yellow worm mass' at (24,171) from (23,171)
1110 4562 0 # Tracking a monster 'yellow worm mass' at (21,174) from (20,174)
1110 4562 0 # Tracking a monster 'yellow worm mass' at (22,175) from (22,176)
1110 4562 0 # Tracking a monster 'yellow worm mass' at (21,172) from (22,172)
1110 4562 0 # Tracking a monster 'yellow worm mass' at (21,170) from (21,171)
1110 4562 0 # Tracking a monster 'yellow worm mass' at (21,169) from (21,170)
1110 4562 0 # Tracking a monster 'yellow worm mass' at (20,170) from (20,169)
1110 4562 0 # Tracking a monster 'yellow worm mass' at (23,171) from (22,170)
1110 4562 0 # Possibility of being surrounded (monsters/safegrids)(8/3)
1110 4562 0 # Loc:20,171 Dep:1 Lev:6 HP:2/46 SP:5/6 Danger:p=22
1110 4562 0 # Performing attack type 1 with raw utility 14 and weighted utility 22.
1110 4562 0 # Facing yellow worm mass at (20,170) who has 17 Hit Points.
1110 4562 0 # Attacking with weapon 'Tulwar (2d4) (+0,+0)'
1113 4572 0 # HIT:the yellow worm mass (+)
1113 4572 0 # Tracking a monster 'yellow worm mass' at (20,174) from (21,173)
1113 4572 0 # Tracking a monster 'yellow worm mass' at (20,169) from (20,168)
1113 4572 0 # Creating a monster 'yellow worm mass' at (21,178), HP: 23, Index: 66
1113 4572 0 # Removing Regional Fear (21,178) because of a LOS yellow worm mass
1113 4572 0 # HIT:the yellow worm mass (2)
1113 4572 0 # Possibility of being surrounded (monsters/safegrids)(8/2)
1113 4572 0 # Loc:20,171 Dep:1 Lev:6 HP:3/46 SP:5/6 Danger:p=25
1113 4572 0 # Performing attack type 1 with raw utility 14 and weighted utility 22.
1113 4572 0 # Facing yellow worm mass at (20,170) who has 7 Hit Points.
1113 4572 0 # Attacking with weapon 'Tulwar (2d4) (+0,+0)'
1117 4578 0 # Aborting (death).
1117 4578 0 # Aborting (player died).
```
