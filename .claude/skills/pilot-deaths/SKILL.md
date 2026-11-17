---
name: pilot-deaths
description: Write the death report of a pilot or verysmall run - replay the deaths locally from the run's own build, show what each dead Borg wore and carried, its last messages and notes, its trip decisions and where it split from the control, then write the observations. Use when the owner asks about the deaths of a run ("tell me about the deaths", "inventory, log, cause"), and offer it after every pilot or verysmall gate.
---

# /pilot-deaths

For borg-rs specimens (borg-reborn-rs, borg-rs). Pilot and verysmall runs only:
a larger tier has too many deaths to read one by one.

1. Find the experiment file and the run id. The run must have finished and been
   collected to the results branch.
2. Generate the report:

   ```sh
   python3 -m zoo.deaths --experiment experiments/NAME.json --run RUN_ID \
     --work "$SCRATCHPAD/deaths-NAME"
   ```

   This reads the run's cells from `origin/results` and groups the deaths by game:
   the same class, seed and play hash in several arms is one death. It downloads
   the run's build artifact (`build-SPECIMEN`) and replays every dying arm plus the
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
5. Commit the report on the experiment's PR branch. Comment a short summary
   on the issue with the GitHub link
   (`https://github.com/diegoami/borg-zoo/blob/BRANCH/reports/NAME-deaths/README.md`),
   and give the owner the same link. Offer to save the deaths in borg-cemetery,
   but don't save them unasked.
