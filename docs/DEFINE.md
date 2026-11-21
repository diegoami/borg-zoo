# Defining an experiment in YAML

The YAML definition in `definitions/NAME.yaml` is the source of the generated
experiment JSON (RULES 15). Use Python 3 with PyYAML installed. Definitions
can reuse existing catalogue entries or create specimens and profiles. A new
seed suite is a separate catalogue entry in `catalogue/suites.json`.

```sh
python3 -m zoo define definitions/NAME.yaml           # write the catalogue entries
python3 -m zoo define --check definitions/*.yaml      # what CI runs: write nothing, fail on any mismatch
python3 -m zoo define --update definitions/NAME.yaml  # rewrite an existing experiment after editing its definition
```

Existing specimens and profiles are reused when they match exactly, and are
never changed. A profile that already has different settings is an error;
give the arm another name, because profiles are frozen once used.

## Example (borg-zoo#151)

```yaml
name: reborn-heal-pilot          # experiments/reborn-heal-pilot.json
issue: 151                       # the borg-zoo issue it answers
question: Does healing when outmatched help, with and without the trip policy and an errands plan?
tier: pilot                      # pilot | verysmall | small (or small-rest) | medium | big | full (RULES 14)

specimen:                        # a new specimen, or the name of an existing one
  name: 4.2.6-reborn-rust-heal
  repository: diegoami/borg-reborn-rs   # kind, impl, exact_turns, depth_stream default from the repository
  ref: f02cd2940a7439a8965b3883270a9a73df7e0bf5
  label: What this build is, in a sentence or two.
  plans:                         # plan files the specimen ships, pinned by sha256
    errands_plan.txt: 084bc3e8...
    errands_plan_ambitious.txt: c3018585...
  # scary_lists:                 # named scary-monster lists (harness/NAME, borg-zoo#228), pinned by sha256;
  #   scary_monsters.txt: d045111b...   # an arm picks one with borg_scary_list: NAME, and may add
  #                                     # borg_scary_list_lines: ["crow | 0-4", "soldier | none", "fragility: blackguard 33"]
  #                                     # (appended to the copy; a later line for a monster replaces it, "| none" removes it)

settings:                        # in every arm
  borg_reborn_core: borg-rs
  borg_reborn_errand: none
  borg_town_plan: 1

profile_prefix: reborn           # profile names: reborn-heal0-trip0-none, ...
vary:                            # each entry multiplies the arms (here 2 x 2 x 3 = 12)
  heal:
    heal0: {}                    # {} sets nothing: the build's default
    heal1: {borg_param_caution_heal_when_outmatched: 1}
  trip:
    trip0: {borg_trip_policy: 0}
    trip1: {borg_trip_policy: 1}
  plan:
    none: {}
    plan: {borg_plan: errands_plan.txt}
    ambitious: {borg_plan: errands_plan_ambitious.txt}

control: [heal0, trip0, none]    # the arm the others are paired against

prespecified: |
  The gate and what is reported, fixed before any result is read.
```

## Keys

| Key | Meaning |
| --- | --- |
| `name` | The experiment name (results are filed under it). Required. |
| `issue` | The borg-zoo issue the experiment answers. |
| `question` | One line; it heads the report. |
| `tier` | `pilot` = `classes-18`; `verysmall` = `classes-1800` starts 1-45 (5 per class); `small`/`medium`/`big`/`full` = the `classes-1800` slices; `small-rest` = starts 46-90, the small tier of a study that ran `verysmall`. Or give `suite` or `suites` instead. |
| `specimen` / `specimens` | One specimen (a new block or an existing name), or a list. |
| `settings` | Settings shared by every arm. |
| `vary` | Dimensions whose options multiply the arms. Option names build the profile names. |
| `arms` | Instead of `vary`: each arm named, with its settings. |
| `profiles` | Instead of `vary` or `arms`: existing profiles reused by name. Use this for later tiers that keep a subset of the pilot's profiles. `settings` does not override a reused profile. |
| `profile_prefix` | The start of each profile name; defaults to `name`, and `''` means none. |
| `control` | The control arm, by its option names; or `control_specimen` and `control_profile`. |
| `prespecified` | The gate and endpoints, fixed before any result is read. |
| `owner_authorization`, `description` | Free text, copied into the experiment. |
| `pilot` | `true` marks a study's first, smallest run on a suite of its own (for example one class's starts) as its pilot. `tier: pilot` and pilot-role suites are pilots already. A new experiment above pilot size is refused until a pilot of the same arms on the same specimens is in the catalogue (RULES 16). |
| `extra` | Any other experiment field (for example `resource_budget`, `retain_evidence`, `shards_by_specimen`, or `cemetery_deaths: false` to skip the death bundles of [CEMETERY-DEATHS.md](CEMETERY-DEATHS.md)). |
| `folder`, `file` | Where the experiment file goes: `smoke` for smoke files, and the file name when it differs from `name`. |

YAML reads unquoted `on`, `off`, `yes` and `no` as true and false. Quote them when they are option names (`'on'`).

## Custom seed suites

Add an imported list of explicit `seeds` with `"external": true` under
`suites` in `catalogue/suites.json`. This keeps the manifest's seeds out of
the generator's exclusion set. Omitting the flag can silently shift an
existing `seed_rule` suite (see [#547](https://github.com/diegoami/borg-zoo/pull/547)).
If the manifest fixes births, set `"birth": "assigned"` and supply one
`assigned_characters` entry per seed, with a string key and
`[race, class]` value. Keep the manifest's order and record its provenance.
See `reborn-native-full45` and `reborn-flight-600-pilot18` for examples.

Use `suite: NAME` in the definition. If this is the first study run on its
own development suite, set `pilot: true`. Later tiers can list the subset
of pilot profiles they are taking forward, with `control_profile` set
explicitly. Generate and check the definition, then run preflight and plan.
The pilot's presence in the catalogue does not by itself clear the results gate.

## Asking for a run

Open a **Run request** issue. Its main field is a definition like the one above.
The zoo session copies it into `definitions/`, generates, checks the build and
the sanity cells, and dispatches the requested tier.

## Saving deaths in the cemetery

Rust headless comparisons replay natural deaths into separate `deaths-*`
artifacts by default. The archived cell still has its `play_sha256` after
the bundle expires. Use [CEMETERY-DEATHS](CEMETERY-DEATHS.md) for the bundle
import, and [the pilot-deaths skill](../.claude/skills/pilot-deaths/SKILL.md)
to read a pilot's deaths from its original build. Specify the selection
in the request or on its issue. A replay whose keys differ from the
recorded hash still needs investigation before it can be used as evidence.
The cemetery PR is the owner's to review and merge.
