"""borg-zoo#539: the resolved-settings receipt is retained, validated and projected for the played class."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from zoo import settings_receipt as sr


def write(tmp, obj, raw=None):
    path = Path(tmp) / sr.FILE
    path.write_bytes(raw if raw is not None else json.dumps(obj).encode())
    return path


def good(cls=7, name='ranger', settings=None):
    return {'schema': sr.SCHEMA, 'class_index': cls, 'class_name': name,
            'effective_settings': {'town_phase_reserve': 2} if settings is None else settings}


class SettingsReceiptTest(unittest.TestCase):
    def test_absent_receipt_stays_null(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(sr.collect(tmp, 'Ranger', {}))

    def test_bytes_and_hash_are_kept_exactly(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw = b'{"schema": "borg-settings-resolved@1",\n "class_index": 7, "class_name": "ranger", "effective_settings": {"town_phase_reserve": 2}}\n'
            write(tmp, None, raw)
            rec = sr.collect(tmp, 'Ranger', {})
            self.assertEqual(rec['status'], 'ok')
            self.assertEqual(rec['raw'].encode(), raw)
            self.assertEqual(rec['sha256'], hashlib.sha256(raw).hexdigest())
            self.assertEqual((rec['schema'], rec['class_index'], rec['class_name']), (sr.SCHEMA, 7, 'ranger'))
            self.assertEqual(rec['effective_settings'], {'town_phase_reserve': 2})

    def test_empty_map_is_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, good(settings={}))
            rec = sr.collect(tmp, 'Ranger', {'borg_param_town_phase_reserve__ranger': 0})
            self.assertEqual(rec['status'], 'ok')
            self.assertEqual(rec['effective_settings'], {})
            self.assertIn('omitted', rec['projection']['borg_param_town_phase_reserve__ranger']['verdict'])

    def test_class_override_projects_to_the_canonical_key_for_the_played_class(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, good())
            prof = {'borg_param_town_phase_reserve__ranger': 2, 'borg_param_town_phase_reserve__mage': 5,
                    'borg_param_town_phase_reserve@ranger': 3, 'borg_reborn_core': 'borg-rs'}
            proj = sr.collect(tmp, 'Ranger', prof)['projection']
            self.assertEqual(proj['borg_param_town_phase_reserve__ranger']['verdict'], 'match')
            self.assertEqual(proj['borg_param_town_phase_reserve__ranger']['canonical'], 'town_phase_reserve')
            self.assertEqual(proj['borg_param_town_phase_reserve__mage']['verdict'], 'not applicable to the played class')
            self.assertEqual(proj['borg_param_town_phase_reserve@ranger']['verdict'], 'differs')
            self.assertNotIn('borg_reborn_core', proj)

    def test_legacy_attack_preference_alias_maps_to_the_family_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, good(settings={'attack_preference_spell_permille': 1600}))
            proj = sr.collect(tmp, 'Ranger', {'borg_param_attack_preference_ranger_spell_permille': 1600,
                                              'borg_param_attack_preference_mage_spell_permille': 1600})['projection']
            self.assertEqual(proj['borg_param_attack_preference_ranger_spell_permille']['canonical'],
                             'attack_preference_spell_permille')
            self.assertEqual(proj['borg_param_attack_preference_ranger_spell_permille']['verdict'], 'match')
            self.assertEqual(proj['borg_param_attack_preference_mage_spell_permille']['verdict'],
                             'not applicable to the played class')

    def test_omitted_value_is_not_asserted(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, good(settings={}))
            verdict = sr.collect(tmp, 'Ranger', {'borg_param_flow_leash_per_level': 3})['projection']
            self.assertTrue(verdict['borg_param_flow_leash_per_level']['verdict'].startswith('omitted'))
            self.assertIsNone(verdict['borg_param_flow_leash_per_level']['receipt'])

    def test_malformed_receipts_get_their_own_status(self):
        cases = {
            'not json': b'{nope',
            'not an object': b'[]',
            'schema': json.dumps(dict(good(), schema='borg-settings-resolved@2')).encode(),
            'class index': json.dumps(dict(good(), class_index=9)).encode(),
            'class name': json.dumps(dict(good(), class_name='mage')).encode(),
            'float value': json.dumps(good(settings={'a': 1.5})).encode(),
            'bool value': json.dumps(good(settings={'a': True})).encode(),
            'not a map': json.dumps(dict(good(), effective_settings=[1])).encode(),
            'played class differs': json.dumps(good()).encode(),
        }
        for label, raw in cases.items():
            with self.subTest(label), tempfile.TemporaryDirectory() as tmp:
                write(tmp, None, raw)
                rec = sr.collect(tmp, 'Mage' if label == 'played class differs' else 'Ranger', {})
                self.assertEqual(rec['status'], 'malformed')
                self.assertTrue(rec['error'])
                self.assertEqual(rec['sha256'], hashlib.sha256(raw).hexdigest())

    def test_cell_record_carries_the_receipt_through_the_adapter(self):
        # The adapter contract: a cell that writes the receipt keeps it, one that does not has None.
        from unittest.mock import patch
        from zoo import borgrs, catalogue
        cat = catalogue.catalogue()
        cell = catalogue.cells(catalogue.experiment('experiments/rs-joint-m12-development.json'), cat)[0]
        spec = cat['specimens']['specimens'][cell['specimen']]
        for with_receipt in (True, False):
            with self.subTest(with_receipt=with_receipt), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / 'build.json').write_text(json.dumps({'source_commit': spec['ref'], 'impl': spec['impl']}))
                (root / 'borg.txt').write_text('borg_cheat_death = FALSE\n')

                def run(argv, **kwargs):
                    out = Path(argv[argv.index('-keylog') + 1]).parent
                    for name in ('keys.log', 'state.log', 'messages.log'):
                        (out / name).write_text('x\n')
                    settings = catalogue.resolve_profile(cat, cell)[1]['settings']
                    (out / 'summary.json').write_text(json.dumps({'race': 'Human', 'class': 'Warrior',
                        'stop_reason': 'turns', 'effective_settings': settings}))
                    if with_receipt:
                        (out / sr.FILE).write_text(json.dumps(good(0, 'warrior', {})))
                    return type('Result', (), {'returncode': 0})()
                with patch('zoo.borgrs.subprocess.run', side_effect=run):
                    record = borgrs.run_cell(cell, root, root / 'work', cat, keep=True)
                if with_receipt:
                    self.assertEqual(record['settings_resolved']['status'], 'ok')
                    self.assertEqual(record['settings_resolved']['class_name'], 'warrior')
                    self.assertEqual(record['outcome'], 'turn_cap')
                else:
                    self.assertIsNone(record['settings_resolved'])


if __name__ == '__main__':
    unittest.main()
