import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from zoo import catalogue, evidence, neo_original, stats
from zoo.__main__ import main

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / 'experiments/originals-20261108-classes-1800.json'


class EvidenceTest(unittest.TestCase):
    def test_inventory_retains_files_and_exact_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'trace.txt').write_bytes(b'final death message\n')
            record = {'suite': 's', 'specimen': 'c', 'profile': 'p', 'seed': 1}
            evidence.attach(record, root)
            self.assertEqual(record['evidence']['files']['trace.txt']['sha256'],
                             hashlib.sha256(b'final death message\n').hexdigest())
            self.assertEqual((root / 'trace.txt').read_bytes(), b'final death message\n')
            evidence.attach(record, root)
            self.assertNotIn('evidence.json', record['evidence']['files'])

    def test_index_separates_failures_caps_and_deaths(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = {'suite': 's', 'specimen': 'neo', 'profile': 'default', 'final': {'turn': 12},
                    'played_race': 'Human', 'played_class': 'Mage'}
            rows = [{**base, 'seed': i, 'outcome': outcome, 'cause': 'eye' if outcome == 'death' else None}
                    for i, outcome in enumerate(('death', 'turn_cap', 'stalled', 'harness_failure'))]
            evidence.write_indexes(tmp, rows)
            deaths = json.loads((Path(tmp) / 'deaths.json').read_text())
            self.assertEqual([r['outcome'] for r in deaths], ['death'])
            self.assertEqual(deaths[0]['diagnosis'], 'unassessed')
            self.assertIn('eye', (Path(tmp) / 'deaths.csv').read_text())

    def test_originals_plan_is_3600_attempts_with_bounded_shards(self):
        exp = catalogue.experiment(EXP)
        plan = catalogue.plan(exp, 4)
        self.assertEqual(plan['cells'], 3600)
        self.assertEqual(len(plan['runs']), 240)
        all_cells = catalogue.cells(exp)
        for arm, count in exp['shards_by_specimen'].items():
            shards = [catalogue.shard(all_cells, arm, i, count) for i in range(count)]
            self.assertEqual(sum(map(len, shards)), 1800)
            wall = exp['resource_budget']['neo_wall_seconds' if arm.startswith('neo') else 'native_wall_seconds']
            self.assertLessEqual(max(map(len, shards)) * wall / 2, 225 * 60)

    def test_retained_shard_counts_exceptions_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def fail(*args, **kwargs):
                raise ValueError('pilot fixture failure')
            argv = ['run', '--experiment', str(EXP), '--specimen', 'angband-e473-original',
                    '--shard', '0', '--shards', '1800', '--build', str(root / 'build'),
                    '--work', str(root / 'work'), '--out', str(root / 'cells.jsonl'), '--jobs', '1']
            with patch('zoo.harness.run_cell', side_effect=fail):
                main(argv)
                rows = [json.loads(line) for line in (root / 'cells.jsonl').read_text().splitlines()]
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]['outcome'], 'harness_failure')
                self.assertIn('pilot fixture failure', rows[0]['error'])
                with self.assertRaises(ValueError):
                    main(argv)


class OriginalNeoTest(unittest.TestCase):
    def setUp(self):
        self.cell = {'suite': 's', 'specimen': 'neo', 'profile': 'default', 'seed': 7,
                     'race': 'Human', 'class': 'Mage'}
        self.spec = {'ref': 'b' * 40, 'engine_ref': 'e' * 40, 'toolkit_ref': 't' * 40}
        self.suite = {'cap': 100000, 'birth': 'assigned'}
        self.raw = {'schema': 'neo-original/run@1', 'outcome': 'death', 'turn': 900,
                    'birth': {'race': 'Human', 'class': 'Mage'}, 'causeOfDeath': 'eye',
                    'provenance': {'engine': {'commit': 'e' * 40}, 'borg': {'commit': 'b' * 40}}}

    def test_death_and_post_cap_death_are_distinct(self):
        row = neo_original.summarise(self.cell, self.spec, self.suite, self.raw, None, 1)
        self.assertEqual(row['outcome'], 'death')
        self.assertNotEqual(stats.pairing_class(row), stats.pairing_class({'harness_kind': 'better-borg-c'}))
        row = neo_original.summarise(self.cell, self.spec, self.suite,
                                     {**self.raw, 'turn': 100001}, None, 1)
        self.assertEqual(row['outcome'], 'turn_cap')
        self.assertEqual(row['died_after_cap']['cause'], 'eye')

    def test_invalid_identity_and_birth_rejected(self):
        row = neo_original.summarise(self.cell, self.spec, self.suite,
                                     {**self.raw, 'provenance': {}}, None, 1)
        self.assertEqual(row['outcome'], 'harness_failure')
        row = neo_original.summarise(self.cell, self.spec, self.suite,
                                     {**self.raw, 'birth': {'race': 'Elf', 'class': 'Mage'}}, None, 1)
        self.assertEqual(row['outcome'], 'config_error')

    def test_harness_failure_does_not_become_birth_error(self):
        row = neo_original.summarise(self.cell, self.spec, self.suite,
                                     {'schema': 'neo-original/run@1', 'outcome': 'harness_failure',
                                      'error': 'unavailable UI'}, None, 1)
        self.assertEqual(row['outcome'], 'harness_failure')
        self.assertEqual(row['error'], 'unavailable UI')

    def test_real_pilot_death_schema_and_messages(self):
        raw = json.loads((ROOT / 'tests/fixtures/neo-original-death.json').read_text())
        cell = {**self.cell, 'seed': raw['seed'], 'race': raw['birth']['race'],
                'class': raw['birth']['class']}
        spec = {**self.spec, 'ref': raw['provenance']['borg']['commit'],
                'engine_ref': raw['provenance']['engine']['commit']}
        row = neo_original.summarise(cell, spec, self.suite, raw, None, 1)
        self.assertEqual(row['outcome'], 'death')
        self.assertEqual(row['cause'], 'metallic green centipede')
        self.assertEqual(row['final']['turn'], 5269)
        self.assertLess(row['final']['hp'], 0)
        self.assertEqual(row['last_messages'], raw['messages'])


class RetainedSafetyTest(unittest.TestCase):
    def test_existing_native_attempt_is_not_deleted(self):
        from zoo import harness
        cat = catalogue.catalogue()
        cell = catalogue.cells(catalogue.experiment(EXP), cat)[0]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build = root / 'build'
            build.mkdir()
            (build / 'build.json').write_text(json.dumps({'source_commit': cat['specimens']['specimens'][cell['specimen']]['ref']}))
            previous = root / 'work' / catalogue.cell_key(cell)
            previous.mkdir(parents=True)
            (previous / 'trace.txt').write_text('unique earlier evidence')
            with self.assertRaisesRegex(ValueError, 'retained attempt already exists'):
                harness.run_cell(cell, build, None, root / 'work', cat, keep=True)
            self.assertEqual((previous / 'trace.txt').read_text(), 'unique earlier evidence')

    def test_shard_collision_does_not_rewrite_previous_inventory(self):
        cat = catalogue.catalogue()
        cell = catalogue.cells(catalogue.experiment(EXP), cat)[0]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            previous = root / 'work' / catalogue.cell_key(cell)
            previous.mkdir(parents=True)
            inventory = previous / 'evidence.json'
            inventory.write_text('unique earlier inventory')
            with self.assertRaisesRegex(ValueError, 'retained attempt already exists'):
                main(['run', '--experiment', str(EXP), '--specimen', cell['specimen'],
                      '--shards', '1800', '--shard', '0', '--build', str(root / 'build'),
                      '--work', str(root / 'work'), '--out', str(root / 'new-output.jsonl')])
            self.assertEqual(inventory.read_text(), 'unique earlier inventory')
            self.assertFalse((root / 'new-output.jsonl').exists())

    def test_missing_lowest_neo_cell_keeps_kind_and_never_pairs(self):
        cat = catalogue.catalogue()
        cat['suites']['classes-1800']['seeds'] = [1, 2]
        base = {'schema': 'borg-zoo/cell@1', 'suite': 'classes-1800', 'profile': 'default',
                'cap': 100000, 'final': {'turn': 100, 'max_depth': 1}, 'first_turn_at_depth': {}}
        rows = [{**base, 'specimen': 'angband-e473-original', 'seed': seed,
                 'harness_kind': 'better-borg-c', 'outcome': 'death'} for seed in (1, 2)]
        rows.append({**base, 'specimen': 'neo-5a9-original', 'seed': 2,
                     'harness_kind': 'neo-original', 'outcome': 'turn_cap'})
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cells = root / 'cells'
            cells.mkdir()
            (cells / 'part.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))
            with patch('zoo.__main__.cat_mod.catalogue', return_value=cat):
                main(['collect', '--experiment', str(EXP), '--cells', str(cells),
                      '--results', str(root / 'results'), '--run-id', 'fixture'])
            target = root / 'results' / 'originals-20261108-classes-1800' / 'fixture'
            actual = [json.loads(line) for line in (target / 'cells.jsonl').read_text().splitlines()]
            missing = next(row for row in actual if row['specimen'] == 'neo-5a9-original' and row['seed'] == 1)
            self.assertEqual(missing['harness_kind'], 'neo-original')
            analysis = stats.analyse(catalogue.experiment(EXP, cat), actual)
            neo = next(row for row in analysis['classes-1800'] if row['specimen'] == 'neo-5a9-original')
            self.assertIsNone(neo['vs_version'])
            self.assertEqual(stats.paired(rows[:2], rows[2:])['pairs'], 0)
