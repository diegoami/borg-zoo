"""borg-rs worlds (borg-zoo#482, borg-reborn-rs #704): pinned world configs,
the world's data made per cell, and the borg_world key kept from the Borg."""
import tempfile
import unittest
from pathlib import Path

from zoo import borgrs

# A stand-in for scripts/make-world.py: makes the four data directories from
# --lib and prints a SHA-256, as the real tool does.
FAKE_TOOL = '''import argparse, hashlib, pathlib, shutil
p = argparse.ArgumentParser(); p.add_argument('--config'); p.add_argument('--lib'); p.add_argument('--out')
a = p.parse_args()
out = pathlib.Path(a.out)
for d in ('gamedata', 'customize', 'help', 'screens'):
    (out / d).mkdir(parents=True)
(out / 'gamedata/world.txt').write_text(pathlib.Path(a.config).read_text())
print(hashlib.sha256(pathlib.Path(a.config).read_bytes()).hexdigest())
'''


class WorldTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.build = root / 'build'
        (self.build / 'game/lib').mkdir(parents=True)
        (self.build / 'worlds').mkdir()
        (self.build / 'tools').mkdir()
        (self.build / 'worlds/breeders-x4.txt').write_text('breeder_weight = 4\n')
        (self.build / 'tools/make-world.py').write_text(FAKE_TOOL)
        self.cell = root / 'cell'
        self.cell.mkdir()
        pin = borgrs.sha256(self.build / 'worlds/breeders-x4.txt')
        self.spec = {'ref': 'abc', 'worlds': {'breeders-x4': pin}}
        self.manifest = {'worlds': {'breeders-x4': pin},
                         'world_tool_sha256': borgrs.sha256(self.build / 'tools/make-world.py')}

    def tearDown(self):
        self.tmp.cleanup()

    def test_the_world_is_made_and_passed_as_the_four_data_directories(self):
        record, root = borgrs.make_world(self.spec, self.manifest, self.build, self.cell, 'breeders-x4')
        self.assertEqual(record['name'], 'breeders-x4')
        self.assertEqual(record['sha256'], self.spec['worlds']['breeders-x4'])
        self.assertRegex(record['data_sha256'], '^[0-9a-f]{64}$')
        argv = borgrs.command(Path('/game/angband'), self.cell, {'seed': 1}, 0, 0, {'cap': 10}, {}, data_root=root)
        data = [a for a in argv[:argv.index('--')] if a.startswith(('-dgamedata=', '-dpref=', '-dhelp=', '-dscreens='))]
        self.assertEqual(data, [f'-dgamedata={root / "gamedata"}', f'-dpref={root / "customize"}',
                                f'-dhelp={root / "help"}', f'-dscreens={root / "screens"}'])

    def test_a_world_the_build_does_not_carry_at_its_pin_is_refused(self):
        (self.build / 'worlds/breeders-x4.txt').write_text('breeder_weight = 8\n')
        with self.assertRaises(ValueError):
            borgrs.make_world(self.spec, self.manifest, self.build, self.cell, 'breeders-x4')
        with self.assertRaises(ValueError):
            borgrs.make_world(self.spec, self.manifest, self.build, self.cell, 'breeders-x8')

    def test_the_world_key_never_reaches_the_borg(self):
        (self.build / 'borg.txt').write_text('borg_respawn_race = 0\nborg_world = none\nborg_x = 1\n')
        profile = {'settings': {'borg_world': 'breeders-x4'}}
        text = borgrs.config_text(self.build, profile)
        self.assertNotIn('borg_world', text)
        self.assertIn('borg_x = 1', text)
        self.assertNotIn('borg_world', borgrs.borg_txt_settings(profile))

    def test_the_world_comes_from_the_profile_else_the_shipped_line(self):
        self.assertEqual(borgrs.world_name({'settings': {'borg_world': 'breeders-x4'}}, 'borg_world = none\n'),
                         'breeders-x4')
        self.assertIsNone(borgrs.world_name({'settings': {}}, 'borg_world = none\n'))
        self.assertIsNone(borgrs.world_name({'settings': {'borg_world': 'none'}}, ''))
        self.assertEqual(borgrs.world_name({'settings': {}}, 'borg_world = breeders-x8\n'), 'breeders-x8')


if __name__ == '__main__':
    unittest.main()
