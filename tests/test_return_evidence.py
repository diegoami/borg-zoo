import json
from pathlib import Path
import tempfile
import unittest
from zoo import returns


class ReturnEvidence(unittest.TestCase):
    def test_recommendations_new_goals_and_arrivals_remain_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p/'state.log').write_text(''.join(f'{turn} 1,1 d{depth}/{depth} hp10/10 sp0/0 f0 au100 xp0 lv1\n'
                for turn, depth in [(0,0),(10,1),(20,1),(30,0),(40,1),(50,1)]))
            app = {'v':4,'event':'application','game_turn':20,'requested_return':True,
                   'before':{'rising':False},'new_return_goal':True}
            (p/'trip.jsonl').write_text('\n'.join(json.dumps(x) for x in [
                {'v':3,'game_turn':20,'decision':{'action':'return','reasons':['unknown(2 >= 2)']}},app,
                {**app,'before':{'rising':True},'new_return_goal':False},
                {'v':3,'game_turn':50,'decision':{'action':'return','reasons':['restock','pack(free 0 <= 1)']}},
                {**app,'game_turn':50}])+'\n')
            (p/'messages.log').write_text('1 20 0 # Going to town (Sell Stuff).\n')
            result = returns.collect(p)
            self.assertEqual(result['town_arrivals'],1)
            self.assertEqual(result['new_return_goals'],2)
            self.assertEqual(result['new_custom_return_goals'],1)
            self.assertEqual(result['already_rising_applications'],1)
            self.assertEqual(result['arrivals_after_custom_goal'],1)
            self.assertEqual(result['arrivals_with_selling_note'],1)
            self.assertEqual(result['sampled_town_turns'],20)
            self.assertEqual(result['sampled_dungeon_turns'],30)

    def test_advisory_legacy_logs_cannot_establish_new_policy_goals(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            (p/'state.log').write_text('0 1,1 d0/0 hp10/10 sp0/0 f0 au10 xp0 lv1\n10 1,1 d1/1 hp10/10 sp0/0 f0 au10 xp0 lv1\n20 1,1 d0/1 hp10/10 sp0/0 f0 au10 xp0 lv1\n')
            (p/'trip.jsonl').write_text(json.dumps({'v':3,'game_turn':10,'decision':{'action':'return','reasons':['unknown(1 >= 1)']}})+'\n')
            result=returns.collect(p)
            self.assertEqual(result['town_arrivals'],1)
            self.assertEqual(result['return_recommendation_records'],1)
            self.assertEqual(result['new_custom_return_goals'],0)

    def test_missing_and_truncated_evidence_does_not_abort_an_outcome(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            (p/'trip.jsonl').write_text('{"v":')
            result=returns.collect(p)
            self.assertFalse(result['state_available'])
            self.assertEqual(result['invalid_trip_records'],1)
            self.assertEqual(result['application_records'],0)
