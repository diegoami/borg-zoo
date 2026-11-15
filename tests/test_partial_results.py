"""Interruption must preserve completed games even without raw retention."""
import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from zoo.__main__ import main


class PartialResultsTest(unittest.TestCase):
    def test_terminated_shard_collects_completed_cell_without_raw_retention(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            exp = root / 'experiment.json'
            exp.write_text(json.dumps({'name': 'interrupted',
                'specimens': ['4.2.6-bbc-m13'], 'control': '4.2.6-bbc-m13',
                'profiles': ['normal'], 'suites': ['smoke']}))
            out = root / 'cells' / 'shard.jsonl'
            code = r'''import sys, threading
from unittest.mock import patch
from zoo.__main__ import main
calls = 0
def run(cell, *args, **kwargs):
    global calls
    calls += 1
    if calls > 1:
        threading.Event().wait(60)
    return {**cell, 'outcome': 'turn_cap', 'wall_seconds': 1,
            'final': {'turn': 20000}, 'first_turn_at_depth': {}}
with patch('zoo.harness.run_cell', side_effect=run):
    main(sys.argv[1:])
'''
            proc = subprocess.Popen([sys.executable, '-c', code, 'run',
                '--experiment', str(exp), '--specimen', '4.2.6-bbc-m13',
                '--build', str(root / 'build'), '--work', str(root / 'work'),
                '--out', str(out), '--jobs', '1'], stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE)
            try:
                deadline = time.monotonic() + 10
                while time.monotonic() < deadline:
                    if out.exists() and out.stat().st_size:
                        break
                    if proc.poll() is not None:
                        self.fail(proc.stderr.read().decode())
                    time.sleep(0.02)
                self.assertTrue(out.exists() and out.stat().st_size,
                                'completed cell was not flushed while next game blocked')
            finally:
                proc.terminate()
                proc.wait(timeout=5)
                proc.stderr.close()
            self.assertEqual(len(out.read_text().splitlines()), 1)
            main(['collect', '--experiment', str(exp), '--cells', str(out.parent),
                  '--results', str(root / 'results'), '--run-id', 'interrupted'])
            rows = [json.loads(line) for line in
                    (root / 'results/interrupted/interrupted/cells.jsonl').read_text().splitlines()]
            self.assertEqual(len(rows), 3)
            self.assertEqual(sum(r['outcome'] == 'turn_cap' for r in rows), 1)
            self.assertEqual(sum(r['outcome'] == 'harness_failure' for r in rows), 2)
