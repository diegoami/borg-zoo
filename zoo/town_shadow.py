"""Inspect v5 shadow snapshots; proposals are never counted as transactions."""
from collections import Counter
import hashlib
import json
import statistics

# Native indices 45..68 at the pinned class-calibration specimen.
PARAMETERS = tuple('borg_town_' + name for name in (
    'plan', 'w_light', 'w_food', 'w_bleeding', 'w_poison', 'w_escape',
    'w_knowledge', 'w_power', 'w_trip', 'share', 'light_depth', 'food_trip',
    'target_depth', 'trip_turns', 'w_gold', 'depth_gain', 'explore_turns',
    'stair_turns', 'food_turns', 'light_turns', 'risk', 'home_discount',
    'w_space', 'power_scale'))
QUALIFICATION = ('Hypothetical snapshot decisions, not executed purchases or independent trips. '
                 'Snapshot spending and retained gold cannot select a survival winner.')


def collect(path, effective):
    result = {'schema': 'borg-zoo/town-shadow@1', 'file': path.name,
              'records': 0, 'checked_records': 0, 'status': 'not_observed',
              'qualification': QUALIFICATION, 'error': None}
    errors = []
    effective = effective if isinstance(effective, dict) else {}
    missing = [name for name in PARAMETERS if type(effective.get(name)) not in (int, bool)]
    vector = None if missing else [int(effective[name]) for name in PARAMETERS]
    result['effective_vector'] = dict(zip(PARAMETERS, vector)) if vector else None
    if missing:
        errors.append('missing/invalid effective parameters: ' + ', '.join(missing))
    if not path.exists():
        errors.append('missing shadow record file')
        result.update(status='config_error', error='; '.join(errors))
        return result
    digest = hashlib.sha256()
    with path.open('rb') as raw:
        for chunk in iter(lambda: raw.read(1024 * 1024), b''):
            digest.update(chunk)
    result['sha256'] = digest.hexdigest()
    spends, retained = [], []
    dispositions, supply = Counter(), Counter()
    with path.open(encoding='utf-8', errors='replace') as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            result['records'] += 1
            try:
                row = json.loads(line)
                if row.get('v') != 5 or row.get('mode') != 0:
                    raise ValueError('expected v5 shadow mode 0')
                params = row.get('params')
                if (not isinstance(params, list) or len(params) != 24
                        or any(type(value) is not int for value in params)
                        or vector is None or params != vector):
                    raise ValueError('recorded parameter vector does not match native effective settings')
                if not isinstance(row.get('limits'), list) or len(row['limits']) != 4:
                    raise ValueError('invalid snapshot limits')
                kit, dispose, plan, wares = (row[key] for key in ('kit', 'dispose', 'plan', 'wares'))
                if len(kit) != len(dispose) or any(len(k) != 12 for k in kit):
                    raise ValueError('invalid kit/disposition pairs')
                if any(type(d) is not int or not 0 <= d <= 4 for d in dispose):
                    raise ValueError('invalid disposition code')
                if any(len(p) != 7 or any(type(v) is not int for v in p) for p in plan):
                    raise ValueError('invalid planned purchase')
                gold = row['limits'][0] + sum(k[8] for k, d in zip(kit, dispose) if d == 2)
                spent = sum(p[4] for p in plan)
                if not 0 <= spent <= gold:
                    raise ValueError('snapshot plan overspends')
                planned_supply = Counter()
                for p in plan:
                    needs = {w[6] for w in wares if len(w) == 9 and w[3] == p[1] and w[6] >= 0}
                    if p[0] == 0 and needs:
                        planned_supply[str(p[1])] += p[3]
                supply.update(planned_supply)
                for k, d in zip(kit, dispose):
                    if k[0] == 1:
                        dispositions[{0: 'home_keep', 1: 'home_store', 2: 'home_sell',
                                      3: 'home_drop', 4: 'home_take'}[d]] += 1
                    elif d == 1:
                        dispositions['pack_store_in_home'] += 1
                spends.append(spent)
                retained.append(gold - spent)
                result['checked_records'] += 1
            except (ValueError, TypeError, KeyError, IndexError, AttributeError) as exc:
                # Keep a bounded diagnostic even when a damaged stream has many rows.
                if len(errors) < 8:
                    errors.append(f'line {number}: {exc}')
    result.update(status='config_error' if errors else 'verified' if result['records'] else 'not_observed',
                  error='; '.join(errors) or None,
                  median_planned_spending=statistics.median(spends) if spends else None,
                  median_retained_gold=statistics.median(retained) if retained else None,
                  planned_supply_copies_by_stack_class=dict(supply),
                  snapshot_home_dispositions=dict(dispositions))
    return result
