"""The full bank stays balanced and every missing cell stays in the denominator."""
import copy
from collections import Counter
import json
from pathlib import Path
import tempfile
import unittest

from zoo import define,encounters as native,incident_bank as b

ROOT=Path(__file__).resolve().parents[1]


def plan_fixture():
    cases=[dict(id=f'case-{i:04d}',scenario=dict(class_idx=i%9,event_kind='death',origin=dict(encounter_family=f'life-{i//9}'))) for i in range(999)]
    groups=[dict(id=name,cases=[c['id'] for c in group]) for name,group in b.execution_groups(cases)]
    plan=dict(schema='borg-zoo/balanced-incident-execution-plan@1',expected_cells=999,cases=cases,batches=groups,
              manifest=dict(horizon_engine_turns=2000,wall_seconds=5),definition=dict(source=dict(commit='a'*40),bank_artifact=dict(sha256='b'*64)))
    plan['plan_hash']=native.digest(plan)
    return plan


class BalancedTest(unittest.TestCase):
    def test_frozen_harvest_definition_matches_equal_nine_class_target(self):
        d,problems,changes=define.plan(ROOT/'definitions/balanced999-incidents-harvest.yaml')
        self.assertEqual((d['expected_cells'],d['per_class'],d['classes']),(999,111,list(range(9))))
        self.assertEqual(problems,[]);self.assertEqual(changes,[])

    def test_smoke_and_full_partition_do_not_repeat_cases(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'plan.json';native.write(path,plan_fixture());plan=b.read_execution_plan(path)
            self.assertEqual(sum(len(x['cases']) for x in plan['batches']),999)
            self.assertEqual(len(plan['batches'][0]['cases']),18)
            self.assertTrue(all(len(x['cases'])<=40 for x in plan['batches']))
            for tier,total in b.TIERS.items():
                prefix=plan['cases'][:total]
                self.assertEqual(set(Counter(c['scenario']['class_idx'] for c in prefix).values()),{total//9})

    def test_unbalanced_or_duplicate_cases_refused_even_with_new_hash(self):
        for fault in ('balance','duplicate','oversized'):
            p=plan_fixture();p.pop('plan_hash')
            if fault=='balance':p['cases'][0]['scenario']['class_idx']=1
            elif fault=='duplicate':p['batches'][1]['cases'][0]=p['batches'][0]['cases'][0]
            else:p['batches'][1]['cases']+=['extra']*10
            p['plan_hash']=native.digest(p)
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/'plan.json';native.write(path,p)
                with self.assertRaises(ValueError):b.read_execution_plan(path)

    def test_flat_downloaded_artifact_cell_is_collected_and_revalidated(self):
        from test_encounters import fixture,receipts,cell
        old=fixture();p=plan_fixture();case=p['cases'][0]
        case.update(scenario_sha256=old['cases'][0]['scenario_sha256'],profile_text=old['cases'][0]['profile_text'])
        case['scenario'].update(old['cases'][0]['scenario']);case['scenario']['class_idx']=0
        p['source_sha256']=old['source_sha256'];p['definition']['source']=old['definition']['source'];p['manifest']['engine_commit']=old['manifest']['engine_commit']
        p.pop('plan_hash');p['plan_hash']=native.digest(p)
        raw=receipts(p,case);trial=json.loads(raw['trial.json']);trial['horizon_engine_turns']=2000;trial['cap_turn']=2101;trial['summary']['game_turns']=2101
        raw['trial.json']=json.dumps(trial);raw['summary.json']=json.dumps(trial['summary'])
        record=cell(p,case,raw);record['schema']='borg-zoo/saved-encounter-cell@1'
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);native.write(root/'plan.json',p)
            native.write(root/'downloaded/artifact'/('case-0000.json'),record)
            b.collect_execution(root/'plan.json',root/'downloaded',root/'report')
            report=native.read(root/'report/comparison.json')
            self.assertEqual(report['cells'][0]['status'],'survived_horizon')
            self.assertEqual(report['invalid_count'],998)

    def test_empty_interrupted_collection_still_reports999_and111_each(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);native.write(root/'plan.json',plan_fixture())
            self.assertEqual(b.collect_execution(root/'plan.json',root/'missing',root/'report'),1)
            report=native.read(root/'report/comparison.json')
            self.assertEqual(report['expected_cells'],999);self.assertEqual(report['invalid_count'],999)
            self.assertEqual({c['missing'] for c in report['per_class'].values()},{111})
            self.assertFalse(report['independent_life'])


if __name__=='__main__':unittest.main()
