# Method and reproducibility

This is a bounded analysis of one already completed run, not a new experiment or Borg strategy. No game or replay was executed by these methods. All 3,600 records were audited before representative cases were selected. The raw collected files remain unchanged at results commit dc0a348aab6f8b3169fa52118fd32e247e7a781f.

Measured source pins: Angband e473720ed88a0f0c7ca66815cef3000eb4a38bc3; Neo engine 5a9cab20621278b74f8376996eba1f6fda14c523; Neo Borg 014c810466ec7ac0b9b7a83416e075238c72edd0; native observer fc9d97cb46aa0aaa27773e5c83a41ec395d515fc; Neo measurement tools 2668adc5ab3e2b6e194c2f1561e248b88850ea98; Zoo 9cd742351f328fcde91ebdc70a620224e4ebfc63. No consumer gameplay corrections are present.

The separate viewer projection used for recorded C inventory parsing is pinned at e1ad87d738118ef1565b8134f07115d44575e9df. It does not run a game. Later presentation changes do not change the measured tooling. Native map files all exist; this parser recognizes 1,799 rectangles, while one recorded map is ragged and remains available verbatim.

The native binary/hash and source-observer patch seal were checked. Neo bundle, all 45 content-pack files and all four measured tool files were checked. The Neo build reports dirty=true because pnpm changes the executable bits on two SDK CLI scripts; its build guard rejects tracked source-content changes and any other mode changes. See build-verification.json. All 240 raw archives and 28,798 raw files passed digest/size checks. Every collected cell equals the downloaded per-shard record; no missing keys, duplicate keys or C/Neo paired statistics are present. See collector-verification.json and raw-verification.json.

The cap is 100,000 engine ticks, ten per normal-speed action; native checks exactly, Neo at Core-loop boundaries. Four timeouts have partial streams and last recorded states, not terminal run.json/maps or complete birth metadata. Original-controller watchdog releases are classified as stalled; the harness did not invent the forty-attempt detector.

Never-move grouping uses inherited NEVER_MOVE flags declared in each pinned content pack. Article prefixes are removed from recorded death causes solely for matching names. Dogs are recorded Maggot-dog causes; poison is the literal poison cause. Unmatched/nonmonster causes remain explicit. A flag does not establish avoidability or blame.

Native first positive-depth location notes can miss brief earlier visits; sampled maxDepth entry times are upper bounds. The report does not compare those medians as exact town-preparation time. Early retail-buy note windows instead use directly recorded native BORG timestamps. Native purchase notes are plans/issued actions, not transaction success. Core 'You bought ...' messages are positive confirmations; native history is bounded, Neo messages.jsonl is complete to stop/timeout. Empty known store stock does not prove no visit. Native energy is cumulative spent energy, whereas Neo energy is the current balance.

Case selection is deterministic: lower median death tick in each of the three largest Neo cause groups (NEVER_MOVE race, Maggot dogs, poison), numeric seed breaks ties. Neo cap references first match class/race, then minimize initial HP difference, birth-stat-vector L1 distance and seed. If no same-race cap exists, the class-only fallback is explicit. C cap references use class/race/initial HP; native birth stats were not captured. A C immobile-death median is included as a failure reference. Different seeds generate different games; these are reference examples, not causal controls. Full selection rules and actual fallback candidates are in case-selection.json.

Book audit: all Core 'Your ... hits/misses ...' messages containing the current class's declared book title are counted as positive projectile evidence. Starting-book-handle throw intents are counted separately, since gate acceptance is not success. A book may be thrown without a hit/miss message; counts are conservative. C complete notes are searched for own-class book throw notes. Class book definitions and TV values are read from the pinned source/content; the source mismatch is the browse predicate, not a statistical inference.

To rerun the data methods, download all run artifacts (no new games), preserving artifact-name folders. Each input artifact folder needs download-receipt.json as its completion marker. The measured Zoo checkout must be at 9cd7423; obtain the viewer presentation.py at e1ad87d. Set task-specific paths and use a fresh output directory:

```sh
export ZOO_CACHE=/path/to/downloaded-artifact-folders
export ZOO_ANALYSIS=/path/to/fresh-analysis
export ZOO_CODE=/path/to/zoo-at-9cd7423
export VIEWER_PRESENTATION=/path/to/presentation-at-e1ad87d.py
python3 methods/content_metadata.py
python3 methods/extract_facts.py
python3 methods/aggregate.py
python3 methods/select_cases.py
python3 methods/book_throws.py
python3 methods/audit_cases.py
```

Methods read the cache and write the designated analysis directory; they never launch an engine or mutate source records. Outcome tables, facts and case IDs are reproducible; wall metadata and local output paths are not game data.

## Fresh-path reproduction receipt

All six published method scripts were rerun successfully with a fresh output directory, the same read-only verified artifact cache, frozen Zoo code 9cd7423 and viewer projection e1ad87d. The aggregate, deterministic case selection and complete book-throw audit were byte-identical to the reviewed analysis. No engine or replay was run. See [method-reproduction.json](method-reproduction.json).

## Selected raw traces archive

`selected-raw-traces.tgz` was missing from the first commits, because `.gitignore` ignored `*.tgz`; the hash first listed for it (`61e7ba52…`) belongs to an archive that was never published. The committed archive was rebuilt from the run's own raw artifacts, without running any game. Each source artifact matched its published SHA-256, and all 76 case files match their cells' recorded inventories. Its archive hash differs only because the original packing settings were not recorded. See [selected-raw-traces.json](selected-raw-traces.json) for the source artifacts, the per-file hashes and the packing command.
