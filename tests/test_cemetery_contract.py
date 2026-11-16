"""Integration with the actual pinned Cemetery adapter, enabled by the smoke CI."""
import os
from pathlib import Path
import tempfile
import unittest

from zoo import scenarios as s


@unittest.skipUnless(os.environ.get('PINNED_CEMETERY_DIR'), 'requires pinned Cemetery checkout (smoke workflow)')
class CemeteryContractTest(unittest.TestCase):
    def test_exporter_destination_is_the_directory_monitored_by_zoo(self):
        bank=Path(os.environ['PINNED_CEMETERY_DIR'])
        definition=s.read(s.catalogue.ROOT/'scenario-experiments/cemetery-warrior-smoke.json')
        module=s.bank_module(bank,definition['bank'])
        generated=module.generate(bank/definition['bank']['manifest'])
        case=next(c for c in generated['cases'] if c['id']==definition['scenario_ids'][0])
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'source';(source/'harness').mkdir(parents=True)
            # Exercise the real adapter's environment and process launch without
            # a game build. A mistakenly invoked exporter would create this dir.
            (source/'harness/run.sh').write_text('#!/bin/bash\nset -eu\nmkdir -p "$1" "$BORG_DEATH_RECORDS_DIR"\n')
            attempt=root/'attempt';attempt.mkdir()
            rc=module.RebornAdapter(source).run(case,generated['root'],attempt/'run')
            self.assertEqual(rc,0)
            self.assertTrue((attempt/'natural-registry-guard').is_dir())
            self.assertTrue((attempt/'profile.txt').is_file())


if __name__=='__main__':unittest.main()
