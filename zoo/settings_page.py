"""The Settings tab: every borg.txt setting an experiment varied, and per
setting the experiments that tested it.

A setting is "tested" by an experiment when its value differs between that
experiment's profiles of one Borg version (a profile that does not write it
uses the build's own value, shown as "build default"). For each such
experiment the setting's page shows the question, the build, the size, deaths
per arm with Wilson 95% intervals, the paired comparison with the control arm
(exact McNemar on the starts where only one of the two died) and a verdict:

- clear difference: an arm differs from the control at p < 0.05 after a
  Bonferroni correction for the number of arms compared;
- suggestive: p < 0.05 for some arm, but not after the correction;
- no difference found: no arm reaches p < 0.05 with at least 270 starts per
  arm (the medium tier and up);
- too small to tell: no arm reaches p < 0.05 with fewer starts than that.

The verdict is about deaths only, the zoo's primary endpoint. Smoke checks
are left out.
"""
import re

from . import catalogue as cat_mod
from . import stats
from .briefs import question
from .site import esc, pval, table, explain

MEDIUM = 270
VERDICTS = ['clear difference', 'suggestive', 'no difference found', 'too small to tell']
VERDICT_NOTE = {
    'clear difference': 'An arm differs from the control in deaths, p < 0.05 after correcting for the number of arms.',
    'suggestive': 'p < 0.05 for an arm, but not after correcting for the number of arms: could be chance.',
    'no difference found': f'No arm differs from the control at p < 0.05, with at least {MEDIUM} starts per arm.',
    'too small to tell': f'No arm differs from the control at p < 0.05, but with fewer than {MEDIUM} starts per arm '
                         'only a large effect could have shown.',
}
TIERS = [('-verysmall', 'verysmall'), ('-small-rest', 'small (rest)'), ('-small', 'small'),
         ('-medium', 'medium'), ('-big', 'big'), ('-full', 'full')]


def slug(key):
    return re.sub(r'[^a-z0-9_]+', '-', key.lower()).strip('-')


def tier(suites):
    names = []
    for suite in suites:
        if suite == 'classes-18':
            names.append('pilot')
        elif suite == 'classes-1800':
            names.append('all 1,800 starts')
        else:
            names.append(next((name for mark, name in TIERS if mark in suite), suite))
    return ', '.join(names)


def fmt(value):
    return 'build default' if value is None else str(value)


def varied(meta, profiles):
    settings = {p: (meta['catalogue'].get('profiles', {}).get(p) or {}).get('settings', {}) for p in profiles}
    keys = sorted({k for s in settings.values() for k in s})
    return settings, [k for k in keys if len({repr(s.get(k)) for s in settings.values()}) > 1]


def analyse(row):
    """Deaths per arm, pairing with the control and the verdict, over row['arm_cells']."""
    arms = []
    for p, cells in row['arm_cells'].items():
        valid = [c for c in cells if c['outcome'] in stats.VALID]
        deaths = sum(c['outcome'] == 'death' for c in valid)
        pair = stats.paired(row['arm_cells'][row['control']], cells) if p != row['control'] else None
        arms.append({'profile': p, 'n': len(valid), 'deaths': deaths, 'ci': stats.wilson(deaths, len(valid)),
                     'paired': pair, 'values': row['values'][p]})
    ps = [a['paired']['death_p'] for a in arms if a['paired'] and a['paired']['death_p'] is not None]
    n = min(a['n'] for a in arms)
    k = max(1, len(arms) - 1)
    if any(p * k < 0.05 for p in ps):
        verdict = 'clear difference'
    elif any(p < 0.05 for p in ps):
        verdict = 'suggestive'
    elif n >= MEDIUM:
        verdict = 'no difference found'
    else:
        verdict = 'too small to tell'
    return {**row, 'arms': arms, 'n': n, 'verdict': verdict}


def experiment_tests(meta, cells):
    """One row per specimen of a run whose profiles vary at least one setting."""
    exp = meta['experiment']
    control = exp.get('control_profile') or exp['profiles'][0]
    out = []
    for specimen in exp['specimens']:
        profiles = [p for p in exp['profiles'] if any(c['specimen'] == specimen and c['profile'] == p for c in cells)]
        if len(profiles) < 2:
            continue
        settings, keys = varied(meta, profiles)
        if not keys:
            continue
        out.append({'metas': [meta], 'specimen': specimen, 'keys': keys,
                    'control': control if control in profiles else profiles[0],
                    'arm_cells': {p: [c for c in cells if c['specimen'] == specimen and c['profile'] == p]
                                  for p in profiles},
                    'values': {p: {k: settings[p].get(k) for k in keys} for p in profiles},
                    'tier': tier(sorted({c['suite'] for c in cells}))})
    return out


def study_key(row):
    """Tiers of one study share the build, the arms and their values."""
    return (row['specimen'], row['control'], tuple(sorted((p, repr(sorted(v.items()))) for p, v in row['values'].items())))


def pooled(rows):
    """The tiers of one study as one row: every start once (newest run wins)."""
    rows = sorted(rows, key=lambda r: r['metas'][0].get('completed', ''))
    arm_cells = {}
    for r in rows:
        for p, cells in r['arm_cells'].items():
            arm_cells.setdefault(p, {}).update({cat_mod.cell_key(c): c for c in cells})
    return {**rows[-1], 'metas': [m for r in reversed(rows) for m in r['metas']],
            'arm_cells': {p: list(c.values()) for p, c in arm_cells.items()},
            'tier': f'{len(rows)} runs pooled ({", ".join(r["tier"] for r in rows)})'}


def collect(runs):
    """{setting: [study]}, a study being {'pooled': row or None, 'runs': [row]}, newest first."""
    smoke = cat_mod.smoke_names()
    studies = {}
    for meta, cells, _ in runs:
        if meta['experiment']['name'] in smoke:
            continue
        for row in experiment_tests(meta, cells):
            studies.setdefault(study_key(row), []).append(row)
    found = {}
    for rows in studies.values():
        rows.sort(key=lambda r: r['metas'][0].get('completed', ''), reverse=True)
        study = {'pooled': analyse(pooled(rows)) if len(rows) > 1 else None,
                 'runs': [analyse(r) for r in rows]}
        for r in study['runs']:
            r.pop('arm_cells')
        if study['pooled']:
            study['pooled'].pop('arm_cells')
        for key in rows[0]['keys']:
            found.setdefault(key, []).append(study)
    for studies_of in found.values():
        studies_of.sort(key=lambda s: s['runs'][0]['metas'][0].get('completed', ''), reverse=True)
    return found


def head_row(study):
    return study['pooled'] or study['runs'][0]


def run_link(meta, base):
    return f'{base}runs/{esc(meta["experiment"]["name"])}/{esc(meta["run_id"])}/index.html'


def best(studies):
    """The setting's strongest result: the best verdict, at the largest size."""
    return min((head_row(s) for s in studies), key=lambda r: (VERDICTS.index(r['verdict']), -r['n']))


INDEX_COLS = [('Setting', 'The exact borg.txt key; the link lists every experiment that varied it.'),
              ('Studies', 'Separate studies that varied it; the tiers of one study (pilot, small, medium...) '
                          'count once.'),
              ('Runs', 'Experiment runs, every tier counted.'),
              ('Largest test', 'The most starts per arm in one study, its tiers pooled.'),
              ('Strongest result', 'The best-supported verdict on deaths among those studies; see the legend.'),
              ('Last tested', 'When the newest of those runs finished (UTC).')]


def index_page(found):
    from .landing import nav
    rows = []
    for key in sorted(found):
        studies = found[key]
        b = best(studies)
        rows.append([f'<a href="{slug(key)}.html"><code>{esc(key)}</code></a>', len(studies),
                     sum(len(s['runs']) for s in studies),
                     f'{max(head_row(s)["n"] for s in studies):,}',
                     f'{esc(b["verdict"])} ({b["n"]:,} per arm)',
                     esc(max(s['runs'][0]['metas'][0].get('completed', '') for s in studies)[:10])])
    legend = ''.join(f'<li><strong>{esc(v)}</strong>: {esc(VERDICT_NOTE[v])}</li>' for v in VERDICTS)
    return (f'<h1>Borg zoo</h1>{nav("settings/index.html", "../")}'
            '<h2>Settings tested</h2>'
            + explain('Every borg.txt setting that took more than one value between the arms of an experiment, '
                      'pilots included. Each link lists those experiments with their build, size, deaths per arm '
                      'and how certain the result is. Verdicts are about deaths only.', INDEX_COLS)
            + f'<ul>{legend}</ul>'
            + (table(INDEX_COLS, rows) if rows else '<p class="muted">No settings tested yet.</p>'))


def result_table(key, row):
    others = [k for k in row['keys'] if k != key]
    cols = [('Arm', 'The profile; (control) marks the arm the others are paired with.'),
            (key, 'The value of this setting in the arm.')] + [(k, 'Also varied in this experiment.') for k in others] + [
        ('Deaths', 'Deaths among finished games.'), ('Death rate (95%)', 'With its Wilson 95% interval.'),
        ('Only control died', 'Starts where the control died and this arm lived.'),
        ('Only this arm died', 'Starts where this arm died and the control lived.'),
        ('p', 'Exact McNemar test on those two counts.')]
    body = []
    for a in row['arms']:
        lo, hi = a['ci']
        rate = f'{100 * a["deaths"] / a["n"]:.1f}% ({100 * lo:.1f}–{100 * hi:.1f}%)' if a['n'] else '–'
        pr = a['paired']
        body.append([esc(a['profile']) + (' (control)' if a['profile'] == row['control'] else ''),
                     f'<code>{esc(fmt(a["values"][key]))}</code>',
                     *[f'<code>{esc(fmt(a["values"][k]))}</code>' for k in others],
                     f'{a["deaths"]}/{a["n"]}', rate,
                     pr['rescued'] if pr else '–', pr['newly_killed'] if pr else '–', esc(pval(pr['death_p'])) if pr else '–'])
    verdict = (f'<p><strong>{esc(row["verdict"][:1].upper() + row["verdict"][1:])}</strong> '
               f'({row["n"]:,} starts per arm, {len(row["arms"])} arms). {esc(VERDICT_NOTE[row["verdict"]])}</p>')
    return verdict + table(cols, body)


def run_line(row):
    meta = row['metas'][0]
    return (f'<a href="{run_link(meta, "../")}">{esc(meta["experiment"]["name"])}</a> · '
            f'{esc(row["tier"])} · {esc(meta.get("completed", "?"))}')


def study_block(key, study):
    head = head_row(study)
    meta = study['runs'][0]['metas'][0]
    exp = meta['experiment']
    issue = cat_mod.issue_of(exp)
    spec = meta['catalogue'].get('specimens', {}).get(head['specimen'], {})
    title = exp['name'] if not study['pooled'] else re.sub(r'-(pilot|verysmall|small-rest|small|medium|big|full|1800)$', '', exp['name'])
    parts = [f'<h3>{esc(title)}</h3>', f'<p>{esc(question(exp))}</p>',
             f'<p class="muted">'
             + (f'<a href="{cat_mod.ISSUES_URL}{issue}">#{issue}</a> · ' if issue else '')
             + f'build {esc(head["specimen"])} (<code>{esc(spec.get("ref", "?")[:8])}</code>) · '
             + (f'{esc(head["tier"])}' if study['pooled'] else run_line(head)) + '</p>']
    parts.append(result_table(key, head))
    if study['pooled']:
        parts.append('<details><summary>Each run on its own</summary>'
                     + ''.join(f'<p class="muted">{run_line(r)}</p>' + result_table(key, r) for r in study['runs'])
                     + '</details>')
    return ''.join(parts)


def setting_page(key, studies):
    from .landing import nav
    heads = [head_row(s) for s in studies]
    counts = {v: sum(r['verdict'] == v for r in heads) for v in VERDICTS}
    summary = ', '.join(f'{n} {v}' for v, n in counts.items() if n)
    runs = sum(len(s['runs']) for s in studies)
    return (f'<h1>Borg zoo</h1>{nav("settings/index.html", "../")}'
            f'<p><a href="index.html">All settings</a></p>'
            f'<h2><code>{esc(key)}</code></h2>'
            f'<p>Varied in {len(studies)} stud{"ies" if len(studies) != 1 else "y"} ({runs} run{"s" if runs != 1 else ""}), '
            f'newest first: {esc(summary)}. A study run in tiers (pilot, small, medium...) is shown pooled, every '
            f'start counted once, with each run below it. Results on different builds are not interchangeable: '
            f'a later build may play differently.</p>'
            + ''.join(study_block(key, s) for s in studies))


def build(runs, out, page):
    found = collect(runs)
    target = out / 'settings'
    target.mkdir(exist_ok=True)
    (target / 'index.html').write_text(page('Settings tested · borg-zoo', index_page(found), base='../'))
    for key, studies in found.items():
        (target / f'{slug(key)}.html').write_text(page(f'{key} · borg-zoo', setting_page(key, studies), base='../'))
    return len(found)
