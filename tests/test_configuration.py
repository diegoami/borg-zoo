import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from zoo import catalogue, configuration


class ConfigurationEvidenceTest(unittest.TestCase):
    def test_capture_collect_and_render_preserve_exact_bytes(self):
        data = b"# original\r\nname = caf\xc3\xa9\r\n"
        digest = hashlib.sha256(data).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work = root / 'work/user'
            work.mkdir(parents=True)
            (work / 'borg.txt').write_bytes(data)
            cell = {'suite': 'smoke', 'specimen': '4.2.6-bbc-m13',
                    'profile': 'normal', 'profile_applied': 'class-specific',
                    'seed': 11, 'config_sha256': digest, 'outcome': 'turn_cap',
                    'requested_profile_settings': {'borg_trip_pack_slack': 0},
                    'effective_options': {'borg_trip_pack_slack': 0}}
            configuration.capture(cell, work.parent, root / 'cells/configurations')
            configuration.collect([cell], root / 'cells', root / 'results')
            self.assertEqual((root / 'results/configurations' / (digest + '.txt')).read_bytes(), data)
            cat = catalogue.catalogue()
            meta = {'experiment': {'specimens': ['4.2.6-bbc-m13'], 'profiles': ['normal']},
                    'catalogue': {'profiles': {'normal': cat['profiles']['normal']},
                                  'specimens': cat['specimens']['specimens']}}
            configuration.build_inspector(meta, [cell], root / 'results', root / 'site')
            self.assertEqual((root / 'site/configurations' / (digest + '.txt')).read_bytes(), data)
            row = json.loads((root / 'site/configurations/games.json').read_text())['games'][0]
            self.assertEqual(row['requested_overrides'], {'borg_trip_pack_slack': 0})
            self.assertEqual(row['applied_profile'], 'class-specific')
            self.assertEqual(row['native_effective_settings'], {'borg_trip_pack_slack': 0})
            # Corruption cannot become a downloadable historical file.
            (root / 'results/configurations' / (digest + '.txt')).write_bytes(b'corrupt')
            configuration.build_inspector(meta, [cell], root / 'results', root / 'bad-site')
            self.assertIsNone(json.loads((root / 'bad-site/configurations/games.json').read_text())['games'][0]['file'])

    def test_missing_file_is_explicit_and_zero_values_have_different_meanings(self):
        with tempfile.TemporaryDirectory() as tmp:
            row = {'config_sha256': 'a' * 64}
            configuration.capture(row, Path(tmp) / 'missing', Path(tmp) / 'blobs')
            self.assertEqual(row['configuration_file']['status'], 'unavailable')
        self.assertIn('pack is full', configuration.explain('borg_trip_pack_slack', 0))
        self.assertIn('disabled', configuration.explain('borg_trip_unknown_stacks', 0))
