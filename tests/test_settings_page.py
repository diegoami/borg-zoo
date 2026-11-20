import tempfile
import unittest
from pathlib import Path

from zoo import settings_page, site


def cell(profile, suite, seed, death):
    return {'specimen': 'spec', 'profile': profile, 'suite': suite, 'seed': seed,
            'outcome': 'death' if death else 'turn_cap', 'final': {}, 'play_sha256': f'{profile}{seed}'}


def run(name, suite, deaths_ctl, deaths_arm, n, completed):
    meta = {'experiment': {'name': name, 'specimens': ['spec'], 'profiles': ['p-ctl', 'p-arm'],
                           'control_profile': 'p-ctl', 'issue': 7},
            'catalogue': {'specimens': {'spec': {'ref': 'abcdef1234'}},
                          'profiles': {'p-ctl': {'settings': {'borg_param_x': 0, 'borg_same': 1}},
                                       'p-arm': {'settings': {'borg_param_x': 1, 'borg_same': 1}}}},
            'run_id': f'{name}-1', 'completed': completed}
    cells = ([cell('p-ctl', suite, s, s in deaths_ctl) for s in range(n)]
             + [cell('p-arm', suite, s, s in deaths_arm) for s in range(n)])
    return meta, cells, None


class SettingsPageTest(unittest.TestCase):
    def test_tiers_pool_into_one_study_and_only_varied_settings_count(self):
        runs = [run('t-pilot', 'classes-18', {1}, {2}, 18, '2026-01-01'),
                run('t-medium', 'classes-1800-medium', set(range(40)), set(), 270, '2026-01-02')]
        found = settings_page.collect(runs)
        self.assertEqual(list(found), ['borg_param_x'])
        [study] = found['borg_param_x']
        self.assertEqual(len(study['runs']), 2)
        pooled = study['pooled']
        self.assertEqual(pooled['n'], 288)
        arm = next(a for a in pooled['arms'] if a['profile'] == 'p-arm')
        self.assertEqual((arm['paired']['rescued'], arm['paired']['newly_killed']), (41, 1))
        self.assertEqual(pooled['verdict'], 'clear difference')
        self.assertEqual(study['runs'][1]['verdict'], 'too small to tell')

    def test_large_null_and_pages_written(self):
        runs = [run('n-full', 'classes-1800', {1, 2, 3}, {4, 5, 6}, 300, '2026-01-03')]
        found = settings_page.collect(runs)
        self.assertEqual(found['borg_param_x'][0]['runs'][0]['verdict'], 'no difference found')
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(settings_page.build(runs, Path(tmp), site.page), 1)
            index = (Path(tmp) / 'settings' / 'index.html').read_text()
            self.assertIn('borg_param_x.html', index)
            page = (Path(tmp) / 'settings' / 'borg_param_x.html').read_text()
            self.assertIn('all 1,800 starts', page)
            self.assertIn('../runs/n-full/n-full-1/index.html', page)


class ChangesPageTest(unittest.TestCase):
    def test_changes_are_binned_and_ranked(self):
        from zoo import changes_page
        runs = [run('h-full', 'classes-1800', set(range(40)), set(range(10)), 300, '2026-01-04')]
        found = settings_page.collect(runs)
        [c] = changes_page.changes(found)
        self.assertEqual(c['bin'], 'helpful')
        self.assertEqual(c['diff'], {'borg_param_x': 1})
        body = changes_page.page_body(found)
        self.assertIn('Plausible changes', body)
        self.assertIn('borg_param_x.html', body)


class DescriptionTest(unittest.TestCase):
    def test_comment_block_describes_the_keys_under_it_and_class_files_do_not(self):
        from zoo import setting_descriptions as sd
        text = ('### Fleeing ###\n\n# Walk to stairs first.\n# Then recall.\n\nborg_param_a = 1\nborg_param_b = 2\n'
                '# Another.\nborg_param_c = 0\n# mage (harness/borg_mage.txt)\nborg_param_d_mage = 3\n')
        found = sd.parse(text)
        self.assertEqual(found['borg_param_a'], 'Walk to stairs first. Then recall.')
        self.assertEqual(found['borg_param_b'], 'Walk to stairs first. Then recall.')
        self.assertEqual(found['borg_param_c'], 'Another.')
        self.assertNotIn('borg_param_d_mage', found)
        base = {'borg_param_d': {'text': 'D.', 'source': 'x/y/z'},
                'borg_param_attack_preference_spell_permille': {'text': 'Spell.', 'source': 'x/y/z'}}
        self.assertTrue(sd.describe('borg_param_d_mage', base)[0].startswith('The Mage value of borg_param_d'))
        self.assertIn('Spell.', sd.describe('borg_param_attack_preference_mage_spell_permille', base)[0])
        self.assertEqual(sd.describe('borg_unknown', base), (None, None))


if __name__ == '__main__':
    unittest.main()
