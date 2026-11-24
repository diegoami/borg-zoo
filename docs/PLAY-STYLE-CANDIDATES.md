# Track P play-style candidates

Use this index to find changes worth testing and settings available to adopt
for their play style. Each row links to the Zoo issue and the evidence behind
the current decision. [FINDINGS.md](FINDINGS.md) holds the experiment write-ups.

## Candidates

| Candidate and issue | Evidence | Owner decision | What changes in play | Pinned evidence | What would change the decision |
| --- | --- | --- | --- | --- | --- |

*The initial backfill will be populated from recent Zoo results.*

## Evidence and decisions

- **Plausible** means a named case, a reproducible mechanism, or an early result
  gives a reason to test the change. State the smallest useful comparison and
  what it should measure.
- **Neutral so far** means a paired comparison found no measurable cost within
  its tested tier and endpoints. Record the coverage and limits of the test.
  Under [RULES 18](../RULES.md), a neutral setting can be **available to adopt
  for play style**. Describe what the owner would see the Borg do differently.
- Record the owner decision independently of the evidence. Use plain labels
  such as **Worth testing**, **Available to adopt for play style**, **Adopted**,
  or **Parked**. Keep adopted and parked rows discoverable when their context
  still matters to the current working line.

## Backfill and upkeep

1. Start with the latest completed and read Zoo runs on the Track P working
   line, then check current issues for plausible candidates awaiting results.
   Use the current baseline and recent behavior-changing PRs to bound the
   backfill. Look further back only if an older finding still bears on a live
   decision and its applicability can be explained.
2. Keep one row per decision. In **Pinned evidence**, link the run or named
   case and record the source build, tested settings and scope (tier, world,
   and class where relevant). For a delayed run, compare its pin with the
   working line before carrying forward its verdict. If a change to the
   relevant behavior makes the evidence stale, say what needs to be rechecked.
3. When a new run or owner decision lands, update the row in place. Read the
   run's gate before changing the evidence label. For a recurring digest,
   surface newly plausible candidates, newly neutral choices, and decisions
   that changed since the previous pass.
