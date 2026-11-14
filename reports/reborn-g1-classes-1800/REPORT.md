# borg-reborn-rs G1 and #183: arm B (guard on), against arm A and the C control

For borg-reborn-rs #128 (G1) and #183 (the half-hit-point travel guard). Descriptive report generated from the stored cells; nothing here is a claim of improvement (RULES 8).

## What was measured

| | |
|---|---|
| Suite | `classes-1800`: 9 classes x 200 seeds, assigned birth, one game per seed |
| Turn cap T | 100,000 engine turns, exact boundary |
| Arm A (guard off, main) | borg-reborn-rs `3113c2e222a97665aa4ae122f4a2fed5c58c6feb`, run 43501324055 (`results/reborn-g1-classes-1800/43501324055-1`) |
| Arm B (guard on) | borg-reborn-rs `5f626d1777ede2042f894e904d662d2a82a606f3` (A plus the guard), run 43501327741 (`results/reborn-g1-classes-1800/43501327741-1`) |
| C control | `angband-e473-original` (angband `e473720`), run 43024245702 (`results/original-c-20261111-classes-1800/43024245702-1`), not rerun |
| Build | `harness/build.sh`, `BORG_IMPL=rust`, defaults profile, no `BORG_PROFILE` (docs/ZOO-INTERFACE.md), `exact_turns` and `depth_stream` on |
| Depth D | 5 |
| Primary endpoint | per class and overall, the share of cells whose max depth reached D = 5 by T |
| Non-inferiority margin | **5 percentage points** (owner message of 2026-11-13, this report's instruction). The experiment file stored with run 43501327741 says 10 points; both are shown, 5 is the one this report is judged on |
| Interval method | Wilson for each share; for B - C a paired Wald 95% interval over the per-seed differences (A, B and C play the same 1,800 seeds). Non-inferior when the lower bound is above minus the margin |
| Unfinished cells | none in A, B or C (all 1,800 finished) |

Max depth was read from `final.max_depth`; it agrees with `first_turn_at_depth["5"] <= T` in every cell of all three runs.

cells where max_depth>=5 and first_turn_at_depth[5]<=T disagree: 0

## 1. Primary endpoint: share reaching depth 5 by T=100,000, B against the C control (paired by seed)
Difference = B minus C, percentage points, paired Wald 95% interval. Non-inferior when the lower bound > -margin.
| Class | Cells | B reaches D (95% CI) | C reaches D (95% CI) | B-C pts [95% CI] | B-only/C-only | Non-inferiority |
|---|---|---|---|---|---|---|
| Warrior | 200 | 0.0% [0.0%, 1.9%] | 34.0% [27.8%, 40.8%] | -34.0 [-40.6, -27.4] | 0/68 | 5pt: not shown / 10pt: not shown |
| Mage | 200 | 0.0% [0.0%, 1.9%] | 1.0% [0.3%, 3.6%] | -1.0 [-2.4, +0.4] | 0/2 | 5pt: NON-INFERIOR / 10pt: NON-INFERIOR |
| Druid | 200 | 0.0% [0.0%, 1.9%] | 1.5% [0.5%, 4.3%] | -1.5 [-3.2, +0.2] | 0/3 | 5pt: NON-INFERIOR / 10pt: NON-INFERIOR |
| Priest | 200 | 0.0% [0.0%, 1.9%] | 1.5% [0.5%, 4.3%] | -1.5 [-3.2, +0.2] | 0/3 | 5pt: NON-INFERIOR / 10pt: NON-INFERIOR |
| Necromancer | 200 | 0.0% [0.0%, 1.9%] | 0.0% [0.0%, 1.9%] | +0.0 [+0.0, +0.0] | 0/0 | 5pt: NON-INFERIOR / 10pt: NON-INFERIOR |
| Paladin | 200 | 0.0% [0.0%, 1.9%] | 0.5% [0.1%, 2.8%] | -0.5 [-1.5, +0.5] | 0/1 | 5pt: NON-INFERIOR / 10pt: NON-INFERIOR |
| Rogue | 200 | 0.0% [0.0%, 1.9%] | 9.0% [5.8%, 13.8%] | -9.0 [-13.0, -5.0] | 0/18 | 5pt: not shown / 10pt: not shown |
| Ranger | 200 | 0.0% [0.0%, 1.9%] | 11.0% [7.4%, 16.1%] | -11.0 [-15.3, -6.7] | 0/22 | 5pt: not shown / 10pt: not shown |
| Blackguard | 200 | 0.0% [0.0%, 1.9%] | 3.5% [1.7%, 7.0%] | -3.5 [-6.1, -0.9] | 0/7 | 5pt: not shown / 10pt: NON-INFERIOR |
| **Overall** | 1800 | 0.0% [0.0%, 0.2%] | 6.9% [5.8%, 8.2%] | -6.9 [-8.1, -5.7] | 0/124 | 5pt: not shown / 10pt: NON-INFERIOR |

Context, A against the C control:
| Class | Cells | A reaches D (95% CI) | C reaches D (95% CI) | A-C pts [95% CI] | A-only/C-only | Non-inferiority |
|---|---|---|---|---|---|---|
| Warrior | 200 | 0.0% [0.0%, 1.9%] | 34.0% [27.8%, 40.8%] | -34.0 [-40.6, -27.4] | 0/68 | 5pt: not shown / 10pt: not shown |
| Mage | 200 | 0.0% [0.0%, 1.9%] | 1.0% [0.3%, 3.6%] | -1.0 [-2.4, +0.4] | 0/2 | 5pt: NON-INFERIOR / 10pt: NON-INFERIOR |
| Druid | 200 | 0.0% [0.0%, 1.9%] | 1.5% [0.5%, 4.3%] | -1.5 [-3.2, +0.2] | 0/3 | 5pt: NON-INFERIOR / 10pt: NON-INFERIOR |
| Priest | 200 | 0.0% [0.0%, 1.9%] | 1.5% [0.5%, 4.3%] | -1.5 [-3.2, +0.2] | 0/3 | 5pt: NON-INFERIOR / 10pt: NON-INFERIOR |
| Necromancer | 200 | 0.0% [0.0%, 1.9%] | 0.0% [0.0%, 1.9%] | +0.0 [+0.0, +0.0] | 0/0 | 5pt: NON-INFERIOR / 10pt: NON-INFERIOR |
| Paladin | 200 | 0.0% [0.0%, 1.9%] | 0.5% [0.1%, 2.8%] | -0.5 [-1.5, +0.5] | 0/1 | 5pt: NON-INFERIOR / 10pt: NON-INFERIOR |
| Rogue | 200 | 0.0% [0.0%, 1.9%] | 9.0% [5.8%, 13.8%] | -9.0 [-13.0, -5.0] | 0/18 | 5pt: not shown / 10pt: not shown |
| Ranger | 200 | 0.0% [0.0%, 1.9%] | 11.0% [7.4%, 16.1%] | -11.0 [-15.3, -6.7] | 0/22 | 5pt: not shown / 10pt: not shown |
| Blackguard | 200 | 0.0% [0.0%, 1.9%] | 3.5% [1.7%, 7.0%] | -3.5 [-6.1, -0.9] | 0/7 | 5pt: not shown / 10pt: NON-INFERIOR |
| **Overall** | 1800 | 0.0% [0.0%, 0.2%] | 6.9% [5.8%, 8.2%] | -6.9 [-8.1, -5.7] | 0/124 | 5pt: not shown / 10pt: NON-INFERIOR |

## 2. B against A (3113c2e guard off -> 5f626d1 guard on), paired by seed
Dead at T = died before the cap. A-only/B-only deaths = seeds where only A / only B died. Medians A -> B; sign test on the paired change (ties dropped).
| Class | Cells | Dead at T: A -> B | A-only / B-only deaths | McNemar p | Max depth | Max level |
|---|---|---|---|---|---|---|
| Warrior | 200 | 10 (5.0%) -> 11 (5.5%) | 9 / 10 | 1.0000 | 1 -> 1; B higher 19, lower 0, p=0.000 | 1 -> 2; B higher 122, lower 11, p=0.000 |
| Mage | 200 | 25 (12.5%) -> 83 (41.5%) | 11 / 69 | 0.0000 | 1 -> 1; B higher 7, lower 2, p=0.180 | 1 -> 2; B higher 107, lower 17, p=0.000 |
| Druid | 200 | 83 (41.5%) -> 130 (65.0%) | 15 / 62 | 0.0000 | 1 -> 1; B higher 8, lower 0, p=0.008 | 1 -> 1; B higher 42, lower 7, p=0.000 |
| Priest | 200 | 35 (17.5%) -> 59 (29.5%) | 19 / 43 | 0.0032 | 1 -> 1; B higher 12, lower 1, p=0.003 | 1 -> 2; B higher 113, lower 15, p=0.000 |
| Necromancer | 200 | 39 (19.5%) -> 95 (47.5%) | 15 / 71 | 0.0000 | 1 -> 1; B higher 5, lower 1, p=0.219 | 1 -> 1; B higher 87, lower 13, p=0.000 |
| Paladin | 200 | 18 (9.0%) -> 40 (20.0%) | 9 / 31 | 0.0007 | 1 -> 1; B higher 11, lower 3, p=0.057 | 1 -> 2; B higher 120, lower 14, p=0.000 |
| Rogue | 200 | 11 (5.5%) -> 23 (11.5%) | 3 / 15 | 0.0075 | 1 -> 1; B higher 5, lower 0, p=0.062 | 1 -> 2; B higher 110, lower 12, p=0.000 |
| Ranger | 200 | 18 (9.0%) -> 53 (26.5%) | 6 / 41 | 0.0000 | 1 -> 1; B higher 9, lower 0, p=0.004 | 1 -> 2; B higher 117, lower 12, p=0.000 |
| Blackguard | 200 | 6 (3.0%) -> 9 (4.5%) | 4 / 7 | 0.5488 | 1 -> 1; B higher 14, lower 3, p=0.013 | 1 -> 2; B higher 108, lower 15, p=0.000 |
| **Overall** | 1800 | 245 (13.6%) -> 503 (27.9%) | 91 / 349 | 0.0000 | 1 -> 1; B higher 90, lower 10, p=0.000 | 1 -> 2; B higher 926, lower 116, p=0.000 |

Deaths B adds: 349 seeds (B died, A did not). Deaths B removes: 91.
By group, added: {'Monster': 304, 'Poison': 35, 'Hunger': 10} | removed: {'Hunger': 21, 'Monster': 70}
| Cause (deaths B adds) | Seeds |
|---|---|
| floating eye | 36 |
| poison | 35 |
| small kobold | 30 |
| soldier | 27 |
| Grip, Farmer Maggot's Dog | 19 |
| Fang, Farmer Maggot's Dog | 17 |
| giant yellow centipede | 15 |
| wild dog | 14 |
| acolyte | 12 |
| starvation | 10 |
| black naga | 10 |
| kobold | 10 |
Added deaths by class: {'Ranger': 41, 'Necromancer': 71, 'Druid': 62, 'Priest': 43, 'Mage': 69, 'Paladin': 31, 'Warrior': 10, 'Rogue': 15, 'Blackguard': 7}
Added deaths: median death turn (B) = 10807; median max depth (B) = 1; median level = 2

## 3. Descriptive
Deaths and top causes per arm (overall):
  A: 245 deaths (13.6%); groups {'Hunger': 29, 'Monster': 210, 'Poison': 6} ; top [('small kobold', 36), ('starvation', 29), ("Fang, Farmer Maggot's Dog", 19), ('battle-scarred veteran', 17), ("Grip, Farmer Maggot's Dog", 13)]
  B: 503 deaths (27.9%); groups {'Monster': 451, 'Hunger': 14, 'Poison': 38} ; top [('small kobold', 56), ('floating eye', 42), ('poison', 38), ("Fang, Farmer Maggot's Dog", 35), ('soldier', 33)]
  C: 619 deaths (34.4%); groups {'Monster': 584, 'Poison': 29, 'Lava': 6} ; top [("Grip, Farmer Maggot's Dog", 69), ("Fang, Farmer Maggot's Dog", 45), ('wild cat', 40), ('soldier', 39), ('giant white mouse', 30)]

Deaths per class (A / B / C):
| Class | A | B | C |
|---|---|---|---|
| Warrior | 10/200 | 11/200 | 64/200 |
| Mage | 25/200 | 83/200 | 62/200 |
| Druid | 83/200 | 130/200 | 141/200 |
| Priest | 35/200 | 59/200 | 48/200 |
| Necromancer | 39/200 | 95/200 | 66/200 |
| Paladin | 18/200 | 40/200 | 37/200 |
| Rogue | 11/200 | 23/200 | 76/200 |
| Ranger | 18/200 | 53/200 | 86/200 |
| Blackguard | 6/200 | 9/200 | 39/200 |

First turn at each depth, median over cells that reached it (share reaching), overall:
| Depth | A: share · median turn | B: share · median turn | C: share · median turn |
|---|---|---|---|
| DL1 | 97.5% · 391 | 99.3% · 381 | 100.0% · 861 |
| DL2 | 0.6% · 4,272 | 3.2% · 20,112 | 67.1% · 19,434 |
| DL3 | 0% · – | 0.1% · 57,710 | 22.3% · 60,656 |
| DL4 | 0% · – | 0% · – | 12.0% · 60,416 |
| DL5 | 0% · – | 0% · – | 6.9% · 61,597 |
| DL6 | 0% · – | 0% · – | 5.3% · 56,618 |
| DL8 | 0% · – | 0% · – | 4.1% · 65,100 |
| DL10 | 0% · – | 0% · – | 2.1% · 65,058 |

Share reaching DL5 by class (A / B / C) and median first turn at DL5:
| Class | A | B | C |
|---|---|---|---|
| Warrior | 0% · – | 0% · – | 34.0% · 61,114 |
| Mage | 0% · – | 0% · – | 1.0% · 78,348 |
| Druid | 0% · – | 0% · – | 1.5% · 57,901 |
| Priest | 0% · – | 0% · – | 1.5% · 66,212 |
| Necromancer | 0% · – | 0% · – | 0% · – |
| Paladin | 0% · – | 0% · – | 0.5% · 37,005 |
| Rogue | 0% · – | 0% · – | 9.0% · 54,391 |
| Ranger | 0% · – | 0% · – | 11.0% · 76,122 |
| Blackguard | 0% · – | 0% · – | 3.5% · 64,911 |

## Reading

- **Neither arm gets off dungeon level 1.** 0 of 1,800 cells in A and in B reach depth 5, and DL2 is reached by 0.6% of A and 3.2% of B (median max depth 1 in both, against 6.9% reaching DL5 for the C control). The primary endpoint therefore cannot separate A from B: it is 0% in both. Where the control also barely reaches DL5 (Mage, Druid, Priest, Necromancer, Paladin: 0 to 1.5%) the arms are within the 5-point margin trivially, because there is nothing to lose.
- **Non-inferiority at 5 points: not shown overall** (B - C = -6.9 points, 95% interval -8.1 to -5.7), nor for Warrior (-34.0), Ranger (-11.0), Rogue (-9.0) or Blackguard (-3.5, interval -6.1 to -0.9). At the 10-point margin the stored experiment file names, the overall result would read non-inferior (lower bound -8.1) while Warrior, Rogue and Ranger would still fail. The verdict flips with the margin, so the two margins are reported side by side; the owner should confirm which one was fixed first.
- **Survival: B dies much more than A** (503 against 245 of 1,800, 27.9% against 13.6%; 349 seeds B-only deaths against 91 A-only, McNemar p < 0.0001). The increase sits in the caster classes and the Ranger (Necromancer +56 points, Mage +29, Druid +23, Ranger +17, Priest +12, Paladin +11); Warrior and Blackguard are unchanged. Both arms stay alive at the cap largely by staying shallow, so A's lower death rate comes with the same lack of progress.
- **Causes of the 349 deaths B adds:** monsters 304 (floating eye 36, small kobold 30, soldier 27, Grip 19, Fang 17), poison 35, starvation 10. B also removes 91 deaths, 21 of them starvation. The added deaths come at a median turn of 10,807, median character level 2, max depth 1. A death by floating eye is the classic result of attacking one, which the cells do not show; this is a lead, not a finding.
- **Level:** B reaches a higher character level than A in 926 of 1,042 seeds that differ (median 2 against 1), and a deeper max depth in 90 against 10: B plays more, and dies more.
- Cell-level reading of why A and B stay at depth 1 is not in this report; it is a question for borg-reborn-rs.
