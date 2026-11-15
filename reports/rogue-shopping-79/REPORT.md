# Does reserve shopping harm Rogues? (#79)

**Still a hypothesis.** Recomputing the existing 3,600 cells reproduces the
issue: 200 Rogue pairs, 32 rescued and 48 newly killed, exact McNemar
p = 0.092912. The new class-pairing table now exposes this comparison on the
run page, alongside finished and unfinished outcomes.

| Class | Rescued | Newly killed | p |
| --- | ---: | ---: | ---: |
| Warrior | 36 | 25 | 0.2000 |
| Mage | 39 | 36 | 0.8176 |
| Druid | 52 | 37 | 0.1374 |
| Priest | 38 | 26 | 0.1686 |
| Necromancer | 0 | 0 | — |
| Paladin | 29 | 23 | 0.4885 |
| Rogue | 32 | 48 | 0.0929 |
| Ranger | 47 | 39 | 0.4505 |
| Blackguard | 26 | 26 | 1.0000 |

Every row has 200 finished pairs. These nine class comparisons were inspected
after the aggregate result. None establishes a class-specific effect. The
Necromancer's 200 identical traces indicate no observed strategy divergence;
that does not prove every changed branch executed neutrally.

The requested Rogue-only class-mask profile (`rs-buy-class-reserve-rogue`,
bit 64) and its class-grid arm already landed in PR #80. They are preserved;
no duplicate profile, suite or large run is added. A fresh confirmation still
needs an owner-agreed primary endpoint and sample size. Extrapolated p-values
at larger sample sizes are not a power calculation. The poison-death pattern
remains a suspected Borg-policy defect for the owner to route; no Borg code
is changed here.

The [verification receipt](verification.json) records every class's full
paired counts, the immutable results-branch commit, two source run IDs and
SHA-256 hashes. Reproduce with the two files at that commit:

```sh
curl -fLsS https://raw.githubusercontent.com/diegoami/borg-zoo/0504c76ffe5af3d2b2205923151ffe471f4af834/results/rs-family-buying-classes-1800/43024249204-1/cells.jsonl -o /tmp/control.jsonl
curl -fLsS https://raw.githubusercontent.com/diegoami/borg-zoo/0504c76ffe5af3d2b2205923151ffe471f4af834/results/rs-family-buying-classes-1800/43024253226-1/cells.jsonl -o /tmp/reserve.jsonl
python3 reports/rogue-shopping-79/recompute.py /tmp/control.jsonl /tmp/reserve.jsonl
```

No recorded result is rewritten. This report reanalyses completed runs; it
is not a new confirmation or a claim that either policy is better.
