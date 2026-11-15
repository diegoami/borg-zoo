import unittest
from zoo.neo_original import profile_args, summarise

class SeededNeoTest(unittest.TestCase):
    def test_opt_in_and_unknown_profile(self):
        self.assertEqual(profile_args({}), ([], []))
        with self.assertRaises(ValueError):
            profile_args({'birth_profile': 'typo'})
        build, run = profile_args({'birth_profile': 'c-seeded-point-buy-v2'})
        self.assertEqual(run, ['--birth-profile', 'c-seeded-point-buy-v2'])
        self.assertIn('--exact-tick-cap', build)
        self.assertIn('--c-gcc-coordinate-order', build)

    def test_wrong_profile_or_missing_adapter_is_configuration_error(self):
        spec = {'ref': 'a'*40, 'engine_ref': 'b'*40, 'toolkit_ref': 'c'*40,
                'birth_profile': 'c-seeded-point-buy-v2'}
        cell = {'race': 'Human', 'class': 'Warrior'}
        record = {'schema': 'neo-original/run@1', 'outcome': 'death', 'turn': 50,
                  'birth': cell, 'provenance': {'engine': {'commit': spec['engine_ref']},
                  'borg': {'commit': spec['ref']}}}
        self.assertEqual(summarise(cell,spec,{'cap':100,'birth':'assigned'},record,None,1)['outcome'],'config_error')
        record['inputs'] = {'birthProfile': spec['birth_profile']}
        self.assertEqual(summarise(cell,spec,{'cap':100,'birth':'assigned'},record,None,1)['outcome'],'config_error')
        record['provenance'].update(exactTickCap=True,cSeedStartup=True,cGccCoordinateOrder=True)
        self.assertEqual(summarise(cell,spec,{'cap':100,'birth':'assigned'},record,None,1)['outcome'],'death')
        record['turn']=101
        self.assertEqual(summarise(cell,spec,{'cap':100,'birth':'assigned'},record,None,1)['outcome'],'harness_failure')
