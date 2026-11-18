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


    def meta(self, name, suite, completed='2026-11-18 00:00 UTC'):
        return {'run_id': name, 'completed': completed,
                'experiment': {'name': name, 'question': 'q', 'suites': [suite], 'specimens': ['sp'],
                               'profiles': ['off', 'on'], 'control': 'sp', 'control_profile': 'off'},
                'catalogue': {'specimens': {'sp': {'repository': 'r', 'ref': 'abcdef12', 'kind': 'borg-rs'}},
                              'profiles': {'off': {'settings': {}}, 'on': {'settings': {'flag': 1}}}}}

    def tier(self, suite, seeds, dead_off, dead_on):
        return [dict(cell(p, s, 'death' if s in d else 'turn_cap'), suite=suite)
                for p, d in (('off', dead_off), ('on', dead_on)) for s in seeds]

    def test_pool_reads_the_tiers_of_one_study_as_one(self):
        small = (self.meta('x-small', 'small'), self.tier('small', [1, 2], {1}, set()), None)
        medium = (self.meta('x-medium', 'medium'), self.tier('medium', [3, 4], {3}, {4}), None)
        [entry] = history.digest([small, medium], pool=True)
        self.assertEqual(entry['experiment'], 'x-small + x-medium')
        self.assertEqual(entry['suites'], ['small', 'medium'])
        control, arm = entry['arms']
        self.assertEqual((control['deaths'], control['finished']), (2, 4))
        self.assertEqual((arm['vs_control']['rescued'], arm['vs_control']['newly_killed']), (2, 1))
        self.assertEqual(len(history.digest([small, medium])), 2)  # unpooled: one entry per run

    def test_pool_never_merges_runs_that_share_a_start(self):
        a = (self.meta('x', 'small'), self.tier('small', [1, 2], {1}, set()), None)
        repeat = (self.meta('x-repeat', 'small', '2026-11-18 01:00 UTC'), self.tier('small', [1, 2], set(), set()), None)
        self.assertEqual(len(history.digest([a, repeat], pool=True)), 2)

    def test_a_pilot_is_not_pooled_with_the_tiers(self):
        pilot = (self.meta('x-pilot', 'classes-18'), self.tier('classes-18', [9], {9}, set()), None)
        small = (self.meta('x-small', 'small'), self.tier('small', [1, 2], {1}, set()), None)
        names = sorted(e['experiment'] for e in history.digest([pilot, small], pool=True))
        self.assertEqual(names, ['x-pilot', 'x-small'])

    def test_pool_keeps_different_arm_sets_apart(self):
        a = (self.meta('x', 'small'), self.tier('small', [1], set(), set()), None)
        other = self.meta('y', 'medium')
        other['experiment']['profiles'] = ['off', 'other']
        b = (other, [dict(cell(p, 2, 'turn_cap'), suite='medium') for p in ('off', 'other')], None)
        self.assertEqual(len(history.digest([a, b], pool=True)), 2)


if __name__ == '__main__':
    unittest.main()
