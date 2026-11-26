"""Death bundles for the cemetery (borg-zoo#176)."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from zoo import borgrs, catalogue, deaths

PLAN = b'[default]\n1-49 loop-levels 0 1\n'
PLAN_SHA = hashlib.sha256(PLAN).hexdigest()
SPECIMEN = '4.2.6-reborn-rust-plan-m13'
BUILD_ID = {'git_rev': 'abc', 'source_sha256': 'src', 'binary_sha256': 'bin'}


def fixture_catalogue():
    cat = copy.deepcopy(catalogue.catalogue())
    cat['specimens']['specimens'][SPECIMEN]['plans'] = {'errands_plan.txt': PLAN_SHA}
    return cat


def cell_for(cat, profile):
    exp = catalogue.experiment('experiments/reborn-plan-m13-classes-18.json', cat)
    return next(c for c in catalogue.cells(exp, cat) if c['profile'] == profile)


class DeathBundleTest(unittest.TestCase):
    def play(self, cat, profile, replay_keys=None, trace_lines=0, keep=False, relative=False, yaml_config=False):
        """Run a cell to a death, then bundle it; (record, entry, bundle dir files, replay env)."""
        cell = cell_for(cat, profile)
        spec = cat['specimens']['specimens'][cell['specimen']]
        race, cls = catalogue.character(cat['suites'][cell['suite']], cell['seed'])
        calls = []

        execute = subprocess.run

        def run(argv, **kwargs):
            if argv[0] == sys.executable:
                return execute(argv, **kwargs)
            out = Path(argv[argv.index('-keylog') + 1]).parent
            calls.append({'argv': argv, 'env': kwargs['env']})
            replay = len(calls) > 1
            if yaml_config:
                self.assertFalse((out / "user/borg.txt").exists())
                self.assertTrue((out / "user/pborg.yaml").is_file())
            (out / 'keys.log').write_text(replay_keys if replay and replay_keys is not None else '1 k 0 0\n')
            plan = out / 'user/errands_plan.txt'
            if plan.exists():
                (out / borgrs.LOADED_PLAN).write_bytes(plan.read_bytes())
            if replay and trace_lines:
                (out / 'trace-core.jsonl').write_text(''.join(f'{{"n": {i}}}\n' for i in range(trace_lines)))
            (out / 'summary.json').write_text(json.dumps({
                'race': race, 'class': cls, 'stop_reason': 'death', 'dead': True,
                'death_cause': 'a crow', 'game_turns': 500, 'seed': cell['seed']}))
            return type('Result', (), {'returncode': 0})()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = {
                'source_commit': spec['ref'], 'impl': spec['impl'], 'binary_sha256': 'bin',
                'build_id': BUILD_ID, 'plans': {'errands_plan.txt': PLAN_SHA}}
            if yaml_config:
                # A stand-in for the pinned converter exercises the receipt round trip.
                converter = root / 'pborg-config.py'
                converter.write_text("import sys\nfor line in sys.stdin:\n"
                                     "    print(line.replace(' = ', ': ').rstrip())\n")
                manifest['build_id'] = dict(BUILD_ID, pborg_config='yaml')
                manifest['pborg_converter_sha256'] = borgrs.sha256(converter)
            (root / 'build.json').write_text(json.dumps(manifest))
            (root / 'borg.txt').write_text('borg_reborn_core = reborn\nborg_cheat_death = FALSE\n')
            (root / 'plans').mkdir()
            (root / 'plans/errands_plan.txt').write_bytes(PLAN)
            with patch('zoo.borgrs.subprocess.run', side_effect=run), \
                    patch('zoo.deaths.subprocess.run', side_effect=run), \
                    patch.dict('os.environ', {'BORG_ERRAND': '/x'}):
                record = borgrs.run_cell(cell, root, root / 'work', cat, keep=keep)
                cwd = os.getcwd()
                try:
                    if relative:  # as compare.yml passes it: --deaths deaths/<specimen>-<shard>
                        os.chdir(root)
                    entry = deaths.bundle(record, cell, root, cat, Path('deaths') if relative else root / 'deaths',
                                          {'experiment': 'x', 'run_id': '42'}, keep=keep)
                finally:
                    os.chdir(cwd)
            out = root / 'deaths' / catalogue.cell_key(cell)
            files = {p.relative_to(out).as_posix(): p.read_bytes() for p in out.rglob('*') if p.is_file()} \
                if out.exists() else {}
        return record, entry, files, calls

    def test_yaml_cell_and_death_replay_record_the_same_settings(self):
        record, entry, files, calls = self.play(fixture_catalogue(), 'reborn-m13-plan-shop',
                                                yaml_config=True)
        self.assertEqual(entry['status'], 'reproduced')
        self.assertEqual(len(calls), 2)
        yaml = files['user/pborg.yaml']
        self.assertIn(b'borg_plan: errands_plan.txt', yaml)
        self.assertEqual(record['pborg_yaml_sha256'], hashlib.sha256(yaml).hexdigest())
        self.assertIn(f"pborg_yaml_sha256={record['pborg_yaml_sha256']}".encode(), files['config.txt'])

    def test_reproduced_death_is_a_cemetery_run_directory(self):
        record, entry, files, calls = self.play(fixture_catalogue(), 'reborn-m13-plan-shop', trace_lines=500)
        self.assertEqual(record['outcome'], 'death')
        self.assertEqual(entry['status'], 'reproduced')
        for name in ('summary.json', 'keys.log', 'config.txt', 'BUILD_ID', 'user/borg.txt',
                     'user/errands_plan.txt', 'zoo-death.json', 'trace-core.jsonl', 'trace-core.lines'):
            self.assertIn(name, files)
        replay = calls[1]
        self.assertIn('-msglog', replay['argv'])
        self.assertIn('-statelog', replay['argv'])
        self.assertEqual(replay['env']['BORG_RUN_DIR'], str(Path(replay['argv'][replay['argv'].index('-keylog') + 1]).parent))
        self.assertNotIn('BORG_ERRAND', replay['env'])
        config = dict(line.split('=', 1) for line in files['config.txt'].decode().splitlines())
        self.assertEqual(config['seed'], str(record['seed']))
        self.assertEqual(config['zoo_profile'], 'reborn-m13-plan-shop')
        self.assertEqual(config['zoo_run'], '42')
        self.assertEqual(config['borg_errands_plan'], 'user/errands_plan.txt')
        self.assertEqual(config['errands_plan_sha256'], PLAN_SHA)
        self.assertEqual(config['borg_txt_sha256'], hashlib.sha256(files['user/borg.txt']).hexdigest())
        self.assertEqual(config['borg_txt_sha256'], record['config_sha256'])
        self.assertIn(b'git_rev=abc\n', files['BUILD_ID'])
        self.assertEqual(len(files['trace-core.jsonl'].splitlines()), deaths.TRACE_KEEP)
        self.assertTrue(files['trace-core.jsonl'].endswith(b'{"n": 499}\n'))
        self.assertEqual(files['trace-core.lines'], b'500\n')
        manifest = json.loads(files['zoo-death.json'])
        self.assertEqual(manifest['record']['play_sha256'], record['play_sha256'])
        self.assertEqual(manifest['build']['trace_core']['lines'], 500)

    def test_a_relative_bundle_root_still_reproduces(self):
        # Run 44098927907: compare.yml's relative --deaths made the game, which runs
        # in the game directory, read and write somewhere else; all 11 bundles failed.
        _, entry, files, calls = self.play(fixture_catalogue(), 'reborn-m13-plan-shop', relative=True)
        argv = calls[1]['argv']
        for flag in ('-keylog', '-summary', '-statelog', '-msglog'):
            self.assertTrue(Path(argv[argv.index(flag) + 1]).is_absolute(), flag)
        self.assertTrue(all(Path(a.split('=', 1)[1]).is_absolute() for a in argv if a.startswith('-duser=')))
        self.assertEqual(entry['status'], 'reproduced')
        self.assertIn('keys.log', files)

    def test_different_replay_keys_are_kept_but_not_reproduced(self):
        _, entry, files, _ = self.play(fixture_catalogue(), 'reborn-m13-shop', replay_keys='1 x 0 0\n')
        self.assertEqual(entry['status'], 'not_reproduced')
        self.assertIn('replay keys', entry['error'])
        self.assertIn('zoo-death.json', files)
        self.assertNotIn('user/errands_plan.txt', files)
        self.assertNotIn('borg_errands_plan', files['config.txt'].decode())

    def test_replay_sets_the_record_streams_only_when_the_cell_did(self):
        record_vars = ('BORG_TOWN_PLAN_RECORD', 'BORG_TRIP_RECORD')
        cat = fixture_catalogue()
        profile = next(name for name, p in cat['profiles'].items()
                       if p.get('settings', {}).get('borg_town_plan') == 1 and p['settings'].get('borg_plan')
                       and any(c['profile'] == name for c in catalogue.cells(
                           catalogue.experiment('experiments/reborn-plan-m13-classes-18.json', cat), cat)))
        _, entry, files, calls = self.play(cat, profile)
        self.assertEqual(entry['status'], 'reproduced')
        for call in calls:
            self.assertFalse(any(v in call['env'] for v in record_vars))
        self.assertNotIn('zoo_record_streams', files['config.txt'].decode())
        _, entry, files, calls = self.play(cat, profile, keep=True)
        self.assertEqual(entry['status'], 'reproduced')
        cell_env, replay_env = calls[0]['env'], calls[1]['env']
        self.assertIn('BORG_TOWN_PLAN_RECORD', cell_env)
        self.assertEqual({v for v in record_vars if v in cell_env}, {v for v in record_vars if v in replay_env})
        self.assertIn('town-plan.jsonl', files)
        self.assertIn('zoo_record_streams=BORG_TOWN_PLAN_RECORD', files['config.txt'].decode())

    def test_index_lines_are_written_while_other_cells_still_play(self):
        import threading
        from zoo import __main__ as cli
        exp_path = 'experiments/reborn-plan-m13-classes-18.json'
        cat = catalogue.catalogue()
        exp = catalogue.load_experiment(exp_path, '', cat)
        mine = catalogue.cells(exp, cat)[:2]
        first, second = (catalogue.cell_key(c) for c in mine)
        seen = {}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            index = root / 'deaths' / deaths.INDEX

            def run_cell(cell, *args, **kwargs):
                key = catalogue.cell_key(cell)
                if key == second:  # blocks until the first death's index line exists
                    for _ in range(200):
                        if index.exists() and index.read_text().strip():
                            seen['before_last_cell'] = index.read_text()
                            break
                        threading.Event().wait(0.05)
                return {**cell, 'outcome': 'death' if key == first else 'turn_cap',
                        'wall_seconds': 0.1, 'play_sha256': 'k'}

            def bundle(record, cell, *args, **kwargs):
                return {'schema': deaths.SCHEMA, 'cell': catalogue.cell_key(cell), 'status': 'reproduced'}

            with patch('zoo.harness.run_cell', side_effect=run_cell), patch('zoo.deaths.bundle', side_effect=bundle), \
                    patch('zoo.configuration.capture'), patch('zoo.catalogue.shard', return_value=mine):
                cli.main(['run', '--experiment', exp_path, '--specimen', mine[0]['specimen'], '--build', str(root),
                          '--work', str(root / 'work'), '--out', str(root / 'cells/c.jsonl'), '--jobs', '2',
                          '--deaths', str(root / 'deaths')])
            self.assertIn(first, seen.get('before_last_cell', ''))
            self.assertEqual(len(index.read_text().splitlines()), 1)

    def test_a_shard_without_deaths_has_an_empty_index(self):
        from zoo import __main__ as cli
        exp_path = 'experiments/reborn-plan-m13-classes-18.json'
        cat = catalogue.catalogue()
        mine = catalogue.cells(catalogue.load_experiment(exp_path, '', cat), cat)[:1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch('zoo.harness.run_cell', side_effect=lambda cell, *a, **k: {**cell, 'outcome': 'turn_cap', 'wall_seconds': 1}), \
                    patch('zoo.configuration.capture'), patch('zoo.catalogue.shard', return_value=mine):
                cli.main(['run', '--experiment', exp_path, '--specimen', mine[0]['specimen'], '--build', str(root),
                          '--work', str(root / 'work'), '--out', str(root / 'cells/c.jsonl'), '--jobs', '1',
                          '--deaths', str(root / 'deaths')])
            self.assertEqual((root / 'deaths' / deaths.INDEX).read_text(), '')

    def test_other_harness_kinds_are_listed_not_dropped(self):
        cat = catalogue.catalogue()
        name = next(n for n, s in cat['specimens']['specimens'].items() if s.get('kind', 'better-borg-c') != 'borg-rs')
        cell = {'suite': 'classes-18', 'specimen': name, 'profile': 'default', 'seed': 7}
        entry = deaths.bundle({'outcome': 'death'}, cell, '/nowhere', cat, '/nowhere', {})
        self.assertEqual(entry['status'], 'unsupported')

    def test_opt_out_and_selection(self):
        self.assertTrue(deaths.enabled({}))
        self.assertFalse(deaths.enabled({'cemetery_deaths': False}))
        self.assertTrue(deaths.wanted({'outcome': 'death'}))
        for outcome in ('turn_cap', 'stalled', 'config_error', 'harness_failure'):
            self.assertFalse(deaths.wanted({'outcome': outcome}))


if __name__ == '__main__':
    unittest.main()
