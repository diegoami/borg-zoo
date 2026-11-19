# Working rules

1. The zoo measures; it does not change Borgs. Borg source changes and new
   Borg parameters belong in the Borg's own repository. A new parameter enters
   the zoo as a profile once that repository exposes it with a default that
   reproduces the original behaviour.
2. Other repositories are read at pinned commits only. Never push to them,
   edit their issues or run anything in another session's worktree.
3. A suspected defect seen in zoo data goes to the owner for routing. Original
   C Borg and C game defects belong on
   [diegoami/neo-angband-tracker](https://github.com/diegoami/neo-angband-tracker/issues).
4. Results are append-only. Never rewrite or delete a run on the `results`
   branch; a corrected run is a new run that says what it corrects.
5. Suites are frozen once they have results. Change a seed list, cap or birth
   rule by adding a new suite.
6. Every run is counted. Stalls, timeouts, crashes, harness failures and
   configuration errors are reported per arm, never dropped and never
   relabelled as deaths.
7. Compare arms only within one workflow run, or say plainly what differs
   (compiler, machine, calendar date, harness commit).
8. No claim of improvement from the tables alone. A claim needs a
   prespecified endpoint, a sized comparison and a confirmation suite the
   owner has agreed.
9. Local heavy runs on the owner's machine take the shared lock:
   `flock /tmp/angband-validation.lock <command>`.
10. No AI attribution trailers in commits or pull request bodies.
11. Run and inspect smoke tests before dispatching a large experiment. Smoke
    and the full experiment must not start together; successful builds alone
    are not acceptance. Check completed cells, applied settings and abnormal
    outcomes before proceeding.
12. Split large experiments into bounded shards, one shard per Actions job.
    For the owner-authorized M12/M13 rerun, wait until all 20 account runner
    slots are free, then use all 20 in one workflow. Do not start alongside
    existing experiments. Use measured smoke timings and the actual worker
    count to size each shard with headroom below the job timeout; never pack
    an entire experiment into one runner job. This supersedes the earlier
    one-job wording, corrected by the owner on 2026-11-15.
13. Persist and flush every completed cell immediately, regardless of raw
    evidence retention. Upload completed records even when a job is cancelled
    or times out. Verify partial-result collection with an interrupted run
    before relying on it for a large experiment.
14. Grow every measurement in tiers, and always propose the smallest first
    (owner, 2026-11-16). After the pilot or smoke, a study runs as nested
    slices of its development suite: small (10 starts per class), medium
    (40), big (100) and full (all). Each tier plays only the starts the
    previous tiers did not, so the four runs together are exactly the full
    study, and each is analysed on everything collected so far. Every tier
    has a written gate, and the next tier is dispatched only after the gate
    is checked and the owner agrees. Never propose or start the full size
    first. The pilot always comes first (RULES 16). An optional verysmall
    tier (starts 1-45, 5 per class) may sit between the pilot and small; a
    study that ran it plays small-rest (starts 46-90) as its small tier, so
    the tiers stay disjoint (owner, 2026-11-17).
15. Every experiment is defined in YAML (owner, 2026-11-16):
    `definitions/NAME.yaml` is the source, and `experiments/NAME.json` (or
    `smoke/`) with any new specimen and profiles is generated from it by
    `python3 -m zoo define definitions/NAME.yaml`. Never edit a generated
    experiment file by hand; change the definition and regenerate with
    `--update`. Each definition names the borg-zoo issue it answers, and
    each report links both. CI fails when a definition and the catalogue
    disagree. The format is in `docs/DEFINE.md`.
16. **Always the pilot first** (owner, 2026-11-17). Every measurement starts
    with a pilot of exactly its arms on exactly its build: the same
    specimen(s) and the same profiles, on `classes-18` (`tier: pilot`), or
    on the study's own suite marked `pilot: true` when it is one class's
    starts. This holds even when a request asks for a bigger tier, and when
    only the build changed, even if the source is the same and only
    `borg.txt` differs. Propose the pilot instead and say why; a larger tier
    follows only after the pilot's gate is checked and the owner agrees
    (RULES 14). `python3 -m zoo define` refuses a new experiment above pilot
    size when the catalogue has no such pilot. Experiments generated before
    this rule are not rechecked.
17. **Several sessions work on this repository at once; claim before you
    act** (owner, 2026-11-19). Any session may work on any issue: a study
    "belonging" to another session only means another session may be
    acting on it right now. Before defining, dispatching or merging
    anything for an issue, read its latest comments, its branches and PRs
    (`gh pr list --search "#N"`, `git ls-remote origin 'refs/heads/*'`) and
    the running workflow runs; if nothing is in flight, post a one-line
    "picked up by a zoo session" comment on the issue first, and only then
    act. If another session claimed it and its work is still moving, leave
    it and say so. Never run two tiers of the same study at once from two
    sessions, never close or supersede another session's PR without the
    owner, and resolve code conflicts by hand (union-merging is safe only
    for catalogue JSON and FINDINGS prose). Every merge waits for
    `python3 -m unittest discover -s tests` to pass.
18. **A change with little effect is not ruled out** (owner, 2026-11-19). The
    owner may prefer a setting because it is a better way to play, not only
    because it saves games. A result that shows no measurable effect, or a
    small one, therefore never ends with "the shipped value stays" as if the
    question were settled. Report every tested value in one of three bins:
    **harmful** (more deaths or clearly less progress, significant or a
    consistent lean across tiers), **neutral** (no measurable cost: safe to
    adopt if preferred) or **helpful**. Say plainly which values are safe to
    adopt, and leave the choice to the owner. A study's issue is closed only
    when the owner says so.
19. **The site is at most about an hour old** (owner, 2026-11-19). The
    statistics site (https://diegoami.github.io/borg-zoo/, including
    `settings/changes.html`) is rebuilt by `pages.yml` every hour on a
    schedule, as well as after every finished run and on pushes to main that
    touch `zoo/`, `catalogue/` or the workflow. A session that finds a page
    more than two hours behind the results branch dispatches
    `gh workflow run pages.yml` and checks why the schedule did not fire.
