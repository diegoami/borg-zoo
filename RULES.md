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
