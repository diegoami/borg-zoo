"""Configured candidate receipts, pairing and interrupted smoke accounting."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from zoo import encounters as n,paired_incidents as p,define,catalogue
from test_encounters import fixture,receipts
ROOT=Path(__file__).resolve().parents[1]


def setup():
    base=n.read(ROOT/'reports/saved-encounters/balanced999-incidents/planning/baseline-plan.json')
    comparison=n.read(ROOT/'reports/saved-encounters/balanced999-incidents/planning/comparison-plan.json')
    plan=dict(schema=p.SCHEMA,cases=base['cases'],batches=base['batches'],arms=comparison['arms'],reference=comparison['definition'],expected_cells=1998,manifest=base['manifest'])
    case=fixture()['cases'][0];case['id']=plan['cases'][0]['id'];case['scenario']['class_idx']=0
    case['scenario']['coverage']=dict(level=1,depth=1,equipment_kind_signature='gear',inventory=[])
    plan['cases'][0]=case
    old=receipts(fixture(),case);t=json.loads(old['trial.json']);t.update(horizon_engine_turns=2000,cap_turn=2101);t['summary']['game_turns']=2101
    arm=plan['arms'][1];arm['source']['commit']='f'*40;arm['build']=t['build'];plan['arms'][0]['source']['commit']='f'*40;plan['arms'][0]['build']=t['build']
    raw={'run/'+k:v for k,v in old.items() if k!='trial.json' and k!='initial-state'}
    raw['initial-state']=old['initial-state'];raw['run/summary.json']=json.dumps(t['summary']);raw['initial-coverage']=json.dumps(case['scenario']['coverage'])
    text=p.candidate_text(plan,case)
    for key,value in dict(borg_reborn_core='FALSE',borg_plan='selected-plan.txt',borg_respawn_race='4',borg_respawn_class='0',borg_cheat_death='FALSE',borg_respawn_winners='FALSE').items():text=catalogue._override(text,key,value)
    h=lambda v:hashlib.sha256(v.encode()).hexdigest()
    loaded=(ROOT/'scenario-inputs/balanced999-speed30/errands_plan.txt').read_text();raw['run/errands_plan.txt']=loaded;raw['run/user/borg.txt']=text
    parameters={k:v for k,v in arm['settings'].items() if k.startswith('borg_param_')}
    raw['run/params-core.json']=json.dumps([dict(name=k.removeprefix('borg_param_'),value=v,origin='borg.txt') for k,v in parameters.items()])
    proof=dict(core='borg-rs',template_sha256=h(p.candidate_text(plan,case)),applied_borg_txt_sha256=h(text),named_parameters=parameters,plan_sha256=h(loaded),loaded_plan_sha256=h(loaded))
    t['configuration']=proof;raw['run/configuration.json']=json.dumps(proof)
    raw['run/config.txt']='\n'.join(['borg_core=borg-rs','borg_core_overrides=on','flags=menu,keep-load-rng','save_sha256='+case['scenario']['save_sha256'],
        'borg_txt_sha256='+h(text),'params_core_sha256='+h(raw['run/params-core.json']),'borg_errands_plan_sha256='+h(loaded)])+'\n'
    raw['trial.json']=json.dumps(t);plan['plan_hash']=n.digest(plan)
    return plan,case,arm,raw,{name:'a'*64 for name in ['keys.log','state.log','messages.log']}


class PairedTest(unittest.TestCase):
    def test_definition_is_generated_and_hash_pinned(self):
        _,problems,changes=define.plan(ROOT/'definitions/balanced999-paired-execution.yaml')
        self.assertEqual(problems,[]);self.assertEqual(changes,[])

    def test_real_requested_bundle_requires_effective_parameters_and_loaded_plan(self):
        plan,case,arm,raw,streams=setup()
        self.assertEqual(p.validate(plan,case,arm,raw,streams),'survived_horizon')
        for fault in ['parameter','plan','classic','state','binary','horizon']:
            damaged=copy.deepcopy(raw)
            if fault=='parameter':damaged['run/params-core.json']='[]'
            elif fault=='plan':damaged['run/errands_plan.txt']='different plan'
            elif fault=='classic':damaged['run/user/borg.txt']=damaged['run/user/borg.txt'].replace('borg_town_plan = 1','borg_town_plan = 0')
            elif fault=='state':damaged['initial-state']='101 0,0 d1/1 hp1/8 sp0/2\n'
            elif fault=='binary':damaged['run/process.json']=damaged['run/process.json'].replace('c'*64,'d'*64)
            else:
                trial=json.loads(damaged['trial.json']);trial['summary']['game_turns']=2102;damaged['run/summary.json']=json.dumps(trial['summary']);damaged['trial.json']=json.dumps(trial)
            with self.subTest(fault=fault),self.assertRaises(ValueError):p.validate(plan,case,arm,damaged,streams)

    def test_partial_smoke_is_collected_with_all36_expected_cells(self):
        plan,case,arm,raw,streams=setup()
        cell=dict(schema='borg-zoo/paired-incident-cell@1',id=case['id'],arm='speed30',plan_hash=plan['plan_hash'],status='survived_horizon',receipts=raw,
                  receipts_sha256={k:hashlib.sha256(v.encode()).hexdigest() for k,v in raw.items()},streams=streams)
        cell['execution_hash']=n.digest(cell)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);n.write(root/'plan.json',plan);n.write(root/'input/speed.json',cell)
            self.assertEqual(p.collect(root/'plan.json',root/'input',root/'report'),1)
            r=n.read(root/'report/comparison.json');self.assertEqual(r['expected_cells'],36);self.assertEqual(r['invalid_count'],35)
            self.assertEqual(sum(c['status']=='survived_horizon' for c in r['cells']),1)
            n.write(root/'input/duplicate.json',cell)
            with self.assertRaisesRegex(ValueError,'repeated'):p.collect(root/'plan.json',root/'input',root/'duplicate-report')
