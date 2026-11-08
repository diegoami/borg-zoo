# Original Angband native pilot

Four attempts, two prespecified independent starts; all alive at the exact native world-tick cap 100000. Each repeated trace, including all recorded RNG states, matches byte for byte. This is a toolkit pilot, not the requested 1800-game result and not an observer-neutrality proof.

| Seed | Race/class | Repeat | Outcome | Ticks | Level | Max depth | HP | Decisions | Wall seconds |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| 884072154 | Human Warrior | 1 | turn_cap | 100000 | 10 | 5 | 110 | 9142 | 35.468 |
| 884072154 | Human Warrior | 2 | turn_cap | 100000 | 10 | 5 | 110 | 9142 | 34.553 |
| 2097768768 | Human Mage | 1 | turn_cap | 100000 | 3 | 1 | 25 | 2975 | 8.547 |
| 2097768768 | Human Mage | 2 | turn_cap | 100000 | 3 | 1 | 25 | 2975 | 8.547 |

Original source e473720ed88a0f0c7ca66815cef3000eb4a38bc3; observer/harness fc9d97cb46aa0aaa27773e5c83a41ec395d515fc. Compiler/platform/data/binary identities are in build.json and source-proof/source-seal.json. All four native final maps, raw traces, configs, input, messages and result records are retained.

Birth assignment used ordinary menus and matched Human Warrior/Human Mage. No C corrections, munchkin or cheat-death settings were introduced. Source seal: 1119 original files unchanged; seven disclosed hook/CMake edits and three added observer/version files.

Both pilot starts survived, so these four attempts do not validate the natural-death output path. No seed was replaced after observing results. The existing unchanged runner classifies death separately from timeout/stall/crash/harness failures; the fresh 1800 suite must retain every attempt.

Observer hooks record without RNG draws or policy replacement; seeding and termination are the declared harness controls. Repeated traces are not a comparison to an uninstrumented run. Native normal-speed action cost100 versus energy10/tick yields10 ticks per action. The source cap is checked after turn++ and is exact.

The native clock is unchanged and calendar/timezone are recorded (2026-11-08, CET). A wrapper preflight/metadata update happened during the first attempt; per-record wrapper digests differ, while the immutable native runner/observer and both repeated play traces remain identical. The final wrapper is frozen at 6925f0825ee40eb6a7ef9543af56d0bee70ba199852feb6182cc0ae0da10d027.

Missing birth-stat/gear snapshots, raw key-command streams, save/replay qualification and causal death analysis remain explicit limitations. Existing result.character has a legacy fixed Human Warrior label; native-record.actual_birth and CHARACTER trace are authoritative.

For larger suites retain all raw directories and maps with --keep; record wall900/stall90/cap100000 before starting. Four sequential pilot game runtimes totaled 87.115 seconds. These two seeds are not a population throughput estimate; freeze sufficient shards and preserve job truncation/failures.
