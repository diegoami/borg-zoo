"""The resolved-settings receipt of a borg-rs cell (borg-zoo#539, borg-reborn-rs#798).

The vendored core writes `settings-resolved.json` beside `params-core.json` when it attaches to a character:
`{"schema": "borg-settings-resolved@1", "class_index": 7, "class_name": "ranger",
"effective_settings": {"town_phase_reserve": 2}}`. The map holds every registered parameter whose live value differs
from its compiled default for that class, with canonical names and integer values. An explicit setting equal to the
compiled class default is omitted, so an empty map is valid and an omitted name needs independent default information
before a specific number can be verified. A missing file means no receipt (None).

`collect` keeps the original bytes and their SHA-256 with the cell, validates the schema, the integer map and the class
against the played class, and projects the profile's written `borg_param_*` keys onto canonical names for the played
class. A malformed receipt gets its own status; it never changes the cell's outcome.
"""
import hashlib
import json
from pathlib import Path

SCHEMA = 'borg-settings-resolved@1'
FILE = 'settings-resolved.json'
CLASSES = ('warrior', 'mage', 'druid', 'priest', 'necromancer', 'paladin', 'rogue', 'ranger', 'blackguard')
_PREFIX = 'borg_param_'


def canonical(written, played):
    """(canonical name, applies) for a written key, for the played class (lowercase), or None for a key that
    is not a borg_param_ setting. `__class` and `@class` suffixes name a class value; the 54 legacy names
    `attack_preference_<class>_<family>_permille` are aliases of the class values of the family's name."""
    if not written.startswith(_PREFIX):
        return None
    name = written[len(_PREFIX):]
    for sep in ('__', '@'):
        if sep in name:
            base, cls = name.rsplit(sep, 1)
            if cls in CLASSES:
                return base, cls == played
    head = 'attack_preference_'
    if name.startswith(head) and name.endswith('_permille'):
        mid = name[len(head):-len('_permille')]
        for cls in CLASSES:
            if mid.startswith(cls + '_'):
                return head + mid[len(cls) + 1:] + '_permille', cls == played
    return name, True


def _bad(raw, text, error):
    return {'status': 'malformed', 'error': error, 'sha256': hashlib.sha256(raw).hexdigest(), 'raw': text,
            'schema': None, 'class_index': None, 'class_name': None, 'effective_settings': None, 'projection': None}


def collect(directory, played_class, profile_settings):
    """The receipt record for a cell's output directory, or None when the cell wrote no receipt."""
    path = Path(directory) / FILE
    if not path.is_file():
        return None
    raw = path.read_bytes()
    text = raw.decode('utf-8', errors='replace')
    try:
        data = json.loads(raw)
    except ValueError as exc:
        return _bad(raw, text, f'not JSON: {exc}')
    if not isinstance(data, dict):
        return _bad(raw, text, 'not a JSON object')
    if data.get('schema') != SCHEMA:
        return _bad(raw, text, f"schema {data.get('schema')!r}, expected {SCHEMA!r}")
    idx, name, settings = data.get('class_index'), data.get('class_name'), data.get('effective_settings')
    if not isinstance(idx, int) or isinstance(idx, bool) or not 0 <= idx < len(CLASSES):
        return _bad(raw, text, f'class_index {idx!r} is not 0-8')
    if name != CLASSES[idx]:
        return _bad(raw, text, f'class_name {name!r} does not match class_index {idx} ({CLASSES[idx]})')
    if not isinstance(settings, dict) or not all(
            isinstance(k, str) and isinstance(v, int) and not isinstance(v, bool) for k, v in settings.items()):
        return _bad(raw, text, 'effective_settings is not a map of names to integers')
    played = (played_class or '').lower()
    if played and played != name:
        return _bad(raw, text, f'receipt class {name!r} differs from the played class {played_class!r}')
    projection = {}
    for key, want in sorted((profile_settings or {}).items()):
        found = canonical(key, name)
        if found is None:
            continue
        canon, applies = found
        if not applies:
            projection[key] = {'canonical': canon, 'written': want, 'verdict': 'not applicable to the played class'}
        elif canon not in settings:
            projection[key] = {'canonical': canon, 'written': want, 'receipt': None,
                               'verdict': 'omitted (equal to the compiled default, or needs default information)'}
        elif isinstance(want, int) and not isinstance(want, bool):
            projection[key] = {'canonical': canon, 'written': want, 'receipt': settings[canon],
                               'verdict': 'match' if settings[canon] == want else 'differs'}
        else:
            projection[key] = {'canonical': canon, 'written': want, 'receipt': settings[canon],
                               'verdict': 'not compared (written value is not an integer)'}
    return {'status': 'ok', 'error': None, 'sha256': hashlib.sha256(raw).hexdigest(), 'raw': text,
            'schema': SCHEMA, 'class_index': idx, 'class_name': name, 'effective_settings': settings,
            'projection': projection}
