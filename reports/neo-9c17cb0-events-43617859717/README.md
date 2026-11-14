# Neo event-host cohort: completed run and death triage

[Run 43617859717](https://github.com/diegoami/borg-zoo/actions/runs/43617859717), completed 2026-11-14 20:49 UTC. [Pinned cells](https://github.com/diegoami/borg-zoo/blob/458395d628b9ab2982d77a4f53a823f5d606d286/results/neo-fork-9c17cb0-events-classes-1800/43617859717-1/cells.jsonl), [metadata](https://github.com/diegoami/borg-zoo/blob/458395d628b9ab2982d77a4f53a823f5d606d286/results/neo-fork-9c17cb0-events-classes-1800/43617859717-1/meta.json), [evidence manifest](https://github.com/diegoami/borg-zoo/blob/458395d628b9ab2982d77a4f53a823f5d606d286/results/neo-fork-9c17cb0-events-classes-1800/43617859717-1/evidence-status.json). Results commit `458395d628b9ab2982d77a4f53a823f5d606d286`. Development suite, descriptive single arm; no paired treatment/control or confirmed survival effect.

Borg `9c17cb0c582fe129008899491372787e91abdade`; engine `06a2321ce30a414df20d1b20d486446e7688171c`; toolkit `02c33cf1871b86ea8e8d7bf8cbc870cf177b736b`; zoo `7f1611e0e0801957307a9bbb8ee55d15a46ee36b`. All 1,800 records agree on these pins and Node v26.13.1. Linux runners include AWS and Azure kernels. Frozen classes-1800, assigned ordinary birth, default settings, 100,000-turn cap; 180 shards, two processes/job, eight concurrent jobs.

## Every outcome

1,800 unique cells, zero missing. Deaths 1,352 (75.11% of all assigned cells); turn caps 415; stalls 32; wall timeout 1. Deaths among death/cap endpoints are 1,352/1,767 (76.51%); this denominator excludes the 33 abnormal outcomes explicitly, never silently. Evidence completeness is reported true on all 1,800 manifests; this review did not download every raw archive.

| Class (200 each) | Death | Cap | Stall | Timeout |
|---|---:|---:|---:|---:|
| Blackguard | 105 | 78 | 17 | 0 |
| Druid | 177 | 20 | 3 | 0 |
| Mage | 186 | 13 | 0 | 1 |
| Necromancer | 178 | 21 | 1 | 0 |
| Paladin | 144 | 52 | 4 | 0 |
| Priest | 130 | 69 | 1 | 0 |
| Ranger | 159 | 40 | 1 | 0 |
| Rogue | 151 | 47 | 2 | 0 |
| Warrior | 122 | 75 | 3 | 0 |

1,099/1,352 deaths (81.3%) occur at character levels 1–2: 715 at level 1 and 384 at level 2. Grip and Fang together account for 273 deaths, 166 at level 1.

| Recorded cause | Deaths |
|---|---:|
| Grip, Farmer Maggot's Dog | 139 |
| Fang, Farmer Maggot's Dog | 134 |
| wild cat | 100 |
| giant yellow centipede | 98 |
| crow | 86 |
| small kobold | 81 |
| giant white mouse | 63 |
| grey mold | 63 |
| poison | 56 |
| grey mushroom patch | 54 |
| a fatal wound | 52 |
| soldier | 44 |
| wild dog | 35 |
| fruit bat | 35 |
| cave spider | 26 |
| giant white centipede | 24 |
| cutpurse | 19 |
| blue yeek | 19 |

A recorded killer is an endpoint, not proof of the decision that caused it. Poison and fatal wounds can outlast the attacker. Counts do not identify how many deaths any particular repair would prevent.

## Ranked causal findings and open attribution

1. **CONFIRMED replay; existing C-origin defect:** Druid102023799, grey mold9582 (corrected acceptance cohort, not one of these 1,800 cells). At9546 HP5/12 retreats from danger16 to stairs; at9556 exploration reuses know1/icky0 and walks west back into danger16, repeats at9576 and dies9582. [TS flow.ts:568–579](https://github.com/diegoami/neo-angband-borg-mod-tracker/blob/9c17cb0c582fe129008899491372787e91abdade/src/flow/flow.ts#L568) matches [C borg-flow.c:434–440](https://github.com/angband/angband/blob/e473720ed88a0f0c7ca66815cef3000eb4a38bc3/src/borg/borg-flow.c#L434): emergency flow marks know before skipping danger. Existing canonical [neo-angband-tracker#404](https://github.com/diegoami/neo-angband-tracker/issues/404). Distinct from repaired port invalidations. Native owner evidence was not rerun here. Do not silently correct C policy in the faithful-port lane.


2. **CONFIRMED engine defect, independent legal control plus exact-hash stall replay:** High-Elf Blackguard406779093 stalls87095 after blind gas87075 and a blindness cure87085. At87095: HP41/46, blindness0, fueled Brightness torch4408 turns, Borg LIGHT4, current cell VIEW=true/glow=false; Core refuses every read. In engine06a2321c, `session/game.ts:1880–1882,2386–2388` refreshes the view from `onTransition`; `player/timed.ts:370–379` invokes that callback BEFORE assigning `p.timed[idx]=v`. `game/known.ts:1299–1305` consequently supplies the OLD blindness value to the view. Core `game/obj-cmd.ts:1282–1283` tests SEEN, not the Borg's LIGHT trait or VIEW bit. [Current C player-timed.c:893–907](https://github.com/angband/angband/blob/e473720ed88a0f0c7ca66815cef3000eb4a38bc3/src/player-timed.c#L893) and imported4.2.6 f308221 have assignment first, then visual update/handle_stuff. Existing upstreamNeo220 is CLOSED; this ordering defect survives its callback-count-only tests (`game/timed-transition.test.ts:168–204`). Treat this as a new recurrence linked to220, not grounds to reopen its resolved historical scope.

   [Standalone real-Core reproducer](blind-view-probe.mjs), Node26, with the built pinned engine and composed pack from the normal zoo build: `node blind-view-probe.mjs ENGINE_CHECKOUT PACK_DIRECTORY`. It uses ordinary seed303 High-Elf Blackguard, no Borg or source mutation. Before: blind0/seen=true/light2; set blind10: seen stays true; cure: blind0/seen=false; explicit `updateFov` control: seen=true. [Recorded output](blind-view-proof.json). This proves the ordering failure, not that it causes every one of the10 dark-reading stalls. No engine correction was implemented.

3. **CONFIRMED recorded port omission; not a death:** Priest199095980 stalls34576, repeating Remove Curse and answering `Uncurse which item?` with cancel. Raw shard111 was downloaded; archive hash and all files of this target cell match the results manifest. [TS item-decurse.ts:59–69](https://github.com/diegoami/neo-angband-borg-mod-tracker/blob/9c17cb0c582fe129008899491372787e91abdade/src/item/item-decurse.ts#L59) emits the verb without choosing the cursed item; [API2 controller.ts:66–71](https://github.com/diegoami/neo-angband-borg-mod-tracker/blob/9c17cb0c582fe129008899491372787e91abdade/src/api2/controller.ts#L66) cancels an item prompt without a pending handle. [C borg-item-decurse.c:129–148](https://github.com/angband/angband/blob/e473720ed88a0f0c7ca66815cef3000eb4a38bc3/src/borg/borg-item-decurse.c#L129) chooses the item and then the curse. Eight of the 18 read stalls end in repeated Remove Curse messages. PR87 deliberately excluded this unresolved FIRST_CURSED seam; this is not evidence that its recharge/identify fix regressed. The seven other instances were classified from cell tails, not each replayed.

4. **CONFIRMED recorded liveness failure; underlying terrain cause unresolved:** Half-Elf Mage1713737383 reaches turn64444, HP4/13, depth1, and emits 5,228 tunnel commands at that same turn (directions8:1782,2:1775,3:1671), ending with `You see nothing there to tunnel.` It times out at2700s. Raw shard1 archive and every target-cell file hash match. [TS API2 controller.ts:149–156](https://github.com/diegoami/neo-angband-borg-mod-tracker/blob/9c17cb0c582fe129008899491372787e91abdade/src/api2/controller.ts#L149) resets its counter when the exact command changes, so rotating directions evades release. This guard is a host adapter, with no direct C equivalent; the C flow/terrain reason for the commands remains unproved. Do not count it as a death or cure it by extending the timeout.

5. **CONFIRMED exact-hash replay; C retreat branch present, saving alternative unproved:** High-Elf Ranger1780052628, grey mushroom487. At388 HP15 on(146,13), approaches the mushroom(146,11). At408 HP13 on(146,12), danger408 and confused: restored desperate stairs chooses south toward the stair. Repeated confusion redirects movement into walls; HP falls13→11→10→8→7→3→2→1. [TS retreat.ts:46–47](https://github.com/diegoami/neo-angband-borg-mod-tracker/blob/9c17cb0c582fe129008899491372787e91abdade/src/fight/retreat.ts#L46) corresponds to [C borg-caution.c:1355–1364](https://github.com/angband/angband/blob/e473720ed88a0f0c7ca66815cef3000eb4a38bc3/src/borg/borg-caution.c#L1355), which attempts nearby upstairs without a confusion gate; strategic retreat is confusion-gated in both ([C:1433](https://github.com/angband/angband/blob/e473720ed88a0f0c7ca66815cef3000eb4a38bc3/src/borg/borg-caution.c#L1433)). Imported4.2.6 caution has the same branch. This case proves the restored branch runs; it does not prove full-controller C equivalence or that removing the branch saves this character.

6. **CONFIRMED exact-hash replay; unsafe approach attribution incomplete:** Kobold Paladin1373700124, floating eye975. At760 HP15, eye(91,61), player(91,64), danger0, noRetreat10; walks north. At780 player(91,63), danger0, noRetreat9; walks north into paralysis range. No later controller command occurs before death. [C danger.c:2417–2419](https://github.com/angband/angband/blob/e473720ed88a0f0c7ca66815cef3000eb4a38bc3/src/borg/borg-danger.c#L2417) and [TS danger.ts:1371](https://github.com/diegoami/neo-angband-borg-mod-tracker/blob/9c17cb0c582fe129008899491372787e91abdade/src/danger/danger.ts#L1371) suppress immobile melee danger beyond adjacency; [C think-dungeon.c:2089,2143](https://github.com/angband/angband/blob/e473720ed88a0f0c7ca66815cef3000eb4a38bc3/src/borg/borg-think-dungeon.c#L2089) has the same5/10 no-retreat fallback. Why the flow accepted the adjacent destination and whether a C controller would do so are not yet established. An adjacent-danger scalar alone is insufficient to call it a port defect.

7. **CONFIRMED exact-hash replay; incomplete visibility attribution:** Hobbit Rogue1954874415, grey mold762. Last command is west at752 after opening a door742; mold strikes twice at753, white icky thing touches759, mold kills762. A second exact-hash diagnostic replay captures the final encounter: at702–752 the API2 monster list stays empty and danger stays0, despite LIGHT2 and a glowing current cell. The final open/walk therefore happens without a known enemy; it is not a stale cache for an already-known mold. The cause of the missing perception remains unproved. Do not group this automatically with #404.

8. **Dog policy remains substantially C-derived:** corrected acceptance Half-Elf Necromancer1574344917, Fang8363: atHP12 the first-step danger4 fails C's strict `>= floor(HP*4/10)=4` check ([C caution.c:1551–1557](https://github.com/angband/angband/blob/e473720ed88a0f0c7ca66815cef3000eb4a38bc3/src/borg/borg-caution.c#L1551)). Prior exact-hash replay and stage checks establish this rejection, not a dog-specific repair. Visible names ending in commas can fail exact race lookup: current C also formats NAME_COMMA in mon-desc.c:224–226, retains it in borg-messages.c:605, and exact-compares names in borg-flow-kill.c:1164; imported4.2.6 has the same lookup. This supports a C-origin lead, not a newly confirmed port bug or a demonstrated cause of all273 dog deaths.

## Other abnormal outcomes

32 stalls:18 read,9 tunnel,2 walk,2 rest,1 hold. Of the read stalls,10 end `You have no light to read by.` and8 repeat Remove Curse. A representative dark-reading stall has the confirmed engine ordering cause above; the other nine require individual attribution. Nine tunnel stalls spend turns chipping futilely; these are separate from the zero-turn alternating-direction timeout. Seventeen stalls are Blackguards. Every abnormal record remains in the cohort.

## Validation and limits

Three newly replayed death command streams (eye1373700124, mushroom1780052628, mold1954874415) match their completed-run SHA256 exactly. The dark-reading Blackguard replay also matches its command hash; the final-mold diagnostic replay preserves its original hash. Instrumentation is in scratch copies, not source worktrees; replays use the correct message/event host and the shared flock validation lock. Raw shards1/89/111 were downloaded and archive SHA256 verified; every retained file of target cells1713737383/406779093/199095980 matches its manifest. See evidence.json for receipts and selected records. Prior corrected-acceptance Druid/Fang and first-shard centipede receipts remain on port issues88/89 and zoo PR89.

No source fix, merge, changed assertion, seed, cap or timeout follows from this report. No full native C controller replay was performed. No claim that all deaths have been attributed. The historical48afb65 cohort used a message-deaf host: comparing its1,500 deaths with these1,352 cannot isolate the effect of the three port repairs. Native C worlds/births differ too and are not paired Neo controls.

Next: route the engine blindness ordering recurrence with its standalone control, route the unresolved Remove Curse choice, and investigate the missing mold perception and eye approach separately from canonical C404. Keep source/integration/host PRs unmerged pending the owner's separate merge approval.
