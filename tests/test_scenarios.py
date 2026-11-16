"""Synthetic impact pairing is distinct from Cemetery's parity verifier."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

from zoo import scenarios as s


def plan_fixture(count=1):
    cases = []
    for depth in range(1, count + 1):
        c = dict(schema='borg-cemetery/synthetic-scenario@1', suite_id='test', revision=1,
                 seed=202, depth=depth, turn_cap=3000, wall_seconds=30,
                 candidate_screen=dict(kind='low_hp_candidate', hp_threshold=2),
                 character_build=dict(id='mage', class_idx=1, race_idx=4, core='reborn',
                                      start='birth', profile='profile.txt', profile_sha256=s.digest('profile')),
                 expected_start=dict(level=1), harness_contract='borg-reborn-rs/synthetic-start@2')
        h = s.digest(c)
        cases.append(dict(c, id='test-' + h[:24], spec_sha256=h))
    targets = [dict(pushid=name, specimen='spec-' + name, repository=s.REPO, commit=sha * 40,
                    harness=dict(repository=s.REPO, commit=sha * 40)) for name, sha in [('old', 'a'), ('new', 'b')]]
    p = dict(schema='borg-zoo/scenario-plan@1', name='smoke', targets=targets, cases=cases,
             definition=dict(bank=dict(repository=s.BANK_REPO, commit='c'*40, manifest='synthetic/test/suite.json')),
             semantics=dict(engine_sha256='e'*64, dungeon_mode='one_way', boundary='after-key', calendar='UTC-real-clock-same-execution'))
    p['plan_sha256'] = s.digest(p)
    return p


def row_fixture(plan, case, target, status):
    receipt = dict(repository=s.REPO, commit=target['commit'], engine_sha256='e'*64,
                   build=dict(git_rev=target['commit'], git_dirty='no', inputs_dirty='no',
                              source_sha256='f'*64, binary_sha256=target['commit'][0]*64))
    inputs = s.execution_input(plan, case, target, receipt, '2026-11-16')
    row = dict(schema='borg-zoo/scenario-cell@1', plan_sha256=plan['plan_sha256'], pushid=target['pushid'],
                scenario_id=case['id'], pairing_sha256=s.pairing_hash(plan, case),
                execution_input=inputs, execution_sha256=s.digest(inputs), status=status, attempted=True,
                evidence={name: dict(sha256='1'*64) for name in ('summary.json', 'process.json', 'config.txt', 'keys.log', 'state.log', 'messages.log')})
    row['receipts'] = {name: json.dumps(dict(fake_adapter=True, scenario=case['id'], binary=receipt['build']['binary_sha256'])) + '\n'
                       for name in ('summary.json', 'process.json', 'config.txt')}
    for name,text in row['receipts'].items():
        row['evidence'][name]['sha256'] = hashlib.sha256(text.encode()).hexdigest()
    return row


class ScenarioTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.plan = plan_fixture()

    def tearDown(self):
        self.tmp.cleanup()

    def cells(self, statuses):
        for t, status in zip(self.plan['targets'], statuses):
            if status is not None:
                s.write(self.root / 'input' / t['pushid'] / 'cells' / 'one.json', row_fixture(self.plan, self.plan['cases'][0], t, status))

    def test_intentional_build_change_and_rescue_are_not_parity_failures(self):
        self.cells(['death', 'survived_to_cap'])
        report = s.collect(self.plan, self.root/'input', self.root/'out')
        self.assertEqual(report['counts'], {'rescued': 1})
        a, b = report['cells']
        self.assertEqual(a['pairing_sha256'], b['pairing_sha256'])
        self.assertNotEqual(a['execution_sha256'], b['execution_sha256'])
        self.assertFalse(report['population_eligible'])
        self.assertIn('Pinned Cemetery', (self.root/'out/index.html').read_text())

    def test_all_outcomes_and_invalid_categories(self):
        a = row_fixture(self.plan, self.plan['cases'][0], self.plan['targets'][0], 'death')
        b = row_fixture(self.plan, self.plan['cases'][0], self.plan['targets'][1], 'death')
        for left, right, wanted in [('death','death','both_died'), ('survived_to_cap','survived_to_cap','both_survived'),
                                    ('survived_to_cap','death','newly_killed'), ('stopped','survived_to_cap','inconclusive'),
                                    ('death','stopped','inconclusive'), ('missing','death','missing')]:
            self.assertEqual(s.compare_pair(dict(a,status=left),dict(b,status=right)),wanted)
        for invalid in s.INVALID:
            self.assertEqual(s.compare_pair(a,dict(b,status=invalid)), 'invalid')

    def test_missing_jobs_keep_full_denominators(self):
        self.cells(['death', None])
        r=s.collect(self.plan,self.root/'input',self.root/'out')
        self.assertEqual((r['expected_cells'],r['collected_cells']),(2,1))
        self.assertEqual(r['counts'],{'missing':1})
        self.assertEqual(r['aggregates'][0]['expected_pairs'],1)

    def test_unstarted_entire_grid_is_missing(self):
        r=s.collect(self.plan,self.root/'absent',self.root/'out')
        self.assertEqual(r['counts'], {'missing':1})

    def test_changed_kit_depth_profile_seed_and_contract_reject_pair(self):
        for field in ('seed','depth','profile','kit','contract','binary','engine','calendar'):
            with self.subTest(field=field):
                row=row_fixture(self.plan,self.plan['cases'][0],self.plan['targets'][0],'death')
                inputs=row['execution_input']
                if field in ('seed','depth'):inputs['scenario'][field]+=1
                elif field=='profile':inputs['scenario']['character_build']['profile_sha256']='0'*64
                elif field=='kit':inputs['scenario']['character_build']['start']='record'
                elif field=='contract':inputs['scenario']['harness_contract']='other'
                elif field=='binary':inputs['build_receipt']['build']['binary_sha256']='not-a-hash'
                elif field=='engine':inputs['build_receipt']['engine_sha256']='0'*64
                else:inputs['calendar']='unknown'
                row['execution_sha256']=s.digest(inputs)
                # Mutating a cell must not mutate the frozen expected plan.
                expected=plan_fixture()
                with self.assertRaises(ValueError):s.validate_cell(expected,expected['cases'][0],expected['targets'][0],row)
                self.plan=plan_fixture()

    def test_corrupt_cells_become_invalid_without_erasing_other_cells(self):
        self.cells(['death','survived_to_cap'])
        p=self.root/'input/old/cells/one.json';r=json.loads(p.read_text());r['execution_input']='bad';p.write_text(json.dumps(r))
        out=s.collect(self.plan,self.root/'input',self.root/'out')
        self.assertEqual(out['counts'],{'invalid':1})
        self.assertEqual(len(out['cells']),2)

    def test_changed_receipt_bytes_cannot_qualify_a_rescue(self):
        self.cells(['death','survived_to_cap'])
        p=self.root/'input/new/cells/one.json';r=json.loads(p.read_text())
        r['receipts']['config.txt']+='changed profile\n';p.write_text(json.dumps(r))
        out=s.collect(self.plan,self.root/'input',self.root/'out')
        self.assertEqual(out['counts'],{'invalid':1})

    def test_duplicate_attempts_do_not_inflate_samples(self):
        self.cells(['death','death'])
        p=self.root/'input/old/cells/one.json'
        s.write(p.with_name('repeat.json'),json.loads(p.read_text()))
        with self.assertRaisesRegex(ValueError,'duplicate'):s.collect(self.plan,self.root/'input',self.root/'out')

    def test_cross_day_comparison_inconclusive(self):
        a=row_fixture(self.plan,self.plan['cases'][0],self.plan['targets'][0],'death')
        b=row_fixture(self.plan,self.plan['cases'][0],self.plan['targets'][1],'survived_to_cap')
        b['execution_input']['calendar']='2026-11-17'
        self.assertEqual(s.compare_pair(a,b),'inconclusive')

    def test_plan_and_json_identity_checks(self):
        self.plan['cases'][0]['depth']=99
        with self.assertRaisesRegex(ValueError,'plan hash'):s.validate_plan(self.plan)
        p=self.root/'duplicate.json';p.write_text('{"a":1,"a":2}')
        with self.assertRaises(ValueError):s.read(p)

    def test_synthetic_pages_stay_out_of_population_loader(self):
        from zoo import site
        self.cells(['death','survived_to_cap'])
        s.collect(self.plan,self.root/'input',self.root/'scenario-results/smoke/run1')
        self.assertEqual(site.load_runs(self.root/'results'), [])
        with patch.object(s.catalogue,'ROOT',self.root):
            s.build_site(self.root/'results',self.root/'site')
        self.assertIn('smoke/run1/index.html',(self.root/'site/scenarios/index.html').read_text())
        self.assertIn('rescued',(self.root/'site/scenarios/smoke/run1/index.html').read_text())

    def test_preparation_rejects_moving_refs_budget_and_bank_changes(self):
        d=json.loads((s.catalogue.ROOT/'scenario-experiments/cemetery-caster-smoke.json').read_text())
        specimen=dict(kind='borg-rs',impl='rust',repository=s.REPO,ref='a'*40)
        cat=dict(specimens=dict(specimens={e['specimen']:dict(specimen,ref=ch*40) for e,ch in zip(d['pushids'],'ab')}))
        generated=dict(cases=[dict(self.plan['cases'][0],id=d['scenario_ids'][0])],
                       manifest_sha256=d['bank']['manifest_sha256'],suite_spec_sha256=d['bank']['suite_spec_sha256'])
        module=types.SimpleNamespace(generate=lambda _:generated)
        path=self.root/'definition.json'
        with patch.object(s,'bank_module',return_value=module):
            path.write_text(json.dumps(d));s.prepare(path,self.root,cat)
            for bad in ('main','v1','abc123'):
                changed=copy.deepcopy(cat)
                changed['specimens']['specimens'][d['pushids'][0]['specimen']]['ref']=bad
                with self.assertRaisesRegex(ValueError,'moving ref'):s.prepare(path,self.root,changed)
            unknown=copy.deepcopy(d);unknown['scenario_ids']=['equipment-index-not-executable'];path.write_text(json.dumps(unknown))
            with self.assertRaisesRegex(ValueError,'unknown scenario'):s.prepare(path,self.root,cat)
            small=copy.deepcopy(d);small['budget']['max_wall_seconds']=1;path.write_text(json.dumps(small))
            with self.assertRaisesRegex(ValueError,'budget'):s.prepare(path,self.root,cat)
            path.write_text(json.dumps(d));generated['suite_spec_sha256']='0'*64
            with self.assertRaisesRegex(ValueError,'digest mismatch'):s.prepare(path,self.root,cat)

    def test_interruption_preserves_completed_cell_and_collects_missing(self):
        self.plan=plan_fixture(2)
        p=self.plan
        adapter=types.SimpleNamespace()
        adapter.describe=lambda *args: row_fixture(p,p['cases'][0],p['targets'][0],'death')['execution_input']['build_receipt']
        calls=[]
        def run(case,root,out):
            if calls:raise KeyboardInterrupt()
            calls.append(case['id']);out.mkdir();out.parent.joinpath('profile.txt').write_text('profile')
            return 0
        adapter.run=run
        class ExecutionError(Exception):pass
        module=types.SimpleNamespace(RebornAdapter=lambda source:adapter,ExecutionError=ExecutionError,
            generate=lambda path:dict(cases=p['cases'],root=self.root,manifest=dict(suite_id='test',revision=1)),
            classify=lambda *args:dict(status='death'),RESULT_SCHEMA='test',report=lambda doc:'report')
        for c in p['cases']:c['character_build']['profile_sha256']=s.file_hash(self._profile())
        # Rehash legitimate fixtures after configuring their immutable profile.
        for c in p['cases']:
            c['spec_sha256']=s.digest({k:v for k,v in c.items() if k not in ('id','spec_sha256')})
        p['plan_sha256']=s.digest({k:v for k,v in p.items() if k!='plan_sha256'})
        with patch.object(s,'bank_module',return_value=module),patch.object(s,'checked_checkout'),patch.object(s,'engine_hash',return_value='e'*64):
            with self.assertRaises(KeyboardInterrupt):s.run_target(p,self.root,self.root,'old',self.root/'interrupted')
        self.assertEqual(len(list((self.root/'interrupted/cells').glob('*.json'))),1)
        # The first fake row has intentionally incomplete evidence, so it is
        # invalid; the uncompleted scenario remains missing, never a death.
        r=s.collect(p,self.root,self.root/'collection')
        self.assertEqual(r['expected_cells'],4)
        self.assertEqual(r['collected_cells'],1)
        self.assertEqual(r['counts'],{'missing':2})

    def test_unsupported_capability_is_recorded_without_gameplay(self):
        class ExecutionError(Exception):
            status='unsupported'
        def unsupported(*args):
            raise ExecutionError('no generated-start capability')
        adapter=types.SimpleNamespace(describe=unsupported)
        module=types.SimpleNamespace(RebornAdapter=lambda source:adapter,ExecutionError=ExecutionError,
            generate=lambda path:dict(cases=self.plan['cases'],root=self.root,manifest=dict(suite_id='test',revision=1)),
            RESULT_SCHEMA='test',report=lambda doc:'unavailable')
        with patch.object(s,'bank_module',return_value=module),patch.object(s,'checked_checkout'):
            for target in self.plan['targets']:
                rows=s.run_target(self.plan,self.root,self.root,target['pushid'],self.root/target['pushid'])
                self.assertEqual(rows[0]['status'],'unsupported')
                self.assertFalse(rows[0]['attempted'])
        report=s.collect(self.plan,self.root,self.root/'report')
        self.assertEqual(report['counts'],{'invalid':1})
        self.assertEqual(report['collected_cells'],2)

    def _profile(self):
        p=self.root/'profile.txt';p.write_text('profile');return p


if __name__=='__main__':unittest.main()
