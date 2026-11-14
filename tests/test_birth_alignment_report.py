"""Meaningful C/Neo representation controls for the pilot report."""
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / 'tools/report-birth-alignment.py'
SPEC = importlib.util.spec_from_file_location('birth_alignment_report', PATH)
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


class BirthAlignmentRepresentationTests(unittest.TestCase):
    def test_inactive_quick_seed_does_not_make_equal_well_states_different(self):
        # C keeps Rand_value=0 at initialization; Neo stores the supplied seed.
        c = dict(quick=False, value=0, stateI=0, state=[12, 34])
        neo = dict(c, value=303)
        self.assertEqual(REPORT.active_rng(c), REPORT.active_rng(neo))

    def test_active_quick_seed_difference_is_not_hidden(self):
        c = dict(quick=True, value=71118219, stateI=0, state=[12, 34])
        neo = dict(c, value=0xC0FFEE)
        self.assertNotEqual(REPORT.active_rng(c), REPORT.active_rng(neo))

    def test_pack_slot_normalization_preserves_quantity_differences(self):
        c = dict(tval=28, sval=5, slot=12, number=3, weight=8)
        neo = dict(c, slot=-1)
        self.assertEqual(REPORT.gear([c]), REPORT.gear([neo]))
        self.assertNotEqual(REPORT.gear([c]), REPORT.gear([dict(neo, number=1)]))


if __name__ == '__main__':
    unittest.main()
