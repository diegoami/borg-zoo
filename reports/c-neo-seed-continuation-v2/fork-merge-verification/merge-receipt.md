Fork merge receipt, owner-authorized 2026-11-15. Upstream submission is deferred; no upstream issue/PR/comment was posted in this merge pass.

Merged after green CI on the preserved proposal heads:

- Engine stock-order PR https://github.com/diegoami/neo-angband-tracker/pull/638 , head916ad0db1312b2037177f9f94f3486f1fac93207, merge8de069a4c14f14867316dcc61f2583019dc640e9.
- Engine starting-kit-order PR https://github.com/diegoami/neo-angband-tracker/pull/639 , headab9a5601893cef9d29ca2df601680896f00b47c6, mergeb4af703493d314aa35cb719604f06103aa4918f4 (current engine master).
- Required Borg measurement-host prerequisite https://github.com/diegoami/neo-angband-borg-mod-tracker/pull/93 , merge90e7c1d4d16ceb27beed3e1ecd6f4a524b501741.
- Required birth/options/exact-cap prerequisite https://github.com/diegoami/neo-angband-borg-mod-tracker/pull/94 , merge4defe69bf2ab5d1c34de3618b05a97b4ed57d3f5.
- Explicit seed-startup adapter https://github.com/diegoami/neo-angband-borg-mod-tracker/pull/95 , preserved head4015f0dcf564ea95f50aab6c13f39e5e56eb4ba8, merge76f25aa70b912f12005ef3cd612e4133bd16c279 (current Borg fork master).

The two stacked toolkit PRs were retargeted to master after their prerequisites merged; their published heads were not rewritten. All topic branches and upstream-candidate PRs are preserved. These are fork merges, not upstream acceptance or a lab deployment. Engine issues https://github.com/diegoami/neo-angband-tracker/issues/635 and https://github.com/diegoami/neo-angband-tracker/issues/636 remain open for upstream resolution under RULES9. The compiler-order adapter is explicit benchmark compatibility, not a portable default-engine correction.

Game evidence already retained: eleven C/Neo pairs (22games), each capped at2000ticks, all22alive at the cap. Nine Human classes plus Dwarf Warrior and High-Elf Mage. The named initial birth/gear/gold/terrain/active-RNG/startup-seed comparisons pass11/11. Both engine proposal heads additionally passed the production Electron Play-the-game smoke through birth, town, stairs, dungeon and item menus. There were four unchanged-behavior control runs. This is not a long survival comparison, and it does not establish identical later trajectories. Clock continuation lead https://github.com/diegoami/neo-angband-tracker/issues/640 remains open and unpatched.

Evidence report: https://github.com/diegoami/borg-zoo/pull/95 . The original records and frozen suites are unchanged. No large cohort was launched. Combined merged-tree local build/targeted checks and a new seed303 game are being recorded separately; default-branch CI was triggered by the normal merges.

Next: finish/record the combined-tree smoke, then investigate the clock/first-world-tick lead under common commands before a further cross-engine survival claim. Offer the preserved engine source topics upstream later, as the owner requested; do not send the compiler-specific adapter as a generic engine fix.
