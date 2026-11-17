"""borg-reborn-rs errands-plan arms through the borg-rs adapter (borg-zoo#123)."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from zoo import borgrs, catalogue

PLAN = b'[default]\n1-49 loop-levels 0 1\n'
PLAN_SHA = hashlib.sha256(PLAN).hexdigest()
SPECIMEN = '4.2.6-reborn-rust-plan-m13'


def fixture_catalogue():
    """The real catalogue, with the plan specimen pinning the fixture plan."""
    cat = copy.deepcopy(catalogue.catalogue())
    cat['specimens']['specimens'][SPECIMEN]['plans'] = {'errands_plan.txt': PLAN_SHA}
    return cat


def cell_for(cat, profile):
    exp = catalogue.experiment('experiments/reborn-plan-m13-classes-18.json', cat)
    return next(c for c in catalogue.cells(exp, cat) if c['profile'] == profile)


class PlanArmsTest(unittest.TestCase):
    def build_dir(self, root, spec, plans=True):
        (root / 'build.json').write_text(json.dumps({
            'source_commit': spec['ref'], 'impl': spec['impl'],
            **({'plans': {'errands_plan.txt': PLAN_SHA}} if plans else {})}))
        (root / 'borg.txt').write_text('borg_reborn_core = reborn\nborg_cheat_death = FALSE\n')
        if plans:
            (root / 'plans').mkdir()
            (root / 'plans/errands_plan.txt').write_bytes(PLAN)

    def run_with(self, cat, profile, rc=0, summary=None, env=None, strip_plans=False,
                 loaded='core', keys_text='1 k 0 0\n'):
        """loaded: 'core' copies the plan as the core does, else the bytes to
        write as the output directory's loaded-plan copy (None: no copy)."""
        cell = cell_for(cat, profile)
        spec = cat['specimens']['specimens'][cell['specimen']]
        if strip_plans:  # the same cell on a specimen that ships no plans
            del spec['plans']
        seen = {}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build_dir(root, spec)

            def run(argv, **kwargs):
                out = Path(argv[argv.index('-keylog') + 1]).parent
                seen['env'] = kwargs['env']
                seen['borg.txt'] = (out / 'user/borg.txt').read_text()
                plan = out / 'user/errands_plan.txt'
                seen['plan'] = plan.read_bytes() if plan.exists() else None
                (out / 'keys.log').write_text(keys_text)
                copy = (seen['plan'] if loaded == 'core' else loaded) if summary is not None else None
                if copy is not None:
                    (out / borgrs.LOADED_PLAN).write_bytes(copy)
                if summary is not None:
                    race, cls = catalogue.character(cat['suites'][cell['suite']], cell['seed'])
                    (out / 'summary.json').write_text(json.dumps({'race': race, 'class': cls, **summary}))
                return type('Result', (), {'returncode': rc})()
            with patch('zoo.borgrs.subprocess.run', side_effect=run), patch.dict('os.environ', env or {}):
                record = borgrs.run_cell(cell, root, root / 'work', cat)
        return record, seen

    def test_plan_cell_ships_the_plan_and_records_its_hash(self):
        record, seen = self.run_with(fixture_catalogue(), 'reborn-m13-plan-shop',
                                     summary={'stop_reason': 'turns', 'dead': False},
                                     env={'BORG_RUN_DIR': '/x', 'BORG_PARAM_foo': '3', 'BORG_ERRAND': '/ladder',
                                          'BORG_ERRANDS_PLAN': '/x/plan.txt', 'BORG_STOPSCARED': 'flee',
                                          'BORG_TOWN_PLAN_RECORD': '/global/bad', 'BORG_TRIP_RECORD': '/global/bad'})
        self.assertEqual(seen['plan'], PLAN)
        self.assertIn('\nborg_plan = errands_plan.txt\n', '\n' + seen['borg.txt'])
        self.assertEqual(record['plan'], {'name': 'errands_plan.txt', 'sha256': PLAN_SHA, 'loaded_sha256': PLAN_SHA})
        self.assertIsNone(record['observed_outcome'])
        self.assertEqual(record['frozen_turn_loop']['bursts'], 0)
        self.assertEqual(record['outcome'], 'turn_cap')
        self.assertIsNone(record['config_error'])
        self.assertEqual([n for n in seen['env'] if n.startswith('BORG_')], [])

    def test_no_plan_cell_gets_no_plan_file(self):
        record, seen = self.run_with(fixture_catalogue(), 'reborn-m13-shop',
                                     summary={'stop_reason': 'turns', 'dead': False})
        self.assertIsNone(seen['plan'])
        self.assertIsNone(record['plan'])
        self.assertNotIn('borg_plan', seen['borg.txt'])

    def test_exit_2_is_a_config_error(self):
        for profile in ('reborn-m13-plan', 'reborn-m13-control'):
            with self.subTest(profile=profile):
                record, _ = self.run_with(fixture_catalogue(), profile, rc=2)
                self.assertEqual(record['outcome'], 'config_error')
                self.assertIn('exit code 2', record['config_error'])

    def test_exit_2_stays_a_harness_failure_without_plans(self):
        record, _ = self.run_with(fixture_catalogue(), 'reborn-m13-control', rc=2, strip_plans=True)
        self.assertEqual(record['outcome'], 'harness_failure')

    def test_borg_stopped_with_a_mismatch_is_a_config_error(self):
        record, _ = self.run_with(fixture_catalogue(), 'reborn-m13-plan',
                                  summary={'stop_reason': 'borg_stopped', 'dead': False, 'race': 'Gnome'})
        self.assertEqual(record['outcome'], 'config_error')
        self.assertIn('expected', record['config_error'])

    def test_borg_stopped_is_its_own_outcome_for_plan_specimens(self):
        record, _ = self.run_with(fixture_catalogue(), 'reborn-m13-plan',
                                  summary={'stop_reason': 'borg_stopped', 'dead': False})
        self.assertEqual(record['outcome'], 'borg_stopped')
        self.assertIsNone(record['error'])

    def test_older_specimens_keep_their_classification(self):
        record, _ = self.run_with(fixture_catalogue(), 'reborn-m13-control', strip_plans=True,
                                  summary={'stop_reason': 'borg_stopped', 'dead': False})
        self.assertEqual(record['outcome'], 'stalled')

    def test_plan_not_loaded_is_a_config_error(self):
        for loaded in (None, b'other plan'):
            with self.subTest(loaded=loaded):
                record, _ = self.run_with(fixture_catalogue(), 'reborn-m13-plan', loaded=loaded,
                                          summary={'stop_reason': 'turns', 'dead': False})
                self.assertEqual(record['outcome'], 'config_error')
                self.assertIn('not loaded', record['config_error'])

    def test_a_plan_loaded_without_being_asked_for_is_a_config_error(self):
        record, _ = self.run_with(fixture_catalogue(), 'reborn-m13-shop', loaded=PLAN,
                                  summary={'stop_reason': 'turns', 'dead': False})
        self.assertEqual(record['outcome'], 'config_error')
        self.assertIn('no plan requested', record['config_error'])

    def test_frozen_turn_loop_is_a_stall(self):
        burst = ''.join(f'52639 k {i:x} 0\n' for i in range(borgrs.LOOP_KEYS))
        normal = ''.join(f'{t} k 0 0\n' for t in range(1, 400))
        record, _ = self.run_with(fixture_catalogue(), 'reborn-m13-plan-shop', keys_text=normal + burst + normal,
                                  summary={'stop_reason': 'turns', 'dead': False})
        self.assertEqual(record['outcome'], 'stalled')
        self.assertEqual(record['observed_outcome'], 'turn_cap')
        self.assertIn('borg-rs#90', record['error'])
        self.assertEqual(record['stall']['kind'], 'frozen_turn_loop')
        self.assertEqual(record['frozen_turn_loop'], {'turn': 52639, 'max_keys': borgrs.LOOP_KEYS,
                                                      'bursts': 1, 'burst_keys': borgrs.LOOP_KEYS})

    def test_loop_checks_without_plans(self):
        burst = ''.join(f'52639 k {i:x} 0\n' for i in range(borgrs.LOOP_KEYS))
        cat = fixture_catalogue()
        cat['specimens']['specimens'][SPECIMEN]['loop_checks'] = True
        record, _ = self.run_with(cat, 'reborn-m13-shop', strip_plans=True, keys_text=burst,
                                  summary={'stop_reason': 'turns', 'dead': False})
        self.assertEqual(record['outcome'], 'stalled')
        self.assertEqual(record['frozen_turn_loop']['bursts'], 1)
        spec = catalogue.catalogue()['specimens']['specimens']['4.2.6-rs-pr92-home-fix']
        self.assertTrue(borgrs.loop_checks(spec) and not spec.get('plans'))

    def test_busy_shopping_turns_are_not_a_loop(self):
        text = ''.join(f'7 k {i:x} 0\n' for i in range(383)) + '8 k 0 0\n'
        self.assertEqual(borgrs.frozen_turn_loop(text), {'turn': 7, 'max_keys': 383, 'bursts': 0, 'burst_keys': 0})
        self.assertEqual(borgrs.frozen_turn_loop('')['bursts'], 0)

    def test_older_specimen_records_are_unchanged(self):
        record, _ = self.run_with(fixture_catalogue(), 'reborn-m13-control', strip_plans=True,
                                  summary={'stop_reason': 'turns', 'dead': False})
        self.assertNotIn('frozen_turn_loop', record)
        self.assertNotIn('observed_outcome', record)

    def test_key_outliers_are_flagged_against_the_arm_median(self):
        def rec(profile, keys, outcome='turn_cap', **extra):
            return {'suite': 's', 'specimen': 'x', 'profile': profile, 'outcome': outcome,
                    'final': {'keys': keys}, **extra}
        shop = [rec('shop', k) for k in (9000, 10000, 10900, 11000, 12000, 16893)]
        loop = rec('shop', 69838, 'stalled', observed_outcome='turn_cap')
        early_death = rec('shop', 835, 'death')
        small_arm = [rec('plan', k) for k in (100, 100000)]
        self.assertEqual(borgrs.flag_key_outliers(shop + [loop, early_death] + small_arm), 1)
        self.assertEqual(loop['key_outlier'], {'keys': 69838, 'arm_median': 11000, 'ratio': 6.35})
        self.assertTrue(all('key_outlier' not in r for r in shop + [early_death] + small_arm))

    def test_tier_suites_are_disjoint_slices_of_classes_1800(self):
        suites = catalogue.catalogue()['suites']
        full = suites['classes-1800']
        union = [s for t in ('small', 'medium', 'big', 'full') for s in suites['classes-1800-' + t]['seeds']]
        self.assertEqual(union, full['seeds'])
        small = suites['classes-1800-small']
        self.assertEqual(len(small['seeds']), 90)
        for seed in small['seeds']:
            self.assertEqual(catalogue.character(small, seed), catalogue.character(full, seed))
        verysmall, rest = suites['classes-1800-verysmall'], suites['classes-1800-small-rest']
        self.assertEqual(verysmall['seeds'] + rest['seeds'], small['seeds'])
        per_class = {}
        for seed in verysmall['seeds']:
            cls = catalogue.character(verysmall, seed)[1]
            per_class[cls] = per_class.get(cls, 0) + 1
        self.assertEqual(sorted(set(per_class.values())), [5])
        with self.assertRaisesRegex(ValueError, 'outside the parent'):
            catalogue.expand_suites({'p': {'seed_rule': {'generator': 'sha256-v1', 'count': 9}, 'birth': 'assigned',
                                           'characters': {'races': ['Human'], 'classes': ['Warrior']}},
                                     't': {'subset': {'suite': 'p', 'range': [5, 10]}}})

    def test_build_carrying_other_plan_bytes_is_refused(self):
        cat = fixture_catalogue()
        cell = cell_for(cat, 'reborn-m13-plan')
        spec = cat['specimens']['specimens'][cell['specimen']]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build_dir(root, spec)
            (root / 'plans/errands_plan.txt').write_bytes(PLAN + b'# edited\n')
            with self.assertRaisesRegex(ValueError, 'does not carry plan'):
                borgrs.run_cell(cell, root, root / 'work', cat)

    def test_copy_plans_checks_the_pinned_hash(self):
        spec = {'ref': 'r', 'plans': {'errands_plan.txt': PLAN_SHA}}
        with tempfile.TemporaryDirectory() as tmp:
            source, out = Path(tmp) / 'src', Path(tmp) / 'out'
            (source / 'harness/plans').mkdir(parents=True)
            out.mkdir()
            with self.assertRaisesRegex(ValueError, 'not in harness/plans'):
                borgrs.copy_plans(spec, source, out)
            (source / 'harness/plans/errands_plan.txt').write_bytes(PLAN)
            self.assertEqual(borgrs.copy_plans(spec, source, out), {'errands_plan.txt': PLAN_SHA})
            self.assertEqual((out / 'plans/errands_plan.txt').read_bytes(), PLAN)
            (source / 'harness/plans/errands_plan.txt').write_bytes(b'other')
            with self.assertRaisesRegex(ValueError, 'catalogue pins'):
                borgrs.copy_plans(spec, source, out)

    def test_plan_names_are_bare_file_names(self):
        for bad in ('../borg.txt', 'plans/x.txt', '.hidden', '', 'borg.txt'):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                borgrs.plan_name(bad)

    def test_catalogue_pins_the_requested_plan_bytes(self):
        spec = catalogue.catalogue()['specimens']['specimens'][SPECIMEN]
        self.assertEqual(spec['plans'], {
            'errands_plan.txt': '922372ba849489c579449f8cd6f827b29ed65b6e8e0f67bd0fe8be2f3cb160cd'})

    def test_profile_plan_must_be_pinned_by_every_specimen(self):
        cat = catalogue.catalogue()
        with tempfile.TemporaryDirectory() as tmp:
            exp = json.loads(Path('experiments/reborn-plan-m13-classes-18.json').read_text())
            for profiles, specimens in ((['reborn-m13-control', 'reborn-m13-ambitious-shop'], [SPECIMEN]),
                                        (['reborn-core-borgrs', 'reborn-m13-plan'], ['4.2.6-reborn-core-pilot'])):
                with self.subTest(profiles=profiles):
                    path = Path(tmp) / 'exp.json'
                    path.write_text(json.dumps({**exp, 'profiles': profiles, 'specimens': specimens,
                                                'control': specimens[0], 'control_profile': profiles[0]}))
                    with self.assertRaisesRegex(ValueError, 'borg_plan'):
                        catalogue.experiment(path, cat)


if __name__ == '__main__':
    unittest.main()
