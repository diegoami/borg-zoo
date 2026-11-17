import json
from pathlib import Path
import tempfile
import unittest

from zoo import define

ROOT = Path(__file__).resolve().parents[1]


class DefineTest(unittest.TestCase):
    def test_every_definition_matches_the_catalogue(self):
        for path in sorted((ROOT / 'definitions').glob('*.yaml')):
            with self.subTest(definition=path.name):
                _, problems, changes = define.plan(path)
                self.assertEqual(problems, [])
                self.assertEqual([(k, n) for k, n, _ in changes], [])

    def test_every_experiment_has_a_definition(self):
        import glob
        defined = set()
        for path in sorted((ROOT / 'definitions').glob('*.yaml')):
            d = define.load(path)
            defined.add(define.target(d, ROOT).relative_to(ROOT).as_posix())
        files = {Path(f).as_posix() for f in glob.glob('experiments/*.json', root_dir=ROOT) + glob.glob('smoke/*.json', root_dir=ROOT)}
        self.assertEqual(sorted(files - defined), [], 'experiment files without a definitions/*.yaml')

    def write(self, root, text):
        for name in ('specimens', 'profiles'):
            (root / 'catalogue').mkdir(exist_ok=True)
        (root / 'catalogue/specimens.json').write_text(json.dumps({'specimens': {}}))
        (root / 'catalogue/profiles.json').write_text(json.dumps({'profiles': {
            'x-a-on': {'settings': {'borg_town_plan': 1, 'k': 9}}}}))
        (root / 'experiments').mkdir()
        path = root / 'd.yaml'
        path.write_text(text)
        return path

    BASE = '''name: x
issue: 1
tier: pilot
prespecified: p
specimen: {name: s, repository: diegoami/borg-reborn-rs, ref: abc}
settings: {borg_town_plan: 1}
'''

    def test_vary_multiplies_and_names_arms(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), self.BASE + "vary:\n  a: {a: {}, b: {k: 2}}\n  c: {'on': {t: 1}, 'off': {t: 0}}\n")
            d, problems, changes = define.plan(path, tmp)
            profiles = {n: b for k, n, b in changes if k == 'profile'}
            # x-a-on already exists with other settings: a conflict, not a new profile
            self.assertEqual(sorted(profiles), ['x-a-off', 'x-b-off', 'x-b-on'])
            self.assertTrue(any('x-a-on' in p for p in problems))
            self.assertEqual(profiles['x-b-on']['settings'], {'borg_town_plan': 1, 'k': 2, 't': 1})
            spec = next(b for k, n, b in changes if k == 'specimen')
            self.assertEqual((spec['kind'], spec['impl'], spec['exact_turns']), ('borg-rs', 'rust', True))
            exp = next(b for k, n, b in changes if k == 'experiment')
            self.assertEqual((exp['issue'], exp['suites'], len(exp['profiles'])), (1, ['classes-18'], 4))

    SMALL = BASE.replace('tier: pilot', 'tier: small') + "vary:\n  a: {a: {}, b: {k: 2}}\n"

    def test_a_tier_above_pilot_needs_a_pilot_first(self):
        # RULES 16 (owner, 2026-11-17): always the pilot first, whatever tier is asked for.
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), self.SMALL)
            _, problems, _ = define.plan(path, tmp)
            self.assertTrue(any(p.startswith('RULES 16') for p in problems), problems)

    def test_a_pilot_of_the_same_arms_lets_the_tier_through(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), self.SMALL)
            (Path(tmp) / 'experiments/x-pilot.json').write_text(json.dumps({
                'name': 'x-pilot', 'suites': ['classes-18'], 'specimens': ['s'], 'profiles': ['x-a', 'x-b']}))
            _, problems, _ = define.plan(path, tmp)
            self.assertEqual([p for p in problems if p.startswith('RULES 16')], [])

    def test_a_pilot_of_other_arms_or_another_specimen_does_not_count(self):
        for pilot in ({'specimens': ['s'], 'profiles': ['x-a']},          # an arm missing
                      {'specimens': ['other'], 'profiles': ['x-a', 'x-b']},  # another build
                      {'specimens': ['s'], 'profiles': ['x-a', 'x-b'], 'suites': ['classes-1800-small']}):  # not a pilot
            with self.subTest(pilot=pilot), tempfile.TemporaryDirectory() as tmp:
                path = self.write(Path(tmp), self.SMALL)
                (Path(tmp) / 'experiments/x-pilot.json').write_text(json.dumps({'name': 'x-pilot', 'suites': ['classes-18'], **pilot}))
                _, problems, _ = define.plan(path, tmp)
                self.assertTrue(any(p.startswith('RULES 16') for p in problems), problems)

    def test_a_declared_pilot_on_its_own_suite_is_a_pilot(self):
        with tempfile.TemporaryDirectory() as tmp:
            text = self.SMALL.replace('tier: small', 'suites: [classes-1800-small-rangers]\npilot: true')
            path = self.write(Path(tmp), text)
            _, problems, changes = define.plan(path, tmp)
            self.assertEqual([p for p in problems if p.startswith('RULES 16')], [])
            exp = next(b for k, n, b in changes if k == 'experiment')
            self.assertTrue(exp['pilot'])

    def test_an_existing_experiment_is_not_rechecked(self):
        # Experiments generated before RULES 16 stay valid: only a new experiment file is checked.
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), self.SMALL)
            _, _, changes = define.plan(path, tmp)
            exp = next(b for k, n, b in changes if k == 'experiment')
            (Path(tmp) / 'experiments/x.json').write_text(json.dumps(exp, indent=2) + '\n')
            _, problems, _ = define.plan(path, tmp)
            self.assertEqual([p for p in problems if p.startswith('RULES 16')], [])

    def test_an_existing_profile_with_other_settings_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(Path(tmp), self.BASE + "vary:\n  a: {a: {}}\n  c: {'on': {t: 1}}\n")
            _, problems, _ = define.plan(path, tmp)
            self.assertTrue(any('x-a-on exists with other settings' in p for p in problems))

    def test_unknown_keys_and_tiers_are_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'bad.yaml'
            path.write_text(self.BASE + 'colour: red\narms: {a: {}}\n')
            with self.assertRaisesRegex(ValueError, 'unknown keys'):
                define.load(path)
            path.write_text(self.BASE.replace('tier: pilot', 'tier: huge') + 'arms: {a: {}}\n')
            with self.assertRaisesRegex(ValueError, 'tier must be'):
                define.load(path)
            path.write_text(self.BASE + 'vary:\n  c: {on: {t: 1}}\n')
            with self.assertRaisesRegex(ValueError, 'quote it'):
                define.arms(define.load(path))


if __name__ == '__main__':
    unittest.main()


class ReportShowsDefinitionTest(unittest.TestCase):
    def test_provenance_links_issue_and_embeds_the_yaml(self):
        from zoo import site
        html = site.provenance_line({'name': 'reborn-heal-pilot'})
        self.assertIn('borg-zoo issue #151', html)
        self.assertIn('definitions/reborn-heal-pilot.yaml', html)
        self.assertIn('<details class="definition" open>', html)
        self.assertIn('caution_heal_when_outmatched', html)  # the YAML itself, not just a link
        self.assertEqual(site.provenance_line({'name': 'no-such-experiment'}), '')
