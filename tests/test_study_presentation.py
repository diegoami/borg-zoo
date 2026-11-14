import copy
import unittest
from zoo import site


class StudyPresentationTest(unittest.TestCase):
    def meta(self):
        return {'experiment': {'name': 'rs-joint-m12-confirm', 'specimens': ['pinned'],
                'profiles': ['rs-joint-old-control', 'rs-joint-risk2000'], 'prespecified': 'Fixed before the run.'},
                'catalogue': {'specimens': {'pinned': {'ref': 'a'*40}}, 'profiles': {
                    'rs-joint-old-control': {'settings': {'borg_town_plan': 0, 'borg_trip_policy': 0}},
                    'rs-joint-risk2000': {'settings': {'borg_town_plan': 1, 'borg_trip_policy': 1,
                        'borg_town_risk': 2000, 'borg_trip_pack_slack': 2, 'borg_trip_unknown_stacks': 4}}}}}

    def test_plain_names_and_visible_frozen_settings_without_mutation(self):
        meta=self.meta(); before=copy.deepcopy(meta)
        page=site.tested_settings(meta)
        self.assertIn('New shopper — ON', page)
        self.assertIn('Existing shopper', page)
        self.assertIn('2x forecast risk', page)
        self.assertIn('2 free spaces / 4 unknown gear stacks', page)
        self.assertIn('not make the character fight more recklessly', page)
        self.assertIn('rs-joint-risk2000', page)
        self.assertEqual(meta,before)
        self.assertIn('New shopping + trip',site.arm_label(meta,'pinned','rs-joint-risk2000'))

    def test_mean_table_includes_deaths_and_excludes_failures(self):
        cells=[{'suite':'s','specimen':'pinned','profile':'rs-joint-risk2000','outcome':outcome,
                'final':{'level':level,'max_depth':depth}}
               for outcome,level,depth in [('death',1,2),('turn_cap',7,4),('wall_timeout',99,99)]]
        page=site.study_summary(self.meta(),cells,'s')
        self.assertIn('4.00',page)
        self.assertIn('3.00',page)
        self.assertNotIn('99.00',page)
        self.assertIn('Reached DL3+',page)
        self.assertIn('Incomplete',page)

    def test_other_experiments_keep_their_original_presentation(self):
        meta=self.meta();meta['experiment']['name']='unrelated'
        self.assertEqual(site.tested_settings(meta),'')
        self.assertEqual(site.study_summary(meta,[],'s'),'')
        self.assertIn('pinned · rs-joint-risk2000',site.arm_label(meta,'pinned','rs-joint-risk2000'))

    def test_home_page_links_explain_the_policy_study(self):
        from zoo import landing
        meta = self.meta()
        meta['run_id'] = 'fixture'
        text = landing.policy_studies([(meta, [], None)])
        self.assertIn('Shopping and return-policy experiments', text)
        self.assertIn('Fresh-seed check', text)
        self.assertIn('rs-joint-m12-confirm/fixture/index.html', text)
        self.assertIn('both the new shopper and the new trip policy', text)
        self.assertEqual(landing.policy_studies([]), '')
