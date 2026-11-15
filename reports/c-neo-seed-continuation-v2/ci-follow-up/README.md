# Full-CI fixture follow-up

The first source proposal CI runs exposed four existing test assumptions. Their failed logs are retained here, with local reproductions and passing focused follow-ups. No runtime code or measured benchmark pin changed.

- Stock PR638 initially had 2 failures, 15073 passes and12 inherited skips. Both failures selected the first generated store ware while requiring it to be wieldable. Commit916ad0db1 supplies an explicit armour ware in the permission fixture; all permission assertions remain unchanged. All141store/loadout tests pass, and Core/SDK/content builds pass.
- Outfit PR639 initially had2failures,15072passes and12 inherited skips. The parser test expected input order rather than C prepend order; its exact expected sequence is corrected. The fuel test could merge its newly created torch into a starting spare and then observe a different torch by name. Commitab9a56018 configures a distinct torch before carrying and selects the controlled object by handle; all fuel/visibility assertions remain intact. All209bind/gear/parser/known-world tests pass, and Core/SDK/content builds pass.

Both source PRs have fresh full CI queued/running at these follow-up heads. This file does not claim those new jobs completed. The12inherited full-engine skips are distinct from the1170-test Borg suite, which had no skips. Toolkit PR95 and zoo-report PR95 are green. Initial-state comparisons remain11/11; these follow-ups change only tests, not either benchmark runtime.
