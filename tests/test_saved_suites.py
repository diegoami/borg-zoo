"""Named suite discovery preserves stable identities and legacy input locations."""
from pathlib import Path
import tempfile
import unittest
from zoo import saved_suites

ROOT=Path(__file__).resolve().parents[1]

class SavedSuitesTest(unittest.TestCase):
    def test_catalogue_pages_link_exact_identity_and_execution_guide(self):
        entries=saved_suites.catalogue_entries(ROOT)
        self.assertEqual(entries[0]['id'],'suite1-v1')
        self.assertIn('synthetic/balanced-999-incidents',entries[0]['bank']['members'])
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)
            listing=saved_suites.build_site(out,ROOT)
            for entry in entries:
                self.assertIn(entry['name'],listing)
                page=(out/'suites'/entry['id']/'index.html').read_text()
                self.assertIn(entry['bank']['sha256'],page)
                self.assertIn('suite-run.yml',page)
                self.assertIn('stage=smoke',page)
                self.assertEqual((out/'suites'/entry['id']/'suite.json').read_bytes(),
                                 (ROOT/'scenario-suites'/entry['id']/'suite.json').read_bytes())

    def test_blocked_preparation_is_visible_but_not_registered(self):
        ids={entry['id'] for entry in saved_suites.catalogue_entries(ROOT)}
        self.assertNotIn('suite2-v1',ids)
        with tempfile.TemporaryDirectory() as temp:
            listing=saved_suites.build_site(Path(temp),ROOT)
            self.assertIn('Suite 2',listing)
            self.assertIn('Preparation blocked; not runnable',listing)
            self.assertIn('0 / 999',listing)
