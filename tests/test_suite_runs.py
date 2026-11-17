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
    """A suite-run dashboard record: one build, no other arm."""
    r=fixture();run='suite1-test';r['expected_cells']=18;r['collected_cells']=18
    for c in r['cases']:c['outcomes']={run:'survived_horizon' if c['class_idx']%2 else 'death'};c['pair']=None
    r['arms']=[dict(id=run,source=dict(repository='diegoami/borg-reborn-rs',commit='c'*40),core='borg-rs',build=dict(binary_sha256='0'*64),
                    settings={},errands_plan_sha256=None,inputs=dict(path='scenario-inputs/'+run,files={}))]
    r.update(title=run+' on Suite 1',suite=dict(id='suite1-v1',name='Suite 1'),comparison=dict(reference=None,candidate=run),counted_arms=[run],pairs={})
    return r


def archived_smoke_record():
    """The first archived suite run (44098246595) carried the old study's two arms as references."""
    r=fixture();run='suite1-test';r['expected_cells']=18;ids=['baseline','speed30']
    for c in r['cases']:
        c['outcomes'][run]='death';c['pair_by_reference']={a:saved.pairing(c['outcomes'][a],'death') for a in ids};c['pair']=c['pair_by_reference']['baseline']
    r['arms'].append(dict(id=run,source=dict(repository='diegoami/borg-reborn-rs',commit='c'*40),core='borg-rs',build=dict(binary_sha256='0'*64),settings={},inputs=dict(path='x',files={})))
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
    def test_suite_record_shows_only_its_own_build(self):
        r=suite_record();saved.validate(r);page=saved.render(r)
        self.assertIn('Deaths per build',page);self.assertIn('55.6%',page)
        self.assertNotIn('Paired outcomes',page);self.assertNotIn('baseline',page)
        case=saved.case_page(r,r['cases'][0])
        self.assertIn('scenario-inputs/suite1-test/borg.txt',case);self.assertNotIn('--core reborn',case)

    def test_archived_record_with_references_renders_as_its_own_build(self):
        r=archived_smoke_record();saved.validate(r);page=saved.render(r)
        self.assertNotIn('Paired outcomes',page);self.assertNotIn('<th>baseline</th>',page);self.assertIn('100.0%',page)

    def test_totals_and_arms_must_match(self):
        for fault in ['cells','arm','invalid']:
            bad=suite_record()
            if fault=='cells':bad['expected_cells']=36
            elif fault=='arm':bad['comparison']['candidate']='nobody'
            else:bad['cases'][0]['outcomes']['suite1-test']='missing'
            with self.subTest(fault=fault),self.assertRaises((ValueError,KeyError)):saved.validate(bad)

    def test_legacy_record_still_needs_its_two_arms(self):
        r=fixture();saved.validate(r)
        r['arms'][1]['id']='other'
        with self.assertRaises((ValueError,KeyError)):saved.validate(r)


if __name__=='__main__':unittest.main()
