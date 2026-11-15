import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from zoo import borgrs, catalogue, site, town_shadow


class ShadowTest(unittest.TestCase):
    def row(self, effective):
        return {'v': 5, 'mode': 0, 'params': [int(effective[k]) for k in town_shadow.PARAMETERS],
                'limits': [100, 10, 10, 1000], 'plan': [[0, 2, 0, 3, 40, 1, 1]],
                'kit': [[1, 1, 1, 1, 1, 0, 0, 0, 20, 1, 0, 0]],
                'dispose': [2], 'wares': [[1, 0, 1, 2, 1, 1, 1, 1, 1]]}

    def effective(self):
        return dict.fromkeys(town_shadow.PARAMETERS, 0)

    def test_valid_empty_missing_and_corrupt_streams_are_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'plan.jsonl'
            eff = self.effective()
            self.assertEqual(town_shadow.collect(path, eff)['status'], 'config_error')
            path.touch()
            self.assertEqual(town_shadow.collect(path, eff)['status'], 'not_observed')
            path.write_text(json.dumps(self.row(eff)) + '\n')
            good = town_shadow.collect(path, eff)
            self.assertEqual(good['status'], 'verified')
            self.assertEqual((good['median_planned_spending'], good['median_retained_gold']), (40, 80))
            self.assertEqual(good['snapshot_home_dispositions'], {'home_sell': 1})
            self.assertEqual(good['planned_supply_copies_by_stack_class'], {'2': 3})
            self.assertEqual(len(good['sha256']), 64)
            for mutation in ('vector', 'version', 'live', 'missing', 'overspend', 'json', 'length'):
                row = self.row(eff)
                if mutation == 'vector': row['params'][4] = 99
                if mutation == 'version': row['v'] = 4
                if mutation == 'live': row['mode'] = 1
                if mutation == 'missing': del row['params']
                if mutation == 'overspend': row['plan'][0][4] = 121
                if mutation == 'length': row['params'].pop()
                path.write_text('{' if mutation == 'json' else json.dumps(row))
                self.assertEqual(town_shadow.collect(path, eff)['status'], 'config_error', mutation)
            path.write_text(json.dumps(self.row(eff)))
            eff.pop(town_shadow.PARAMETERS[-1])
            self.assertEqual(town_shadow.collect(path, eff)['status'], 'config_error')

    def test_native_adapter_uses_unique_streams_checks_vectors_and_preserves_outcomes(self):
        cat = catalogue.catalogue()
        exp = catalogue.experiment('smoke/town-class-shadow-smoke.json', cat)
        cells = catalogue.cells(exp, cat)
        spec = cat['specimens']['specimens'][cells[0]['specimen']]
        paths = []
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'build.json').write_text(json.dumps({'source_commit': spec['ref'], 'impl': 'rust'}))
            (root / 'borg.txt').write_text('borg_cheat_death = FALSE\n')
            for i, cell in enumerate(cells[:3]):
                _, profile = catalogue.resolve_profile(cat, cell)
                eff = {**self.effective(), **profile['settings']}
                def run(argv, **kwargs):
                    record_path = Path(kwargs['env']['BORG_TOWN_PLAN_RECORD'])
                    self.assertNotEqual(str(record_path), '/global/path')
                    paths.append(record_path)
                    row = self.row(eff)
                    if i == 1: row['params'][0] = 1
                    record_path.write_text(json.dumps(row) + '\n')
                    out = record_path.parent
                    (out / 'keys.log').write_text('same game')
                    (out / 'summary.json').write_text(json.dumps({'race': 'Human', 'class': cell['class'],
                        'dead': True, 'stop_reason': 'death', 'effective_settings': eff if i < 2 else 42}))
                    return type('Result', (), {'returncode': 0})()
                with patch('zoo.borgrs.subprocess.run', side_effect=run), patch.dict('os.environ', {
                        'BORG_TOWN_PLAN_RECORD': '/global/path'}):
                    record = borgrs.run_cell(cell, root, root / 'work', cat)
                self.assertEqual(record['outcome'], 'death' if i == 0 else 'config_error')
                self.assertEqual(record['observed_outcome'], 'death')
                self.assertEqual(record['profile_applied'], catalogue.resolve_profile(cat, cell)[0])
                self.assertTrue((paths[-1].parent / 'keys.log').exists())
            self.assertNotEqual(paths[0], paths[1])

    def test_all_classes_select_correct_profiles_and_unretained_or_live_plans_fail(self):
        cat = catalogue.catalogue()
        exp = catalogue.experiment('smoke/town-class-shadow-smoke.json', cat)
        cells = catalogue.cells(exp, cat)
        self.assertEqual(len(cells), 36)
        self.assertEqual({c['class'] for c in cells}, set(catalogue.CLASSES))
        for cell in cells:
            applied, profile = catalogue.resolve_profile(cat, cell)
            if 'probe-by-class' in cell['profile']:
                cls = cell['class']
                for key, value in {'Mage': ('borg_town_w_gold', 50),
                                   'Ranger': ('borg_town_home_discount', 750),
                                   'Blackguard': ('borg_town_risk', 1500)}.items():
                    if cls == key: self.assertEqual(profile['settings'][value[0]], value[1])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'bad.json'
            path.write_text(json.dumps({**exp, 'retain_evidence': False}))
            with self.assertRaisesRegex(ValueError, 'retain_evidence'):
                catalogue.experiment(path, cat)
            bad = copy.deepcopy(cat)
            name = 'rs-town-reference-normal'
            bad['profiles'][name]['settings']['borg_town_plan'] = 1
            path.write_text(json.dumps(exp))
            with self.assertRaisesRegex(ValueError, 'planner off'):
                catalogue.experiment(path, bad)

    def test_report_keeps_failed_attempts_and_all_nine_classes(self):
        cat = catalogue.catalogue()
        exp = catalogue.experiment('smoke/town-class-shadow-smoke.json', cat)
        cells = catalogue.cells(exp, cat)
        record = {**cells[0], 'outcome': 'wall_timeout'}
        meta = {'experiment': exp, 'catalogue': {**cat, 'specimens': cat['specimens']['specimens']}}
        html = site.town_shadow_table(meta, [record])
        for cls in catalogue.CLASSES: self.assertIn(cls, html)
        self.assertIn('wall_timeout', html)
        self.assertIn('not executed purchases', html)
        self.assertIn('unavailable', html)
