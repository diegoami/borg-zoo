import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from zoo import borgrs, catalogue, evidence, town


class TownEvidenceTest(unittest.TestCase):
    def test_receipts_not_plans_and_quantity_not_resulting_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / 'state.log').write_text('0 -\n1 x au100 lv1\n2 x au60 lv1\n')
            (out / 'messages.log').write_text(
                "1 1 0 # Entering a '4' shop\n"
                '1 1 0 # Buying 2 Potions of Cure Light Wounds.\n'
                '2 2 0 You bought 2 Potions of Cure Light Wounds for 40 gold.\n'
                '2 2 0 You have 7 Potions of Cure Light Wounds (a).\n'
                '2 2 0 # Buying a Scroll of Recall.\n')
            summary = town.collect(out)
            self.assertEqual(summary['purchases'], 1)
            self.assertEqual(summary['items'][0]['units'], 2)
            self.assertEqual(summary['gold_spent'], 40)
            self.assertEqual(summary['wallet_checks'], {'True': 1})

    def test_absent_state_and_wallet_mismatch_are_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / 'messages.log').write_text('1 1 0 You bought a Torch for 2 gold.\n')
            self.assertEqual(town.collect(out)['wallet_checks'], {'None': 1})
            (out / 'state.log').write_text('0 x au10\n1 x au9\n')
            (out / 'messages.log').write_text('0 0 0 # Buying a Torch.\n1 1 0 You bought a Torch for 2 gold.\n')
            self.assertEqual(town.collect(out)['wallet_checks'], {'False': 1})

    def test_capture_adds_messages_and_one_state_stream(self):
        argv = borgrs.command('/game', Path('/out'), {'seed': 1}, 0, 0,
                              {'cap': 20}, {'depth_stream': True}, keep=True)
        self.assertEqual(argv.count('-statelog'), 1)
        self.assertEqual(argv[argv.index('-msglog') + 1], '/out/messages.log')

    def test_retention_through_adapter_for_timeout_and_cap(self):
        cat = catalogue.catalogue()
        cell = catalogue.cells(catalogue.experiment('experiments/rs-joint-m12-development.json'), cat)[0]
        spec = cat['specimens']['specimens'][cell['specimen']]
        for timeout in (False, True):
            with self.subTest(timeout=timeout), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / 'build.json').write_text(json.dumps({'source_commit': spec['ref'], 'impl': spec['impl']}))
                (root / 'borg.txt').write_text('borg_cheat_death = FALSE\n')
                def run(argv, **kwargs):
                    self.assertNotIn('BORG_TOWN_PLAN_RECORD', kwargs['env'])  # control stays off
                    self.assertNotIn('BORG_TRIP_RECORD', kwargs['env'])
                    out = Path(argv[argv.index('-keylog') + 1]).parent
                    for name in ('keys.log', 'state.log', 'messages.log'):
                        (out / name).write_text('partial raw evidence\n')
                    if timeout:
                        raise borgrs.subprocess.TimeoutExpired(argv, 1)
                    settings = catalogue.resolve_profile(cat, cell)[1]['settings']
                    (out / 'summary.json').write_text(json.dumps({'race': 'Human', 'class': 'Warrior',
                        'stop_reason': 'turns', 'effective_settings': settings}))
                    return type('Result', (), {'returncode': 0})()
                with patch('zoo.borgrs.subprocess.run', side_effect=run), patch.dict('os.environ', {
                        'BORG_TOWN_PLAN_RECORD': '/global/bad', 'BORG_TRIP_RECORD': '/global/bad'}):
                    record = borgrs.run_cell(cell, root, root / 'work', cat, keep=True)
                    out = root / 'work' / catalogue.cell_key(cell)
                    self.assertTrue((out / 'keys.log').exists())
                    self.assertTrue((out / 'state.log').exists())
                    self.assertEqual(record['outcome'], 'wall_timeout' if timeout else 'turn_cap')
                    with self.assertRaisesRegex(ValueError, 'overwrite retained'):
                        borgrs.run_cell(cell, root, root / 'work', cat, keep=True)
                    evidence.attach(record, out)
                    if not timeout:
                        self.assertTrue(record['evidence']['complete'])

    def test_purchase_index_is_preserved_at_collection(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = {'suite': 's', 'specimen': 'b', 'profile': 'p', 'seed': 1,
                      'outcome': 'turn_cap', 'town_activity': {'items': [{
                          'shop_index': 4, 'item': 'a Potion', 'transactions': 1, 'units': 1, 'gold': 20}]}}
            evidence.write_indexes(tmp, [record])
            self.assertIn('a Potion', (Path(tmp) / 'town-purchases.csv').read_text())
