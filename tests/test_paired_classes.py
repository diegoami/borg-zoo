import unittest
from zoo import catalogue, stats


def cell(profile, seed, outcome, cls='Rogue', kind='borg-rs'):
    return {'suite': 's', 'specimen': 'one', 'profile': profile, 'seed': seed,
            'cap': 100, 'outcome': outcome, 'played_class': cls, 'harness_kind': kind,
            'final': {'turn': 10, 'max_depth': 1, 'max_level': 1},
            'first_turn_at_depth': {}, 'play_sha256': f'{profile}-{seed}'}


class PairedClassTest(unittest.TestCase):
    def setUp(self):
        self.exp = {'specimens': ['one'], 'profiles': ['control', 'arm'], 'control': 'one',
                    'control_profile': 'control', 'suites': ['s']}

    def test_class_pairs_exclude_failures_and_unmatched_characters(self):
        cells = [cell('control', 1, 'death'), cell('arm', 1, 'turn_cap'),
                 cell('control', 2, 'turn_cap'), cell('arm', 2, 'death'),
                 cell('control', 3, 'death'), cell('arm', 3, 'wall_timeout'),
                 cell('control', 4, 'death', 'Mage'), cell('arm', 4, 'turn_cap'),
                 cell('control', 5, 'death', 'Mage'), cell('arm', 5, 'death', 'Mage')]
        rows = stats.paired_by_class(self.exp, cells)['s']
        rogue = next(r for r in rows if r['class'] == 'Rogue')
        self.assertEqual((rogue['paired']['pairs'], rogue['paired']['rescued'],
                          rogue['paired']['newly_killed'], rogue['unfinished']), (2, 1, 1, 1))
        mage = next(r for r in rows if r['class'] == 'Mage')
        self.assertEqual((mage['paired']['pairs'], mage['paired']['both_died']), (1, 1))

    def test_harness_mismatch_is_not_a_pair(self):
        cells = [cell('control', 1, 'death'), cell('arm', 1, 'turn_cap', kind='mandos')]
        self.assertEqual(stats.paired_by_class(self.exp, cells)['s'][0]['paired']['pairs'], 0)

    def test_mode_cutoff_exclusion_survives_class_filter(self):
        exp = {**self.exp, 'specimens': ['4.2.6-bbc-m7', '4.2.6-bbc-m8'],
               'control': '4.2.6-bbc-m7', 'profiles': ['default'], 'control_profile': 'default'}
        cells = [{**cell('default', 1, 'death'), 'specimen': s} for s in exp['specimens']]
        self.assertEqual(stats.paired_by_class(exp, cells, catalogue.catalogue()['specimens']['specimens'])['s'], [])
