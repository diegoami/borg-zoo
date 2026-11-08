"""What a run was doing when it stopped short of an endpoint.

Recorded for every run that did not finish (stalled, wall timeout, crash,
harness failure, config error), so a stall can be told apart from another:
a level cycle that spends energy without game time (better-borg-c#204,
neo-angband-tracker#403), a zero-energy retry, or a process that stopped
deciding. The `kind` is a heuristic label over the counters; the counters
and the note tail are the evidence.
"""
from collections import Counter

TAIL = 20
NOTE_CHARS = 160


def _kind(decisions_delta, energy_delta, depth_changes, keys_delta=None):
    if decisions_delta == 0 and not keys_delta:
        return 'no_decisions'
    if depth_changes:
        return 'level_cycle'
    if energy_delta == 0:
        return 'zero_energy_retry'
    if energy_delta and energy_delta > 0:
        return 'energy_without_time'
    return 'unclassified'


def observer(states, trace_text):
    """From better-borg-c observer STATE records and BORG notes."""
    if not states:
        return {'source': 'observer', 'kind': 'no_states'}
    last = states[-1]
    frozen = last.get('turn')
    at_frozen = [s for s in states if s.get('turn') == frozen]
    first = at_frozen[0]
    depths = [s.get('depth') for s in at_frozen]
    depth_changes = sum(1 for a, b in zip(depths, depths[1:]) if a != b)
    decisions_delta = (last.get('decisions') or 0) - (first.get('decisions') or 0)
    energy_delta = (last.get('energy') or 0) - (first.get('energy') or 0)
    notes = []
    for line in trace_text.splitlines():
        if line.startswith('BORG '):
            parts = line.split(' ', 2)
            if len(parts) == 3 and parts[1].lstrip('-').isdigit():
                notes.append((int(parts[1]), parts[2][:NOTE_CHARS]))
    frozen_notes = [text for turn, text in notes if turn == frozen]
    recent = states[-TAIL:]
    span_turns = recent[-1].get('turn', 0) - recent[0].get('turn', 0)
    span_decisions = (recent[-1].get('decisions') or 0) - (recent[0].get('decisions') or 0)
    return {
        'source': 'observer',
        # Sampled states can alias a stair cycle; more than one depth at the
        # frozen turn is a level change too.
        'kind': _kind(decisions_delta, energy_delta, depth_changes or len({d for d in depths if d is not None}) > 1),
        'last_turn': frozen,
        'states_at_last_turn': len(at_frozen),
        'decisions_delta': decisions_delta,
        'energy_delta': energy_delta,
        'depth_changes': depth_changes,
        'depth_changes_note': 'counted between state records, which are sampled every 100 decisions; a lower bound',
        'depths_seen': sorted({d for d in depths if d is not None}),
        'turns_per_1000_decisions': (round(1000 * span_turns / span_decisions, 1) if span_decisions else None),
        'top_notes_at_last_turn': Counter(frozen_notes).most_common(5),
        'note_tail': [f'{turn} {text}' for turn, text in notes[-TAIL:]],
        'position': None,
        'position_note': 'the observer records no player position',
    }


def borgh(keys_text, summary):
    """From a borgh key log (`<turn> <event> <keycode> <mods>` per key)."""
    rows = []
    for line in keys_text.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0].isdigit():
            rows.append((int(parts[0]), parts[1], parts[2]))
    if not rows:
        return {'source': 'borgh', 'kind': 'no_keys', 'stop_reason': summary.get('stop_reason')}
    frozen = rows[-1][0]
    at_frozen = [r for r in rows if r[0] == frozen]
    depth = summary.get('depth')
    return {
        'source': 'borgh',
        'kind': _kind(None, None, 0, keys_delta=len(at_frozen)) if len(at_frozen) <= 1 else 'keys_without_time',
        'stop_reason': summary.get('stop_reason'),
        'last_turn': frozen,
        'keys_at_last_turn': len(at_frozen),
        'top_keys_at_last_turn': Counter(f'{e} {k}' for _, e, k in at_frozen).most_common(5),
        'key_tail': [' '.join(map(str, r)) for r in rows[-TAIL:]],
        'depth': depth,
        'energy_delta': None,
        'position': None,
        'position_note': 'borgh records no energy or player position',
    }
