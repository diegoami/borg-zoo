"""Native town arrivals and optional trip-application observations.

A false-to-true rising goal is an observed incremental request at that call,
not proof the character would never return without the policy. Existing goals
may originate in earlier policy calls. Never equate recommendations with trips.
"""
from bisect import bisect_right
from collections import Counter
import json


def collect(directory):
    from .borgrs import parse_state_log
    from .town import MESSAGE
    state_file = directory / 'state.log'
    states = parse_state_log(state_file.read_text(errors='replace')) if state_file.exists() else []
    journeys = []
    active = None
    town_turns = dungeon_turns = 0
    previous = None
    for state in states:
        if previous:
            elapsed = max(0, state['turn'] - previous['turn'])
            if previous['depth'] == 0:
                town_turns += elapsed
            else:
                dungeon_turns += elapsed
        if state['depth'] > 0 and active is None:
            active = {'departure_turn': state['turn'], 'arrival_turn': None,
                      'end_turn': state['turn'], 'applications': 0,
                      'new_return_goals': 0, 'new_custom_return_goals': 0,
                      'return_recommendations': 0, 'already_rising_applications': 0,
                      'custom_reasons': [], 'general_notes': []}
            journeys.append(active)
        if active:
            active['end_turn'] = state['turn']
            if state['depth'] == 0:
                active['arrival_turn'] = state['turn']
                active = None
        previous = state
    starts = [j['departure_turn'] for j in journeys]

    def journey_at(turn):
        index = bisect_right(starts, turn) - 1
        if index >= 0 and turn <= journeys[index]['end_turn']:
            return journeys[index]
        return None

    application_records = invalid_trip_records = 0
    last_reasons = []
    trip = directory / 'trip.jsonl'
    if trip.exists():
        with trip.open() as stream:
            for line in stream:
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    invalid_trip_records += 1
                    continue
                journey = journey_at(row.get('game_turn', -1))
                if row.get('event') == 'application':
                    application_records += 1
                    if journey is None:
                        continue
                    journey['applications'] += 1
                    journey['already_rising_applications'] += bool(row['before']['rising'])
                    if row.get('new_return_goal'):
                        journey['new_return_goals'] += 1
                        custom = [r.split('(')[0] for r in last_reasons
                                  if r.startswith(('pack(', 'unknown(', 'purse('))]
                        # Restock is a shared survival/supply criterion. Keep its
                        # co-firing recommendations out of the custom-only count.
                        if custom and 'restock' not in last_reasons:
                            journey['new_custom_return_goals'] += 1
                            journey['custom_reasons'] = sorted(set(journey['custom_reasons'] + custom))
                else:
                    last_reasons = row.get('decision', {}).get('reasons', [])
                    if journey and row.get('decision', {}).get('action') == 'return':
                        journey['return_recommendations'] += 1
    notes = {
        'selling pressure': ('# Going to town (Sell Stuff',),
        'restock/food': ('# returning to town to restock', '# Leaving (restock)',
                         '# Fleeing (restock)', '# Leaving (need food)', '# Fleeing (need food)'),
        'restoration': ('# Going to town (Fix Level)', '# Going to town (Fix Experience)'),
        'periodic/scumming': ('# Going to town (I miss my home)', '# Going to town (scumming check)'),
        'scared': ('# Fleeing (Scary guy on level)', '# Fleeing and leaving the level. (scaryguy)'),
    }
    messages = directory / 'messages.log'
    if messages.exists():
        with messages.open(errors='replace') as stream:
            for line in stream:
                match = MESSAGE.match(line)
                if not match:
                    continue
                journey = journey_at(int(match[2]))
                if journey:
                    for reason, prefixes in notes.items():
                        if match[4].startswith(prefixes) and reason not in journey['general_notes']:
                            journey['general_notes'].append(reason)
    (directory / 'return-events.jsonl').write_text(''.join(json.dumps(j) + '\n' for j in journeys))
    arrived = [j for j in journeys if j['arrival_turn'] is not None]
    return {
        'schema': 'borg-zoo/return-activity@1', 'state_available': bool(states), 'departures': len(journeys),
        'town_arrivals': len(arrived), 'application_records': application_records, 'invalid_trip_records': invalid_trip_records,
        'new_return_goals': sum(j['new_return_goals'] for j in journeys),
        'new_custom_return_goals': sum(j['new_custom_return_goals'] for j in journeys),
        'arrivals_after_custom_goal': sum(j['new_custom_return_goals'] > 0 for j in arrived),
        'arrivals_with_selling_note': sum('selling pressure' in j['general_notes'] for j in arrived),
        'unfinished_journeys_with_custom_goal': sum(j['arrival_turn'] is None and j['new_custom_return_goals'] > 0 for j in journeys),
        'already_rising_applications': sum(j['already_rising_applications'] for j in journeys),
        'return_recommendation_records': sum(j['return_recommendations'] for j in journeys),
        'custom_reasons_by_journey': dict(Counter(r for j in journeys for r in j['custom_reasons'])),
        'general_notes_by_journey': dict(Counter(r for j in journeys for r in j['general_notes'])),
        'sampled_town_turns': town_turns, 'sampled_dungeon_turns': dungeon_turns,
        'qualification': 'Actual arrivals use observed depth>0 to depth=0 transitions. Time allocation uses the previous per-key state. Missing state observations are flagged; their zero counts are unavailable observations. Invalid trip lines are counted and retained raw. New goals require v4 application records; older logs cannot establish them. Custom goals exclude co-firing restock. Associations and general notes can overlap; no exclusive counterfactual cause is claimed.',
    }
