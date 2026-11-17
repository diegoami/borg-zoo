"""Saved starts have their own strict contract and complete mixed-class counts."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from zoo import encounters as e
from zoo import define

ROOT = Path(__file__).resolve().parents[1]


def fixture():
    cases = []
    for i in range(8):
        scenario = dict(class_idx=i // 2 + 1, race_idx=4, birth_seed=301 + i, start_turn=101,
                        save_sha256=f'{i:064x}', baseline_profile_sha256='a' * 64,
                        checkpoint=dict(depth=1, max_depth=1), initial_observed=dict(hp=8, max_hp=8, sp=0, max_sp=2),
                        origin=dict(encounter_family='shared-life', parent_death_id=None))
        cases.append(dict(id=f'case-{i}', scenario_sha256=f'{i+10:064x}', scenario=scenario, profile_text='rest_turns = 75\n'))
    p = dict(schema='borg-zoo/saved-encounter-plan@1', expected_cells=8, cases=cases,
             source_sha256='b' * 64, zoo_commit='c' * 40, runner_sha256='d' * 64,
             manifest=dict(horizon_engine_turns=1000, wall_seconds=5, engine_commit='e' * 40),
             definition=dict(name='test', issue=144, definition='definitions/test.yaml',
                             source=dict(commit='f' * 40), bank=dict(commit='a' * 40)))
    p['plan_hash'] = e.digest(p)
    return p


def receipts(p, case, status='survived_horizon'):
    s = case['scenario']
    summary = dict(loaded=True, loaded_turn=101, calendar='fixed', seed=s['birth_seed'], class_idx=s['class_idx'], race_idx=4,
                   game_options=dict(cheat_live=False), dead=status == 'death', stop_reason='death' if status == 'death' else 'turns',
                   game_turns=1101, hp=-1 if status == 'death' else 8, depth=1)
    build = dict(git_rev='f' * 40, source_sha256='b' * 64, inputs_dirty='no', impl='rust',
                 engine_upstream='e' * 40, binary_sha256='c' * 64)
    process = dict(status='success', exit_code=0, executable_sha256_before='c' * 64, executable_sha256_after='c' * 64)
    trial = dict(source_commit='f' * 40, scenario_sha256=case['scenario_sha256'], save_sha256=s['save_sha256'],
                 startup_contract='fresh_borg_saved_engine_rng', borg_memory_restored=False, start_turn=101,
                 horizon_engine_turns=1000, cap_turn=1101, status=status, exit_code=0,
                 build=build, process=process, summary=summary, profile_sha256='a' * 64)
    return {'trial.json': json.dumps(trial), 'summary.json': json.dumps(summary), 'process.json': json.dumps(process),
            'config.txt': f"borg_core=reborn\nflags=menu,keep-load-rng,save=input.save\nsave_sha256={s['save_sha256']}\nprofile_sha256={'a'*64}\n",
            'params.json': json.dumps(dict(parameters=[dict(name='rest_turns', value=75)])),
            'initial-state': '101 0,0 d1/1 hp8/8 sp0/2\n'}


def cell(p, case, raw):
    hashes = {k: hashlib.sha256(v.encode()).hexdigest() for k, v in raw.items()}
    trial = json.loads(raw['trial.json'])
    return dict(id=case['id'], plan_hash=p['plan_hash'], receipts=raw, receipts_sha256=hashes,
                execution_hash=e.digest(dict(plan=p['plan_hash'], scenario=case['scenario_sha256'], build=trial['build'], receipts=hashes)),
                status=trial['status'])


class EncounterTest(unittest.TestCase):
    def test_yaml_and_catalogue_reproduce_frozen_saved_definition(self):
        d, problems, changes = define.plan(ROOT / 'definitions/cemetery-mixed-caster-encounters-smoke.yaml')
        self.assertEqual(d['kind'], 'saved-encounter-smoke')
        self.assertEqual(problems, [])
        self.assertEqual(changes, [])

    def test_native_receipts_require_saved_start_rng_and_effective_profile(self):
        p = fixture()
        c = p['cases'][0]
        raw = receipts(p, c)
        self.assertEqual(e.validate_receipts(p, c, raw), 'survived_horizon')
        for key, replacement in [('initial-state', '101 0,0 d1/1 hp1/8 sp0/2\n'),
                                 ('params.json', '{"parameters": []}'),
                                 ('config.txt', raw['config.txt'].replace('keep-load-rng', 'different'))]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                e.validate_receipts(p, c, dict(raw, **{key: replacement}))
        altered = json.loads(raw['trial.json'])
        altered['borg_memory_restored'] = True
        with self.assertRaises(ValueError):
            e.validate_receipts(p, c, dict(raw, **{'trial.json': json.dumps(altered)}))

    def test_collection_preserves_missing_cells_and_per_class_denominators(self):
        p = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            e.write(root / 'plan.json', p)
            for i in range(2):
                c = p['cases'][i]
                e.write(root / 'attempt/cells' / (c['id'] + '.json'), cell(p, c, receipts(p, c, 'death' if i == 0 else 'survived_horizon')))
            result = e.collect(root / 'plan.json', root / 'attempt', root / 'report')
            self.assertEqual(len(result['cells']), 8)
            self.assertEqual(result['invalid_count'], 6)
            self.assertEqual(result['per_class']['Mage'], {'death': 1, 'survived_horizon': 1})
            self.assertEqual(result['per_class']['Priest'], {'missing': 2})
            self.assertFalse(result['independent_life'])

    def test_changed_or_copied_cell_does_not_count_as_survival(self):
        p = fixture()
        for change in ('receipt', 'identity'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                c = p['cases'][0]
                record = cell(p, c, receipts(p, c))
                if change == 'receipt':
                    record['receipts']['params.json'] = '{}'
                else:
                    record['id'] = 'copied-from-another-case'
                e.write(root / 'plan.json', p)
                e.write(root / 'attempt/cells' / (c['id'] + '.json'), record)
                report = e.collect(root / 'plan.json', root / 'attempt', root / 'report')
                self.assertEqual(report['cells'][0]['status'], 'invalid_receipt')
                self.assertEqual(report['invalid_count'], 8)

    def test_plan_refuses_lost_class_mix_even_with_recomputed_hash(self):
        p = fixture()
        p.pop('plan_hash')
        p['cases'][0]['scenario']['class_idx'] = 0
        p['plan_hash'] = e.digest(p)
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / 'plan.json'
            e.write(file, p)
            with self.assertRaises(ValueError):
                e.load_plan(file)

    def test_failed_trial_is_preserved_without_inventing_binary_receipt(self):
        p = fixture()
        c = p['cases'][0]
        raw = receipts(p, c)
        trial = json.loads(raw['trial.json'])
        trial.update(status='failed', error='build missing')
        trial.pop('build')
        self.assertEqual(e.validate_receipts(p, c, {'trial.json': json.dumps(trial)}), 'failed')


if __name__ == '__main__':
    unittest.main()
