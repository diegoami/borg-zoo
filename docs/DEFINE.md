# Defining an experiment in YAML

Every experiment has a definition, `definitions/NAME.yaml` (RULES 15). It is the
only thing to write by hand. This command writes the experiment file and any new
specimen and profiles:

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
tier: pilot                      # pilot | small | medium | big | full (RULES 14)

specimen:                        # a new specimen, or the name of an existing one
  name: 4.2.6-reborn-rust-heal
  repository: diegoami/borg-reborn-rs   # kind, impl, exact_turns, depth_stream default from the repository
  ref: f02cd2940a7439a8965b3883270a9a73df7e0bf5
  label: What this build is, in a sentence or two.
  plans:                         # plan files the specimen ships, pinned by sha256
    errands_plan.txt: 084bc3e8...
    errands_plan_ambitious.txt: c3018585...

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
| `tier` | `pilot` = `classes-18`, `small`/`medium`/`big`/`full` = the `classes-1800` slices. Or give `suite` or `suites` instead. |
| `specimen` / `specimens` | One specimen (a new block or an existing name), or a list. |
| `settings` | Settings shared by every arm. |
| `vary` | Dimensions whose options multiply the arms. Option names build the profile names. |
| `arms` | Instead of `vary`: each arm named, with its settings. |
| `profiles` | Instead of `vary` or `arms`: existing profiles reused by name. |
| `profile_prefix` | The start of each profile name; defaults to `name`, and `''` means none. |
| `control` | The control arm, by its option names; or `control_specimen` and `control_profile`. |
| `prespecified` | The gate and endpoints, fixed before any result is read. |
| `owner_authorization`, `description` | Free text, copied into the experiment. |
| `extra` | Any other experiment field (for example `resource_budget`, `retain_evidence`, `shards_by_specimen`). |
| `folder`, `file` | Where the experiment file goes: `smoke` for smoke files, and the file name when it differs from `name`. |

YAML reads unquoted `on`, `off`, `yes` and `no` as true and false. Quote them when they are option names (`'on'`).

## Asking for a run

Open a **Run request** issue. Its main field is a definition like the one above.
The zoo session copies it into `definitions/`, generates, checks the build and
the sanity cells, and dispatches the requested tier.
