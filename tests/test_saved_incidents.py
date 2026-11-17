"""Saved-state comparisons have balanced complete denominators and their own site."""
from collections import Counter
import copy
import json
from pathlib import Path
import tempfile
import unittest
from zoo import saved_incidents as s


def fixture():
    cases=[]
    for i in range(18):
        outcomes=dict(baseline='death',speed30='survived_horizon')
        cases.append(dict(id=f'case-{i}',class_idx=i%9,race_idx=2,birth_seed=1000+i,start_turn=100,historical_type='death',
            coverage=dict(level=1,depth=1,equipment=[],inventory=[dict(description='<img src=x onerror=alert(1)>')]),selection=dict(trigger_turn=100),origin=dict(encounter_family='same-life'),
            save_sha256='c'*64,scenario_sha256='d'*64,suite='synthetic/bank/shards/000.json',outcomes=outcomes,pair='rescued',details={}))
    return dict(schema=s.SCHEMA,name='saved-study',tier='smoke',expected_cells=36,collected_cells=36,invalid_count=0,stopped_count=0,pairs=dict(rescued=18),cases=cases,
      run_url='https://github.com/diegoami/borg-zoo/actions/runs/1',evidence_url='https://github.com/diegoami/borg-cemetery',howto_url='https://github.com/diegoami/borg-cemetery/blob/main/docs/RUN-A-SCENARIO.md',
      arms=[dict(id='baseline',source=dict(repository='diegoami/borg-reborn-rs',commit='a'*40),core='reborn',build=dict(binary_sha256='e'*64)),
            dict(id='speed30',source=dict(repository='diegoami/borg-reborn-rs',commit='b'*40),core='borg-rs',build=dict(binary_sha256='f'*64),settings={'borg_param_attack_speed_fight_danger_tenths':30},errands_plan_sha256='1'*64)])


class SavedSiteTest(unittest.TestCase):
    def test_site_lists_saved_report_and_every_case_without_natural_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);path=root/'saved-incident-results/saved-study/1/comparison.json';path.parent.mkdir(parents=True);path.write_text(json.dumps(fixture()))
            rows,errors=s.build_site(root/'results',root/'site/scenarios')
            self.assertEqual(len(rows),1);self.assertEqual(errors,[])
            page=(root/'site/scenarios/saved/saved-study/1/index.html').read_text()
            self.assertIn('36 cells',page);self.assertIn('Run one scenario',page)
            self.assertEqual(len(list((root/'site/scenarios/saved/saved-study/1/cases').glob('*/index.html'))),18)
            case=(root/'site/scenarios/saved/saved-study/1/cases/case-0/index.html').read_text()
            self.assertIn('single_encounter.py',case);self.assertIn('--source-commit',case)
            self.assertNotIn('<img src=x',case);self.assertIn('&lt;img',case)
            self.assertFalse((root/'results').exists())

    def test_mismatched_pairs_or_class_balance_and_unsafe_links_are_rejected(self):
        for fault in ['count','class','pairs','link']:
            r=fixture()
            if fault=='count':r['expected_cells']=35
            elif fault=='class':r['cases'][0]['class_idx']=1
            elif fault=='pairs':r['pairs']={'rescued':17}
            else:r['howto_url']='javascript:alert(1)'
            with self.subTest(fault=fault),self.assertRaises(ValueError):s.validate(r)

    def test_bad_saved_report_is_visible_as_unavailable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);path=root/'saved-incident-results/saved-study/1/comparison.json';path.parent.mkdir(parents=True);path.write_text('{"schema":"unknown"}')
            rows,errors=s.build_site(root/'results',root/'site')
            self.assertEqual(rows,[]);self.assertEqual(len(errors),1)
