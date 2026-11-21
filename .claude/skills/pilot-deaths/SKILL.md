---
name: pilot-deaths
description: Write the death report of a pilot or verysmall run - replay the deaths locally from the run's own build, show what each dead Borg wore and carried, its last messages and notes, its trip decisions and where it split from the control, then write the observations. Use when the owner asks about the deaths of a run ("tell me about the deaths", "inventory, log, cause"), and offer it after every pilot or verysmall gate.
---

# /pilot-deaths

For borg-rs specimens (borg-reborn-rs, borg-rs). Pilot and verysmall runs only:
a larger tier has too many deaths to read one by one.

1. Find the experiment file and the run id. The run must have finished and been
   collected to the results branch.
2. Generate the report on Linux from a checkout of the collected run's definition.
   This helper assumes one borg-rs-kind specimen and uses the archived build.
   For a source-based screen recording, see [death-report](../death-report/SKILL.md)
   and its optional `~/projects/borg-reborn-rs` clone reference.

   ```sh
   python3 -m zoo.death_report --experiment experiments/NAME.json --run RUN_ID \
     --work "$SCRATCHPAD/deaths-NAME"
   ```

   This reads the run's cells from `origin/results` and groups the deaths by game:
   the same class, seed and play hash in several arms is one death. It downloads
   the run's Linux build artifact (`build-SPECIMEN`; 7 days normally, 90
   with `retain_evidence`) and replays every dying arm plus the
   control with `zoo run --keep`. Then it checks each replayed play hash against
   CI and writes `reports/NAME-deaths/README.md` and `evidence/`. It exits 1 if
   any replay does not match CI. In that case, stop and report the mismatch:
   the evidence is not the CI game.
3. Read the evidence for each distinct death:
   - what was worn and carried, and what was left at home;
   - the last game messages and Borg notes;
   - the counts (Cure potions, Phase Door, unknown potions, failed teleports,
     trip returns, trip returns followed by "going down");
   - for a death the control does not have, the first line where the game differs
     from the control, which is usually the varied setting acting.
4. Replace the README's **Observations** placeholder. Cover what each death had
   and did not use (escapes, healing, unread scrolls, unspent spell points, oil
   not thrown), and what the varied setting changed. Use grep on the kept logs in
   the work dir for anything the README does not show (town transactions:
   `town-transactions.jsonl`; depth over time: `state.log`). Write observations
   only, never a diagnosis.
5. The README also has a **Handover** section, written by the script, for a session in the Borg's
   repository. It gives the exact build, each death's `borg.txt` (`evidence/<death>/borg.txt`), the
   raw command and the seed, race, class and play hash to re-run each death. Add to it the
   "where to look first" items from the observations.
6. Give the owner a ready-to-paste prompt for that session. Use the template below, with the
   report's GitHub link and two or three of the observations.
7. Commit the report on the experiment's PR branch. Comment a short summary
   on the issue with the GitHub link
   (`https://github.com/diegoami/borg-zoo/blob/BRANCH/reports/NAME-deaths/README.md`),
   and give the owner the same link. Offer to save the deaths in borg-cemetery,
   but don't save them unasked.

## Prompt template for the Borg's repository session

```
Work in diegoami/borg-reborn-rs with me on the deaths of borg-zoo run RUN_ID (EXPERIMENT, borg-zoo#ISSUE).
Read the death report first: REPORT_URL. Its "Handover" section has the exact build (REF), each
death's borg.txt in evidence/<death>/borg.txt, and the command, seed, race, class and play hash to
re-run each death.

1. Build REF (BORG_IMPL=rust harness/build.sh) in a worktree, then re-run every death in the
   table and confirm each keys.log hash matches. Stop and tell me if any differs.
2. For each death, read the evidence, then show me the decision that killed it: the notes and code
   path, and the parameter or rule that decided. Observations from the zoo, not yet diagnosed:
   - OBSERVATION 1
   - OBSERVATION 2
3. I'll choose the parameters or rules to change. For each change, re-run the same deaths with
   the new value (a borg.txt key, or a BORG_PARAM_* override where the code reads one) and show me
   before and after for each death. Then run the borg-reborn-rs tests.
4. Changes go in a PR in borg-reborn-rs. When it merges, write me the request for the borg-zoo
   session: a new specimen at the merged commit and a pilot (or verysmall) of the same arms.
Follow borg-reborn-rs's AGENTS.md, RULES.md and docs/GUIDED-DEBUGGING.md.
```
