"""What the zoo has already tried: one compact digest of every experiment run.

  python3 -m zoo.history --results RESULTS [--json OUT] [--match TEXT] [--since YYYY-MM-DD] [--pool]

For each experiment run (single-arm runs of one tag merged, as on the site):
its question, issue, tier (suite), specimens, and per arm the settings that
differ from the control arm, deaths / finished, mean final level, mean
deepest level, unfinished cells, and the pairing against the control
(rescued, newly killed, exact McNemar p, identical plays). Read only; the
next-experiments skill (.claude/skills/next-experiments) reasons over it.

--pool reads the tiers of one study as one (RULES 14: "each is analysed on
everything collected so far"): runs with exactly the same specimens, profiles
and control, over disjoint starts, are merged into one entry listing every
run. Runs that share a start are never merged (a repeat is not a new game),
and a pilot stays on its own.

Descriptive only (RULES 14): a development-suite difference is a lead for
the next tier, never a claim.
"""
import argparse
import json
import sys
from statistics import mean

from . import stats
from .briefs import question
from .site import load_runs


def settings_of(meta, profile):
    return (meta['catalogue'].get('profiles', {}).get(profile) or {}).get('settings', {})


def differs(meta, profile, control):
    """The settings this arm writes differently from the control arm."""
    own, base = settings_of(meta, profile), settings_of(meta, control)
    keys = sorted(set(own) | set(base))
    return {k: own.get(k, '(unset)') for k in keys if own.get(k) != base.get(k)}


def arm_row(meta, cells, specimen, profile, control_key, by_arm):
    arm = by_arm.get((specimen, profile), [])
    s = stats.arm_summary(arm)
    valid = [c for c in arm if c['outcome'] in stats.VALID]
    row = {
        'specimen': specimen, 'profile': profile,
        'differs_from_control': differs(meta, profile, control_key[1]),
        'cells': s['cells'], 'finished': s['valid'], 'unfinished': s['cells'] - s['valid'],
        'deaths': s['deaths'],
        'mean_level': round(mean(c['final'].get('max_level') or 0 for c in valid), 2) if valid else None,
        'mean_depth': round(mean(c['final'].get('max_depth') or 0 for c in valid), 2) if valid else None,
    }
    if (specimen, profile) != control_key and control_key in by_arm:
        p = stats.paired(by_arm[control_key], arm)
        row['vs_control'] = {k: p[k] for k in ('pairs', 'rescued', 'newly_killed', 'identical_traces', 'death_p')}
    return row


def is_pilot(meta):
    """A pilot run (pilot-role suites, or "pilot": true): read on its own, never pooled with tiers."""
    exp = meta['experiment']
    roles = {(meta['catalogue'].get('suites', {}).get(x) or {}).get('role') for x in exp['suites']}
    return bool(exp.get('pilot')) or roles == {'pilot'} or exp['suites'] == ['classes-18']


def study_key(meta):
    """What makes runs tiers of one study: the same specimens, profiles and control, both non-pilot."""
    exp = meta['experiment']
    return (tuple(sorted(exp['specimens'])), tuple(sorted(exp['profiles'])),
            exp.get('control') or exp['specimens'][0], exp.get('control_profile') or exp['profiles'][0],
            is_pilot(meta))


def starts(cells):
    return {(c['specimen'], c['profile'], c['suite'], c['seed']) for c in cells}


def pool_runs(runs):
    """Merge runs of one study over disjoint starts; (meta, cells, None, [run names]) per study."""
    groups = []
    for meta, cells, extra in sorted(runs, key=lambda r: r[0].get('completed', '')):
        key = study_key(meta)
        for g in groups:
            if g['key'] == key and not key[-1] and not (starts(cells) & g['starts']):
                g['cells'] += cells
                g['starts'] |= starts(cells)
                g['names'].append(meta['experiment']['name'])
                g['suites'] += [x for x in meta['experiment']['suites'] if x not in g['suites']]
                g['completed'] = max(g['completed'], meta.get('completed', ''))
                break
        else:
            groups.append({'key': key, 'meta': meta, 'cells': list(cells), 'starts': starts(cells),
                           'names': [meta['experiment']['name']], 'suites': list(meta['experiment']['suites']),
                           'completed': meta.get('completed', '')})
    out = []
    for g in groups:
        meta = dict(g['meta'], completed=g['completed'])
        meta['experiment'] = dict(g['meta']['experiment'], suites=g['suites'],
                                  name=' + '.join(g['names']))
        out.append((meta, g['cells'], None))
    return out


def digest(runs, match=None, since=None, pool=False):
    out = []
    if pool:
        runs = pool_runs(runs)
    for meta, cells, _ in runs:
        exp = meta['experiment']
        completed = meta.get('completed', '')
        if since and completed[:10] < since:
            continue
        text = json.dumps(exp)
        if match and match.lower() not in text.lower():
            continue
        by_arm = {}
        for c in cells:
            by_arm.setdefault((c['specimen'], c['profile']), []).append(c)
        control_key = (exp.get('control') or exp['specimens'][0], exp.get('control_profile') or exp['profiles'][0])
        arms = [arm_row(meta, cells, s, p, control_key, by_arm)
                for s in exp['specimens'] for p in exp['profiles'] if (s, p) in by_arm]
        specs = meta['catalogue'].get('specimens', {})
        out.append({
            'experiment': exp['name'], 'question': question(exp), 'issue': exp.get('issue'),
            'completed': completed, 'suites': exp['suites'],
            'specimens': {n: {'repository': specs.get(n, {}).get('repository'), 'ref': specs.get(n, {}).get('ref'),
                              'kind': specs.get(n, {}).get('kind')} for n in exp['specimens']},
            'control': list(control_key), 'arms': arms,
            'prespecified': exp.get('prespecified', ''),
        })
    return out


def markdown(entries):
    lines = []
    for e in entries:
        lines.append(f"## {e['experiment']} ({e['completed'][:10]}, {', '.join(e['suites'])}"
                     + (f", issue #{e['issue']}" if e.get('issue') else '') + ')')
        lines.append(f"{e['question']}")
        refs = ', '.join(f"{n} = {v['repository']}@{(v['ref'] or '?')[:8]}" for n, v in e['specimens'].items())
        lines.append(f"Specimens: {refs}. Control: {e['control'][1]} on {e['control'][0]}.")
        lines.append('')
        lines.append('| arm | differs from control | deaths/finished | unfinished | mean CL | mean depth | rescued/newly killed (p) | identical plays |')
        lines.append('|---|---|---:|---:|---:|---:|---|---:|')
        for a in e['arms']:
            d = ', '.join(f'{k}={v}' for k, v in a['differs_from_control'].items()) or '(control)'
            v = a.get('vs_control')
            pair = (f"{v['rescued']}/{v['newly_killed']} (p {v['death_p']:.2g})" if v and v['death_p'] is not None
                    else f"{v['rescued']}/{v['newly_killed']}" if v else '–')
            lines.append(f"| {a['specimen']}:{a['profile']} | {d} | {a['deaths']}/{a['finished']} | {a['unfinished']} | "
                         f"{a['mean_level']} | {a['mean_depth']} | {pair} | {v['identical_traces'] if v else '–'} |")
        lines.append('')
    return '\n'.join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--results', required=True, help='the results directory (results branch: results/)')
    ap.add_argument('--json', help='also write the digest as JSON here')
    ap.add_argument('--match', help='only experiments whose definition mentions this text (a setting, issue, specimen)')
    ap.add_argument('--since', help='only runs completed on or after YYYY-MM-DD')
    ap.add_argument('--pool', action='store_true',
                    help='read the tiers of one study (same specimens, profiles, control; disjoint starts) as one')
    a = ap.parse_args(argv)
    entries = digest(load_runs(a.results), a.match, a.since, a.pool)
    if a.json:
        with open(a.json, 'w') as f:
            json.dump(entries, f, indent=1)
    sys.stdout.write(markdown(entries) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
