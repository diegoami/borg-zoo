import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from zoo import catalogue as cat_mod  # noqa: E402
from zoo import borgrs, harness, landing, mandos, neo_original, site, stall, stats  # noqa: E402
from zoo.__main__ import main  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def cell(specimen, seed, outcome, max_depth=3, turn=20000, profile='default', trace=None):
    return {'schema': 'borg-zoo/cell@1', 'suite': 'smoke', 'specimen': specimen, 'profile': profile,
            'seed': seed, 'outcome': outcome, 'cap': 20000,
            'final': {'turn': turn, 'max_depth': max_depth, 'max_level': 5},
            'first_turn_at_depth': {'2': 1000} if max_depth >= 2 else {},
            'trace_sha256': trace}


class CatalogueTest(unittest.TestCase):
    def test_every_experiment_validates(self):
        for path in (ROOT / 'experiments').glob('*.json'):
            exp = cat_mod.experiment(path)
            self.assertTrue(cat_mod.cells(exp))

    def test_specimen_refs_are_full_shas(self):
        cat = cat_mod.catalogue()
        self.assertEqual(len(cat['specimens']['harness']['commit']), 40)
        for spec in cat['specimens']['specimens'].values():
            self.assertEqual(len(spec['ref']), 40)

    def test_profile_text_and_expected_options(self):
        profile = {'settings': {'borg_plays_risky': True, 'borg_uses_swaps': False, 'borg_enchant_limit': 9}}
        self.assertEqual(cat_mod.profile_text(profile),
                         'borg_enchant_limit = 9\nborg_plays_risky = TRUE\nborg_uses_swaps = FALSE\n')
        self.assertEqual(cat_mod.expected_options(profile),
                         {'borg_plays_risky': 1, 'borg_uses_swaps': 0, 'borg_enchant_limit': 9})
        self.assertNotEqual(cat_mod.profile_sha256(profile), cat_mod.profile_sha256({'settings': {}}))

    def test_shards_partition_each_specimen(self):
        exp = cat_mod.experiment(ROOT / 'experiments/switches-early.json')
        cells = cat_mod.cells(exp)
        for specimen in exp['specimens']:
            mine = [c for c in cells if c['specimen'] == specimen]
            dealt = [c for i in range(4) for c in cat_mod.shard(cells, specimen, i, 4)]
            self.assertEqual(sorted(map(cat_mod.cell_key, dealt)), sorted(map(cat_mod.cell_key, mine)))

    def test_unknown_names_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / 'bad.json'
            bad.write_text(json.dumps({'name': 'x', 'specimens': ['nope'], 'profiles': ['default'],
                                       'suites': ['smoke'], 'control': 'nope'}))
            with self.assertRaises(ValueError):
                cat_mod.experiment(bad)


class ShippedBaseTest(unittest.TestCase):
    SHIPPED = ('# comment borg_uses_swaps = TRUE\nborg_uses_swaps = TRUE\nborg_plays_risky = FALSE\n\n'
               '[BEGIN FORMULA SECTION]\nPower\n[\n]\n[END FORMULA SECTION]\n')

    def test_shipped_overrides_and_inserts_before_formulas(self):
        profile = {'base': 'shipped', 'settings': {'borg_uses_swaps': False, 'borg_uses_dynamic_calcs': True}}
        text = cat_mod.profile_text(profile, self.SHIPPED)
        self.assertIn('\nborg_uses_swaps = FALSE\n', text)
        self.assertIn('# comment borg_uses_swaps = TRUE', text)
        self.assertLess(text.index('borg_uses_dynamic_calcs = TRUE'), text.index('[BEGIN FORMULA SECTION]'))
        self.assertIn('[END FORMULA SECTION]', text)

    def test_shipped_requires_the_file(self):
        with self.assertRaises(ValueError):
            cat_mod.profile_text({'base': 'shipped', 'settings': {}})

    def test_shipped_profile_without_settings_is_the_file(self):
        self.assertEqual(cat_mod.profile_text({'base': 'shipped', 'settings': {}}, self.SHIPPED), self.SHIPPED)


class SeedSetTest(unittest.TestCase):
    def test_rule_suites_are_deterministic_disjoint_and_in_range(self):
        a, b = cat_mod.catalogue()['suites'], cat_mod.catalogue()['suites']
        self.assertEqual(a['dev-2000']['seeds'], b['dev-2000']['seeds'])
        owner = {}
        for name, suite in a.items():
            self.assertEqual(len(suite['seeds']), len(set(suite['seeds'])), name)
            for seed in suite['seeds']:
                self.assertTrue(1 <= seed <= cat_mod.SEED_MAX, (name, seed))
                if 'seed_rule' in suite:
                    self.assertNotIn(seed, owner, (name, seed, owner.get(seed)))
                owner.setdefault(seed, name)
        self.assertEqual(len(a['dev-2000']['seeds']), 2000)

    def test_classes_1800_200k_doubles_the_cap_on_fresh_disjoint_seeds(self):
        suites = cat_mod.catalogue()['suites']
        base, deep = suites['classes-1800'], suites['classes-1800-200k']
        self.assertEqual(deep['cap'], base['cap'] * 2)
        self.assertEqual(len(deep['seeds']), len(base['seeds']))
        self.assertEqual(deep['characters'], base['characters'])
        self.assertFalse(set(deep['seeds']) & set(base['seeds']))  # rule suites never overlap
        exp = cat_mod.experiment(ROOT / 'experiments/classes-200k-best.json')
        self.assertEqual(exp['specimens'], ['4.2.6'])  # the recommended mix is measured separately: see below
        self.assertEqual(len(cat_mod.cells(exp)), 3600)
        exp = cat_mod.experiment(ROOT / 'experiments/classes-200k-recommended.json')
        self.assertEqual(exp['profiles'], ['default'])  # munchkin-wdr is a no-op on this specimen's own default
        self.assertEqual(len(cat_mod.cells(exp)), 1800)

    def test_every_suite_declares_a_role(self):
        for name, suite in cat_mod.catalogue()['suites'].items():
            self.assertIn(suite.get('role'), ('pilot', 'development', 'confirmation', 'sealed'), name)

    def test_sealed_suite_needs_the_owner(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'x.json'
            exp = {'name': 'x', 'specimens': ['4.2.6'], 'profiles': ['default'],
                   'suites': ['sealed-2000'], 'control': '4.2.6'}
            path.write_text(json.dumps(exp))
            with self.assertRaises(ValueError):
                cat_mod.experiment(path)
            path.write_text(json.dumps({**exp, 'unsealed_by_owner': '2026-12-01: final claim on X'}))
            self.assertTrue(cat_mod.experiment(path))


class CharacterTest(unittest.TestCase):
    class FakeRunner:
        @staticmethod
        def birth_keys(random_birth=False):
            return 'key space\nkey a\nkey a\nkey a\nkey enter\nkey enter\nkey C-z\n'

    def test_assigned_suite_covers_every_class_and_race(self):
        suite = cat_mod.catalogue()['suites']['classes-1800']
        chars = [cat_mod.character(suite, seed) for seed in suite['seeds']]
        classes = {c for _, c in chars}
        self.assertEqual(classes, set(cat_mod.CLASSES))
        for cls in cat_mod.CLASSES:
            mine = [r for r, c in chars if c == cls]
            self.assertEqual(len(mine), 200)
            self.assertEqual({*mine}, set(cat_mod.RACES))

    def test_birth_input_double_taps(self):
        keys = harness.birth_input(self.FakeRunner, 'Dwarf', 'Priest')
        self.assertTrue(keys.startswith('key space\nkey f\nkey f\nkey d\nkey d\nkey a\nkey enter\n'))
        self.assertEqual(harness.birth_input(self.FakeRunner, 'Human', 'Warrior'), self.FakeRunner.birth_keys())
        self.assertIn('key o\nkey o\nkey m\nkey m\n', harness.birth_input(self.FakeRunner, 'Kobold', 'Blackguard'))

    def test_wrong_character_is_a_config_error(self):
        rec = harness.summarise({'specimen': 's', 'profile': 'p', 'suite': 'x', 'seed': 1,
                                 'race': 'Dwarf', 'class': 'Priest'},
                                {'outcome': 'turn_cap', 'states': [{'kind': 'turn_cap', 'turn': 9}]},
                                'CHARACTER Measure Human Warrior\nBORG_OPTIONS borg_x=0\n', {'settings': {}},
                                {'ref': 'a' * 40}, {'cap': 9, 'birth': 'assigned'}, {})
        self.assertEqual(rec['outcome'], 'config_error')
        self.assertEqual((rec['played_race'], rec['played_class']), ('Human', 'Warrior'))

    def test_by_class_table(self):
        exp = {'suites': ['s'], 'specimens': ['a'], 'profiles': ['p']}
        cells = [{'suite': 's', 'specimen': 'a', 'profile': 'p', 'played_class': k, 'outcome': o}
                 for k, o in (('Mage', 'death'), ('Mage', 'turn_cap'), ('Warrior', 'turn_cap'))]
        rows = stats.by_character(exp, cells, 'class')['s']
        self.assertEqual([(r['value'], r['arms'][0]['deaths'], r['arms'][0]['n']) for r in rows],
                         [('Mage', 1, 2), ('Warrior', 0, 1)])


class HarnessParsingTest(unittest.TestCase):
    def test_options_mismatch_becomes_config_error(self):
        trace = 'CHARACTER x\nBORG_OPTIONS borg_plays_risky=0 borg_uses_swaps=1\n'
        profile = {'settings': {'borg_plays_risky': True}}
        spec = {'ref': 'a' * 40}
        suite = {'cap': 20000, 'birth': 'fixed'}
        result = {'outcome': 'turn_cap', 'states': [{'kind': 'turn_cap', 'turn': 20000, 'max_depth': 2}]}
        rec = harness.summarise({'specimen': 's', 'profile': 'p', 'suite': 'smoke', 'seed': 1},
                                result, trace, profile, spec, suite, {})
        self.assertEqual(rec['outcome'], 'config_error')
        self.assertIn('borg_plays_risky', rec['config_error'])

    def test_matching_options_keep_outcome_and_depth_marks(self):
        trace = 'BORG_OPTIONS borg_plays_risky=1\n'
        states = [{'kind': 'progress', 'turn': 500, 'max_depth': 1},
                  {'kind': 'progress', 'turn': 900, 'max_depth': 3},
                  {'kind': 'death', 'turn': 1200, 'max_depth': 3}]
        rec = harness.summarise({'specimen': 's', 'profile': 'p', 'suite': 'smoke', 'seed': 1},
                                {'outcome': 'death', 'states': states}, trace,
                                {'settings': {'borg_plays_risky': True}}, {'ref': 'a' * 40},
                                {'cap': 20000, 'birth': 'fixed'}, {})
        self.assertEqual(rec['outcome'], 'death')
        self.assertEqual(rec['first_turn_at_depth'], {'1': 500, '2': 900, '3': 900})
        self.assertEqual(rec['boundary'], 'exact')

    def test_milestones_uses_the_last_sampled_state(self):
        states = [{'turn': 2000, 'max_depth': 1, 'level': 2, 'max_level': 2},
                  {'turn': 4000, 'max_depth': 2, 'level': 4, 'max_level': 4},
                  {'turn': 8000, 'max_depth': 2, 'level': 6, 'max_level': 7}]
        rows = harness.milestones(states, cap=8000, fractions=(0.5, 1.0))
        self.assertEqual(rows, [{'turn': 4000, 'level': 4, 'max_depth': 2},
                                {'turn': 8000, 'level': 7, 'max_depth': 2}])
        self.assertEqual(harness.milestones([], cap=8000, fractions=(0.5,)),
                         [{'turn': 4000, 'level': None, 'max_depth': None}])


class PlayHashTest(unittest.TestCase):
    def test_config_lines_do_not_change_the_play_hash(self):
        a = 'CHARACTER x\nBORG_OPTIONS borg_plays_risky=0\nACTIVE_OPTIONS a=1\nSTATE progress turn=5\n'
        b = 'CHARACTER x\nBORG_OPTIONS borg_plays_risky=1\nACTIVE_OPTIONS a=1\nSTATE progress turn=5\n'
        c = 'CHARACTER x\nBORG_OPTIONS borg_plays_risky=1\nACTIVE_OPTIONS a=1\nSTATE progress turn=6\n'
        self.assertEqual(harness.play_sha256(a), harness.play_sha256(b))
        self.assertNotEqual(harness.play_sha256(b), harness.play_sha256(c))
        self.assertTrue(stats.same_play({'play_sha256': 'p', 'trace_sha256': 'x'},
                                        {'play_sha256': 'p', 'trace_sha256': 'y'}))


class BorgRsTest(unittest.TestCase):
    def test_config_text_sets_birth_and_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'borg.txt').write_text('borg_respawn_race = -1\nborg_respawn_class = -1\n'
                                                'borg_cheat_death = FALSE\nborg_munchkin_start = FALSE\n'
                                                'borg_munchkin_depth = 16\n')
            profile = {'settings': {'borg_munchkin_start': True, 'borg_munchkin_depth': 6}}
            text = borgrs.config_text(tmp, profile)
            self.assertIn('borg_respawn_race = 0\n', text)
            self.assertIn('borg_munchkin_start = TRUE\n', text)
            self.assertIn('borg_munchkin_depth = 6\n', text)
            self.assertIsNone(borgrs.check_config(text, profile))
            self.assertIsNotNone(borgrs.check_config('borg_munchkin_start = FALSE\n', profile))

    def test_exact_turns_and_statelog_are_opt_in_per_specimen(self):
        suite = {'cap': 20000}
        cmd = borgrs.command('/g/angband', Path('/w'), {'seed': 1}, 0, 0, suite, {})
        self.assertNotIn('-exact-turns', cmd)
        self.assertNotIn('-statelog', cmd)
        cmd = borgrs.command('/g/angband', Path('/w'), {'seed': 1}, 0, 0, suite,
                             {'exact_turns': True, 'depth_stream': True})
        self.assertIn('-exact-turns', cmd)
        self.assertEqual(cmd[cmd.index('-statelog') + 1], '/w/state.log')

    def test_reborn_specimens_declare_exact_turns_and_depth_stream(self):
        specs = cat_mod.catalogue()['specimens']['specimens']
        for name in ('4.2.6-reborn-rust', '4.2.6-reborn-c-pristine', '4.2.6-reborn-c-bbc-m7'):
            self.assertEqual(specs[name]['kind'], 'borg-rs')
            self.assertTrue(specs[name]['exact_turns'])
            self.assertTrue(specs[name]['depth_stream'])
        # Existing borg-rs specimens keep their meaning: no opt-in flags.
        self.assertNotIn('exact_turns', specs['4.2.6-rs-m0'])
        self.assertNotIn('depth_stream', specs['4.2.6-rs-m0'])

    def test_state_log_parsing_and_milestones(self):
        text = ('100 5,5 d- -\n'  # no player state yet: skipped
                '100 5,5 d0/0 hp10/10 sp0/0 f5000 au50 xp0 lv1 t- o- p0 e0 r0\n'
                '2000 6,6 d1/1 hp15/15 sp0/0 f4500 au150 xp40 lv2 t- o- p0 e0 r0\n'
                '5000 6,6 d2/2 hp20/20 sp0/0 f4000 au300 xp120 lv3 t- o- p0 e0 r0\n'
                '10000 7,7 d3/3 hp30/30 sp0/0 f3000 au900 xp500 lv5 t1:3 o- p0 e0 r0\n')
        states = borgrs.parse_state_log(text)
        self.assertEqual(len(states), 4)
        self.assertEqual(states[-1], {'turn': 10000, 'depth': 3, 'max_depth': 3, 'gold': 900, 'xp': 500, 'level': 5})
        self.assertEqual(borgrs.first_turns_at_depth(states, marks=(1, 2, 3)), {'1': 2000, '2': 5000, '3': 10000})
        rows = borgrs.milestones(states, cap=10000, fractions=(0.5, 1.0))
        self.assertEqual(rows, [{'turn': 5000, 'level': 3, 'max_depth': 2, 'gold': 300},
                                {'turn': 10000, 'level': 5, 'max_depth': 3, 'gold': 900}])
        self.assertEqual(borgrs.milestones([], cap=10000, fractions=(0.5,)),
                         [{'turn': 5000, 'level': None, 'max_depth': None, 'gold': None}])

    def test_borg_rs_specimens_reject_random_birth(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / 'bad.json'
            bad.write_text(json.dumps({'name': 'x', 'specimens': ['4.2.6-rs-m0'], 'profiles': ['default'],
                                       'suites': ['early-50-random'], 'control': '4.2.6-rs-m0'}))
            with self.assertRaises(ValueError):
                cat_mod.experiment(bad)

    def test_plan_carries_build_kind(self):
        exp = cat_mod.experiment(ROOT / 'experiments/rs-smoke.json')
        plan = cat_mod.plan(exp, 2)
        kinds = {b['specimen']: b['kind'] for b in plan['builds']}
        self.assertEqual(kinds, {'4.2.6-rs-m0-c': 'borg-rs', '4.2.6-rs-m0': 'borg-rs', '4.2.6': 'better-borg-c'})
        self.assertTrue(all('kind' in r and 'ref' in r for r in plan['runs']))

    def test_rs_m7_and_m8_specimens_share_their_tagged_commit_and_carries(self):
        specs = cat_mod.catalogue()['specimens']['specimens']
        for name_rust, name_c, tag, carries in (('4.2.6-rs-m7', '4.2.6-rs-m7-c', '4.2.6-impact-v7', 76),
                                                 ('4.2.6-rs-m8', '4.2.6-rs-m8-c', '4.2.6-impact-v8', 88)):
            rust, c = specs[name_rust], specs[name_c]
            self.assertEqual(rust['ref'], c['ref'])
            self.assertEqual((rust['tag'], c['tag']), (tag, tag))
            self.assertEqual((rust['carries'], c['carries']), (carries, carries))
            self.assertEqual((rust['impl'], c['impl']), ('rust', 'c'))
        self.assertNotEqual(specs['4.2.6-rs-m7']['ref'], specs['4.2.6-rs-m8']['ref'])
        for name in ('rs-m7-smoke', 'rs-m8-smoke'):
            exp = cat_mod.experiment(ROOT / f'experiments/{name}.json')
            self.assertTrue(cat_mod.cells(exp))

    def test_bbc_m8_matches_rs_m8s_tag_and_carries(self):
        specs = cat_mod.catalogue()['specimens']['specimens']
        bbc, rs = specs['4.2.6-bbc-m8'], specs['4.2.6-rs-m8']
        self.assertEqual((bbc['tag'], bbc['carries']), ('4.2.6-impact-v8', 88))
        self.assertEqual((bbc['tag'], bbc['carries']), (rs['tag'], rs['carries']))
        self.assertNotEqual(bbc['ref'], rs['ref'])  # same milestone, different repositories
        exp = cat_mod.experiment(ROOT / 'experiments/m8-smoke.json')
        self.assertTrue(cat_mod.cells(exp))
        exp = cat_mod.experiment(ROOT / 'experiments/classes-m8-munchkin.json')
        self.assertEqual(exp['profiles'], ['default'])  # munchkin-wdr is a no-op on M8 (review #39)
        self.assertEqual(len(cat_mod.cells(exp)), 3600)

    def test_bbc_m9_carries_ten_more_than_m8_no_rs_counterpart_yet(self):
        specs = cat_mod.catalogue()['specimens']['specimens']
        m8, m9 = specs['4.2.6-bbc-m8'], specs['4.2.6-bbc-m9']
        self.assertEqual((m9['tag'], m9['carries']), ('4.2.6-impact-v9', 98))
        self.assertEqual(m9['carries'] - m8['carries'], 10)
        self.assertNotIn('4.2.6-rs-m9', specs)  # borg-rs has not tagged v9 yet
        exp = cat_mod.experiment(ROOT / 'experiments/m9-smoke.json')
        self.assertTrue(cat_mod.cells(exp))

    def test_no_pairing_across_harnesses(self):
        exp = cat_mod.experiment(ROOT / 'experiments/rs-smoke.json')
        cells = []
        for s in exp['specimens']:
            for seed in (11, 29):
                c = cell(s, seed, 'turn_cap')
                c['harness_kind'] = 'better-borg-c' if s == '4.2.6' else 'borg-rs'
                cells.append(c)
        rows = {r['specimen']: r for r in stats.analyse(exp, cells)['smoke'] if r['profile'] == 'default'}
        self.assertIsNotNone(rows['4.2.6-rs-m0']['vs_version'])
        self.assertIsNone(rows['4.2.6']['vs_version'])


class StallTest(unittest.TestCase):
    def test_level_cycle_without_time(self):
        states = [{'kind': 'progress', 'turn': 59800, 'decisions': 16000, 'energy': 5000, 'depth': 2},
                  {'kind': 'progress', 'turn': 59893, 'decisions': 16100, 'energy': 6000, 'depth': 2},
                  {'kind': 'progress', 'turn': 59893, 'decisions': 16200, 'energy': 16000, 'depth': 1},
                  {'kind': 'progress', 'turn': 59893, 'decisions': 16300, 'energy': 26000, 'depth': 2}]
        trace = ('BORG 59893 # Munchkin Mode.  Power Climb. \n'
                 'BORG 59893 # Munchkin Mode.  Power Diving. \n'
                 'BORG 59893 # Munchkin Mode.  Power Climb. \n')
        st = stall.observer(states, trace)
        self.assertEqual(st['kind'], 'level_cycle')
        self.assertEqual((st['states_at_last_turn'], st['decisions_delta'], st['energy_delta'], st['depth_changes']),
                         (3, 200, 20000, 2))
        self.assertEqual(st['top_notes_at_last_turn'][0], ('# Munchkin Mode.  Power Climb. ', 2))

    def test_aliased_cycle_is_found_from_level_feelings(self):
        states = [{'turn': 9, 'decisions': 0, 'energy': 0, 'depth': 2},
                  {'turn': 9, 'decisions': 100, 'energy': 10000, 'depth': 2}]
        self.assertEqual(stall.observer(states, '')['kind'], 'energy_without_time')
        trace = 'BORG 9 # FEELING_DANGER:8 (+)\nBORG 9 # Fleeing level. Munchkin Mode\n'
        st = stall.observer(states, trace)
        self.assertEqual((st['kind'], st['level_feeling_notes_at_last_turn']), ('level_cycle', 1))

    def test_zero_energy_retry_and_no_decisions(self):
        same = [{'turn': 10, 'decisions': 100, 'energy': 50, 'depth': 3},
                {'turn': 10, 'decisions': 200, 'energy': 50, 'depth': 3}]
        self.assertEqual(stall.observer(same, '')['kind'], 'zero_energy_retry')
        stuck = [{'turn': 10, 'decisions': 100, 'energy': 50, 'depth': 3}]
        self.assertEqual(stall.observer(stuck, '')['kind'], 'no_decisions')

    def test_borgh_keys_without_time(self):
        keys = '100 1 3c 0\n120 1 3e 0\n120 1 3c 0\n120 1 3e 0\n'
        st = stall.borgh(keys, {'stop_reason': 'blocked', 'depth': 2})
        self.assertEqual((st['kind'], st['last_turn'], st['keys_at_last_turn']), ('keys_without_time', 120, 3))

    def test_finished_runs_carry_no_stall(self):
        rec = harness.summarise({'specimen': 's', 'profile': 'p', 'suite': 'smoke', 'seed': 1},
                                {'outcome': 'turn_cap', 'states': [{'kind': 'turn_cap', 'turn': 20000}]},
                                'BORG_OPTIONS borg_plays_risky=0\n', {'settings': {}}, {'ref': 'a' * 40},
                                {'cap': 20000, 'birth': 'fixed'}, {})
        self.assertIsNone(rec['stall'])


class LandingTest(unittest.TestCase):
    def test_forest_axis_adapts_and_draws_each_row(self):
        svg = landing.forest([('a', 0.36, (0.30, 0.43), False), ('b', 0.10, (0.07, 0.15), True),
                              ('c', None, (None, None), False)],
                             x_label='Share of runs that died', y_label='Borg version', highlight_label='other')
        self.assertEqual(svg.count('<circle'), 2 + 2)  # two rows, two legend dots
        self.assertIn('>Share of runs that died<', svg)
        self.assertIn('>Borg version<', svg)
        self.assertIn('>95% interval<', svg)
        self.assertIn('>50%<', svg)
        self.assertNotIn('>60%<', svg)

    def test_landing_answers_from_a_milestones_run(self):
        exp = cat_mod.experiment(ROOT / 'experiments/milestones-early.json')
        cells = [dict(cell(s, seed, 'death' if seed % 3 == 0 else 'turn_cap', turn=500 if seed % 3 == 0 else 100000),
                      suite='early-50', cap=100000) for s in exp['specimens'] for seed in range(1001, 1013)]
        meta = {'experiment': exp, 'run_id': 'r1', 'completed': '2026-11-08 00:00 UTC',
                'catalogue': {'specimens': cat_mod.catalogue()['specimens']['specimens'],
                              'suites': cat_mod.catalogue()['suites']}}
        page = landing.landing_page([(meta, cells, None)], [])
        self.assertIn("Do better-borg-c's fixes change early survival?", page)
        self.assertIn('Not measurably', page)
        self.assertNotIn('Which settings change early survival?', page)
        self.assertIn('class="tab active" href="detailed.html"', page)

    def test_find_arm_prefers_more_seeds_over_newer(self):
        small = [dict(cell('4.2.6', s, 'turn_cap'), profile='default') for s in (1, 2)]
        big = [dict(cell('4.2.6', s, 'death' if s < 30 else 'turn_cap'), profile='default') for s in range(100)]
        newer = {'experiment': {'name': 'smoke'}, 'completed': '2026-11-09 00:00 UTC'}
        older_bigger = {'experiment': {'name': 'classes-1800'}, 'completed': '2026-11-01 00:00 UTC'}
        runs = [(newer, small, None), (older_bigger, big, None)]
        s, meta, _ = landing.find_arm(runs, '4.2.6', 'default', {})
        self.assertEqual(meta['experiment']['name'], 'classes-1800')
        self.assertEqual(s['valid'], 100)

    def test_find_arm_matches_a_specimens_earlier_name(self):
        """Results recorded before the 2026-11-08 rename use the old name (catalogue
        "formerly") - e.g. the real classes-m5 run has 1,800 "bbc-m4" cells, not
        "4.2.6-bbc-m4"; missing that silently drops the only development-scale run."""
        old_named_big = [dict(cell('bbc-m4', s, 'turn_cap'), profile='default') for s in range(1800)]
        new_named_tiny = [dict(cell('4.2.6-bbc-m4', s, 'turn_cap'), profile='default') for s in range(3)]
        runs = [({'experiment': {'name': 'm4-smoke'}, 'completed': '2026-11-09 00:00 UTC'}, new_named_tiny, None),
                ({'experiment': {'name': 'classes-m5'}, 'completed': '2026-11-08 05:05 UTC'}, old_named_big, None)]
        specs = {'4.2.6-bbc-m4': {'formerly': ['bbc-m4']}}
        s, meta, _ = landing.find_arm(runs, '4.2.6-bbc-m4', 'default', specs)
        self.assertEqual(meta['experiment']['name'], 'classes-m5')
        self.assertEqual(s['valid'], 1800)
        # no alias configured: falls back to exact match only, same as before
        self.assertEqual(landing.find_arm(runs, '4.2.6-bbc-m4', 'default', {})[0]['valid'], 3)

    def test_card_exemplars_scatters_every_setup_with_a_class_grid(self):
        def arm(specimen, profile, deaths, n, completed, classes=()):
            cells = [dict(cell(specimen, s, 'death' if s < deaths else 'turn_cap', max_depth=5 if s % 2 else 1),
                          profile=profile, played_class=classes[s % len(classes)] if classes else None)
                     for s in range(n)]
            return ({'experiment': {'name': specimen + profile, 'suites': ['classes-1800']},
                     'run_id': 'r1', 'completed': completed}, cells, None)

        classes = ('Warrior', 'Mage')
        runs = [arm('4.2.6', 'default', 40, 100, '2026-11-09 00:00 UTC', classes),
                arm('4.2.6', 'munchkin-wdr', 25, 100, '2026-11-08 00:00 UTC', classes),
                arm('4.2.6-bbc-munchkin-by-class', 'default', 20, 100, '2026-11-09 01:00 UTC', classes),
                arm('neo-b3-api2-upstream', 'default', 60, 100, '2026-11-08 20:00 UTC', classes)]
        card = landing.card_exemplars(runs)
        for name in ('Vanilla', 'Vanilla + munchkin', 'Recommended mix', 'better-borg-c M8', 'borg-rs M8 (Rust)',
                     'Neo Angband (Mandos, upstream)'):
            self.assertIn(name, card)
        self.assertIn('never paired', card)
        self.assertIn('source</a>', card)  # the catalogue's own source link, not hand-written
        self.assertIn('By class', card)
        self.assertIn('>Warrior<', card)
        self.assertIn('>Mage<', card)
        self.assertNotIn('>Druid<', card)  # no data for it: excluded, not shown empty
        self.assertIn('not one controlled comparison', card)  # cross-run caveat (review finding #38 S1)
        self.assertIn('classes-1800 · 2026-11-09 00:00 UTC', card)  # run/suite/date per row (S2)
        self.assertIn('most finished cells', card)  # not "newest": that is only the tiebreaker (S3)
        self.assertNotIn('newest, most-sampled', card)
        self.assertIn('Depth + level', card)  # the combined figure, not the DL5 threshold rate
        self.assertNotIn('DL5', card)
        self.assertNotIn('reached DL', card)
        self.assertIn('class="dot rust"', card)  # the Rust port's own color, not just its triangle shape
        self.assertNotIn('M8 + munchkin', card)  # dropped: a no-op on both lines (review #39)
        self.assertIsNone(landing.card_exemplars([]))

    def test_turn_snapshots_section_labels_turns_and_skips_arms_without_milestones(self):
        def arm_with_milestones(specimen, profile, n, cap, level, depth):
            cells = []
            for s in range(n):
                c = dict(cell(specimen, s, 'turn_cap', max_depth=depth, turn=cap), profile=profile, cap=cap,
                         milestones=[{'turn': int(cap * f), 'level': level, 'max_depth': depth} for f in
                                     (0.25, 0.5, 0.75, 1.0)])
                cells.append(c)
            return cells

        runs = [({'experiment': {'name': 'classes-1800', 'suites': ['classes-1800']},
                  'run_id': 'r1', 'completed': '2026-11-09 00:00 UTC'},
                 arm_with_milestones('4.2.6', 'default', 10, 100000, 2, 1) +
                 arm_with_milestones('4.2.6-bbc-munchkin-by-class', 'default', 10, 100000, 4, 3) +
                 [dict(cell('4.2.6-rs-m4', s, 'turn_cap'), profile='default', cap=100000)
                  for s in range(10)],  # no milestones: no depth_stream, as real rs-m4 has none
                 None)]
        specs = cat_mod.catalogue()['specimens']['specimens']
        points, found = landing.exemplar_points(runs, specs)
        section = landing.turn_snapshots_section(found)
        self.assertIn('Progress over turns', section)
        for turn in ('25,000', '50,000', '75,000', '100,000'):
            self.assertIn(turn, section)
        self.assertIn('class-cell', section)
        # Vanilla (circle) and the recommended mix (diamond) have milestones at all 4 fractions,
        # so 4 marks each; rs-m4 (triangle) has none, so it contributes no mark anywhere, not a
        # half-drawn one - a dot needs both an x and a y, which the docstring should (and does) say.
        self.assertEqual(section.count('<circle class="dot "'), 4)
        self.assertEqual(section.count('<polygon class="dot hi"'), 4)
        self.assertNotIn('<polygon class="dot "', section)
        self.assertEqual(landing.turn_snapshots_section([]), '')

    def test_class_grid_shares_one_axis_scale_across_classes(self):
        # One class near the top of both axes, the other near the bottom:
        # under a per-cell auto-scaled axis these would draw gridlines at
        # different percentages; review #39 found the footer's claimed
        # "0-50-100%" was true for at most one class at a time. The y-axis is
        # now a plain depth+level number (not a 0-100% rate), so the exact
        # tick count depends on the data; what must hold is that every cell
        # gets the SAME count, proving one shared scale, not one each.
        def arm(classes_and_outcomes):
            cells = []
            for cls, (deaths, n) in classes_and_outcomes.items():
                cells += [dict(cell('4.2.6', s + hash(cls) % 1000, 'death' if s < deaths else 'turn_cap',
                                     max_depth=5 if s % 2 else 1), profile='default', played_class=cls)
                          for s in range(n)]
            return ({'experiment': {'name': 'classes', 'suites': ['classes-1800']},
                     'run_id': 'r1', 'completed': '2026-11-09 00:00 UTC'}, cells, None)

        runs = [arm({'Warrior': (5, 100), 'Mage': (95, 100)})]
        specs = cat_mod.catalogue()['specimens']['specimens']
        grid = landing.class_grid(runs, specs)
        cells = grid.split('<div class="class-cell">')[1:]
        self.assertEqual(len(cells), 2)
        tick_counts = [c.count('class="axis"') for c in cells]
        self.assertEqual(tick_counts[0], tick_counts[1])
        self.assertGreater(tick_counts[0], 2)

    def test_overview_page_has_no_milestone_cards(self):
        page = landing.overview_page([])
        self.assertIn('class="tab active" href="index.html"', page)
        self.assertNotIn("Do better-borg-c's fixes change early survival?", page)
        self.assertNotIn('How far has the Rust port got?', page)
        self.assertIn('Add your Borg to the zoo', page)
        self.assertIn('issues/30', page)
        self.assertIn('pull/32', page)


    def test_port_status_reads_identity_and_skips(self):
        specs = {'4.2.6': {'carries': 0, 'ref': 'a'}, '4.2.6-bbc-m1': {'carries': 2, 'ref': 'b'},
                 '4.2.6-bbc-m2': {'carries': 7, 'ref': 'c'}, '4.2.6-bbc-m3': {'carries': 34, 'ref': 'd'},
                 '4.2.6-rs-m0-c': {'kind': 'borg-rs', 'impl': 'c', 'ref': 'r0'},
                 '4.2.6-rs-m0': {'kind': 'borg-rs', 'impl': 'rust', 'ref': 'r0', 'formerly': ['rs-rust']},
                 '4.2.6-rs-m2-c': {'kind': 'borg-rs', 'impl': 'c', 'ref': 'r2'},
                 '4.2.6-rs-m2': {'kind': 'borg-rs', 'impl': 'rust', 'ref': 'r2'}}
        old = [dict(cell(s, seed, 'turn_cap'), play_sha256=f'k{seed}') for s in ('4.2.6-rs-m0-c', 'rs-rust') for seed in (1, 2)]
        new = [dict(cell(s, seed, 'turn_cap'), play_sha256=f'k{seed}{s[-1] if seed == 2 else ""}')
               for s in ('4.2.6-rs-m2-c', '4.2.6-rs-m2') for seed in (1, 2)]
        runs = [({'experiment': {'specimens': ['4.2.6-rs-m0-c', 'rs-rust']}}, old, None),
                ({'experiment': {'specimens': ['4.2.6-rs-m2-c', '4.2.6-rs-m2']}}, new, None)]
        cols = {c['n']: c for c in landing.port_status(runs, specs)}
        self.assertEqual((cols[0]['state'], cols[0]['rust']['same'], cols[0]['rust']['pairs']), ('identical', 2, 2))
        self.assertEqual(cols[1]['state'], 'skipped')
        self.assertEqual((cols[2]['state'], cols[2]['rust']['same']), ('differs', 1))
        self.assertEqual(cols[3]['state'], 'not_yet')
        self.assertIn('games identical', landing.port_diagram(list(cols.values())))


class ClassProfileTest(unittest.TestCase):
    def test_a_class_dependent_profile_resolves_per_seed(self):
        cat = cat_mod.catalogue()
        suite = cat['suites']['classes-1800']
        by_class = {}
        for seed in suite['seeds'][:18]:
            cls = cat_mod.character(suite, seed)[1]
            by_class[cls] = cat_mod.resolve_profile(cat, {'suite': 'classes-1800', 'profile': 'munchkin-wdr',
                                                          'seed': seed})[0]
        self.assertEqual(by_class['Warrior'], 'munchkin-d6')
        self.assertEqual(by_class['Ranger'], 'munchkin-d6')
        self.assertEqual(by_class['Mage'], 'default')
        self.assertEqual(cat_mod.resolve_profile(cat, {'suite': 'smoke', 'profile': 'munchkin-wdr', 'seed': 11})[0],
                         'munchkin-d6')  # fixed birth is a Warrior
        self.assertEqual(cat_mod.profile_parts(cat, 'munchkin-wdr'), ['default', 'munchkin-d6'])

    def test_a_class_dependent_profile_needs_a_known_class(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'x.json'
            path.write_text(json.dumps({'name': 'x', 'specimens': ['4.2.6'], 'profiles': ['munchkin-wdr'],
                                        'suites': ['early-50-random'], 'control': '4.2.6'}))
            with self.assertRaisesRegex(ValueError, 'random birth'):
                cat_mod.experiment(path)
def mandos_record(outcome='turn_cap', turn=100004, race='Dwarf', cls='Warrior', settings=None, **extra):
    flags = {f: False for f in mandos.FLAGS.values()}
    flags['borg.selfScum'] = True
    flags.update(settings or {})
    rec = {'schema': 'mandos/zoo-run@1', 'outcome': outcome, 'turn': turn, 'depth': 2, 'maxDepth': 3,
           'level': 6, 'maxLevel': 7, 'hp': 40, 'maxHp': 60, 'energy': 50, 'decisions': 900, 'attempts': 905,
           'loopCalls': 905, 'noCommandReplies': 5, 'causeOfDeath': 'a soldier' if outcome == 'death' else None,
           'birth': {'race': race, 'class': cls, 'raceSelection': 'assigned', 'classSelection': 'assigned'},
           'settings': flags, 'cfg': {}, 'firstDepthTurns': {'0': 0, '1': 30, '3': 5000},
           'turnCap': {'requested': 100000, 'actual': turn, 'overshoot': turn - 100000, 'exact': turn == 100000,
                       'unit': 'core_game_tick'},
           'playSha256': 'ab' * 32, 'provenance': {'bundleSha256': 'cd' * 32, 'runtime': {'node': 'v22.23.4'}},
           'metadata': {'wallTimeMs': 1000.0}, 'stall': None, 'stopped': None}
    rec.update(extra)
    return rec


class MandosTest(unittest.TestCase):
    def setUp(self):
        self.cat = cat_mod.catalogue()
        self.spec = self.cat['specimens']['specimens']['neo-b3-mandos']
        self.suite = dict(self.cat['suites']['classes-18'])
        self.cell = {'suite': 'classes-18', 'specimen': 'neo-b3-mandos', 'profile': 'default', 'seed': 42}

    def summary(self, record, profile='default', states=(), error=None):
        return mandos.summarise(dict(self.cell, profile=profile), self.spec, self.cat['profiles'][profile],
                                self.suite, record, list(states), ('Dwarf', 'Warrior'), error, 1.0)

    def test_command_names_birth_cap_settings_and_fresh_outputs(self):
        cmd = mandos.command('/src', '/b/bundle', self.cell, 'Dwarf', 'Warrior', 100000, Path('/w/run'),
                             Path('/w/settings.json'))
        self.assertEqual(cmd[:2], ['node', '/src/tools/zoo-run.mjs'])
        for flag, value in (('--bundle', '/b/bundle'), ('--seed', '42'), ('--turns', '100000'), ('--race', 'Dwarf'),
                            ('--class', 'Warrior'), ('--out', '/w/run/run.json'), ('--settings', '/w/settings.json')):
            self.assertEqual(cmd[cmd.index(flag) + 1], value)
        self.assertEqual(mandos.flags(self.cat['profiles']['plays-risky']), {'borg.playsRisky': True})

    def test_all_six_outcomes(self):
        expected = {'death': 'death', 'turn_cap': 'turn_cap', 'stalled': 'stalled', 'borg_stopped': 'borg_stopped',
                    'decision_cap': 'decision_cap', 'harness_failure': 'harness_failure'}
        for raw, zoo in expected.items():
            turn = 5000 if raw == 'death' else 100004
            rec = mandos_record(raw, turn=turn, stall={'kind': 'repeat', 'command': {'code': 'walk'}}
                                if raw == 'stalled' else None, error={'message': 'boom'} if raw == 'harness_failure'
                                else None)
            self.assertEqual(self.summary(rec)['outcome'], zoo, raw)
        self.assertEqual(self.summary(mandos_record('death', turn=5000))['cause'], 'a soldier')

    def test_missing_or_foreign_record_is_a_harness_failure(self):
        self.assertEqual(self.summary(None, error='no run.json (exit code 1)')['outcome'], 'harness_failure')
        self.assertEqual(self.summary({'schema': 'other@1', 'outcome': 'death'})['outcome'], 'harness_failure')

    def test_overshoot_is_kept_and_a_death_after_the_cap_is_alive_at_the_cap(self):
        c = self.summary(mandos_record('turn_cap', turn=101016))
        self.assertEqual((c['turn_cap']['requested'], c['turn_cap']['actual'], c['turn_cap']['overshoot']),
                         (100000, 101016, 1016))
        late = self.summary(mandos_record('death', turn=100300))
        self.assertEqual(late['outcome'], 'turn_cap')
        self.assertEqual(late['died_after_cap'], {'turn': 100300, 'cause': 'a soldier'})

    def test_effective_settings_and_character_are_checked(self):
        ok = self.summary(mandos_record(settings={'borg.playsRisky': True}), profile='plays-risky')
        self.assertIsNone(ok['config_error'])
        self.assertEqual(ok['settings_effective']['borg.playsRisky'], True)
        bad = self.summary(mandos_record(), profile='plays-risky')
        self.assertEqual(bad['outcome'], 'config_error')
        self.assertEqual(self.summary(mandos_record(race='Human'))['outcome'], 'config_error')

    def test_provenance_states_and_play_hash(self):
        c = self.summary(mandos_record())
        self.assertEqual(c['play_sha256'], 'ab' * 32)
        self.assertEqual(c['binary_sha256'], 'cd' * 32)
        self.assertEqual(c['first_turn_at_depth'], {'0': 0, '1': 30, '3': 5000})
        self.assertEqual(c['boundary'], 'after-key')
        self.assertEqual(c['final']['loop_calls'], 905)
        states = [{'kind': 'periodic', 'turn': 900, 'decisions': 100, 'depth': 1, 'energy': 0},
                  {'kind': 'periodic', 'turn': 900, 'decisions': 200, 'depth': 2, 'energy': 300}]
        st = self.summary(mandos_record('stalled', stall={'kind': 'repeat', 'command': {'code': 'walk'}}),
                          states=states)['stall']
        self.assertEqual((st['kind'], st['decisions_delta'], st['energy_delta'], st['depth_changes']),
                         ('repeat', 100, 300, 1))

    def test_unfinished_runs_are_never_deaths(self):
        cells = [dict(self.summary(mandos_record(o, turn=5000 if o == 'death' else 100004)), seed=i)
                 for i, o in enumerate(['death', 'stalled', 'borg_stopped', 'decision_cap', 'harness_failure'])]
        s = stats.arm_summary(cells)
        self.assertEqual((s['deaths'], s['valid']), (1, 1))

    def test_experiments_reject_what_mandos_cannot_do(self):
        with tempfile.TemporaryDirectory() as tmp:
            for exp, message in (({'specimens': ['neo-b3-mandos'], 'profiles': ['default'], 'suites': ['early-50-random']},
                                  'no random birth'),
                                 ({'specimens': ['neo-b3-mandos'], 'profiles': ['money-scum-5k'], 'suites': ['smoke']},
                                  'cannot apply'),
                                 ({'specimens': ['neo-b3-borg-1.4.0-beta.4'], 'profiles': ['default'],
                                   'suites': ['smoke']}, 'cannot be measured yet')):
                path = Path(tmp) / 'x.json'
                path.write_text(json.dumps({'name': 'x', 'control': exp['specimens'][0], **exp}))
                with self.assertRaisesRegex(ValueError, message):
                    cat_mod.experiment(path, self.cat)

    def test_neo_runs_are_never_paired_with_c_runs(self):
        exp = {'name': 'mixed', 'specimens': ['4.2.6', 'neo-b3-mandos'], 'profiles': ['default'],
               'suites': ['smoke'], 'control': '4.2.6'}
        cells = [dict(cell('4.2.6', s, 'death'), harness_kind='better-borg-c') for s in (11, 29, 47)]
        cells += [dict(self.summary(mandos_record('turn_cap')), suite='smoke', seed=s, specimen='neo-b3-mandos')
                  for s in (11, 29, 47)]
        rows = {r['specimen']: r for r in stats.analyse(exp, cells)['smoke']}
        self.assertIsNone(rows['neo-b3-mandos']['vs_version'])


def api2_record(specimen, outcome='turn_cap', **extra):
    lane = {'upstream': 'upstream', 'port-only': 'port-only'}
    rec = mandos_record(outcome, controllerProfile='api2-plugin', commandStreamProfile='api2-intents-v1',
                        acceptedCommands=899, commandStreamEvents=901, hostReads={'worldReads': 900},
                        crossModFlags={'bugfix.borgFixes': True}, profileLimits={'stores': 'Core'})
    rec['provenance'] = dict(rec['provenance'], commit=specimen['ref'],
                             lane={'name': lane[specimen['lane']], 'includesCTranslations': False})
    rec.update(extra)
    return rec


class NeoOriginalTest(unittest.TestCase):
    def test_boundary_and_died_after_cap(self):
        spec = {'ref': 'b' * 40, 'engine_ref': 'e' * 40, 'toolkit_ref': 't' * 40}
        suite = {'cap': 1000, 'birth': 'assigned'}
        cell = {'suite': 's', 'specimen': 'x', 'profile': 'default', 'seed': 1, 'race': 'Human', 'class': 'Warrior'}
        record = {'schema': 'neo-original/run@1', 'outcome': 'death', 'turn': 1200, 'causeOfDeath': 'a rat',
                  'provenance': {'engine': {'commit': 'e' * 40}, 'borg': {'commit': 'b' * 40}},
                  'birth': {'race': 'Human', 'class': 'Warrior'}}
        rec = neo_original.summarise(cell, spec, suite, record, None, 1.0)
        self.assertEqual(rec['boundary'], 'after-key')
        self.assertEqual(rec['outcome'], 'turn_cap')
        self.assertEqual(rec['died_after_cap'], {'turn': 1200, 'cause': 'a rat'})


class MandosApi2LaneTest(unittest.TestCase):
    def setUp(self):
        self.cat = cat_mod.catalogue()
        self.specs = self.cat['specimens']['specimens']
        self.suite = dict(self.cat['suites']['smoke'])

    def summary(self, name, record, seed=11):
        cell = {'suite': 'smoke', 'specimen': name, 'profile': 'default', 'seed': seed}
        return mandos.summarise(cell, self.specs[name], self.cat['profiles']['default'], self.suite, record, [],
                                ('Dwarf', 'Warrior'), None, 1.0)

    def test_lanes_are_exact_tag_snapshots_with_the_same_profiles(self):
        up, port = self.specs['neo-b3-api2-upstream'], self.specs['neo-b3-api2-port.2']
        self.assertEqual((up['ref'], port['ref']), ('45dee074117d8b4ef49b4b28cd26f118b167ac49',
                                                    'ca659c519de769b6eb42ef62cb0bf088d57f9772'))
        for spec in (up, port):
            self.assertEqual((spec['controller_profile'], spec['command_stream_profile']),
                             ('api2-plugin', 'api2-intents-v1'))
            self.assertNotIn('pending', spec)
        self.assertEqual(self.specs['neo-b3-mandos']['command_stream_profile'], mandos.LEGACY_STREAM)

    def test_profiles_lane_and_counters_are_kept(self):
        spec = self.specs['neo-b3-api2-port.2']
        c = self.summary('neo-b3-api2-port.2', api2_record(spec))
        self.assertEqual(c['outcome'], 'turn_cap')
        self.assertEqual((c['controller_profile'], c['command_stream_profile']), ('api2-plugin', 'api2-intents-v1'))
        self.assertEqual(c['lane']['name'], 'port-only')
        self.assertEqual((c['final']['accepted_commands'], c['final']['command_stream_events']), (899, 901))
        self.assertEqual(c['cross_mod_flags'], {'bugfix.borgFixes': True})

    def test_a_record_of_another_profile_or_commit_is_a_harness_failure(self):
        spec = self.specs['neo-b3-api2-upstream']
        legacy = mandos_record()  # no profile fields: the legacy play-session runner
        c = self.summary('neo-b3-api2-upstream', legacy)
        self.assertEqual(c['outcome'], 'harness_failure')
        self.assertIn('commandStreamProfile', c['error'])
        moved = api2_record(spec)
        moved['provenance']['commit'] = '0' * 40
        self.assertEqual(self.summary('neo-b3-api2-upstream', moved)['outcome'], 'harness_failure')
        # The legacy specimen still accepts its own records.
        self.assertEqual(mandos.profile_errors(self.specs['neo-b3-mandos'], legacy), [])
        self.assertTrue(mandos.profile_errors(self.specs['neo-b3-mandos'], api2_record(spec)))

    def test_the_lanes_pair_with_each_other_but_not_with_legacy_mandos(self):
        up, port = self.specs['neo-b3-api2-upstream'], self.specs['neo-b3-api2-port.2']
        cells = []
        for s in (11, 29, 47):
            cells.append(dict(self.summary('neo-b3-api2-upstream', api2_record(up, 'death', turn=5000), s)))
            cells.append(dict(self.summary('neo-b3-api2-port.2', api2_record(port), s)))
            legacy_spec = self.specs['neo-b3-mandos']
            cells.append(dict(mandos.summarise({'suite': 'smoke', 'specimen': 'neo-b3-mandos', 'profile': 'default',
                                                'seed': s}, legacy_spec, self.cat['profiles']['default'],
                                               self.suite, mandos_record(), [], ('Dwarf', 'Warrior'), None, 1.0)))
        exp = {'name': 'lanes', 'specimens': ['neo-b3-api2-upstream', 'neo-b3-api2-port.2', 'neo-b3-mandos'],
               'profiles': ['default'], 'suites': ['smoke'], 'control': 'neo-b3-api2-upstream'}
        rows = {r['specimen']: r for r in stats.analyse(exp, cells)['smoke']}
        self.assertEqual(rows['neo-b3-api2-port.2']['vs_version']['rescued'], 3)
        self.assertIsNone(rows['neo-b3-mandos']['vs_version'])
        # Equal hashes under different stream profiles are not identical play.
        a, b = cells[1], cells[2]
        self.assertEqual(a['play_sha256'], b['play_sha256'])
        self.assertFalse(stats.same_play(a, b))
        self.assertTrue(stats.same_play(a, dict(a)))


class SubsetSuiteTest(unittest.TestCase):
    def test_subset_keeps_the_parent_assignment(self):
        cat = cat_mod.catalogue()
        sub, parent = cat['suites']['classes-1800-warriors'], cat['suites']['classes-1800']
        self.assertEqual(len(sub['seeds']), 200)
        for seed in sub['seeds']:
            self.assertEqual(cat_mod.character(sub, seed), cat_mod.character(parent, seed))
            self.assertEqual(cat_mod.character(sub, seed)[1], 'Warrior')

    def test_warrior_confirmation_seeds_are_fresh(self):
        cat = cat_mod.catalogue()
        mine = set(cat['suites']['warriors-600']['seeds'])
        others = {s for name, suite in cat['suites'].items() if name != 'warriors-600' for s in suite['seeds']}
        self.assertEqual(len(mine), 600)
        self.assertFalse(mine & others)


class StatsTest(unittest.TestCase):
    def test_progress_score_is_the_median_of_the_combined_figure_not_two_medians(self):
        cells = [cell('a', 1, 'turn_cap', max_depth=1), cell('a', 2, 'turn_cap', max_depth=5),
                 cell('a', 3, 'turn_cap', max_depth=9)]
        cells[0]['final']['max_level'] = 20  # score 21: high level, low depth
        cells[1]['final']['max_level'] = 1   # score 6
        cells[2]['final']['max_level'] = 1   # score 10
        # sum of separate medians would be median(depth)=5 + median(level)=1 = 6; the real,
        # per-cell-then-medianed figure is different: scores sorted are 6, 10, 21 -> median 10.
        self.assertEqual(stats.progress_score(cells), 10)
        # A death still counts (how far it got, not whether it survived) - DESIGN.md "Open questions" #1.
        dead = dict(cell('a', 4, 'death'), final={'turn': 10, 'max_depth': 50, 'max_level': 50})  # score 100
        self.assertEqual(stats.progress_score(cells + [dead]), 15.5)  # scores 6,10,21,100 -> (10+21)/2
        self.assertIsNone(stats.progress_score([cell('a', 1, 'stalled')]))  # operational: excluded

    def test_milestone_progress_score_combines_per_cell_and_excludes_early_deaths(self):
        def with_milestones(c, rows):
            return dict(c, milestones=rows)

        cells = [
            with_milestones(cell('a', 1, 'turn_cap'), [{'turn': 50, 'level': 1, 'max_depth': 20}]),  # score 21
            with_milestones(cell('a', 2, 'turn_cap'), [{'turn': 50, 'level': 1, 'max_depth': 1}]),    # score 2
            with_milestones(cell('a', 3, 'death', turn=70),
                            [{'turn': 50, 'level': 3, 'max_depth': 3}]),  # died after turn 50: score 6
            with_milestones(cell('a', 4, 'death', turn=10),
                            [{'turn': 50, 'level': 9, 'max_depth': 9}]),  # died before: excluded
        ]
        rows = stats.milestone_progress_score(cells, fractions=(1.0,))
        self.assertEqual(rows, [{'fraction': 1.0, 'turn': 50, 'n': 3, 'score': 6}])  # sorted 2,6,21 -> median 6
        self.assertEqual(stats.milestone_progress_score([cell('a', 1, 'turn_cap')], fractions=(1.0,)),
                         [{'fraction': 1.0, 'turn': None, 'n': 0, 'score': None}])

    def test_wilson_and_mcnemar(self):
        lo, hi = stats.wilson(0, 10)
        self.assertEqual(lo, 0.0)
        self.assertAlmostEqual(hi, 0.2775, places=3)
        self.assertEqual(stats.mcnemar_exact(0, 0), None)
        self.assertAlmostEqual(stats.mcnemar_exact(0, 6), 0.03125)
        self.assertEqual(stats.mcnemar_exact(3, 3), 1.0)

    def test_paired_counts(self):
        control = [cell('a', 1, 'death', turn=500), cell('a', 2, 'turn_cap', trace='x'),
                   cell('a', 3, 'death', turn=900), cell('a', 4, 'stalled')]
        arm = [cell('b', 1, 'turn_cap', max_depth=5), cell('b', 2, 'turn_cap', trace='x'),
               cell('b', 3, 'turn_cap'), cell('b', 4, 'turn_cap')]
        v = stats.paired(control, arm)
        self.assertEqual((v['pairs'], v['rescued'], v['newly_killed'], v['identical_traces']), (3, 2, 0, 1))
        self.assertEqual(v['goal_gained'], 1)

    def test_operational_outcomes_are_not_deaths(self):
        s = stats.arm_summary([cell('a', 1, 'stalled'), cell('a', 2, 'death', turn=10), cell('a', 3, 'turn_cap')])
        self.assertEqual((s['valid'], s['deaths'], s['counts']['stalled']), (2, 1, 1))

    def test_milestone_table_excludes_deaths_before_the_milestone_turn(self):
        """A death's last state is its death state. A cell that died at turn 666 on a
        20,000-turn cap must not contribute that death to the 20,000-turn row just
        because milestones() always fills all four fractions (review finding on #33:
        milestone_table counted every death at every later milestone)."""
        def with_milestones(c, rows):
            return dict(c, milestones=rows)

        cells = [
            with_milestones(cell('a', 1, 'turn_cap'), [{'turn': 50, 'level': 4, 'max_depth': 1, 'gold': 100}]),
            with_milestones(cell('a', 2, 'turn_cap'), [{'turn': 50, 'level': 6, 'max_depth': 2, 'gold': 300}]),
            with_milestones(cell('a', 3, 'death', turn=70),
                            [{'turn': 50, 'level': 2, 'max_depth': 1}]),  # died after turn 50: still counts
            with_milestones(cell('a', 4, 'death', turn=10),
                            [{'turn': 50, 'level': 1, 'max_depth': 0, 'gold': 999}]),  # died before: excluded
            dict(cell('a', 5, 'stalled'), milestones=None),  # operational: excluded
        ]
        rows = stats.milestone_table(cells, fractions=(1.0,))
        self.assertEqual(rows, [{'fraction': 1.0, 'turn': 50, 'n': 3,
                                 'median_level': 4, 'median_max_depth': 1, 'median_gold': 200}])
        self.assertEqual(stats.milestone_table([cell('a', 1, 'turn_cap')], fractions=(1.0,)),
                         [{'fraction': 1.0, 'turn': None, 'n': 0,
                           'median_level': None, 'median_max_depth': None, 'median_gold': None}])


class EndToEndTest(unittest.TestCase):
    def test_collect_and_site(self):
        exp = cat_mod.experiment(ROOT / 'experiments/milestones-smoke.json')
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / 'cells').mkdir()
            records = [cell(s, seed, 'death' if (s == '4.2.6' and seed == 11) else 'turn_cap')
                       for s in exp['specimens'] for seed in (11, 29)]
            (tmp / 'cells/a.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in records))
            main(['collect', '--experiment', str(ROOT / 'experiments/milestones-smoke.json'),
                  '--cells', str(tmp / 'cells'), '--results', str(tmp / 'results'), '--run-id', 't-1'])
            run = tmp / 'results/milestones-smoke/t-1'
            cells = [json.loads(x) for x in (run / 'cells.jsonl').read_text().splitlines()]
            self.assertEqual(len(cells), 15)
            self.assertEqual(sum(c['outcome'] == 'harness_failure' for c in cells), 5)
            self.assertEqual(json.loads((run / 'meta.json').read_text())['missing_cells'], 5)
            self.assertEqual(site.build_site(tmp / 'results', tmp / 'site'), 1)
            page = (tmp / 'site/runs/milestones-smoke/t-1/index.html').read_text()
            self.assertIn('Paired against 4.2.6, same profile', page)
            self.assertIn('Rescued', page)
            self.assertNotIn('same version', page)

    def test_site_renders_milestones_when_present(self):
        exp = cat_mod.experiment(ROOT / 'experiments/milestones-smoke.json')
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / 'cells').mkdir()
            records = [dict(cell(s, seed, 'turn_cap'), milestones=[{'turn': 5000, 'level': 10, 'max_depth': 4}])
                       for s in exp['specimens'] for seed in (11, 29)]
            (tmp / 'cells/a.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in records))
            main(['collect', '--experiment', str(ROOT / 'experiments/milestones-smoke.json'),
                  '--cells', str(tmp / 'cells'), '--results', str(tmp / 'results'), '--run-id', 't-1'])
            self.assertEqual(site.build_site(tmp / 'results', tmp / 'site'), 1)
            page = (tmp / 'site/runs/milestones-smoke/t-1/index.html').read_text()
            self.assertIn('Level, max depth and gold by engine turn', page)
            self.assertIn('lv 10', page)

    def test_two_paired_views(self):
        exp = {"name": "two-views", "specimens": ["4.2.6", "4.2.6-bbc-m4"], "profiles": ["default", "shipped", "dynamic-calcs"], "suites": ["early-50"], "control": "4.2.6", "control_profile": "default"}
        cells = [dict(cell(s, seed, 'turn_cap', profile=p), suite='early-50')
                 for s in exp['specimens'] for p in exp['profiles'] for seed in (1, 2)]
        rows = stats.analyse(exp, cells)['early-50']
        by = {(r['specimen'], r['profile']): r for r in rows}
        self.assertIsNone(by[('4.2.6', 'default')]['vs_version'])
        self.assertIsNone(by[('4.2.6', 'default')]['vs_profile'])
        self.assertIsNotNone(by[('4.2.6', 'dynamic-calcs')]['vs_profile'])
        self.assertIsNone(by[('4.2.6', 'dynamic-calcs')]['vs_version'])
        self.assertIsNotNone(by[('4.2.6-bbc-m4', 'dynamic-calcs')]['vs_version'])
        self.assertIsNotNone(by[('4.2.6-bbc-m4', 'dynamic-calcs')]['vs_profile'])


if __name__ == '__main__':
    unittest.main()
