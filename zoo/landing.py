"""The landing page: the main questions answered from the newest runs.

Every number on the page is computed from the results store when the site is
built; nothing is written by hand. A question whose experiment has no run yet
is left out.
"""
import math

from . import catalogue as cat_mod
from . import stats
from .site import esc, explain, num, pct, pval, table




def forest(rows, x_label, y_label, highlight_label=None, x_max=None):
    """Dot (rate) and whisker (95% interval) per row, as inline SVG.

    rows: (label, rate, (lo, hi), highlight). Each row is one arm, named on
    the left under y_label; the horizontal axis is the death rate, titled
    x_label. The axis ends at the next 10% above the highest interval, so the
    chart stays readable on a phone. A legend under the axis says what the
    dot, the line and a highlighted dot mean.
    """
    if x_max is None:
        top_hi = max([hi for _, rate, (lo, hi), _ in rows if hi is not None] or [0.5])
        x_max = max(0.3, math.ceil((top_hi + 0.02) * 10) / 10)
    label_w, val_w, plot_w, row_h, head = 184, 52, 244, 28, 24
    width = label_w + plot_w + val_w
    plot_bottom = head + row_h * len(rows)
    height = plot_bottom + 70
    x = lambda v: label_w + plot_w * min(max(v, 0.0), x_max) / x_max  # noqa: E731
    parts = [f'<svg class="forest" viewBox="0 0 {width} {height}" role="img" '
             f'aria-label="{esc(x_label)}, with 95% interval, for each {esc(y_label)}">',
             f'<text class="head" x="{label_w - 10}" y="16" text-anchor="end">{esc(y_label)}</text>',
             f'<text class="head" x="{width - 4}" y="16" text-anchor="end">Deaths</text>']
    for i in range(0, int(x_max * 100) + 1, 10):
        xv = x(i / 100)
        parts.append(f'<line class="axis" x1="{xv:.1f}" y1="{head}" x2="{xv:.1f}" y2="{plot_bottom}"/>')
        parts.append(f'<text class="tick" x="{xv:.1f}" y="{plot_bottom + 14}" text-anchor="middle">{i}%</text>')
    parts.append(f'<text class="head" x="{label_w + plot_w / 2:.1f}" y="{plot_bottom + 32}" '
                 f'text-anchor="middle">{esc(x_label)}</text>')
    for n, (label, rate, (lo, hi), highlight) in enumerate(rows):
        y = head + row_h * n + row_h / 2
        parts.append(f'<text x="{label_w - 10}" y="{y + 4:.1f}" text-anchor="end">{esc(label)}</text>')
        if rate is None:
            continue
        parts.append(f'<line class="ci" x1="{x(lo):.1f}" y1="{y:.1f}" x2="{x(hi):.1f}" y2="{y:.1f}"/>')
        parts.append(f'<circle class="dot{" hi" if highlight else ""}" cx="{x(rate):.1f}" cy="{y:.1f}" r="5"/>')
        parts.append(f'<text class="val" x="{width - 4}" y="{y + 4:.1f}" text-anchor="end">{pct(rate)}</text>')
    ly = plot_bottom + 56
    legend = [('<circle class="dot" cx="{0}" cy="{1}" r="5"/>', 'death rate'),
              ('<line class="ci" x1="{2}" y1="{1}" x2="{3}" y2="{1}"/>', '95% interval')]
    if highlight_label:
        legend.append(('<circle class="dot hi" cx="{0}" cy="{1}" r="5"/>', highlight_label))
    lx = 8
    for mark, text in legend:
        parts.append(mark.format(lx + 6, ly - 4, lx, lx + 14))
        parts.append(f'<text class="tick" x="{lx + 20}" y="{ly}">{esc(text)}</text>')
        lx += 34 + 6.5 * len(text)
    parts.append('</svg>')
    return '<div class="chart">' + ''.join(parts) + '</div>'


def newest(runs, names):
    for name in names:
        for meta, cells, _ in runs:
            if meta['experiment']['name'] == name:
                return meta, cells
    return None, None


def link(meta):
    return f'runs/{esc(meta["experiment"]["name"])}/{esc(meta["run_id"])}/index.html'


def suite_rows(meta, cells):
    exp = meta['experiment']
    suite = exp['suites'][0]
    return suite, meta['catalogue']['suites'][suite], stats.analyse(exp, cells)[suite]


def card_milestones(runs):
    meta, cells = newest(runs, ['classes-m6', 'classes-m5', 'milestones-wide', 'milestones-early'])
    if not meta:
        return None
    suite, s, rows = suite_rows(meta, cells)
    specs = meta['catalogue']['specimens']
    chart = forest([(f'{r["specimen"]} ({specs[r["specimen"]].get("carries", "?")} fixes)',
                     r['summary']['death_rate'], r['summary']['death_ci'], False) for r in rows],
                   x_label=f'Share of runs that died before {s["cap"]:,} engine turns',
                   y_label='Borg version (fixes carried)')
    ps = [r['vs_version']['death_p'] for r in rows if r['vs_version'] and r['vs_version']['death_p'] is not None]
    rates = [r['summary']['death_rate'] for r in rows if r['summary']['death_rate'] is not None]
    differs = [r['specimen'] for r in rows if r['vs_version'] and (r['vs_version']['death_p'] or 1) < 0.05]
    answer = ('<strong>Not measurably, in the early game.</strong> ' if not differs else
              f'<strong>{esc(", ".join(differs))} differ from the original (p &lt; 0.05).</strong> ')
    answer += (f'Deaths range {pct(min(rates))}–{pct(max(rates))} across versions'
               + (f'; the smallest paired p against the original is {pval(min(ps))}.' if ps else '.'))
    who = ('every class and race' if s['birth'] == 'assigned' else
           'a Human Warrior' if s['birth'] == 'fixed' else f'{esc(s["birth"])} birth')
    return (f'<div class="card wide"><h2>Do better-borg-c\'s fixes change early survival?</h2>'
            f'<p class="answer">{answer}</p>{chart}'
            f'<p class="foot">{len(s["seeds"]):,} seeds per version, {who}. '
            f'<a href="{link(meta)}">Full tables</a></p></div>')


def milestone_number(name, prefix):
    if prefix == 'bbc' and name == 'pristine':
        return 0
    head = f'{prefix}-m'
    rest = name[len(head):] if name.startswith(head) else ''
    return int(rest) if rest.isdigit() else None


def identity(runs, rust, twin, formerly=()):
    """Best evidence that a Rust specimen plays like its C twin: (identical, pairs, meta).

    formerly: names the Rust specimen had in older runs.
    """
    best = (0, 0, None)
    names = {rust, *formerly}
    for meta, cells, _ in runs:
        if twin not in meta['experiment']['specimens'] or not names & set(meta['experiment']['specimens']):
            continue
        play = {}
        for c in cells:
            if c['outcome'] in stats.VALID and c.get('play_sha256'):
                who = rust if c['specimen'] in names else c['specimen']
                play.setdefault((c['suite'], c['profile'], c['seed']), {})[who] = c['play_sha256']
        pairs = [v for v in play.values() if rust in v and twin in v]
        same = sum(1 for v in pairs if v[rust] == v[twin])
        if len(pairs) > best[1]:
            best = (same, len(pairs), meta)
    return best


def port_status(runs, specs):
    """One column per better-borg-c milestone: its C specimen and the borg-rs state."""
    columns = {}
    for name, s in specs.items():
        if s.get('kind', 'better-borg-c') == 'better-borg-c':
            n = milestone_number(name, 'bbc')
            if n is not None:
                columns[n] = {'n': n, 'c': name, 'carries': s.get('carries'), 'rust': None}
    for name, s in specs.items():
        n = milestone_number(name, 'rs')
        if s.get('kind') != 'borg-rs' or s.get('impl') != 'rust' or n not in columns:
            continue
        twin = next((k for k, v in specs.items() if v.get('kind') == 'borg-rs' and v.get('impl') == 'c'
                     and v['ref'] == s['ref']), None)
        same, pairs, meta = identity(runs, name, twin, s.get('formerly', ())) if twin else (0, 0, None)
        columns[n]['rust'] = {'name': name, 'twin': twin, 'same': same, 'pairs': pairs, 'meta': meta,
                              'tag': s.get('tag')}
    ported = [n for n, c in columns.items() if c['rust']]
    top = max(ported) if ported else -1
    for n, c in columns.items():
        c['state'] = ('identical' if c['rust'] and c['rust']['pairs'] and c['rust']['same'] == c['rust']['pairs']
                      else 'differs' if c['rust'] and c['rust']['pairs']
                      else 'unmeasured' if c['rust'] else 'skipped' if n < top else 'not_yet')
    return [columns[n] for n in sorted(columns)]


STATE_TEXT = {'identical': 'ported', 'differs': 'ported', 'unmeasured': 'ported',
              'skipped': 'skipped', 'not_yet': 'not yet'}


def port_diagram(cols):
    """better-borg-c milestones on top, the borg-rs Rust port below, as inline SVG."""
    lane_w, col_w, box_w, top, box_h, gap = 92, 96, 84, 22, 46, 30
    width = lane_w + col_w * len(cols)
    height = top + box_h * 2 + gap + 56
    parts = [f'<svg class="port" viewBox="0 0 {width} {height}" role="img" '
             f'aria-label="Which better-borg-c milestones the borg-rs Rust port carries">',
             f'<text class="lane" x="0" y="{top + box_h / 2 + 4}">better-borg-c</text>',
             f'<text class="lane" x="0" y="{top + box_h + gap + box_h / 2 - 3}">borg-rs</text>',
             f'<text class="lane sub" x="0" y="{top + box_h + gap + box_h / 2 + 11}">Rust port</text>']
    for i, c in enumerate(cols):
        x = lane_w + col_w * i
        cx = x + box_w / 2
        parts.append(f'<text class="head" x="{cx}" y="14" text-anchor="middle">M{c["n"]}</text>')
        parts.append(f'<rect class="c" x="{x}" y="{top}" width="{box_w}" height="{box_h}" rx="6"/>')
        parts.append(f'<text x="{cx}" y="{top + 19}" text-anchor="middle">{esc(c["c"])}</text>')
        parts.append(f'<text class="small" x="{cx}" y="{top + 35}" text-anchor="middle">'
                     f'{esc(c["carries"])} fixes</text>')
        y = top + box_h + gap
        state = c['state']
        if c['rust']:
            parts.append(f'<line class="link" x1="{cx}" y1="{top + box_h}" x2="{cx}" y2="{y}"/>')
        parts.append(f'<rect class="r {state}" x="{x}" y="{y}" width="{box_w}" height="{box_h}" rx="6"/>')
        if c['rust']:
            r = c['rust']
            parts.append(f'<text x="{cx}" y="{y + 15}" text-anchor="middle">{esc(r["name"])}</text>')
            lines = ([f'{r["same"]:,} of {r["pairs"]:,}', 'games identical'] if r['pairs'] else ['not measured'])
            for k, line in enumerate(lines):
                parts.append(f'<text class="small" x="{cx}" y="{y + 29 + 12 * k}" text-anchor="middle">{line}</text>')
        else:
            parts.append(f'<text class="small" x="{cx}" y="{y + box_h / 2 + 4}" text-anchor="middle">'
                         f'{STATE_TEXT[state]}</text>')
    ly = height - 12
    legend = [('identical', 'ported, plays like the C Borg'), ('differs', 'ported, plays differently'),
              ('skipped', 'skipped'), ('not_yet', 'not ported yet')]
    lx = 0
    for state, text in legend:
        parts.append(f'<rect class="r {state}" x="{lx}" y="{ly - 10}" width="14" height="12" rx="3"/>')
        parts.append(f'<text class="small" x="{lx + 19}" y="{ly}">{esc(text)}</text>')
        lx += 30 + 6.2 * len(text)
    parts.append('</svg>')
    return '<div class="chart">' + ''.join(parts) + '</div>'


def card_port(runs):
    specs = cat_mod.catalogue()['specimens']['specimens']
    cols = port_status(runs, specs)
    if not any(c['rust'] for c in cols):
        return None
    done = [c for c in cols if c['rust']]
    latest = done[-1]
    r = latest['rust']
    measured = [c for c in done if c['rust']['pairs']]
    evidence = ''
    if measured:
        m = measured[-1]['rust']
        evidence = (f' On {m["pairs"]:,} games, {esc(m["name"])} pressed the same keys as the C Borg of the same '
                    f'tree ({esc(m["twin"])}) in {m["same"]:,}. <a href="{link(m["meta"])}">Run</a>')
    tag = f', tag <code>{esc(r["tag"])}</code>' if r.get('tag') else ''
    return (f'<div class="card wide"><h2>How far has the Rust port got?</h2>'
            f'<p class="answer"><strong>Milestone {latest["n"]}</strong> ({esc(r["name"])}{tag}): the Rust Borg '
            f'carries better-borg-c\'s fixes up to M{latest["n"]}.{evidence}</p>{port_diagram(cols)}'
            f'<p class="foot">Each column is a better-borg-c milestone; the box below it is the borg-rs version that '
            f'carries the same fixes. "Same" counts games whose key logs are identical, key for key, between the '
            f'Rust Borg and the C Borg built in the same borg-rs tree.</p></div>')


def unfinished(runs):
    hits = []
    total = 0
    for meta, cells, _ in runs:
        total += len(cells)
        hits += [(meta, c) for c in cells if c['outcome'] not in stats.VALID]
    return hits, total


def card_stalls(runs):
    hits, total = unfinished(runs)
    leads = {(c['specimen'], c['seed']) for _, c in hits}
    return (f'<div class="card"><h2>Stalls and crashes</h2>'
            f'<p class="answer"><span class="big">{len(hits):,}</span> of {total:,} runs stopped without reaching '
            f'death or the turn cap, on {len(leads):,} version and seed pairs. Each is a lead for a liveness bug.</p>'
            f'<p><a href="stalls.html">See the list</a></p></div>')


STALL_COLS = [('Version', 'The Borg version that stopped.'),
              ('Seed', 'The seed; rerunning it reproduces the stop.'),
              ('Character', 'The race and class played.'),
              ('Outcome', 'stalled: game time stopped advancing; wall_timeout: out of real time; crash: the game '
                          'process died; harness_failure: the runner failed; config_error: the settings did not '
                          'take effect.'),
              ('Stall kind', 'A heuristic label: level_cycle (changes level without game time passing), '
                             'energy_without_time (energy rises, the clock does not), zero_energy_retry (repeats '
                             'without spending energy), no_decisions (no Borg decisions seen at the frozen turn), '
                             'keys_without_time (borgh: keys sent while the turn stays frozen), no_states (no state record, '
                             'as when the runner itself failed).'),
              ('Last turn', 'The engine turn at which the run stopped advancing, in the first run listed.'),
              ('Profiles', 'The settings profiles under which this version stopped on this seed.'),
              ('Most repeated note', 'The Borg note, or key, repeated most often at the frozen turn.'),
              ('Experiments', 'Where it happened; each run page has the counters.')]


def stalls_page(runs):
    from collections import Counter
    hits, total = unfinished(runs)
    groups = {}
    for m, c in hits:
        groups.setdefault((c['specimen'], c['seed'], c['outcome']), []).append((m, c))
    rows = []
    for (specimen, seed, outcome), g in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        st = [c.get('stall') or {} for _, c in g]
        notes = Counter(t for s in st for t, _ in (s.get('top_notes_at_last_turn') or s.get('top_keys_at_last_turn')
                                                   or [])[:1])
        c0 = g[0][1]
        char = (' '.join(x for x in (c0.get('played_race'), c0.get('played_class')) if x)
                or (c0.get('character') or '').split(';')[0])
        rows.append([esc(specimen), seed, esc(char or '–'), esc(outcome),
                     esc(', '.join(sorted({s.get('kind') for s in st} - {None})) or '–'),
                     num(st[0].get('last_turn', g[0][1]['final'].get('turn'))),
                     esc(', '.join(sorted({c['profile'] for _, c in g}))),
                     esc(notes.most_common(1)[0][0][:60]) if notes else '–',
                     ', '.join(f'<a href="{link(m)}">{esc(m["experiment"]["name"])}</a>'
                               for m in {m['experiment']['name']: m for m, _ in g}.values())])
    by_outcome = Counter(c['outcome'] for _, c in hits)
    by_kind = Counter((c.get('stall') or {}).get('kind') or '–' for _, c in hits)
    summary = table(['Outcome', 'Runs'], [[esc(k), f'{v:,}'] for k, v in by_outcome.most_common()]) + \
        table(['Stall kind', 'Runs'], [[esc(k), f'{v:,}'] for k, v in by_kind.most_common()])
    body = (f'<p><a href="index.html">Borg zoo</a></p><h1>Stalls and crashes</h1>'
            f'<p class="lead">{len(hits):,} of {total:,} runs stopped without reaching death or the turn cap. They '
            f'are left out of every death rate and listed here, because each one is a lead for a liveness bug: '
            f'seed 1045\'s munchkin stair cycle became '
            f'<a href="https://github.com/diegoami/neo-angband-tracker/issues/403">neo-angband-tracker#403</a>.</p>'
            f'<h2>By outcome and kind</h2><div class="pair">{summary}</div>'
            f'<h2>Every version and seed</h2>'
            + explain('One row per version, seed and outcome, most repeated first. A seed that stopped under several '
                      'profiles or in several experiments appears once, with all of them listed.', STALL_COLS)
            + (table(STALL_COLS, rows, left=5) if rows else '<p class="muted">None.</p>'))
    return body


def versions_table():
    cat = cat_mod.catalogue()
    specs = cat['specimens']['specimens']
    rows = []
    for name, s in specs.items():
        repo = s['repository']
        rows.append([esc(name),
                     f'<a href="https://github.com/{esc(repo)}/commit/{esc(s["ref"])}"><code>{esc(s["ref"][:10])}</code></a>',
                     esc(s.get('kind', 'better-borg-c') + (' · ' + s['impl'] if s.get('impl') else '')),
                     esc(s.get('carries', '–')), esc(s.get('label', ''))])
    cols = [('Version', 'The name used in every table.'),
            ('Commit', 'The commit that is built and run.'),
            ('Harness', 'How it is run: better-borg-c (the game with better-borg-c\'s observer), or borg-rs '
                        '(borg-rs\'s headless borgh frontend) with its C or Rust Borg.'),
            ('Fixes', 'How many fixes from the tracker the version carries; 0 is the original Borg.'),
            ('What it is', 'A short description.')]
    return (explain('Every Borg version the zoo can run. Runs are paired only between versions with the same '
                    'harness.', cols) + table(cols, rows, left=5))


def versions_page():
    return f'<p><a href="index.html">Borg zoo</a></p><h1>Versions</h1>{versions_table()}'


RUN_COLS = [('Experiment', 'The question being asked; the link opens its tables.'),
            ('Completed', 'When the run finished (UTC).'),
            ('Versions', 'How many Borg versions it compares.'),
            ('Profiles', 'How many settings profiles it compares.'),
            ('Runs', 'Games played: versions × profiles × seeds.'),
            ('Finished', 'Games that reached an endpoint (death or the turn cap); the rest stalled, timed out '
                         'or failed.')]


def landing_page(runs, run_rows):
    total = sum(len(c) for _, c, _ in runs)
    latest = runs[0][0].get('completed', '?') if runs else '–'
    cards = [c for c in (card_milestones(runs), card_port(runs), card_stalls(runs)) if c]
    return (
        f'<h1>Borg zoo</h1>'
        f'<p class="muted">{total:,} runs · {len(runs)} experiment runs · latest {esc(latest)}</p>'
        f'<p class="lead">Angband Borg versions played headless on the same seeds: the original C Borg, '
        f'better-borg-c\'s milestones of carried fixes, and the borg-rs Rust port.</p>'
        f'<div class="cards">{"".join(cards)}</div>'
        f'<h2>Experiment runs</h2>'
        + (explain('Every recorded run, newest first. Each page explains its tables.', RUN_COLS)
           + table(RUN_COLS, run_rows) if run_rows else '<p class="muted">No results yet.</p>') +
        f'<p class="muted"><a href="versions.html">Versions</a> · <a href="stalls.html">Stalls and crashes</a> · '
        f'<a href="https://github.com/diegoami/borg-zoo/blob/main/docs/DESIGN.md">Method</a> · '
        f'<a href="https://github.com/diegoami/borg-zoo/tree/results">Raw results</a> · '
        f'<a href="https://github.com/diegoami/borg-zoo">Source</a></p>')
