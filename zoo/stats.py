"""Per-arm summaries and paired comparisons over one experiment run.

Everything here is descriptive. Small suites give wide intervals; the site
says so next to every table.
"""
import math
from statistics import median

VALID = ('death', 'turn_cap', 'completion')
OUTCOMES = ('death', 'turn_cap', 'completion', 'stalled', 'wall_timeout', 'crash',
            'harness_failure', 'config_error', 'borg_stopped', 'decision_cap')
DEPTH_GOAL = 5


def wilson(successes, n, z=1.959964):
    if n == 0:
        return (None, None)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def mcnemar_exact(b, c):
    """Two-sided exact binomial test on the discordant pairs b and c."""
    n = b + c
    if n == 0:
        return None
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def arm_key(cell):
    return (cell['specimen'], cell['profile'])


def survived(cell):
    return cell['outcome'] in ('turn_cap', 'completion')


def reached(cell, depth=DEPTH_GOAL):
    return (cell['final'].get('max_depth') or 0) >= depth


def arm_summary(cells):
    counts = {o: 0 for o in OUTCOMES}
    for c in cells:
        counts[c['outcome'] if c['outcome'] in counts else 'harness_failure'] += 1
    valid = [c for c in cells if c['outcome'] in VALID]
    deaths = [c for c in valid if c['outcome'] == 'death']
    n = len(valid)
    goal = [c for c in valid if survived(c) and reached(c)]
    depths = [c['final'].get('max_depth') or 0 for c in valid]
    levels = [c['final'].get('max_level') or 0 for c in valid]
    death_turns = [c['final'].get('turn') for c in deaths if c['final'].get('turn') is not None]
    return {
        'cells': len(cells), 'valid': n, 'counts': counts,
        'deaths': len(deaths), 'death_rate': len(deaths) / n if n else None,
        'death_ci': wilson(len(deaths), n),
        'goal': len(goal), 'goal_rate': len(goal) / n if n else None, 'goal_ci': wilson(len(goal), n),
        'median_max_depth': median(depths) if depths else None,
        'median_max_level': median(levels) if levels else None,
        'median_death_turn': median(death_turns) if death_turns else None,
    }


def pairing_class(cell):
    """Runs pair only within one harness kind and, for Mandos, one
    command-stream profile: the same seed is the same game only under the
    same frontend, and play hashes are comparable only under the same stream
    encoding. Mandos cells recorded before the profile field are legacy."""
    kind = cell.get('harness_kind', 'better-borg-c')
    if kind == 'mandos':
        return kind, cell.get('command_stream_profile') or 'play-session'
    return kind, None


def same_play(a, b):
    """Identical play: equal play hashes (configuration lines excluded) when
    both runs have one, else equal full-trace hashes. Runs recorded before
    the play hash existed only match under the same configuration. Runs of
    different pairing classes never match."""
    if pairing_class(a) != pairing_class(b):
        return False
    if a.get('play_sha256') and b.get('play_sha256'):
        return a['play_sha256'] == b['play_sha256']
    return bool(a.get('trace_sha256')) and a.get('trace_sha256') == b.get('trace_sha256')


def paired(control_cells, arm_cells):
    control = {(c['suite'], c['seed']): c for c in control_cells if c['outcome'] in VALID}
    rescued = newly_killed = both_died = both_lived = identical = 0
    goal_gained = goal_lost = 0
    for c in arm_cells:
        if c['outcome'] not in VALID:
            continue
        k = control.get((c['suite'], c['seed']))
        if not k or pairing_class(k) != pairing_class(c):
            continue
        a_dead, k_dead = c['outcome'] == 'death', k['outcome'] == 'death'
        if k_dead and not a_dead:
            rescued += 1
        elif a_dead and not k_dead:
            newly_killed += 1
        elif a_dead:
            both_died += 1
        else:
            both_lived += 1
        a_goal, k_goal = survived(c) and reached(c), survived(k) and reached(k)
        goal_gained += a_goal and not k_goal
        goal_lost += k_goal and not a_goal
        if same_play(c, k):
            identical += 1
    pairs = rescued + newly_killed + both_died + both_lived
    return {'pairs': pairs, 'rescued': rescued, 'newly_killed': newly_killed,
            'both_died': both_died, 'both_lived': both_lived, 'identical_traces': identical,
            'death_p': mcnemar_exact(rescued, newly_killed),
            'goal_gained': goal_gained, 'goal_lost': goal_lost,
            'goal_p': mcnemar_exact(goal_gained, goal_lost)}


def survival_table(cells, cap, fractions=(0.25, 0.5, 0.75, 1.0)):
    valid = [c for c in cells if c['outcome'] in VALID]
    n = len(valid)
    rows = []
    for f in fractions:
        t = int(cap * f)
        dead = sum(1 for c in valid if c['outcome'] == 'death' and (c['final'].get('turn') or 0) <= t)
        rows.append({'turn': t, 'alive': (n - dead) / n if n else None})
    return rows


def milestone_table(cells, fractions=(0.25, 0.5, 0.75, 1.0)):
    """Median level, max depth and (where logged) gold on hand at turn
    fractions of the cap, over finished runs that recorded milestones
    (the better-borg-c observer, and borg-rs specimens with depth_stream).

    Not a survival or depth-reached rate: a cell missing from the median
    (no milestones, or dead before that fraction's turn) is simply excluded,
    so n can differ per row; it never substitutes a death for a value.
    """
    valid = [c for c in cells if c['outcome'] in VALID and c.get('milestones')]
    rows = []
    for i, f in enumerate(fractions):
        at_f = [c['milestones'][i] for c in valid if len(c['milestones']) > i]
        turn = next((m['turn'] for m in at_f), None)
        levels = [m['level'] for m in at_f if m.get('level') is not None]
        depths = [m['max_depth'] for m in at_f if m.get('max_depth') is not None]
        golds = [m['gold'] for m in at_f if m.get('gold') is not None]
        rows.append({'fraction': f, 'turn': turn, 'n': len(at_f),
                     'median_level': median(levels) if levels else None,
                     'median_max_depth': median(depths) if depths else None,
                     'median_gold': median(golds) if golds else None})
    return rows


def depth_table(cells, marks=(2, 3, 5, 10)):
    valid = [c for c in cells if c['outcome'] in VALID]
    rows = []
    for m in marks:
        turns = [c['first_turn_at_depth'].get(str(m)) for c in valid]
        hit = [t for t in turns if t is not None]
        rows.append({'depth': m, 'reached': len(hit) / len(valid) if valid else None,
                     'median_turn': median(hit) if hit else None})
    return rows


def analyse(exp, cells):
    """Per suite: one row per arm, with two paired comparisons.

    vs_version pairs an arm with the control specimen under the same profile;
    vs_profile pairs it with the control profile on the same specimen.
    """
    control_profile = exp.get('control_profile', exp['profiles'][0])
    by_suite = {}
    for suite in exp['suites']:
        arms = {}
        for c in cells:
            if c['suite'] == suite:
                arms.setdefault(arm_key(c), []).append(c)
        rows = []
        for specimen in exp['specimens']:
            for profile in exp['profiles']:
                arm = arms.get((specimen, profile), [])
                if not arm:
                    continue
                version_key = (exp['control'], profile)
                profile_key = (specimen, control_profile)
                # Pair only runs from the same harness and stream profile: that
                # the same seed gives the same game under another frontend is
                # not verified (pairing_class).
                same_kind = (version_key in arms and
                             pairing_class(arms[version_key][0]) == pairing_class(arm[0]))
                rows.append({
                    'specimen': specimen, 'profile': profile,
                    'summary': arm_summary(arm),
                    'vs_version': (paired(arms[version_key], arm)
                                   if specimen != exp['control'] and same_kind else None),
                    'vs_profile': (paired(arms[profile_key], arm)
                                   if profile != control_profile and profile_key in arms else None),
                    'survival': survival_table(arm, arm[0]['cap']),
                    'depths': depth_table(arm),
                    'milestones': milestone_table(arm),
                })
        by_suite[suite] = rows
    return by_suite


def by_character(exp, cells, field):
    """Deaths per class (field "class") or race (field "race") per arm.

    Uses the character actually played; arms keep the experiment's order.
    """
    key = 'played_' + field
    out = {}
    for suite in exp['suites']:
        suite_cells = [c for c in cells if c['suite'] == suite and c.get(key)]
        if not suite_cells:
            continue
        values = sorted({c[key] for c in suite_cells})
        arms = [(s, p) for s in exp['specimens'] for p in exp['profiles']]
        table = []
        for v in values:
            row = {'value': v, 'arms': []}
            for arm in arms:
                mine = [c for c in suite_cells if (c['specimen'], c['profile']) == arm and c[key] == v
                        and c['outcome'] in VALID]
                deaths = sum(1 for c in mine if c['outcome'] == 'death')
                row['arms'].append({'arm': arm, 'n': len(mine), 'deaths': deaths,
                                    'rate': deaths / len(mine) if mine else None})
            table.append(row)
        out[suite] = table
    return out
