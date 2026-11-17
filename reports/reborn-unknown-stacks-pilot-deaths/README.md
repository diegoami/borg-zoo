# Deaths in reborn-unknown-stacks-pilot (borg-zoo#170)

This report covers the deaths in [run 44054277431](https://github.com/diegoami/borg-zoo/actions/runs/44054277431): `reborn-bundle-none-speed30` on `4.2.6-reborn-rust-speed-fight` (binary cdfee89a) with `borg_trip_unknown_stacks` 2, 3, 4 and 5. It is a reading aid, not a cemetery entry or a causal diagnosis.

Three arms (unknown2, unknown3 and the control unknown5) were replayed locally from the CI build artifact with traces kept. All 54 replayed games matched their CI `play_sha256`. The unknown4 arm was not replayed: its Ranger death has the same play hash as unknown3. Each death's equipment, inventory and home, its last 300 log lines and its trip decisions are in `evidence/`.

There are 12 deaths in 72 games, but only 5 distinct games:

| Start | Arms where it dies | Killed by | Char level | Dungeon level | Game turn | Escapes and healing left |
|---|---|---|---|---|---|---|
| Blackguard Half-Elf 888896726 | all four (same game) | a giant white mouse | 4 | 1 | 57,520 | no potions; 9 unread scrolls of 3 unknown kinds |
| Druid Half-Elf 934061548 | all four (same game) | a crow | 2 | 1 | 27,401 | none; SP 4/4 unspent |
| Rogue Human 1502695781 | unknown2 only | a white worm mass | 3 | 1 (max 2) | 27,060 | none; 8 Flasks of oil, 4 Potions of Boldness |
| Ranger Half-Elf 1739161339 | unknown3, unknown4 (same game) | a giant yellow centipede | 6 | 2 (max 3) | 74,797 | none known; unknown potions (8 Light Yellow, 1 Smoky) and 3 unknown scroll kinds |
| Ranger Half-Elf 1739161339 | unknown5 (control) | a fatal wound (bleeding) | 5 | 2 (max 3) | 58,170 | quaffed an unknown potion at 1 HP: Blindness |

## What unknown_stacks changed: the trip "return" goes down when no up stair is known

Where unknown2 and unknown3 play differently from the control, the game splits at a trip decision `Trip: return via search: unknown(N >= threshold)`. In each case the Borg next logs `Looking for up stairs. Going up.`, then `Bored but unable to flow to up stairs.` and `no up stairs found, going down`. So a decision to go back to town to learn unknown items is carried out as a descent whenever no up staircase is known.

- **Ranger 1739161339, unknown3:** the return fired 16 times between game turns 46,061 and 74,045, with 4 to 5 unknown stacks. None of them reached town: after each it went between DL2 and DL3. It had used its only Word of Recall at turn 3,668. It died on DL2 still carrying the unknown items the trip was meant to identify.
- **Rogue 1502695781, unknown2:** the return fired 4 times from turn 17,052 (2 unknown stacks). The first two went to DL2 instead of town. The third reached town at turn 21,168. There it sold its unknown potions (one was a Potion of Heroism) and bought 2 Phase Door scrolls, a Potion of Boldness, 5 Flasks of oil and wine. Before dying it used up both Phase Door scrolls and all 5 Cure Light Wounds potions, and threw oil 9 times, but none after its last potion at turn 26,832. It died at 1/22 HP while backing away from a white worm mass, with no escape left. In the control this start reaches the turn cap.
- **Blackguard 888896726:** the return fired twice in unknown2 (2 and 3 unknown stacks), but it was already fleeing and the game's keys were identical to the control's. The setting made no difference to this death.

## Each death

### Blackguard 888896726: giant white mouse, DL1, character level 4, same game in every arm

This is the same game as in the #164 pilot report (same play hash).

- **Equipment:** Tulwar (2d4), Wooden Torch, Leather Shield.
- **Inventory:** Necromantic Tome, 5 Rations of Food, 12 Pints of Fine Wine, and three unread kinds of unknown scroll (3, 2 and 4 of them).
- **Gold:** 22.
- **Death:** at 1/41 HP it kept fighting breeding mice while logging `Scary guy on level`, `Looking for Up Stair` and `no up stairs found, going down`. It never read the unknown scrolls.

### Druid 934061548: crow, DL1, character level 2, same game in every arm

- **Equipment:** Whip (1d3), Wooden Torch.
- **Inventory:** Lesser Charms, 5 Rations of Food, 12 Pints of Fine Wine, a Scroll of Detect Invisible, 2 Wooden Torches.
- **Gold:** 33.
- **Death:** it drank its last Cure Light Wounds potion and read its last Phase Door scroll, then meleed the crow with the whip (`attack type 1`) at 4/19 HP. Its SP were 4/4 and it cast nothing.

### Rogue 1502695781 (unknown2): white worm mass, DL1, character level 3

- **Equipment:** Dagger (1d4), Wooden Torch, Soft Leather Armour, Wicker Shield, Leather Gloves.
- **Inventory:** 5 Rations of Food, 16 Pints of Fine Wine, 8 Flasks of oil, 4 Potions of Boldness, 4 Wooden Torches.
- **Home:** 2 Scrolls of Blessing, a Wooden Torch.
- **Gold:** 37.
- **Death:** poisoned and at 1 to 4 HP, it kept backing up and flowing toward an up staircase (`Desperate for Stairs`). The worm mass kept breeding into its path, and it died with 8 Flasks of oil unthrown in this last fight.

### Ranger 1739161339 (unknown3 and unknown4): giant yellow centipede, DL2, character level 6

- **Equipment:** Main Gauche (1d5), Short Bow (x2), Robe, Cloak [1,+5], Leather Sandals, 29 Arrows.
- **Inventory:** 2 copies of Lesser Charms, food, a Flask of oil, 8 Potions of Boldness, a Smoky Potion, 8 Light Yellow Potions, 8 + 1 + 1 unknown scrolls, a spare Robe.
- **Gold:** 304.
- **Death:** at 10/47 HP it meleed a cutpurse while a giant yellow centipede bit and stung it. At 5/47 it turned on the centipede with the Main Gauche, still in melee with a bow and arrows equipped. Earlier `Fleeing (failed to teleport)` notes show it had no teleport.

### Ranger 1739161339 (unknown5, control): bleeding, DL2, character level 5

- **Equipment:** Main Gauche, Short Bow, Wooden Torch of Brightness, Robe, Leather Gloves of Free Action, Leather Sandals, 62 Arrows.
- **Inventory:** food, 5 Potions of Boldness, a Smoky Potion, 4 Light Yellow Potions, 3 Scrolls of Treasure Detection, 8 + 1 unknown scrolls.
- **Gold:** 201.
- **Death:** a wild cat brought it to 1/34 HP with a cut, after its last Cure Light Wounds potion and a failed teleport (`Fleeing (failed to teleport)`). It took the stairs twice. Then, still bleeding at 1 HP, it quaffed an unknown Light Yellow Potion, which was Blindness, and died of the wound 3 game turns later.

## Handover: working on these deaths in borg-reborn-rs

This section is for a borg-reborn-rs session that changes parameters or code against these deaths. borg-reborn-rs owns the Borg. The zoo only measures, and any change is measured here later as a new specimen.

### What to start from

- **Build:** borg-reborn-rs `193d9076747cd5c52e1fe1f6ea314570d8f3873a` (zoo specimen `4.2.6-reborn-rust-speed-fight`, binary sha256 `cdfee89a…`). Build it with `BORG_IMPL=rust harness/build.sh` (docs/ZOO-INTERFACE.md), or use CI's artifact `build-4.2.6-reborn-rust-speed-fight` from run 44054277431: `gh run download 44054277431 -R diegoami/borg-zoo -n build-4.2.6-reborn-rust-speed-fight`.
- **Settings:** `evidence/borg-txt/` holds the exact `user/borg.txt` of the three replayed arms, written for the Rogue (race 0, class 6). They differ only in `borg_trip_unknown_stacks` (2, 3, 5). For another character, change `borg_respawn_race` and `borg_respawn_class`. No plan file is used.
- **Evidence:** `evidence/<death>/` has `inventory-at-death.txt`, `messages-tail.log`, `trip-decisions.log`, `summary.json` and `borg-log.txt`.

### Re-running one death

From the built `game/` directory, with no `BORG_*` variables in the environment (the zoo clears them), and `OUT` holding a `user/` with the arm's `borg.txt` plus empty `save/ archive/ panic/ scores/`:

```sh
env -u BORG_PROFILE -u BORG_CORE -u BORG_ERRAND -u BORG_PLAN TZ=UTC LANG=C.UTF-8 LC_ALL=C.UTF-8 \
  ./angband -mborgh -n -uBorg -duser=$OUT/user -dsave=$OUT/save -darchive=$OUT/archive -dpanic=$OUT/panic -dscores=$OUT/scores \
  -- -seed SEED -race R -class C -turns 100000 -keylog $OUT/keys.log -summary $OUT/summary.json -menu-letters \
  -exact-turns -statelog $OUT/state.log -msglog $OUT/messages.log
```

`sha256sum keys.log` must equal the play hash below; if it doesn't, it isn't the same game.

| Death | Seed | -race | -class | Arm (`borg_trip_unknown_stacks`) | Play sha256 (first 16) |
|---|---|---|---|---|---|
| Rogue, white worm mass | 1502695781 | 0 (Human) | 6 | 2 | `cce831e533b1038c` |
| Ranger, giant yellow centipede | 1739161339 | 1 (Half-Elf) | 7 | 3 (4 plays the same game) | `b9cce8f0a62b` |
| Ranger, bleeding after unknown potion | 1739161339 | 1 (Half-Elf) | 7 | 5 | `79fa531f5b3b` |
| Blackguard, giant white mouse | 888896726 | 1 (Half-Elf) | 8 | any | `4ad4df8138935dbd` |
| Druid, crow | 934061548 | 1 (Half-Elf) | 2 | any | `b08aec02a1c347db` |

In borg-zoo, `python3 -m zoo.deaths --experiment experiments/reborn-unknown-stacks-pilot.json --run 44054277431` replays and checks all of them (borg-zoo PR #180).

### Where to look first (observations, not diagnoses)

1. **A trip return for unknown items becomes a descent.** When no up staircase is known, `Trip: return … unknown(N >= threshold)` is followed by `no up stairs found, going down`. The value-3 Ranger did this 16 times and never reached town. Compare the Rogue's and the value-3 Ranger's `trip-decisions.log` with the control's split shown above.
2. **The Borg doesn't use what it carries when cornered.**
   - The Rogue died with 8 Flasks of oil.
   - The Blackguard died with 9 unread scrolls.
   - The Druid died with 4/4 spell points unspent.
   - The value-3 Ranger meleed with a bow and 29 arrows equipped.
3. **An unknown potion quaffed as a last resort at 1 HP** (control Ranger: Blindness, then death by bleeding).

### After a change

Commit it in borg-reborn-rs with a PR there. Then ask the borg-zoo session for a new specimen at the merged commit and a pilot (or verysmall) of the same arms, to compare with run 44054277431.
