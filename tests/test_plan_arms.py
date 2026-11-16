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

    def run_with(self, cat, profile, rc=0, summary=None, env=None):
        cell = cell_for(cat, profile)
        spec = cat['specimens']['specimens'][cell['specimen']]
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
                (out / 'keys.log').write_text('1 k 0 0\n')
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
                                     env={'BORG_RUN_DIR': '/x', 'BORG_PARAM_foo': '3', 'BORG_ERRAND': '/ladder'})
        self.assertEqual(seen['plan'], PLAN)
        self.assertIn('\nborg_plan = errands_plan.txt\n', '\n' + seen['borg.txt'])
        self.assertEqual(record['plan'], {'name': 'errands_plan.txt', 'sha256': PLAN_SHA})
        self.assertEqual(record['outcome'], 'turn_cap')
        self.assertIsNone(record['config_error'])
        for name in ('BORG_RUN_DIR', 'BORG_PARAM_foo', 'BORG_ERRAND'):
            self.assertNotIn(name, seen['env'])

    def test_no_plan_cell_gets_no_plan_file(self):
        record, seen = self.run_with(fixture_catalogue(), 'reborn-m13-shop',
                                     summary={'stop_reason': 'turns', 'dead': False})
        self.assertIsNone(seen['plan'])
        self.assertIsNone(record['plan'])
        self.assertNotIn('borg_plan', seen['borg.txt'])

    def test_exit_2_is_a_config_error(self):
        record, _ = self.run_with(fixture_catalogue(), 'reborn-m13-plan', rc=2)
        self.assertEqual(record['outcome'], 'config_error')
        self.assertIn('exit code 2', record['config_error'])

    def test_borg_stopped_is_its_own_outcome_for_plan_specimens(self):
        record, _ = self.run_with(fixture_catalogue(), 'reborn-m13-plan',
                                  summary={'stop_reason': 'borg_stopped', 'dead': False})
        self.assertEqual(record['outcome'], 'borg_stopped')
        self.assertIsNone(record['error'])

    def test_older_specimens_keep_their_classification(self):
        self.assertEqual(borgrs.STOP['borg_stopped'], 'stalled')

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
        for bad in ('../borg.txt', 'plans/x.txt', '.hidden', ''):
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
