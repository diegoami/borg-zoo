---
name: next-experiments
description: Go through every experiment the zoo has already run and propose the best next experiments, each as a draft YAML definition with the evidence behind it. Use when the owner asks what to run next, what to try after a result, which settings are worth testing, or types /next-experiments (optionally with a focus such as a setting, an issue or a Borg line).
---

# /next-experiments

Propose what to run next from what was already tried. Read, rank, draft; never
dispatch, and never write a definition into `definitions/` until the owner picks one.

## 1. Gather what was tried

1. Results: `git fetch origin results:refs/remotes/origin/results` and check the branch out somewhere outside
   this tree (for example `git worktree add ../zoo-results origin/results`), then
   `python3 -m zoo.history --results ../zoo-results/results --pool --json /tmp/history.json`.
   `--pool` reads the tiers of one study (same specimens, profiles and control, disjoint
   starts) as one entry, as RULES 14 asks; a pilot always stays on its own. Drop `--pool`
   to see each run separately.
   It prints, per experiment run: question, issue, tier, pinned refs, and per arm
   the settings that differ from the control, deaths / finished, mean level and
   depth, unfinished cells, and the pairing against the control (rescued, newly
   killed, McNemar p, identical plays). Narrow with `--match SETTING_OR_ISSUE`
   and `--since YYYY-MM-DD` when the owner gave a focus.
2. Conclusions and constraints, in this order:
   - `docs/OPEN-WORK.md` and the study issue: current owner decisions override any
     proposal (for example: plan-town is measured only with a plan and the return
     dimension; no arm a decision has ruled out).
   - `docs/FINDINGS.md`: what each finished experiment showed, and what it overturned.
   - `catalogue/shortcuts.json` / `docs/PROFILES.md`: each named arm set's status
     (dispatched, pilot done, small tier done, superseded, obsolete).
   - `definitions/*.yaml`: what is defined but has no run yet (dispatched or pending).
   - Open issues and PRs: `gh issue list --repo diegoami/borg-zoo --state open` and
     `gh pr list --repo diegoami/borg-zoo`. Do not propose what is already open. Read the
     comments: a "Picked up by a zoo session" comment means another session owns it, and
     run requests from borg-reborn-rs (issues titled "Pilot: …" with a definition) are
     work waiting, not proposals to make again.
   - Death evidence: check the run's `deaths-*` artifacts and any imported dossiers
     in borg-cemetery (`runs/zoo-*`); reproduced bundles carry the messages; `/pilot-deaths` and the cemetery's
     `/animate-death` show what happened. A death cause the arms did not touch is a
     candidate for a new switch in the Borg, not for another zoo run.
3. New knobs in the Borgs: settings a specimen's repository added since its last
   measured ref (for borg-reborn-rs: `git log REF..origin/main -- harness/borg.txt
   borg-core/src/params.rs docs/CALIBRATION.md`, merged PRs that say "flag",
   "parameter" or "default 0"). A new switch with no run is a candidate.

## 2. Read the evidence honestly

- Every development-suite figure is descriptive (RULES 14). A difference is a lead
  for the next tier, not a result. Say "leads", never "improves".
- Results are tied to their exact ref: a different source hash is a different game.
  Never pool or compare arms across specimens unless the same experiment paired them.
- Read `identical plays`: an arm that played the control's keys in most pairs did not
  exercise its setting. Its "no difference" means "not tested", not "no effect".
  Likewise two arms with identical rows (as (4,1) and (4,2) in #147) mean that
  dimension did nothing at that tier: drop it rather than measuring it again.
- Count events, not percentages, at pilot size (18 starts per arm).
- A "stalled" cell is a stall only when the frozen-turn check found gold unchanged;
  a `purchase_burst` (#205) is shopping and the cell kept its outcome.
- A newer main is a newer game: a lead on one ref can reverse on the next (on 2026-11-18
  reserve 100 with curve 50 led on e0aa2e0a and was the worst curve on dd5f026e). Check
  that the lead's specimen is still current main before proposing its next tier; if not,
  propose the pilot again on current main.
- Unfinished cells (stalls, timeouts) are findings of their own: a stall in an arm is
  a reason for a fix and a re-run before any comparison.

## 3. Generate candidates

Consider, and keep the ones the evidence supports:
- **Next tier** of a lead: a pilot or small run whose arm leads its control with
  rescued > newly killed and few identical plays. Tiers grow one at a time:
  pilot → small → medium → big → full (RULES 14). Drop the arms that showed nothing.
  Read each tier gate and get the owner's go before dispatching the next.
- **Always a pilot first** (RULES 16): any new arm, and any arm on a new specimen, starts
  with a pilot of exactly those arms on exactly that build. `zoo define` refuses a bigger
  tier without one. Never propose small or larger for arms that have no pilot on the
  current specimen.
- **Untested combination** of two dimensions that each led alone, at the tier the
  stronger one reached. Keep the factorial small: the arms multiply.
- **Untested knob**: a new setting with no run, as a pilot against its default.
- **Re-run on a new ref** when a fix landed that changes the game (only when the
  fix bears on the question; otherwise the old run stands).
- **Confirmation** on fresh seeds (`classes-1800-b`, `warriors-600`) for a lead that
  survived the medium tier: the only way to a claim.
- **Close a question**: when a dimension showed nothing twice, propose dropping it
  (a line in FINDINGS/shortcuts) instead of another run.

## 4. Rank and present

Rank by (how much the result would change a decision) ÷ (games it costs), and
prefer cheap tiers first. Present at most five, as:

```
### N. <one-line question>
Why now: the evidence (experiment, arm, figures from the digest, finding or issue).
What it decides: the decision each outcome would lead to.
Design: specimen/ref, arms (what varies), control, tier, games (arms × starts),
        and whether to retain evidence (needed when an endpoint counts notes in
        surviving games; about 1.5 MB per game, so pilots only).
Risk: confounds, identical-play risk, what would make it uninformative.
Draft definition:
  <YAML in docs/DEFINE.md's form: name, issue (or "new"), question, tier,
   specimen, settings, vary or arms, control, prespecified gate and endpoints>
```

Then a one-paragraph "Not proposed, and why" for the obvious ideas you rejected
(already run, ruled out by an owner decision, dimension showed nothing).

## 5. After the owner picks

Only then: write the chosen YAML to `definitions/NAME.yaml` (a borg-reborn-rs specimen
whose shipped `harness/borg.txt` sets `borg_scary_list` must pin it under `scary_lists`,
or the build is refused), run
`python3 -m zoo define definitions/NAME.yaml`, `python3 -m zoo define --check
definitions/*.yaml`, `python3 -m zoo preflight --experiment experiments/NAME.json`
and the tests, add a shortcut (see /profiles), and open the catalogue PR. Starting
the run stays the owner's call.
