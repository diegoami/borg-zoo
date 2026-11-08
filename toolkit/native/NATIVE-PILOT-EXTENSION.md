# Original Angband remaining-class pilot

Seven prespecified first-round class starts ran once each with the unchanged original runtime and pinned observer. Four natural deaths and three exact turn caps; zero failures. Together with the earlier Warrior/Mage pilot this covers all nine classes (11 attempts, nine independent starts; repeated Warrior/Mage traces match). These attempts do not count toward the fresh 1800 suite.

| Class | Seed | Outcome | Native cause | Tick | Level | Max depth | HP | Seconds |
|---|---:|---|---|---:|---:|---:|---:|---:|
| Druid | 2109297965 | death | a small kobold | 9313 | 1 | 1 | -1 | 2.312 |
| Priest | 1217781050 | death | a crow | 35223 | 3 | 1 | -3 | 7.940 |
| Necromancer | 176707408 | death | a mean-looking mercenary | 65262 | 2 | 1 | -1 | 4.621 |
| Paladin | 352388688 | turn_cap | (alive and well) | 100000 | 6 | 2 | 73 | 15.620 |
| Rogue | 1277697136 | turn_cap | (alive and well) | 100000 | 7 | 2 | 38 | 34.239 |
| Ranger | 129607500 | death | a wild cat | 55565 | 4 | 2 | -2 | 20.251 |
| Blackguard | 1751715076 | turn_cap | (alive and well) | 100000 | 6 | 2 | 72 | 29.293 |

All seven used the stable wrapper6925f0825ee40eb6a7ef9543af56d0bee70ba199852feb6182cc0ae0da10d027. The manifest was frozen before any outcomes; its SHA-256 is b31788556e43bbc891d5bd1ae751fd65e36591c212aca01458cb3f513875a40a. No seed was replaced, no attempt retried and no runtime/source changes were made.

For every natural death, final state has kind=death, dead=1 and negative HP; native cause matches both the trace and final native map. Recent messages are present. Every referenced evidence SHA-256 verifies. All attempted raw directories are retained, including censored survivors. This verifies the death export endpoint, not a cause-of-death policy diagnosis or replay fidelity.

All builds/pilots were serialized under /tmp/angband-validation.lock; the worker has stopped and released it. The four prior pilot records remain unchanged. Their metadata-only wrapper revision is disclosed in NATIVE-PILOT.md; native-run.pilot-initial.py preserves the initial bytes (a93251ee7d7e7b358f1b78055c4701f80fc5a348b0e992cfe972a3b7364fe932). Because the wrapper originally hashed its source file at record-write time, the second Warrior record names the updated on-disk file, while it loaded the initial wrapper before the edit. The immutable native runner/observer and both repeated play traces were unchanged.
