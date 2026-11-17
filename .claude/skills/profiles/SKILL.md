---
name: profiles
description: Show what the owner can ask the zoo to run - the named arm sets (shortcuts), the settings asked for so far with what was learned, and the specimens behind them. Use when the owner asks what runs or settings exist, types /profiles, or wants to add a shortcut.
---

# /profiles

The answer lives in `docs/PROFILES.md`, generated from `catalogue/shortcuts.json`
and the catalogue.

1. Regenerate it first so it is current: `python3 -m zoo.profiles_page`.
2. Show the owner the **Shortcuts** table from `docs/PROFILES.md`. If they name a
   shortcut, also show its section: the varying settings per profile, and its runs.
3. If the owner gave an argument (a shortcut, an issue number or a setting name),
   show only the matching rows.
4. To add a shortcut: add an entry to `catalogue/shortcuts.json` (issue, status,
   what, profiles, runs), regenerate the page, and run
   `python3 -m unittest tests.test_profiles_page`. Every profile must already exist
   in `catalogue/profiles.json`. Commit the shortcut with the page.
5. When a run finishes for a shortcut, add it to that shortcut's `runs` with a one-line
   result, and update `status`.

A run request reads: "TIER run of SHORTCUT on REPOSITORY REF". Tiers grow
pilot → (verysmall →) small → medium → big → full, one at a time (RULES 14).
