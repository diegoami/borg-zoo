# Review prompt: shared data foundation (borg-zoo#114, PR #119)

The owner chooses and runs the reviewer. The documents were written with a
Claude model, so a reviewer from another model family is preferred. Paste
everything below the line into the reviewer's session, started in a clean
clone of `diegoami/borg-zoo`.

---

You are reviewing an architecture and plan, not code. Your job is to find
design defects that would make the system lose, double-count or mislabel
games, or make the plan fail, before any of it is built. Be concrete and
skeptical. A finding without a failure scenario is not a finding.

## Exact boundary

- Repository: `diegoami/borg-zoo`, pull request #119.
- Base: `00abdc9ebe1bd0d6b53a21054037e2604d08f402` (`main` when the branch
  was cut).
- Content under review: `6469853` (the proposal and the owner's recorded
  decisions). This prompt was added by a later documentation-only commit.
  Review the diff `00abdc9..6469853`:
  ```sh
  git fetch origin design/shared-data-foundation-114
  git diff 00abdc9 6469853 --stat
  ```
- Files: `docs/data-foundation/README.md` (decision), `ARCHITECTURE.md`,
  `RESUME.md`, `PLAN.md`, `baseline/`, and a one-paragraph pointer in
  `README.md`.
- Owner decisions D1–D7 recorded in `PLAN.md` are settled direction. Do not
  re-argue them. Do report it if the design cannot honour one of them.

## Read first

1. Issue #114 and its comments: `gh issue view 114 -R diegoami/borg-zoo --comments`.
   It defines the requirements and deliverables.
2. `RULES.md` and `docs/DESIGN.md` in this repository: current measurement
   rules (append-only results, every run counted, no failure relabelled as a
   death, pairing only within one execution).
3. borg-cemetery PR #2 (`diegoami/borg-cemetery`, branch
   `design/battle-scenario-architecture`, head `ca7f62b`), especially
   `docs/architecture/scenario-contract.md` and `firebase-backend.md`. The
   plan claims the foundation sits under that design and resolves its
   finding R4.

## What to check

1. **Requirements coverage.** Map every deliverable and requirement in #114
   (including the comment about borg-reborn-rs#320 and #308 plan state) to
   where the documents answer it. List anything missing or answered only by
   assertion.
2. **Identity and invariants** (`ARCHITECTURE.md`). Are the identity tuples
   sufficient and minimal? Find a case where two different things get one
   identity, or one thing gets two. Can any sequence of retries, worker
   losses, corrections, forks or resumes count a life twice, drop an
   expected game, or turn a failure into a death or a survival?
3. **Protocols.** Ingestion, checkpoint sealing and resume leases rely only
   on create-if-absent and replace-if-unchanged. Look for races: two
   publishers, a publisher dying between blob and commit, a lease holder
   paused past expiry who then writes, clock skew on `expires_at`, the
   index step reading a batch mid-write, finalize running before a late
   shard. Say whether fencing tokens are actually enforced by something, or
   only by convention.
4. **Resume audit** (`RESUME.md`). Spot-check its claims against the pinned
   sources it names (better-borg-c `9ca98661`, borg-reborn-rs `ec9058d1`,
   Mandos `d32b69f`). Is the qualification protocol enough to prove an
   exact continuation, including "checkpointing adds no action or RNG
   draw"? Is fresh-Borg restart kept strictly separate, as decision D4
   requires?
5. **Storage decision** (`README.md`). Are the options compared fairly,
   including Firestore as borg-cemetery PR #2 proposes it? Do the measured
   numbers support the conclusion? Check vendor claims (conditional writes,
   OIDC, free tiers, Pages and file-size limits) against current
   documentation and say which you verified.
6. **Baseline.** Reproduce at least the cell count, compressed size and
   the SQLite benchmark from `baseline/README.md`. Heavy local commands on
   the owner's machine must run under
   `flock /tmp/angband-validation.lock <command>`.
7. **Plan** (`PLAN.md`). Are the milestones ordered by real dependencies,
   are the acceptance tests able to fail, are the estimates plausible, and
   is every destructive or link-breaking step named? Is the salvage scope
   consistent with invariant 11 (nothing reconstructed by guessing) and the
   2027-02-06 artifact expiry?

## Rules for the reviewer

- Read only. Do not push, comment on issues or pull requests, dispatch
  workflows, start experiments or create cloud resources.
- Do not edit other repositories or another session's worktree.
- No AI attribution lines in anything you write.

## Output

Write one Markdown report:

1. **Verdict:** accept, accept with specified changes, or reject.
2. **Findings**, most severe first. Each has: severity (high, medium, low),
   file and line, the defect in one sentence, a concrete failure scenario
   (inputs or sequence of events, and the wrong result), and the smallest
   correction you would accept.
3. **Coverage table** for check 1.
4. **What you verified and how:** commands run with their output, sources
   read at which commit, vendor documentation consulted with its date.
   Mark anything you could not verify.
