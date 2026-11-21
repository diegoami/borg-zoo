---
name: propose-config
description: Propose changes to borg-reborn-rs's main configuration (the shipped harness/borg.txt) from what the zoo has measured - for each shipped setting, the evidence for its value against the alternatives tried, a recommendation (change, keep, needs confirmation) and the exact borg.txt lines, plus a ready-to-file borg-reborn-rs issue. Use when the owner asks what main should ship, which defaults to change, whether a tested flag should be turned on or off, or types /propose-config (optionally with a setting or an issue as focus).
---

# /propose-config

Propose what borg-reborn-rs `main` should ship in `harness/borg.txt`, from zoo evidence.
**Propose only.** The zoo does not change Borgs (RULES 1) and never edits another
repository or its issues (RULES 2). The output is a proposal for the owner, plus an issue
body for borg-reborn-rs that the owner files (or asks a borg-reborn-rs session to file).

## 1. What main ships now

1. Find current main without touching any other session's checkout:
   `gh api repos/diegoami/borg-reborn-rs/commits/main -q .sha`, then
   `gh api "repos/diegoami/borg-reborn-rs/contents/harness/borg.txt?ref=SHA" -q .content | base64 -d`.
   Every non-comment `name = value` line is a shipped setting.
2. For each `borg_param_*` line, the compiled default and its meaning are in
   `borg-core/src/params.rs` at that SHA (`NAME => (default, unit, min, max, source, "meaning")`).
   Settings read by the shell (e.g. `borg_trip_*`, `borg_scary_list`) are documented in
   `borg.txt`'s own comments.
3. Note which settings ship a value **different from the compiled default**: those are
   the owner's earlier decisions, and the evidence behind each is what to re-examine.
4. **Which zoo specimen is current main?** Find the catalogue specimen whose `ref` is that
   SHA, or the newest one before it (`catalogue/specimens.json`). Then count what changed
   since: `git log SPECIMEN_REF..SHA --oneline` in a scratch clone. A merge that "changes
   play" means the evidence on the older specimen is for a different game.

## 2. The evidence for each setting

1. Fetch with `git fetch origin results:refs/remotes/origin/results`, then check out
   `git worktree add --detach ../zoo-results origin/results` and run
   `python3 -m zoo.history --results ../zoo-results/results --pool --json /tmp/history.json`.
   Narrow with `--match SETTING_NAME` for each shipped setting you examine.
2. For a setting, collect every entry where an arm differs from its control in that
   setting only (or a factorial where it is one dimension). For each, record:
   - the specimen ref, and whether it is current main or how many play-changing merges behind;
   - the tier and starts (pilot 18; small 90; with medium 360; with big 900; full 1,800);
   - deaths per arm, rescued / newly killed and McNemar p against the **shipped value's**
     arm (not just against the run's control), mean final level and deepest level;
   - identical plays: an arm that played the shipped arm's keys on most starts did not test
     anything.
3. Read the death and behaviour evidence too: `docs/FINDINGS.md`, the issue's result comments
   (they carry note counts such as Phase Door departures or trip returns), the cemetery's
   death dossiers for the run (`runs/zoo-*` in borg-cemetery), and any stall or loop found in
   an arm (a real loop is a defect to fix, whatever the death counts say).
4. Owner decisions in `docs/OPEN-WORK.md` and on the issue override the evidence: if the
   owner chose a value on purpose (for example "a Phase Door floor was rejected"), report the
   evidence but do not propose against the decision without saying so.

## 3. Grade each setting

Use these grades, strongest first, and never upgrade one:

| Grade | When | Proposal |
|---|---|---|
| **Change: confirmed** | a prespecified confirmation on fresh starts passed for the alternative (RULES 8) | change the shipped line |
| **Change: strong lead** | at least medium tier (360 starts) on current main's game, the alternative beats the shipped value with p < 0.05 after correcting for the comparisons in that run, and no class or progress cost | propose the change *and* the confirmation run that would make it confirmed |
| **Lead, needs confirmation** | the same direction at two tiers, or p < 0.2 at medium or larger, on current main's game | keep the shipped value for now; propose the next tier or a confirmation (hand it to `/next-experiments`) |
| **Neutral: simplify** | no difference at ≥ 360 starts, and the setting costs nothing either way | propose the simpler value (usually the compiled default) only if it removes behaviour no one asked for; otherwise keep |
| **Neutral: fixes a known failure** | no difference overall, but the targeted failure (a named death, a loop) is fixed with no cost in level or depth | propose shipping it, saying plainly that it fixes a case and does not lower deaths overall |
| **Shipped value is harmful** | the shipped arm is worse than an alternative at ≥ 360 starts (same bar as strong lead), or it causes stalls or loops | propose reverting, with the evidence |
| **Not enough evidence** | pilot only, or only on an older game | no change; say what run would answer it |

Alongside the evidence grade, label tested values harmful, neutral or helpful
when the evidence supports it (RULES 18). Flag pilots with unexercised
settings separately. Leave the choice of a neutral value to the owner.

Rules that keep the grades honest:
- **One game per ref.** Never pool or compare across specimens; a lead on an older specimen
  only supports "re-run on current main". (On 2026-11-18 reserve 100 with curve 50 led on
  e0aa2e0a and was the worst curve on dd5f026e.)
- **Count every comparison.** In a 3×3 grid there are eight comparisons against the control;
  correct for them (Bonferroni is enough) before calling anything strong.
- **Pilots never change config.** 18 starts per arm are direction only.
- **Interactions:** a setting measured with the others at old values may behave differently
  once they change. Note which other shipped settings differed in the evidence run.
- **Cost:** mean level and depth, deaths by class (casters vs fighters), and behaviour counts.
  A change that saves fighters and kills casters is not a free win.

## 4. Present

At most the settings with something to say, strongest first:

```
### <setting> = <shipped> (compiled <default>)
What it does: <one line, from params.rs or borg.txt>
Evidence: <run(s), ref, tier/starts> - table of arms: value, deaths, rescued/newly killed vs shipped (p), level, depth, identical plays
Grade: <grade>
Proposal: <change to X / keep / revert / run Y first>
borg.txt: <the exact line(s) as they would read>
Confirmation still needed: <the run, as a one-line /next-experiments item, or "none">
```

End with "Kept, and why" (one line per shipped setting examined with no proposal) and
"Not examined" (shipped settings with no zoo evidence at all, which are candidates for
`/next-experiments`).

## 5. The borg-reborn-rs issue

Draft, do not file, an issue for diegoami/borg-reborn-rs:
- **Title:** `Shipped config from zoo evidence: <the changes, comma-separated>`.
- **Body:** for each proposed change, the setting, current and proposed value, the grade, the
  zoo runs as links with the key figures, and the exact `harness/borg.txt` diff. Then the
  confirmation runs still owed, and a note that the zoo will pilot the new main once it
  lands (RULES 16).

Show it to the owner. File it only when the owner says so, and then through the owner or a
borg-reborn-rs session: the zoo session does not open issues there (RULES 2). Post a short
pointer on the zoo issues the evidence came from.
