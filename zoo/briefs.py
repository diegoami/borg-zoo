"""Reader-facing questions, separate from frozen experiment/run records.

These describe the comparison, never its result. New experiments without an
editorial question get a factual summary of the dimensions they vary.
"""
QUESTIONS = {
    'neo-b4-parity-books-v1-small': 'Small tier: how does the Neo parity-and-books candidate play on the first 90 development starts?',
    'neo-b4-parity-books-v1-1800': 'How does the Neo beta.4-engine candidate with six parity repairs and retained spellbook value survive and progress?',
    'rs-additive-returns': 'Do the four added return-trigger settings change survival and town visits when legacy returns stay active and shopping, combat and depth rules are fixed?',
    'neo-fork-48afb65-classes-1800': 'How does the Neo fork with corrected store-phase equipment changes survive and progress?',
    'neo-fork-9c17cb0-classes-1800': 'How does the Neo repair candidate play under its historical message-deaf host?',
    'neo-fork-9c17cb0-events-classes-1800': 'How does the Neo repair candidate survive with event and message delivery restored?',
    'rs-pr85-full': 'When should the repaired Rust Borg return to town: a full pack, spare room, or unknown items worth identifying?',
    'classes-explicit': 'Does the special stair-climbing start for Warriors, Druids and Rangers help them survive and progress?',
    'reborn-g1-classes-1800': 'Can the reborn Rust Borg reach dungeon level 5, and does refusing travel below half health help?',
    'reborn-e-classes-1800': 'How does the reborn Rust Borg compare with the original C Borg and better-borg-c M7?',
    'reborn-pilot-c-classes-1800': 'Does the borg-rs core inside the reborn shell work better with the ladder errand?',
    'reborn-plan-m13-classes-18': 'Do the class errands plan and the M13 shopping run cleanly in the zoo?',
    'reborn-plans-m13-classes-18': 'Does the ambitious errands plan run cleanly in the zoo alongside the other four arms?',
    'reborn-trip-3x3-classes-18': 'Does the trip policy add anything to the town planner, with and without an errands plan?',
    'reborn-plan-m13-small': 'Tier small: do a class errands plan, the M13 town planner, both, or the ambitious plan with the planner help the borg-rs core in the reborn shell?',
    'reborn-plan-m13-medium': 'Tier medium: do a class errands plan, the M13 town planner, both, or the ambitious plan with the planner help the borg-rs core in the reborn shell?',
    'reborn-plan-m13-big': 'Tier big: do a class errands plan, the M13 town planner, both, or the ambitious plan with the planner help the borg-rs core in the reborn shell?',
    'reborn-plan-m13-full': 'Tier full: do a class errands plan, the M13 town planner, both, or the ambitious plan with the planner help the borg-rs core in the reborn shell?',
    'reborn-survival-small': 'Do the flee-healing and Phase Door fixes change deaths in the #123 small tier?',
    'reborn-livelock-small': 'Does the #421 fix remove the stair livelock without changing the no-plan arms?',
    'reborn-maxdepth-returns-small': 'Under max-depth plans, does a tighter return setting lower deaths, and at what cost in progress?',
    'reborn-attackpref-small': "Do the owner's class/family attack preferences change deaths, and at what cost in progress?",
    'reborn-plan-m13-classes-1800': 'Do a class errands plan, the M13 shopping, both together, or the ambitious plan with shopping help the borg-rs core in the reborn shell?',
    'rs-joint-m12-development': 'Which combination of shopping, risk tolerance and earlier town returns helps the Rust Borg?',
    'rs-joint-m12-confirm': 'Does the selected shopping and risk policy still help on fresh seeds?',
    'rs-home-fix-returns': 'Do the added town-return triggers help the Rust Borg once the Home oil loop is fixed?',
    'rs-kit-trip-development': 'Which expanded-inventory and all-item return settings help the Rust Borg?',
    'rs-kit-trip-confirm': 'Does the expanded-inventory and all-item return policy help on fresh seeds?',
    'rs-buy-combinations': 'Do class-specific and special-start shopping overrides actually change play?',
    'rs-family-buying-classes-1800': 'Which shopping and item-identification settings help across all nine classes?',
    'rs-family-buying-normal': 'Do the shopping strategies and buying unknown items help with special modes off?',
    'rs-family-buying-munchkin': 'Do the shopping strategies and buying unknown items help with the special stair-climbing start on?',
    'town-negative': 'What happens when the Rust Borg cannot use shops?',
    'town-negative-classes-1800': 'How much do shops matter across all nine classes with special modes off?',
    'town-negative-munchkin-classes-1800': 'How much do shops matter when every class uses the special stair-climbing start?',
    'mandos-api2-classes-1800': 'Do the Neo Borg port repairs change play or survival compared with upstream?',
    'mandos-api2-classes-18': 'Do the repaired and upstream Neo Borg lanes behave differently on a small class sample?',
    'mandos-classes-18': 'How does full Mandos survive and progress on a small sample covering every class?',
    'neo-fork-classes-1800': 'How does the repaired Neo Borg fork survive and progress across all nine classes?',
    'neo-merged-seeded-v2-1800': 'How does the pre-truth-fix merged Neo repair stack survive and progress on 1,800 seeded-v2 starts?',
    'neo-merged-seeded-v2-corrected-1800': 'How does the corrected Neo repair stack survive and progress on 1,800 seeded-v2 starts?',
    'neo-truth-100-seeded-v2-1800': 'How does the truth-corrected Neo repair stack survive and progress on 1,800 seeded-v2 starts?',
    'originals-20261108-classes-1800': 'How do the official C and Neo Borgs perform in their own games?',
    'original-c-20261111-classes-1800': 'What is the original C Borg baseline when rerun alongside the Rust M11 study?',
    'original-c-42cd156-classes-1800': 'How does the newer official C Borg perform on the standard class suite?',
    'classes-munchkin': 'Does starting with repeated stair-climbing to depth 6 help the original Borg across all classes?',
    'classes-m5-munchkin': 'Does the depth-6 stair-climbing start help the original Borg and M5?',
    'classes-m8-munchkin': 'How do C M8 and Rust M8 perform with the same class-specific stair-climbing start?',
    'munchkin-random': 'Does the depth-6 stair-climbing start help across randomly chosen races and classes?',
    'munchkin-confirm': 'Does the stair-climbing start benefit repeat on fresh seeds?',
    'munchkin-by-class-confirm': 'Does giving Warriors, Druids and Rangers the depth-6 stair-climbing start reduce deaths on fresh seeds?',
    'munchkin-default-check': 'Does the built-in class-specific start play exactly like the equivalent explicit settings?',
    'munchkin-default-off': 'Does switching off the class-specific start reproduce the original behaviour?',
    'stair-dash-confirm': 'Does heading for the nearest free staircase when desperate reduce Warrior deaths on fresh seeds?',
    'bisect-m5-m6-warriors': 'Which individual fix between M5 and M6 changes Warrior play?',
    'warriors-confirm': 'Do the Warrior survival differences between the original, M5 and M6 repeat on fresh seeds?',
    'stall-1045': 'Can the runner detect the known endless staircase cycle on seed 1045?',
    'dive-styles-early': 'Which descent style helps early survival: ordinary, stair-climbing, risky or shallow?',
    'switches-early': 'Which existing Borg settings change early survival and progress?',
    'switches-early-2': 'Do money collection, chest risk and gold or mana priorities change early play?',
    'classes-200k-best': 'Does the class-specific stair-climbing start still help the original Borg at 200,000 turns?',
    'classes-200k-recommended': 'How does the recommended M7 configuration perform at 200,000 turns?',
    'milestones-deep': 'Do M4’s fixes help compared with the original Borg over 400,000 turns?',
    'milestones-big': 'Does M4 reduce early deaths compared with the original Borg on 2,000 seeds?',
    'milestones-wide': 'How do the C milestones change survival, progress and stalls on 500 fresh seeds?',
    'milestones-early': 'Which C milestones change early survival compared with the original Borg?',
    'milestones-early-random': 'Which C milestones help when race and class are chosen by the seed?',
    'classes-milestones': 'Does C milestone 4 help compared with the original Borg across all nine classes?',
    'classes-m5': 'Do C milestones 4 and 5 help compared with the original Borg across all nine classes?',
    'classes-m6': 'Do C milestones 5 and 6 help compared with the original Borg across all nine classes?',
    'classes-m7': 'How do M6, M7 and M7 with a class-specific start compare with the original Borg?',
    'classes-m9-m10': 'How do M9 and M10 perform compared with the original Borg under their shipped defaults?',
    'rs-early': 'Does the Rust port press exactly the same keys as its C counterpart?',
    'classes-rs': 'Does the Rust port reproduce its C counterpart across all nine classes?',
    'm12-m13-explicit': 'Do the M12 and M13 fixes change survival and progress under the same explicit modes?',
}
for milestone in (2, 3, 4, 6):
    QUESTIONS[f'classes-rs-m{milestone}'] = (
        f'Do the Rust M{milestone} fixes help, and does the port still play exactly like its C counterpart?')
for milestone in (11, 12, 13):
    QUESTIONS[f'classes-v{milestone}'] = (
        f'How does C M{milestone} perform with the class-specific stair-climbing start on and off?')
    QUESTIONS[f'classes-rs-m{milestone}'] = (
        f'How does Rust M{milestone} perform with the class-specific stair-climbing start on and off?')


PROFILE_LABELS = {
    'rs-additive-existing': 'Existing shopping + legacy returns',
    'rs-additive-shopping-only': 'New shopping + legacy returns only',
    'rs-additive-p0-u0': 'Legacy returns + full-pack trigger (0,0)',
    'rs-additive-p1-u2': 'Legacy returns + one slot / two unknown stacks (1,2)',
    'rs-additive-p1-u4': 'Legacy returns + one slot / four unknown stacks (1,4)',
    'rs-additive-p2-u4': 'Legacy returns + two slots / four unknown stacks (2,4)',
    'rs-pr85-existing': 'Existing shopping and returns',
    'rs-pr85-shopping-only': 'New shopping, legacy returns',
    'rs-pr85-return-p0-u0': 'Full pack; learning return off (0,0)',
    'rs-pr85-return-p1-u2': 'One free slot / two unknown stacks (1,2)',
    'rs-pr85-return-p1-u4': 'One free slot / four unknown stacks (1,4)',
    'rs-pr85-return-p2-u4': 'Two free slots / four unknown stacks (2,4)',


    'default': 'Build defaults (can differ between versions)',
    'normal': 'Ordinary play; all special modes off',
    'munchkin-class': 'Depth-6 stair-climbing start for Warrior, Druid and Ranger',
    'munchkin-wdr': 'Depth-6 stair-climbing start for Warrior, Druid and Ranger',
    'munchkin-d6': 'Depth-6 stair-climbing start for every class',
    'munchkin-on': 'Stair-climbing start for every class',
    'lunal': 'Deep-dungeon stair-climbing mode',
    'rs-joint-old-control': 'Existing behaviour; new shopping and trip policies off',
    'rs-joint-live-reference': 'New shopping and trip policies on; original risk forecast',
    'rs-joint-risk1500': 'New policies on; risk forecast multiplied by 1.5',
    'rs-joint-risk2000': 'New policies on; risk forecast doubled',
    'rs-joint-risk2500': 'New policies on; risk forecast multiplied by 2.5',
    'rs-joint-risk2000-earlier': 'Doubled risk forecast and earlier town returns',
    'rs-kit-trip-control': 'Existing shopping and return rules',
    'rs-kit-trip-default': 'Expanded inventory and all-item returns with default priorities',
    'rs-kit-trip-risk1500': 'Expanded inventory and all-item returns with 1.5× supply risk',
    'rs-kit-trip-attack50': 'Expanded inventory and all-item returns with attack priority 50',
    'rs-kit-trip-support25': 'Expanded inventory and all-item returns with support priority 25',
    'rs-kit-trip-knowledge5': 'Expanded inventory and all-item returns with learning priority 5',
    'rs-kit-trip-earlier': 'Expanded inventory and all-item returns with earlier town returns',
}


def profile_label(name):
    label = PROFILE_LABELS.get(name)
    return f'{label} ({name})' if label else name


def question(exp):
    if exp['name'] in QUESTIONS:
        return QUESTIONS[exp['name']]
    versions, profiles = len(exp['specimens']), len(exp['profiles'])
    if versions > 1 and profiles > 1:
        return 'How do these Borg versions and settings compare on the same seed suite?'
    if versions > 1:
        return 'How do these Borg versions compare under the same settings?'
    if profiles > 1:
        return 'How do these settings change survival and progress for this Borg version?'
    return 'How does this Borg configuration survive and progress on this seed suite?'
