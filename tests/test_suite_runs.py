"""One build on a frozen saved suite: definitions, stages and the dashboard record."""
from collections import Counter
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from zoo import incident_bank as bank, saved_incidents as saved, suite_runs as sr
from tests.test_saved_incidents import fixture

ROOT=Path(__file__).resolve().parents[1]
DEFINITION=ROOT/'definitions/suite1-reborn-main-4d83dd26-stock.yaml'


def suite_record():
    """A suite-run dashboard record: the legacy fixture's two arms as references, plus one run."""
    r=fixture();r['expected_cells']=18;r['collected_cells']=18
    run='suite1-test';ids=['baseline','speed30']
    for c in r['cases']:
        c['outcomes'][run]='survived_horizon' if c['class_idx']%2 else 'death'
        c['pair_by_reference']={a:saved.pairing(c['outcomes'][a],c['outcomes'][run]) for a in ids};c['pair']=c['pair_by_reference']['baseline']
    r['arms'].append(dict(id=run,source=dict(repository='diegoami/borg-reborn-rs',commit='c'*40),core='borg-rs',build=dict(binary_sha256='0'*64),
                          settings={},errands_plan_sha256=None,inputs=dict(path='scenario-inputs/'+run,files={})))
    r.update(title=run+' on Suite 1',suite=dict(id='suite1-v1',name='Suite 1'),comparison=dict(reference='baseline',candidate=run),counted_arms=[run],
             pairs=dict(Counter(c['pair'] for c in r['cases'])),pairs_by_reference={a:dict(Counter(c['pair_by_reference'][a] for c in r['cases'])) for a in ids})
    return r


class SuiteTest(unittest.TestCase):
    def test_suite1_manifest_pins_its_plan_and_gear_for_every_case(self):
        m=sr.suite(ROOT,'suite1-v1')
        cases=bank.read_execution_plan(ROOT/m['cases_plan']['path'])['cases']
        gear=json.loads((ROOT/m['gear']['path']).read_text())['cases']
        self.assertEqual([c['id'] for c in cases],list(gear))
        self.assertEqual(Counter(c['scenario']['class_idx'] for c in cases),Counter({i:111 for i in range(9)}))
        self.assertTrue(all(len(v)==3 and all(len(h)==16 for h in v) for v in gear.values()))

    def test_definition_generates_and_rejects_drift(self):
        import yaml
        d=yaml.safe_load(DEFINITION.read_text())
        _,problems,changes=sr.definition_plan(d,DEFINITION,ROOT)
        self.assertEqual((problems,changes),([],[]))  # the committed JSON is current
        for fault in ['settings','source','file','question']:
            bad=copy.deepcopy(d)
            if fault=='settings':bad['settings']={'profile':'reborn-bundle-none-speed30'}
            elif fault=='source':bad['source']['commit']='f'*40
            elif fault=='file':bad['inputs']['files']['borg.txt']='0'*64
            else:bad['question']=' '
            with self.subTest(fault=fault),self.assertRaises((ValueError,KeyError)):sr.definition_plan(bad,DEFINITION,ROOT)

    def test_settings_parse_ignores_comments(self):
        text='# borg_x = 1\nborg_a = 5   # note\n borg_b=TRUE\nother = 1\n'
        self.assertEqual(sr.settings_of(text),{'borg_a':'5','borg_b':'TRUE'})


class SuiteRecordTest(unittest.TestCase):
    def test_suite_record_validates_and_renders_every_arm(self):
        r=suite_record();saved.validate(r)
        page=saved.render(r)
        for text in ['suite1-test on Suite 1','against baseline','against speed30','suite1-test deaths']:self.assertIn(text,page)
        case=saved.case_page(r,r['cases'][0])
        self.assertIn('scenario-inputs/suite1-test/borg.txt',case)

    def test_only_the_run_counts_toward_invalid_and_totals_must_match(self):
        r=suite_record();r['cases'][0]['outcomes']['speed30']='missing';r['cases'][0]['pair_by_reference']['speed30']='invalid'
        r['pairs_by_reference']['speed30']=dict(Counter(c['pair_by_reference']['speed30'] for c in r['cases']))
        saved.validate(r)  # a reference's gap does not count against this run
        for fault in ['by_reference','cells','arm']:
            bad=suite_record()
            if fault=='by_reference':bad['pairs_by_reference']['speed30']={'both_died':18}
            elif fault=='cells':bad['expected_cells']=36
            else:bad['comparison']['candidate']='nobody'
            with self.subTest(fault=fault),self.assertRaises((ValueError,KeyError)):saved.validate(bad)

    def test_legacy_record_still_needs_its_two_arms(self):
        r=fixture();saved.validate(r)
        r['arms'][1]['id']='other'
        with self.assertRaises((ValueError,KeyError)):saved.validate(r)


if __name__=='__main__':unittest.main()
