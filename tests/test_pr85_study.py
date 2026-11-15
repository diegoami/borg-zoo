import unittest
from zoo import catalogue, site


class ReturnStudyPresentation(unittest.TestCase):
    def test_learning_disabled_is_distinct_from_zero_threshold_and_shopping_is_fixed(self):
        cat = catalogue.catalogue()
        exp = catalogue.experiment(catalogue.ROOT / 'experiments/rs-pr85-full.json', cat)
        meta = {'experiment': exp, 'catalogue': {'profiles': cat['profiles']}}
        html = site.tested_settings(meta)
        self.assertIn('learning returns off', html)
        self.assertIn('Shopping is fixed in the four threshold arms.', html)
        self.assertNotIn('This compares both policies together.', html)
        base = cat['profiles']['rs-pr85-return-p2-u4']['settings']
        for name in exp['profiles']:
            settings = cat['profiles'][name]['settings']
            if settings['borg_trip_policy']:
                differences = {k for k in base if base[k] != settings[k]}
                self.assertLessEqual(len(differences), 2)
                self.assertTrue(differences <= {'borg_trip_pack_slack', 'borg_trip_unknown_stacks'})

    def test_exact_owner_grid_is_frozen_in_the_experiment(self):
        cat=catalogue.catalogue()
        exp=catalogue.experiment(catalogue.ROOT/'experiments/rs-pr85-full.json',cat)
        pairs={tuple(cat['profiles'][name]['settings'][key] for key in ('borg_trip_pack_slack','borg_trip_unknown_stacks'))
               for name in exp['profiles'] if cat['profiles'][name]['settings']['borg_trip_policy']==1}
        self.assertEqual(pairs,{(0,0),(1,2),(1,4),(2,4)})
        self.assertEqual(len(catalogue.cells(exp,cat)),10800)
