"""Paired planning retains every case and the exact requested Zoo setup."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zoo import define,encounters as native,incident_comparison as comparison
from test_incident_bank import plan_fixture
ROOT=Path(__file__).resolve().parents[1]


def baseline_fixture():
    p=plan_fixture();p['definition_sha256']=native.sha(ROOT/'scenario-experiments/balanced999-incidents-execution.json')
    p['definition']['bank_artifact'].update(id=14289964111,run_id=43979480269)
    for i,c in enumerate(p['cases']):
        c['scenario_sha256']=f'{i:064x}'
        c['scenario'].update(race_idx=i%11,start_turn=100,save_sha256=f'{i+1000:064x}')
    p.pop('plan_hash');p['plan_hash']=native.digest(p);return p


class ComparisonTest(unittest.TestCase):
    def test_both_yaml_definitions_are_current(self):
        for name in ['balanced999-incidents-execution','balanced999-incidents-speed30-comparison']:
            _,problems,changes=define.plan(ROOT/'definitions'/(name+'.yaml'))
            self.assertEqual(problems,[]);self.assertEqual(changes,[])

    def test_same999_saves_are_planned_in_both_arms_with_balanced_tiers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);native.write(root/'baseline.json',baseline_fixture())
            with patch.object(native,'git',return_value='f'*40):
                p=comparison.freeze(ROOT/'scenario-experiments/balanced999-incidents-speed30-comparison.json',root/'baseline.json',root/'plan.json')
            self.assertEqual(p['expected_cells'],1998);self.assertEqual(len(p['cases']),999)
            self.assertEqual([s['cumulative_cells'] for s in p['stages']],[36,180,720,1800,1998])
            self.assertEqual(p['arms'][1]['settings']['borg_param_attack_speed_fight_danger_tenths'],30)
            self.assertEqual(p['arms'][1]['settings']['borg_plan'],'errands_plan.txt')
            self.assertEqual(p['status'],'planned_not_executed')
            self.assertEqual(len({c['save_sha256'] for c in p['cases']}),999)
            self.assertNotEqual(p['cases'][0]['candidate_borg_txt_sha256'],p['cases'][1]['candidate_borg_txt_sha256'])
            body={k:v for k,v in p.items() if k!='plan_hash'};self.assertEqual(native.digest(body),p['plan_hash'])

    def test_changed_profile_cannot_be_relabelled_as_exact_zoo_setup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);native.write(root/'baseline.json',baseline_fixture())
            definition=native.read(ROOT/'scenario-experiments/balanced999-incidents-speed30-comparison.json')
            definition['reference_profile']['settings']['borg_param_attack_speed_fight_danger_tenths']=60
            native.write(root/'definition.json',definition)
            with self.assertRaisesRegex(ValueError,'snapshot differs'):
                comparison.freeze(root/'definition.json',root/'baseline.json',root/'plan.json')
