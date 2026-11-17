"""The borg-rs core's named scary list as a pinned data file (borg-zoo#228, borg-reborn-rs#518)."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from zoo import borgrs, catalogue, deaths

LIST = b'# monster | from clevel | class exceptions | flags\nGrip, Farmer Maggot\'s Dog | 5 | - | -\n'
LIST_SHA = hashlib.sha256(LIST).hexdigest()
SPECIMEN = '4.2.6-reborn-rust-main-dd5f026e'
PROFILE = 'reborn-scary-test'


def fixture_catalogue(pin=True):
    cat = copy.deepcopy(catalogue.catalogue())
    if pin:
        cat['specimens']['specimens'][SPECIMEN]['scary_lists'] = {'scary_monsters.txt': LIST_SHA}
    cat['profiles'][PROFILE] = {'settings': {'borg_reborn_core': 'borg-rs', 'borg_scary_list': 'scary_monsters.txt'}}
    return cat


def cell():
    return {'suite': 'classes-18', 'specimen': SPECIMEN, 'profile': PROFILE, 'seed': 1548306106}


class ScaryListTest(unittest.TestCase):
    def build(self, root, spec):
        (root / 'build.json').write_text(json.dumps({
            'source_commit': spec['ref'], 'impl': spec['impl'], 'binary_sha256': 'bin',
            'build_id': {'git_rev': spec['ref'], 'source_sha256': 'src'},
            'scary_lists': {'scary_monsters.txt': LIST_SHA}}))
        (root / 'borg.txt').write_text('borg_reborn_core = reborn\nborg_cheat_death = FALSE\n')
        (root / 'scary_lists').mkdir()
        (root / 'scary_lists/scary_monsters.txt').write_bytes(LIST)

    def play(self, cat, dead=False):
        c = cell()
        spec = cat['specimens']['specimens'][SPECIMEN]
        race, cls = catalogue.character(cat['suites']['classes-18'], c['seed'])
        seen = []

        def run(argv, **kwargs):
            out = Path(argv[argv.index('-keylog') + 1]).parent
            listed = out / 'user/scary_monsters.txt'
            seen.append({'borg.txt': (out / 'user/borg.txt').read_text(),
                         'list': listed.read_bytes() if listed.exists() else None})
            (out / 'keys.log').write_text('1 k 0 0\n')
            (out / 'summary.json').write_text(json.dumps({
                'race': race, 'class': cls, 'stop_reason': 'death' if dead else 'turns', 'dead': dead,
                'death_cause': 'a crow' if dead else None, 'seed': c['seed']}))
            return type('Result', (), {'returncode': 0})()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build(root, spec)
            with patch('zoo.borgrs.subprocess.run', side_effect=run), patch('zoo.deaths.subprocess.run', side_effect=run):
                record = borgrs.run_cell(c, root, root / 'work', cat)
                entry, files = None, {}
                if dead:
                    entry = deaths.bundle(record, c, root, cat, root / 'deaths', {'run_id': '1'})
                    out = root / 'deaths' / catalogue.cell_key(c)
                    files = {p.relative_to(out).as_posix(): p.read_bytes() for p in out.rglob('*') if p.is_file()}
        return record, seen, entry, files

    def test_the_cell_gets_the_pinned_list_and_records_it(self):
        record, seen, _, _ = self.play(fixture_catalogue())
        self.assertEqual(seen[0]['list'], LIST)
        self.assertIn('\nborg_scary_list = scary_monsters.txt\n', '\n' + seen[0]['borg.txt'])
        self.assertEqual(record['scary_list'], {'name': 'scary_monsters.txt', 'sha256': LIST_SHA})
        self.assertEqual(record['outcome'], 'turn_cap')

    def test_a_cell_without_the_setting_gets_no_list(self):
        cat = fixture_catalogue()
        cat['profiles'][PROFILE]['settings'].pop('borg_scary_list')
        record, seen, _, _ = self.play(cat)
        self.assertIsNone(seen[0]['list'])
        self.assertIsNone(record['scary_list'])

    def test_a_death_bundle_keeps_the_list_and_its_hash(self):
        _, seen, entry, files = self.play(fixture_catalogue(), dead=True)
        self.assertEqual(entry['status'], 'reproduced')
        self.assertEqual(seen[1]['list'], LIST)  # the replay got the same file
        self.assertEqual(files['user/scary_monsters.txt'], LIST)
        config = dict(l.split('=', 1) for l in files['config.txt'].decode().splitlines())
        self.assertEqual((config['borg_scary_list'], config['scary_list_sha256']), ('scary_monsters.txt', LIST_SHA))

    def test_a_list_the_specimen_does_not_pin_is_refused(self):
        cat = fixture_catalogue(pin=False)
        exp = {'name': 'x', 'specimens': [SPECIMEN], 'profiles': [PROFILE], 'suites': ['classes-18'],
               'control': SPECIMEN, 'control_profile': PROFILE}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'x.json'
            path.write_text(json.dumps(exp))
            with self.assertRaisesRegex(ValueError, 'borg_scary_list'):
                catalogue.experiment(str(path), cat)

    def test_the_build_copies_and_checks_the_pinned_list(self):
        spec = {'ref': 'r', 'scary_lists': {'scary_monsters.txt': LIST_SHA}}
        with tempfile.TemporaryDirectory() as tmp:
            src, out = Path(tmp) / 'src', Path(tmp) / 'out'
            (src / 'harness').mkdir(parents=True)
            out.mkdir()
            (src / 'harness/scary_monsters.txt').write_bytes(LIST)
            self.assertEqual(borgrs.copy_scary_lists(spec, src, out), {'scary_monsters.txt': LIST_SHA})
            self.assertEqual((out / 'scary_lists/scary_monsters.txt').read_bytes(), LIST)
            (src / 'harness/scary_monsters.txt').write_bytes(LIST + b'edited\n')
            with self.assertRaisesRegex(ValueError, 'catalogue pins'):
                borgrs.copy_scary_lists(spec, src, out)


if __name__ == '__main__':
    unittest.main()
