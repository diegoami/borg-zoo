"""Resume cannot dispatch full collection before native smoke acceptance."""
from pathlib import Path
import unittest
import yaml

class HarvestWorkflowTest(unittest.TestCase):
    def test_resume_full_collection_depends_on_native_smoke_assembly(self):
        w=yaml.safe_load((Path(__file__).resolve().parents[1]/'.github/workflows/harvest-incidents.yml').read_text())
        jobs=w['jobs'];full=jobs['full-harvest']
        self.assertIn('assemble',full['needs'])
        self.assertIn("needs.assemble.result == 'success'",full['if'])
        self.assertTrue(any(s.get('name')=='Mixed-class native restart smoke on the assembled bank' for s in jobs['assemble']['steps']))
        self.assertNotIn('--smoke','\n'.join(s.get('run','') for s in full['steps']))
        assembled=jobs['full-assemble']
        self.assertIn('full-harvest',assembled['needs'])
        self.assertTrue(any('incident-full-selection-*' in str(s) for s in assembled['steps']))
        self.assertTrue(any('--per-class 111' in s.get('run','') for s in assembled['steps']))
