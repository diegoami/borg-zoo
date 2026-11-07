"""Per-arm summaries and paired comparisons over one experiment run.

Everything here is descriptive. Small suites give wide intervals; the site
says so next to every table.
"""
import math
from statistics import median

VALID = ('death', 'turn_cap', 'completion')
OUTCOMES = ('death', 'turn_cap', 'completion', 'stalled', 'wall_timeout', 'crash',
            'harness_failure', 'config_error')
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


def same_play(a, b):
    """Identical play: equal play hashes (configuration lines excluded) when
    both runs have one, else equal full-trace hashes. Runs recorded before
    the play hash existed only match under the same configuration."""
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
        if not k:
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
                # Pair only runs from the same harness: that the same seed gives
                # the same game under another frontend is not verified.
                same_kind = (version_key in arms and
                             arms[version_key][0].get('harness_kind', 'better-borg-c') ==
                             arm[0].get('harness_kind', 'better-borg-c'))
                rows.append({
                    'specimen': specimen, 'profile': profile,
                    'summary': arm_summary(arm),
                    'vs_version': (paired(arms[version_key], arm)
                                   if specimen != exp['control'] and same_kind else None),
                    'vs_profile': (paired(arms[profile_key], arm)
                                   if profile != control_profile and profile_key in arms else None),
                    'survival': survival_table(arm, arm[0]['cap']),
                    'depths': depth_table(arm),
                })
        by_suite[suite] = rows
    return by_suite
