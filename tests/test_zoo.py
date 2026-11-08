import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from zoo import catalogue as cat_mod  # noqa: E402
from zoo import borgrs, harness, landing, site, stall, stats  # noqa: E402
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

    def test_every_suite_declares_a_role(self):
        for name, suite in cat_mod.catalogue()['suites'].items():
            self.assertIn(suite.get('role'), ('pilot', 'development', 'confirmation', 'sealed'), name)

    def test_sealed_suite_needs_the_owner(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'x.json'
            exp = {'name': 'x', 'specimens': ['pristine'], 'profiles': ['default'],
                   'suites': ['sealed-2000'], 'control': 'pristine'}
            path.write_text(json.dumps(exp))
            with self.assertRaises(ValueError):
                cat_mod.experiment(path)
            path.write_text(json.dumps({**exp, 'unsealed_by_owner': '2026-12-01: final claim on X'}))
            self.assertTrue(cat_mod.experiment(path))


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

    def test_borg_rs_specimens_reject_random_birth(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / 'bad.json'
            bad.write_text(json.dumps({'name': 'x', 'specimens': ['rs-rust'], 'profiles': ['default'],
                                       'suites': ['early-50-random'], 'control': 'rs-rust'}))
            with self.assertRaises(ValueError):
                cat_mod.experiment(bad)

    def test_plan_carries_build_kind(self):
        exp = cat_mod.experiment(ROOT / 'experiments/rs-smoke.json')
        plan = cat_mod.plan(exp, 2)
        kinds = {b['specimen']: b['kind'] for b in plan['builds']}
        self.assertEqual(kinds, {'rs-c': 'borg-rs', 'rs-rust': 'borg-rs', 'pristine': 'better-borg-c'})
        self.assertTrue(all('kind' in r and 'ref' in r for r in plan['runs']))

    def test_no_pairing_across_harnesses(self):
        exp = cat_mod.experiment(ROOT / 'experiments/rs-smoke.json')
        cells = []
        for s in exp['specimens']:
            for seed in (11, 29):
                c = cell(s, seed, 'turn_cap')
                c['harness_kind'] = 'better-borg-c' if s == 'pristine' else 'borg-rs'
                cells.append(c)
        rows = {r['specimen']: r for r in stats.analyse(exp, cells)['smoke'] if r['profile'] == 'default'}
        self.assertIsNotNone(rows['rs-rust']['vs_version'])
        self.assertIsNone(rows['pristine']['vs_version'])


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
                              ('c', None, (None, None), False)])
        self.assertEqual(svg.count('<circle'), 2)
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


class StatsTest(unittest.TestCase):
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


class EndToEndTest(unittest.TestCase):
    def test_collect_and_site(self):
        exp = cat_mod.experiment(ROOT / 'experiments/milestones-smoke.json')
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / 'cells').mkdir()
            records = [cell(s, seed, 'death' if (s == 'pristine' and seed == 11) else 'turn_cap')
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
            self.assertIn('Paired against pristine, same profile', page)
            self.assertIn('Rescued', page)
            self.assertNotIn('same version', page)

    def test_two_paired_views(self):
        exp = {"name": "two-views", "specimens": ["pristine", "bbc-m4"], "profiles": ["default", "shipped", "dynamic-calcs"], "suites": ["early-50"], "control": "pristine", "control_profile": "default"}
        cells = [dict(cell(s, seed, 'turn_cap', profile=p), suite='early-50')
                 for s in exp['specimens'] for p in exp['profiles'] for seed in (1, 2)]
        rows = stats.analyse(exp, cells)['early-50']
        by = {(r['specimen'], r['profile']): r for r in rows}
        self.assertIsNone(by[('pristine', 'default')]['vs_version'])
        self.assertIsNone(by[('pristine', 'default')]['vs_profile'])
        self.assertIsNotNone(by[('pristine', 'dynamic-calcs')]['vs_profile'])
        self.assertIsNone(by[('pristine', 'dynamic-calcs')]['vs_version'])
        self.assertIsNotNone(by[('bbc-m4', 'dynamic-calcs')]['vs_version'])
        self.assertIsNotNone(by[('bbc-m4', 'dynamic-calcs')]['vs_profile'])


if __name__ == '__main__':
    unittest.main()
