# The 17 non-mushroom deaths of track-p 9085c266 (full tier), replayed on the heads

Run [45028029063](https://github.com/diegoami/borg-zoo/actions/runs/45028029063), experiment `reborn-trackp-9085c266-full`
(#645), specimen `4.2.6-reborn-rust-trackp-9085c266`, arm `reborn-head-shipped`, 900 starts of `classes-1800-full`, 100,000 turns.
28 deaths: 11 are grey mushroom patch deaths, the other 17 are the subject of this page.

This is an investigation page for the Borg's repository: **leads, not fixes**. Every lead names the seed and the game turns where it can
be seen, on a build where the same game is played again key for key. "Verified" means read in the logs, the key stream or the source at the
pinned commit. "Inference" means not checked.

## Reproduction on the current heads (verified)

Played locally with the zoo's own `borgrs.build` and `borgrs.run_cell`. The settings are each build's shipped `harness/borg.txt` plus the
arm `reborn-head-shipped` (`borg_reborn_core = borg-rs`, `borg_reborn_errand = none`). The specimen entries were held in memory: the
catalogue's `4.2.6-reborn-rust-trackp-4b2c2fcf` pins a ref that is not a commit (#663 fixes it).

- **Local 9085c266:** 17 of 17 play hashes are identical to the zoo cells. The local runs play the zoo's games.
- **track-p head `4b2c2fcf913e352ebd7bef5f16a531e8fc50d92a`:** **15 of 17 still die, each in the identical game** (same play hash
  as 9085c266). The two town deaths survive to the cap. Between 9085c266 and 4b2c2fcf the Borg's code changes only in #899, the
  cursed-light swap (`borg_cursed.rs`, `borg_light.rs`), and in `borg_junk.rs`; the frontend's build capture also changes.
- **main head `c29664e1d378d63e3e61f716ffdc2146b2f53ca0`:** **0 of 17 die**, and all 17 games are identical to the zoo's f57499d0
  games (same play hash; f57499d0 is run 44976971265, the same 900 starts). Main adds the same four files to f57499d0 that track-p
  adds to 9085c266.
  - Main also saves both f57499d0 town deaths, which were the same torch loop: 653243095 and 1965910635 now reach the cap.
    1965910635 logs one `# Replacing cursed Wooden Torch` instead of looping.

**So the 15 deaths come from track-p-only code**, the ten PRs from f57499d0 to 9085c266: #864 town room, #874 kill-on-sight, #875
point-blank throws, #873 variety and Phase Door, #868 confused attack, #892 Recall forecast, #888/#894 light radius (shipped 0), #905
full-pack junk, #904 ship confused attack.

**Where track-p and main split (verified, first differing key in `keys.log`): in every one of the 15, during the first town visit.**

| Seed | Turn | track-p does | main does |
|---|---|---|---|
| 1312323730 | 91 | leaves the General Store for the Alchemist | buys 2 rations |
| 1294425391 | 111 | leaves for the Alchemist | buys 15 flasks of oil |
| 312081895 | 121 | a different key at the same message context (not identified) | |
| 901451811 | 121 | a different key during the torch purchase | |
| 453254028 | 151 | 6 Phase Door first | 7 CLW first |
| 592754909 | 171 | 6 Phase Door | 1 CSW |
| 1895660873 | 231 | Alchemist: 6 Phase Door | Weaponsmith first |
| 857532386 | 241 | 6 Phase Door | 1 CSW |
| 1398933929 | 341 | 6 Phase Door | 1 CSW |
| 1024822556 | 441 | 6 Phase Door | 6 CLW |
| 17626119 | 441 | a different key during the torch purchase | |
| 1194051723 | 531 | 6 Phase Door | 35 flasks of oil |
| 681096527 | 541 | 6 Phase Door | 2 CLW |
| 2125189042 | 831 | 6 Phase Door | 9 CLW |
| 282602274 | 991 | 3 Phase Door | 2 Phase Door |

- **In 9 of the 15, track-p buys Phase Door where main buys CLW, CSW or oil.** This is #873 (staples and `town_phase_reserve` 6 at 150%).
  In one more (282602274) it buys more Phase Door. Two split in the torch purchase and two skip a purchase main makes.
- **This is where the games split, not what killed them.** After the split every later event differs; it says nothing about the fight at
  the end.
- 15 of 15 is no measured effect of #873. The whole tier had 17 non-mushroom deaths on 9085c266 against 14 on f57499d0, two-sided exact
  test p = 0.72.

## The 15 deaths that still happen on 4b2c2fcf, with their lead

Turn windows are game turns. Notes are the Borg's own lines from `messages.log`; "check" is `trace-core.jsonl`'s decision name. "Left at
death" is the gear at death, from the recorder replay.

| Seed | Character, CL/DL | Killer | Where to look | Lead | Left at death |
|---|---|---|---|---|---|
| 453254028 | Half-Elf Necro 1/1 | Grip | 3262–3421 | A Phase Door lands next to a grey mushroom patch. Then `Attack on sight: grey mushroom patch (kill-on-sight)` while confused: 5 swings into walls ("chip away futilely", "spin around"). Grip and a wild dog kill it. | 0 CLW, 5 Phase |
| 857532386 | Elf Necro 6/2 | Grip | 49674–49773 | Eight confused kill-on-sight swings at the patch, all into walls, while Grip bites it from 35 to −3 HP. The trace has danger 204–212 and `fight_before_flight` every turn. | 15 CLW, 1 CSW, 12 Phase, 3 Speed |
| 1398933929 | Dwarf Necro 1/1 | wild cat | 1812–1830 | Fast-fragile attack on sight: 2 oil throws, no hit. The Borg rates the cat at "7.6 damage/turn = 95% of HP 8"; it took 9. | 9 CLW, 6 Phase |
| 592754909 | Kobold Mage 2/1 | crow | 3521–3574 | `Emergency use of an Attack Spell` with no mana: "You faint… paralysed". The same mechanism killed f57499d0's 1378676237. | 4 CLW, 1 CSW, 5 Phase |
| 2125189042 | Half-Troll Necro 2/1 | crow | 8280–8350 | After a Phase Door at 2/17 HP, the check is `borg_recover` (rest) with the crow on the level. | 12 CLW, 7 Phase |
| 681096527 | Elf Ranger 2/1 | crow | 8980–9024 | Two arrows, one hit; HP 18 → 1 in two turns. Shoots a kobold at 1 HP. No CLW bought at any visit. | 0 CLW, 4 Phase |
| 1294425391 | Elf Priest 1/1 | wild cat | 12306–12397 | At 2/11 HP it melees the cat on sight: the heal ban, `fast_fragile_no_heal = 1`. | 4 CLW, 0 Phase, no Recall |
| 1194051723 | Elf Paladin 1/1 | fatal wound | 1551–1700 | Fang: 6 oil throws, 1 hit. All 5 CLW drunk; Phase Door only at 2 HP; dies bleeding. After each miss: `Guessing wall (50,87) near target (51,88)`, and (50,87) is the Borg's own grid. | 0 CLW, 5 Phase |
| 1024822556 | Dunadan Druid 1/1 | Fang | 2342–3086 | 74 player turns of flight. `Refusing flight Recall` 51 times (exposure 107–144 HP); 5 tries at a lock; all 8 CLW and 6 Phase used. The wall guess lands on the Borg's own grid here too. | 0 CLW, 0 Phase |
| 312081895 | Half-Troll Blackguard 4/2 | poison | 39389–39700 | Two-step loop: `borg_flow_dark` steps west next to an immobile white jelly, `borg_caution` steps back east, about 10 times, HP 52 → 8. Before that: the last Word of Recall read at 10848, a trapdoor at 10990, 29,000 turns on DL2 with "no up stairs found". | 0 CLW, 10 Phase, no Recall |
| 1895660873 | Gnome Ranger 3/1 | poison | 16453–16670 | In a corridor of white worm masses with "Bored but unable to flow to up stairs", `Boosting bravery (2) from 7 to 100`; melee goes on at 1 HP while poisoned. 0 gold and no Recall. | 6 CLW, 2 Neutralize Poison |
| 17626119 | Gnome Priest 3/1 | small kobold | 7905–8105 | A confusion trap, then 7 confused swings (check `borg_attack`), 1 hit, HP 25 → −1. No cure, although CLW lowers confusion by 20 (`object.txt`). | 4 CLW, 3 Neutralize Poison |
| 1312323730 | Elf Warrior 5/1 | kobold archer | 24784–24984 | `Invisible monster nearby`, then `borg_recover` (rest) 18 times at danger 0 while "You are hit by something sharp!", 39 → −1 HP. | 10 CLW, 6 Phase |
| 282602274 | Hobbit Ranger 1/1 | grey mold | 5444–5467 | After one arrow the mold reads "0 Hit Points". `borg_flow_old` walks next to it at danger 0. Spores 12 → 5 HP, then a melee miss. | 6 CLW, 10 Phase |
| 901451811 | Hobbit Priest 4/2 | wild cat | 48192–48294 | A paralysis trap ("strange white mist") at full HP; killed while paralysed. No decision to look at. | 3 CLW, 2 CSW |

**Nine of the 15 died with cure potions in the pack** (gear dump), ten with the paralysed priest.

## Leads by group

1. **Kill-on-sight on the grey mushroom patch while a moving monster attacks (453254028, 857532386). track-p-only code.**
   - `attack_on_sight` runs inside `fight_before_flight` (`borg_think_dungeon.rs:763`), before the cures and flight.
   - For a `kill-on-sight` entry it is gated only by `category_attack_safe_with(…, false)`: `other_danger <= HP ×
     caution_flee_danger_hp_multiplier` (2, `borg_caution.rs:2828`).
   - That gate held while Grip bit the Borg from 35 to 6 HP. Lead: what `other_danger` is for an adjacent Grip in these thinks.
   - These two belong with the 11 mushroom deaths, so **13 of the 28** deaths involve the patch.
2. **Fast-fragile cats and crows (1398933929, 592754909, 2125189042, 681096527, 1294425391).**
   - The #842 settings and `borg_fast_fragile.rs` are identical on main and track-p, and f57499d0's full tier also lost 3 games to crows.
     So this is the same policy meeting different games.
   - Sub-leads, each one seed:
     - the incoming damage per turn is rated below what the cat did (1398933929, 1822);
     - an emergency attack spell is cast without mana (592754909, 3562; f57499d0 1378676237, 7431);
     - a rest at 2/17 HP with 12 CLW (2125189042, 8342);
     - the heal ban at 2 HP with 4 CLW (1294425391, 12396).
3. **Fang at CL1 (1194051723, 1024822556).**
   - Oil at point blank mostly misses (1 of 6 and 3 of 6), and every CLW and Phase Door goes before the end.
   - Lead, effect unknown: after a missed throw at an adjacent target, the guessed wall is the Borg's own grid.
4. **Loops.**
   - The cursed-torch loop is fixed on both heads (verified above).
   - Still present on 4b2c2fcf: the `borg_flow_dark` ↔ `borg_caution` two-step beside an immobile white jelly (312081895). The
     danger is 0 on the far grid and 36 on the near one, so each check undoes the other.
5. **Singles.**
   - Rest under an unseen archer at danger 0 (1312323730).
   - An HP estimate of 0 for a wounded mold, then a step next to it (282602274).
   - The bravery boost overriding cures at 1 HP while poisoned (1895660873).
   - Confused melee after a confusion trap with CLW unused (17626119).
6. **Two deaths without Word of Recall (312081895, 1895660873).**
   - Both read their last scroll and left town without another. One had 0 gold. The other had 235 gold and bought only a torch, with
     `buy_recall_from_gold` 200 on track-p.
   - Whether the price or the #864 Recall curve explains that is inference.

## Filed in borg-reborn-rs (2026-11-22)

New issues, label `bug`:
- [#980](https://github.com/diegoami/borg-reborn-rs/issues/980): emergency attack spell with no mana (592754909; f57499d0 1378676237).
- [#981](https://github.com/diegoami/borg-reborn-rs/issues/981): rests at danger 0 under an unseen archer (1312323730).
- [#982](https://github.com/diegoami/borg-reborn-rs/issues/982): rests at 2/17 HP with 12 CLW after a crow (2125189042).
- [#983](https://github.com/diegoami/borg-reborn-rs/issues/983): confused melee with CLW unused; `caution_confused_clw_cure` ships 0 (17626119).
- [#984](https://github.com/diegoami/borg-reborn-rs/issues/984): leaves town with 235 gold and no Word of Recall (312081895).
- [#985](https://github.com/diegoami/borg-reborn-rs/issues/985): the bravery boost overrides cures while poisoned (1895660873).
- [#986](https://github.com/diegoami/borg-reborn-rs/issues/986): Fang at CL1, "winning" while oil lands 1 in 6 (1194051723, 1024822556).
- [#987](https://github.com/diegoami/borg-reborn-rs/issues/987): a 127-gold Ranger buys Phase Door first and no CLW (681096527); measured by
  borg-zoo#669.

New cases added as comments to existing issues:
- [#974](https://github.com/diegoami/borg-reborn-rs/issues/974): 857532386, Grip while confused by a patch.
- [#929](https://github.com/diegoami/borg-reborn-rs/issues/929): 1194051723 and 1024822556, the guessed wall on the Borg's own grid. The source path is
  named there.
- [#932](https://github.com/diegoami/borg-reborn-rs/issues/932): 312081895, the `borg_flow_dark` against `borg_caution` two-step.
- [#975](https://github.com/diegoami/borg-reborn-rs/issues/975): 282602274, a grey mold at 0 HP.
- [#926](https://github.com/diegoami/borg-reborn-rs/issues/926): 1294425391, the heal ban at 2 HP; 1398933929, "the next turn kills" on mean
  damage.

## What this cannot show, and what would settle it

- **Whether any one change caused any one death.** The games split in the first town visit, so a seed that survives on main shows only a
  different path. A paired arm on track-p with #873's staples and Phase Door reserve set back would measure that; dispatching it is the
  owner's call.
- **Whether the potions would have saved the cat, crow, archer and mold cases.** That needs counterfactual replays from a saved state at the
  turns above (borg-cemetery cases; the dossiers for all 28 are on branch `runs/2026-11-22-trackp-9085-full-deaths`).
- **The values behind the leads:**
  - `other_danger` in group 1;
  - why the archer's danger and the mold's HP read 0;
  - why the confusion cure did not fire for 17626119.

  A replay with a counter or a trace line at those turns settles each.
- 900 starts give 15 non-mushroom deaths on 9085c266 (17 less the two patch-and-Grip deaths) and 14 on f57499d0: no rate claim either way.

## Reproduce one death on 4b2c2fcf

Build `diegoami/borg-reborn-rs` at `4b2c2fcf913e352ebd7bef5f16a531e8fc50d92a` with `BORG_IMPL=rust harness/build.sh`.

`OUT/user/borg.txt` is the shipped `harness/borg.txt` with these lines overridden:
- `borg_respawn_race` = the race index and `borg_respawn_class` = the class index (table below);
- `borg_cheat_death` and `borg_respawn_winners` = `FALSE`;
- `borg_reborn_core = borg-rs` and `borg_reborn_errand = none`.

Also copy `harness/scary_monsters.txt` into `OUT/user/` and create empty `save/`, `archive/`, `panic/` and `scores/` under `OUT`. Then,
from `build/rust/game`:

```
env -u BORG_PROFILE -u BORG_CORE -u BORG_ERRAND -u BORG_PLAN TZ=UTC LANG=C.UTF-8 LC_ALL=C.UTF-8 \
  ./angband -mborgh -n -uBorg -duser=$OUT/user -dsave=$OUT/save -darchive=$OUT/archive -dpanic=$OUT/panic -dscores=$OUT/scores \
  -- -seed SEED -race R -class C -turns 100000 -keylog $OUT/keys.log -summary $OUT/summary.json -menu-letters \
  -exact-turns -statelog $OUT/state.log -msglog $OUT/messages.log
```

`sha256sum keys.log` must start with the hash below; it is the same on 9085c266.

| Seed | -race | -class | Play sha256 (4b2c2fcf = 9085c266) |
|---|---|---|---|
| 1194051723 | 2 Elf | 5 Paladin | `7fb11d46a041a04a` |
| 1398933929 | 5 Dwarf | 4 Necromancer | `9653a0d480ef1dd2` |
| 1024822556 | 8 Dunadan | 2 Druid | `3687ca84c5cdeb34` |
| 453254028 | 1 Half-Elf | 4 Necromancer | `dc80aab7809ff55b` |
| 592754909 | 10 Kobold | 1 Mage | `b13a6f0fc76ff016` |
| 282602274 | 3 Hobbit | 7 Ranger | `13e34b27193b2e8c` |
| 17626119 | 4 Gnome | 3 Priest | `2412238a8aa2949c` |
| 2125189042 | 7 Half-Troll | 4 Necromancer | `6f2825472c67b78f` |
| 681096527 | 2 Elf | 7 Ranger | `665b0b0cf9c3af43` |
| 1294425391 | 2 Elf | 3 Priest | `48c375a0737f6a60` |
| 1895660873 | 4 Gnome | 7 Ranger | `31c994254ecdb188` |
| 1312323730 | 2 Elf | 0 Warrior | `7243fba61d12f4b2` |
| 312081895 | 7 Half-Troll | 8 Blackguard | `4aa99f20ea1ca7e6` |
| 901451811 | 3 Hobbit | 3 Priest | `1e3dbe93416cda9a` |
| 857532386 | 2 Elf | 4 Necromancer | `651b016bd55a467b` |

The two town deaths on 9085c266 (968685682 Gnome Blackguard, 375646941 Half-Elf Rogue, the cursed-torch loop) reach the cap on
4b2c2fcf: `7fe5dc4ddc467c21` and `cf1240f4f3110d73`.
