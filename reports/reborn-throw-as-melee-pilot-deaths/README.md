# Deaths in reborn-throw-as-melee-pilot (borg-zoo#427)

Run [44599308992](https://github.com/diegoami/borg-zoo/actions/runs/44599308992), specimen `4.2.6-reborn-rust-t568-7c9b4cd1`. A reading aid written by `python3 -m zoo.death_report`, not a cemetery entry or a causal diagnosis.

2 deaths in 36 games, 1 distinct dying games. Replayed locally from the run's own build artifact, arms `reborn-throwmelee-ctl`: every replayed play hash matches CI.

| Game | Dies in | Killed by | Char level | Dungeon level | Game turn | Keys |
|---|---|---|---|---|---|---|
| [Paladin Human 766958386](#paladin-766958386-f95d63c0) | `reborn-throwmelee-ctl`, `reborn-throwmelee-throw` | poison | 3 | 0 (max 1) | 5100 | 630 |

## Observations

- **Paladin 766958386 (poison, CL3, town, turn 5,100).**
  - **How the fight started:** at CL1 with 17 of 17 HP on DL1, the Borg found a **yellow jelly** (immobile, poison touch) on the square next to it. It noted danger 1,224 ("Fleeing (excessive danger)"). Teleport failed ("Leaving (failed to teleport)"), and it was "unable to flow to up stairs". It considered Phase Door ("twitchy") but didn't read one at that point. Bravery was then boosted to 30,000, and it fought.
  - **The fight:** about 120 game turns of melee with a Main Gauche (1d5), mostly while poisoned. It drank all four Potions of Cure Light Wounds ("Healing (outmatched)") and killed the jelly at 13 HP, jumping to CL3.
  - **After the kill:** it left by the up stairs, still poisoned at 7 of 39 HP, and walked toward the Alchemy shop with 8 gold. It died of poison on the way.
  - **What it had and didn't use:**
    - **24 Flasks of oil**, never thrown, in both arms of #427. With `attack_throw_as_melee = 1` the game is byte-identical (play `f95d63c0`): every choice was attack type 1 (melee);
    - an unknown Icky Green Potion, never quaffed;
    - stepping away from the jelly. The jelly never moves. `caution_ranged_vs_immobile` (#426) is 0 on this specimen.
  - **Where it comes from:** the same start reaches the cap on 0d8b61d7 and 592c6984, so the game reaching this jelly is new on e5cc5469.

## Handover: working on these deaths in the Borg's repository

For a session in diegoami/borg-reborn-rs that changes parameters or code against these deaths. That repository owns the Borg; the zoo only measures, and any change is measured here later as a new specimen.

- **Build:** `diegoami/borg-reborn-rs` at `7c9b4cd190fe20abe6916e587d38c93eb3d62da6` (zoo specimen `4.2.6-reborn-rust-t568-7c9b4cd1`): `BORG_IMPL=rust harness/build.sh`, or the run's CI artifact: `gh run download 44599308992 -R diegoami/borg-zoo -n build-4.2.6-reborn-rust-t568-7c9b4cd1`.
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
| [Paladin 766958386](#paladin-766958386-f95d63c0) | 766958386 | 0 (Human) | 5 | `reborn-throwmelee-ctl` | `f95d63c06128f4c9` |

In borg-zoo, `python3 -m zoo.death_report --experiment experiments/reborn-throw-as-melee-pilot.json --run 44599308992` replays and checks them all. After a change: a PR in the Borg's repository, then ask the borg-zoo session for a new specimen at the merged commit and a pilot (or verysmall) of the same arms.

<a id="paladin-766958386-f95d63c0"></a>
## Paladin Human 766958386: poison

- Dies in: `reborn-throwmelee-ctl`, `reborn-throwmelee-throw`, the same game (play `f95d63c06128f4c9`).
- Same start elsewhere: none.
- Last state line: `5100 24,4 d0/1 hp-1/39 sp0/4 f8949 au8 xp42 lv3 t7:80 o2:4630,4:4996 p8f7b0a6cfc43fca8 e077dedf2fd623fcd r08ee9afe362a4c74`

- Cure potions quaffed: 5; Phase Door read: 4; Unknown potions quaffed: 0; Healing (outmatched) notes: 4; Potion of Speed quaffed: 0; Failed teleports: 2; Trip returns: 0; Trip returns followed by "going down": 0.

### Worn and carried at death

```
Borg the Human Paladin, Level 3/3
Exp: 142  Gold: 8  Turn: 5100
Killed on level: 0 (max. 1) by poison
```

**Character Equipment**

```
a) Main Gauche (1d5) (+0,+0)
f) Wooden Torch (4996 turns)
i) Cloak [1,+0]
m) Wicker Shield [2,+0]
n) Hard Leather Cap [2,+0]
p) Pair of Leather Sandals [1,+0]
```

**Character Inventory**

```
a) Holy Book of Prayers [Novice's Handbook]
b) 5 Rations of Food
c) 24 Flasks of oil
d) Icky Green Potion
e) Wooden Torch (4630 turns)
f) Dagger (1d4) (+0,+0)
```

**Home Inventory (page 1)**

```
a) a Scroll of Protection from Evil
b) a Wooden Torch (5000 turns)
```

### Last trip decisions

```
243 1351 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
326 2894 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
463 4491 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
533 4842 0 # Trip: continue via none (plan 1): at-plan(1 = 1)
614 4992 0 # Trip: descend via search (plan 2): below-plan(1 < 2)
```

### Last 30 game messages

```
585 4935 0 The draining fails.
585 4940 35 The yellow jelly touches you.
586 4940 56 You are more poisoned!
589 4940 2 You hit the yellow jelly.
589 4945 0 The yellow jelly drains your mana away.
589 4945 0 The draining fails.
593 4947 2 You hit the yellow jelly.
593 4950 35 The yellow jelly touches you.
593 4950 56 You are more poisoned!
594 4955 0 The yellow jelly drains your mana away.
594 4955 0 The draining fails.
598 4955 0 You feel much better.
598 4955 129 You are full!
598 4955 0 You have no more Potions of Cure Light Wounds (d).
599 4960 35 The yellow jelly touches you.
600 4960 56 You are more poisoned!
600 4960 129 You are no longer full.
601 4965 35 The yellow jelly touches you.
601 4965 56 You are more poisoned!
605 4965 2 You hit the yellow jelly.
605 4965 6 You have destroyed the yellow jelly.
605 4965 7 Welcome to level 2.
606 4965 7 Welcome to level 3.
606 4965 0 You can learn 1 more prayer.
609 4972 9 You have learned the prayer of Detect Evil.
612 4982 125 Your light source is a Wooden Torch (5000 turns) (f).
612 4982 125 You were holding a Wooden Torch (4630 turns) (e).
618 5022 78 You enter a maze of up staircases.
628 5100 8 You die.
629 5100 0 Score not registered for borgs.
```

### Last 30 Borg notes

```
614 4992 0 # Boosting bravery (1) from 10 to 20!
614 4992 0 # Fleeing and leaving the level. Brave Thinking.
614 4992 0 # heading down (bored and spastic).
614 4992 0 # Considering Phase (twitchy)
614 4992 0 # Boosting bravery (2) from 10 to 156!
614 4992 0 # Fleeing and leaving the level. Brave Thinking.
614 4992 0 # Flowing toward up-stairs at cost 3
614 4992 0 # Looking for stairs. Flee, brave.
615 5002 0 # Loc:23,96 Dep:1 Lev:3 HP:9/39 SP:0/4 Danger:p=7
615 5002 0 # Flowing toward up-stairs at cost 2
615 5002 0 # Desperate for Stairs (one)
616 5012 0 # Loc:22,96 Dep:1 Lev:3 HP:8/39 SP:0/4 Danger:p=7
616 5012 0 # Flowing toward up-stairs at cost 1
616 5012 0 # Desperate for Stairs (one)
617 5022 0 # Loc:21,96 Dep:1 Lev:3 HP:7/39 SP:0/4 Danger:p=3
617 5022 0 # Standing on up-stairs
617 5022 0 # Leaving via up stairs.
620 5022 0 # Standing on dn-stairs
620 5022 0 # Flowing toward Alchemy Shop at cost 16
621 5032 0 # Flowing toward Alchemy Shop at cost 15
622 5042 0 # Flowing toward Alchemy Shop at cost 14
623 5052 0 # Flowing toward Alchemy Shop at cost 13
624 5062 0 # Flowing toward Alchemy Shop at cost 12
625 5072 0 # Creating a monster 'boil-covered wretch' at (4,10), HP: 1, Index: 6
625 5072 0 # Removing Regional Fear (4,10) because of a LOS boil-covered wretch
625 5072 0 # Flowing toward Alchemy Shop at cost 11
626 5082 0 # Flowing toward Alchemy Shop at cost 10
627 5092 0 # Flowing toward Alchemy Shop at cost 9
629 5100 0 # Aborting (death).
629 5100 0 # Aborting (player died).
```
