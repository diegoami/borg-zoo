import unittest

from zoo import deaths

DUMP = """
  [Character Equipment]

a) Dagger (1d4) (+0,+0)
b) (nothing)
  [Character Inventory]

a) 5 Rations of Food
  [Home Inventory (page 1)]

a) (nothing)
"""

LOG = """\
 10 100 0 # Trip: return via search (plan 1): unknown(2 >= 2)
 10 100 0 # Looking for up stairs.  Going up.
 10 100 0 # no up stairs found, going down
 12 110 0 # Quaffing Potions of Cure Light Wounds.
 13 120 8 You die.
"""


class DeathsTest(unittest.TestCase):
    def test_groups_deaths_by_game(self):
        cells = [{'profile': p, 'class': 'Rogue', 'seed': 1, 'play_sha256': h, 'outcome': o}
                 for p, h, o in (('a', 'x', 'death'), ('b', 'x', 'death'), ('c', 'y', 'death'), ('d', 'z', 'turn_cap'))]
        groups = deaths.death_groups(cells)
        self.assertEqual([[c['profile'] for c in g] for g in groups], [['a', 'b'], ['c']])

    def test_dump_sections_drop_empty_slots(self):
        s = deaths.dump_sections(DUMP)
        self.assertEqual(s['Character Equipment'], ['a) Dagger (1d4) (+0,+0)'])
        self.assertEqual(s['Character Inventory'], ['a) 5 Rations of Food'])
        self.assertEqual(s['Home Inventory (page 1)'], [])
        self.assertEqual(s['Character Quiver'], [])

    def test_counts_and_split(self, tmp=None):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'm.log'
            p.write_text(LOG)
            rows = deaths.messages(p)
        c = deaths.counts(rows)
        self.assertEqual(c['Trip returns'], 1)
        self.assertEqual(c['Trip returns followed by "going down"'], 1)
        self.assertEqual(c['Cure potions quaffed'], 1)
        other = rows[:3] + [(110, 'x', ' 12 110 0 # something else')]
        self.assertEqual(deaths.first_split(rows, other)['turn'], 110)
        self.assertIsNone(deaths.first_split(rows, rows))


if __name__ == '__main__':
    unittest.main()
