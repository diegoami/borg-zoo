"""zoo.history: the digest the next-experiments skill reads."""
import unittest

from zoo import history


def cell(profile, seed, outcome, level=3, depth=2):
    return {'suite': 's', 'specimen': 'sp', 'profile': profile, 'seed': seed, 'outcome': outcome,
            'final': {'max_level': level, 'max_depth': depth}}


class HistoryTest(unittest.TestCase):
    def test_arms_show_their_differences_and_pairing(self):
        meta = {'run_id': 'r1', 'completed': '2026-11-16 00:00 UTC',
                'experiment': {'name': 'x', 'question': 'Does flag help?', 'suites': ['s'], 'specimens': ['sp'],
                               'profiles': ['off', 'on'], 'control': 'sp', 'control_profile': 'off'},
                'catalogue': {'specimens': {'sp': {'repository': 'r', 'ref': 'abcdef12', 'kind': 'borg-rs'}},
                              'profiles': {'off': {'settings': {'core': 'borg-rs'}},
                                           'on': {'settings': {'core': 'borg-rs', 'flag': 1}}}}}
        cells = [cell('off', 1, 'death'), cell('off', 2, 'death'), cell('off', 3, 'turn_cap'),
                 cell('on', 1, 'turn_cap', level=5), cell('on', 2, 'death'), cell('on', 3, 'turn_cap')]
        [entry] = history.digest([(meta, cells, None)])
        control, arm = entry['arms']
        self.assertEqual(control['differs_from_control'], {})
        self.assertNotIn('vs_control', control)
        self.assertEqual(arm['differs_from_control'], {'flag': 1})
        self.assertEqual((arm['deaths'], arm['finished']), (1, 3))
        self.assertEqual(arm['vs_control']['rescued'], 1)
        self.assertEqual(arm['vs_control']['newly_killed'], 0)
        self.assertIn('flag=1', history.markdown([entry]))
        self.assertEqual(history.digest([(meta, cells, None)], match='nomatch'), [])
        self.assertEqual(history.digest([(meta, cells, None)], since='2026-11-17'), [])


if __name__ == '__main__':
    unittest.main()
