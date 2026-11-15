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

    def test_build_identity_is_prominent_and_links_to_the_exact_tree(self):
        meta = self.meta()
        meta['catalogue']['specimens']['pinned'] = {
            'repository': 'diegoami/borg-rs', 'ref': 'a' * 40,
            'source': 'https://example.test/design-note'}
        meta['catalogue']['harness'] = {
            'repository': 'diegoami/borg-rs', 'commit': 'b' * 40}
        meta['catalogue']['suites'] = {
            's': {'seeds': [1, 2], 'cap': 100, 'birth': 'fixed', 'description': 'Fixture suite.'}}
        meta['experiment']['suites'] = ['s']
        meta['experiment']['control'] = 'pinned'
        meta['experiment']['control_profile'] = 'rs-joint-old-control'
        meta['run_id'] = 'fixture'
        brief = site.experiment_brief(meta)
        self.assertIn('Builds compared', brief)
        self.assertIn('diegoami/borg-rs', brief)
        self.assertIn('a' * 40, brief)
        self.assertIn('https://github.com/diegoami/borg-rs/tree/' + 'a' * 40, brief)
        page = site.run_page(meta, [])
        self.assertIn('Builds compared and environment', page)
        self.assertIn('exact source', page)

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

    def test_study_identity_table_names_choice_experiment_repository_build_and_deaths(self):
        meta = self.meta()
        meta['experiment']['name'] = 'rs-kit-trip-confirm'
        meta['experiment']['profiles'] = ['rs-kit-trip-control', 'rs-kit-trip-default']
        meta['catalogue']['specimens']['pinned'] = {
            'repository': 'diegoami/borg-rs', 'ref': 'c' * 40}
        meta['catalogue']['profiles'] = {
            'rs-kit-trip-control': {'settings': {'borg_town_plan': 0, 'borg_trip_policy': 0}},
            'rs-kit-trip-default': {'settings': {'borg_town_plan': 1, 'borg_trip_policy': 1}}}
        cells = [
            {'specimen': 'pinned', 'profile': 'rs-kit-trip-control', 'outcome': 'death'},
            {'specimen': 'pinned', 'profile': 'rs-kit-trip-default', 'outcome': 'turn_cap'}]
        page = site.study_identity_table(meta, cells)
        self.assertIn('Choice', page)
        self.assertIn('Experiment ID', page)
        self.assertIn('Repository', page)
        self.assertIn('Build', page)
        self.assertIn('Deaths', page)
        self.assertIn('rs-kit-trip-confirm', page)
        self.assertIn('diegoami/borg-rs', page)
        self.assertIn('c' * 40, page)
        self.assertIn('100.0%', page)
        self.assertIn('0.0%', page)

    def test_repaired_model_explains_coverage_and_inventory_priorities(self):
        meta = self.meta()
        meta['experiment']['name'] = 'rs-kit-trip-confirm'
        meta['experiment']['profiles'] = ['rs-kit-trip-control', 'rs-kit-trip-default']
        meta['catalogue']['profiles'] = {
            'rs-kit-trip-control': {'settings': {'borg_town_plan': 0, 'borg_trip_policy': 0}},
            'rs-kit-trip-default': {'settings': {'borg_town_plan': 1, 'borg_trip_policy': 1,
                'borg_town_risk': 1000, 'borg_town_w_attack': 50,
                'borg_town_w_support': 25, 'borg_town_w_knowledge': 5}}}
        page = site.tested_settings(meta)
        self.assertIn('104 ordinary shop kinds', page)
        self.assertIn('eligible unknown stacks', page)
        self.assertIn('Attack 50 / support 25 / learning 5', page)
        self.assertNotIn('fixes now being developed are not included', page)
        cells = [{'suite': 's', 'specimen': 'pinned', 'profile': profile,
                  'outcome': outcome, 'final': {'level': 1, 'max_depth': 1}}
                 for profile, outcome in [('rs-kit-trip-control', 'turn_cap'),
                                          ('rs-kit-trip-default', 'death')]]
        self.assertIn('integrated-default candidate had 1 more deaths',
                      site.study_summary(meta, cells, 's'))
