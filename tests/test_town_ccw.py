import json
from pathlib import Path
import tempfile
import unittest

from zoo import town, town_ccw


class TownCcwCensusTest(unittest.TestCase):
    def test_unseen_purchase_after_gate_opens_with_verified_departure(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            base = {
                'v': 20, 'mode': 1, 'visit': 7, 'step': 0, 'gturn': 10, 'gold': 650,
                'kit': [[0, 0, 185, 6]], 'traits': [], 'limits': [650, 8, 24, 300],
                'shops': [[4, [[2, 26, 10, 3, 200, 1]]]], 'available': [[4, 2, 3]],
                'wares': [[4, 2, 233, 1, 1, 4, -1, 0, 0]], 'urgent': [],
                'paction': 1, 'act': [4, 13, 2, 125],
            }
            staples = [[0, 1, -20_000_000, 20_000_000, 0], [1, 1, -150_000, 150_000, 0],
                       [4, 1, 0, 6000, 0], [61, 1, -6000, 6000, 0]]
            opened = {**base, 'step': 1, 'gturn': 11, 'gold': 400, 'limits': [400, 7, 24, 300],
                      'kit': base['kit'] + [[0, 1, 208, 2]], 'traits': [[38, 2]],
                      'act': [4, 2, 1, 200], 'capability_curves': staples + [[82, 1000, -2000, 0, 0]]}
            last = {**opened, 'step': 2, 'gturn': 12, 'gold': 200, 'paction': 7,
                    'kit': opened['kit'] + [[0, 2, 233, 1]]}
            plans = [{**base, 'capability_curves': staples + [[82, 0, 1000, 0, 0]]}, opened, last]
            (directory / 'town-plan.jsonl').write_text(''.join(json.dumps(p) + '\n' for p in plans))
            (directory / 'settings-resolved.json').write_text(json.dumps({'effective_settings': town_ccw.SETTINGS}))
            descent = {'game_turn': 13, 'depth': 1, 'equipped': None, 'radius': 2, 'unlight': True}
            (directory / 'town-departure-fuel.jsonl').write_text(json.dumps(descent) + '\n')
            states = ('10 1,1 d0/2 hp10/10 sp0/0 f0 au650 xp0 lv1 pabc eabc\n'
                      '10 1,1 d0/2 hp10/10 sp0/0 f0 au400 xp0 lv1 pdef eabc\n'
                      '11 1,1 d0/2 hp10/10 sp0/0 f0 au400 xp0 lv1 pdef eabc\n'
                      '11 1,1 d0/2 hp10/10 sp0/0 f0 au200 xp0 lv1 p321 eabc\n'
                      '12 1,1 d0/2 hp10/10 sp0/0 f0 au200 xp0 lv1 p321 eabc\n'
                      '13 1,1 d1/2 hp10/10 sp0/0 f0 au200 xp0 lv1 p321 eabc\n')
            (directory / 'state.log').write_text(states)
            (directory / 'messages.log').write_text(
                '0 10 0 # Town plan executing action 1 at shop 4 slot 13\n'
                '1 10 0 You bought 2 Scrolls of Word of Recall for 250 gold.\n'
                '2 11 0 # Buying 2 x Scrolls of Word of Recall.\n'
                '2 11 0 # Town plan executing action 1 at shop 4 slot 2\n'
                '3 11 0 You bought a Chartreuse Potion for 200 gold.\n'
                '4 12 0 # Buying Potions of Cure Critical Wounds {unseen}.\n')
            town.collect(directory)
            census = town_ccw.collect(directory, town_ccw.SOURCE)
            self.assertEqual(census['status'], 'ok', census)
            row, = census['visits']
            self.assertEqual(row['first_recall_gated']['turn'], 10)
            self.assertEqual(row['first_gate_open']['turn'], 11)
            self.assertEqual([event['kind'] for event in row['purchases']], ['recall', 'ccw'])
            self.assertTrue(row['purchases'][1]['unseen'])
            self.assertTrue(row['bought_ccw'])
            self.assertEqual(row['departure_pack']['ccw'], 1)
            self.assertEqual(row['departure_pack']['recall'], 2)
            self.assertEqual(row['departure_pack']['phase_door'], 6)

            record = {'specimen': 'build', 'seed': 12, 'profile': 'ship', 'suite': 'pilot',
                      'outcome': 'turn_cap', 'ccw_census': census}
            missing_record = {k: v for k, v in record.items() if k != 'ccw_census'}
            missing_record.update(seed=13, outcome='harness_failure')
            town_ccw.publish(directory, [record, missing_record])
            summary = json.loads((directory / 'ccw-census.json').read_text())
            self.assertEqual(summary['max_dl_at_least_2']['gate_open'], {'visits': 1, 'starts': 1})
            self.assertEqual(summary['cells'][1]['status'], 'unavailable')

            (directory / 'state.log').write_text(states.replace('d1/2 hp10/10 sp0/0 f0 au200 xp0 lv1 p321',
                                                                 'd1/2 hp10/10 sp0/0 f0 au200 xp0 lv1 p999'))
            changed, = town_ccw.collect(directory, town_ccw.SOURCE)['visits']
            self.assertIsNone(changed['departure_pack'])
            self.assertEqual(changed['last_town_pack']['ccw'], 1)

    def test_measurement_errors_do_not_count_as_zero_opportunities(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = town_ccw.collect(tmp, town_ccw.SOURCE)
            self.assertEqual(result['status'], 'unavailable')
            self.assertIn('town-plan.jsonl', result['missing'])
