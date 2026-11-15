# Fork merge verification

Owner authorized fork merges on2026-11-15, with upstream submission later. Engine PR638/639 and Borg prerequisite PR93/94 plus adapter PR95 were merged after green CI on their preserved heads. Exact merge commits/checks are recorded in the JSON receipts. No topic heads were rewritten, no upstream submissions were made, and no lab deployment or large cohort was performed.

Actual combined engine master: b4af703493d314aa35cb719604f06103aa4918f4. Actual combined Borg/toolkit master:76f25aa70b912f12005ef3cd612e4133bd16c279. An isolated build of those merged trees passes Core/SDK/content compilation and350affected store/loadout/bind/gear/parser/known-world tests in11files, with no skips in this focused gate.

A fresh seed303 Human Warrior Neo game on those merged trees reaches2000ticks alive. Its named initial stats/HP/SP, exact gear/gold, placement, all town terrain, active main RNG pool/index, Borg startup seed and post-seed main stream match the retained native C303 observations. This is additional to the eleven C/Neo pairs already retained; those22games each reached2000ticks alive. Both engine proposal heads also passed production Electron gameplay smoke. These are bounded game tests, not a representative survival cohort or whole-trajectory equivalence proof. Clock/first-world-tick lead diegoami/neo-angband-tracker#640 remains open and unpatched.

Post-merge default-branch CI was triggered normally and is separate from the recorded green pre-merge PR checks. The local combined-tree checks and game above are complete; this receipt does not claim pending default-branch workflows finished. Source issues635/636 remain open pending upstream acceptance under owner RULES9.

Extract merged-game-evidence.tgz into a fresh directory and copy pairs.json into that directory. Run the toolkit's tools/zoo/alignment/compare-startup.mjs with that copied pairs.json path. The archive includes the exact composed pack, compiled bundle, native observations, Neo run record and command/message/state logs. The compiler-order adapter remains explicitly opt-in and must not be described as a portable default-engine correction.
