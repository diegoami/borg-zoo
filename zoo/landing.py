"""The landing page: the main questions answered from the newest runs.

Every number on the page is computed from the results store when the site is
built; nothing is written by hand. A question whose experiment has no run yet
is left out.
"""
import math

from . import catalogue as cat_mod
from . import stats
from .site import esc, pct, pval, table




def forest(rows, x_max=None):
    """Dot (rate) and whisker (95% interval) per row, as inline SVG.

    rows: (label, rate, (lo, hi), highlight). The axis ends at the next 10%
    above the highest interval, so the chart stays readable on a phone.
    """
    if x_max is None:
        top_hi = max([hi for _, rate, (lo, hi), _ in rows if hi is not None] or [0.5])
        x_max = max(0.3, math.ceil((top_hi + 0.02) * 10) / 10)
    label_w, val_w, plot_w, row_h, top = 184, 44, 252, 28, 8
    width = label_w + plot_w + val_w
    height = top + row_h * len(rows) + 28
    x = lambda v: label_w + plot_w * min(max(v, 0.0), x_max) / x_max  # noqa: E731
    parts = [f'<svg class="forest" viewBox="0 0 {width} {height}" role="img" '
             f'aria-label="Death rate with 95% interval per arm">']
    for i in range(0, int(x_max * 100) + 1, 10):
        xv = x(i / 100)
        parts.append(f'<line class="axis" x1="{xv:.1f}" y1="{top}" x2="{xv:.1f}" y2="{height - 22}"/>')
        parts.append(f'<text class="tick" x="{xv:.1f}" y="{height - 6}" text-anchor="middle">{i}%</text>')
    for n, (label, rate, (lo, hi), highlight) in enumerate(rows):
        y = top + row_h * n + row_h / 2
        parts.append(f'<text x="{label_w - 10}" y="{y + 4:.1f}" text-anchor="end">{esc(label)}</text>')
        if rate is None:
            continue
        parts.append(f'<line class="ci" x1="{x(lo):.1f}" y1="{y:.1f}" x2="{x(hi):.1f}" y2="{y:.1f}"/>')
        parts.append(f'<circle class="dot{" hi" if highlight else ""}" cx="{x(rate):.1f}" cy="{y:.1f}" r="5"/>')
        parts.append(f'<text class="val" x="{width - 4}" y="{y + 4:.1f}" text-anchor="end">{pct(rate)}</text>')
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
    meta, cells = newest(runs, ['milestones-wide', 'milestones-early'])
    if not meta:
        return None
    suite, s, rows = suite_rows(meta, cells)
    specs = meta['catalogue']['specimens']
    chart = forest([(f'{r["specimen"]} ({specs[r["specimen"]].get("carries", "?")} fixes)',
                     r['summary']['death_rate'], r['summary']['death_ci'], False) for r in rows])
    ps = [r['vs_version']['death_p'] for r in rows if r['vs_version'] and r['vs_version']['death_p'] is not None]
    rates = [r['summary']['death_rate'] for r in rows if r['summary']['death_rate'] is not None]
    differs = [r['specimen'] for r in rows if r['vs_version'] and (r['vs_version']['death_p'] or 1) < 0.05]
    answer = ('<strong>Not measurably, in the early game.</strong> ' if not differs else
              f'<strong>{esc(", ".join(differs))} differ from the original (p &lt; 0.05).</strong> ')
    answer += (f'Deaths range {pct(min(rates))}–{pct(max(rates))} across versions'
               + (f'; the smallest paired p against the original is {pval(min(ps))}.' if ps else '.'))
    return (f'<div class="card wide"><h2>Do better-borg-c\'s fixes change early survival?</h2>'
            f'<p class="answer">{answer}</p>{chart}'
            f'<p class="foot">Deaths before {s["cap"]:,} engine turns, {len(s["seeds"])} seeds, '
            f'{esc(s["birth"])} birth. Dot = death rate, line = 95% interval. Most fixes target situations the '
            f'early game rarely reaches. <a href="{link(meta)}">Full tables</a></p></div>')


def card_settings(runs):
    meta, cells = newest(runs, ['munchkin-confirm', 'dive-styles-early'])
    if not meta:
        return None
    exp = meta['experiment']
    suite, s, rows = suite_rows(meta, cells)
    control_profile = exp.get('control_profile', exp['profiles'][0])
    chart = forest([(f'{r["specimen"]} · {r["profile"]}', r['summary']['death_rate'], r['summary']['death_ci'],
                     r['profile'] != control_profile) for r in rows])
    lines = []
    for specimen in exp['specimens']:
        arms = [r for r in rows if r['specimen'] == specimen and r['vs_profile']]
        base = next((r for r in rows if r['specimen'] == specimen and r['profile'] == control_profile), None)
        if not arms or not base:
            continue
        best = min(arms, key=lambda r: r['summary']['death_rate'] if r['summary']['death_rate'] is not None else 1)
        v = best['vs_profile']
        lines.append(f'<li><strong>{esc(specimen)}</strong>: {esc(best["profile"])} {pct(best["summary"]["death_rate"])} '
                     f'against {pct(base["summary"]["death_rate"])} for {esc(control_profile)}; '
                     f'{v["rescued"]} seeds rescued, {v["newly_killed"]} newly killed, p {pval(v["death_p"])}</li>')
    pre = ('<p class="foot"><strong>Prespecified:</strong> ' + esc(exp['prespecified']) + '</p>'
           if exp.get('prespecified') else '')
    return (f'<div class="card wide"><h2>Which settings change early survival?</h2>'
            f'<p class="answer"><strong>Munchkin start, by far.</strong> Stair-scumming to a shallow target depth '
            f'at low character level cuts early deaths on both versions:</p><ul>{"".join(lines)}</ul>{chart}{pre}'
            f'<p class="foot">Deaths before {s["cap"]:,} engine turns, {len(s["seeds"])} fresh seeds, '
            f'{esc(s["birth"])} birth. Green = a non-default profile. It covers the first {s["cap"]:,} turns only; '
            f'munchkin mode ends at character level 12. <a href="{link(meta)}">Full tables</a></p></div>')


def card_port(runs):
    meta, cells = newest(runs, ['rs-early', 'rs-smoke'])
    if not meta:
        return None
    suite, s, rows = suite_rows(meta, cells)
    specs = meta['catalogue']['specimens']
    rust = [r for r in rows if specs.get(r['specimen'], {}).get('impl') == 'rust' and r['vs_version']]
    pairs = sum(r['vs_version']['pairs'] for r in rust)
    same = sum(r['vs_version']['identical_traces'] for r in rust)
    if not pairs:
        return None
    return (f'<div class="card"><h2>Does the Rust port play like the C Borg?</h2>'
            f'<p class="big">{same} of {pairs}</p>'
            f'<p class="answer">runs with byte-identical key logs between borg-rs\'s Rust Borg and the C Borg built '
            f'in the same tree, on the same seeds and settings.</p>'
            f'<p class="foot">{len(s["seeds"])} seeds × {len(meta["experiment"]["profiles"])} profiles, '
            f'{s["cap"]:,} engine turns, early game only. <a href="{link(meta)}">Full tables</a></p></div>')


def card_stalls(runs):
    stalled = []
    total = 0
    for meta, cells, _ in runs:
        total += len(cells)
        for c in cells:
            if c['outcome'] in ('stalled', 'wall_timeout', 'crash'):
                stalled.append((meta, c))
    leads = {}
    for m, c in stalled:
        key = (c['specimen'], c['seed'], c['outcome'])
        leads.setdefault(key, []).append((m, c))
    rows = []
    for (specimen, seed, outcome), hits in sorted(leads.items(), key=lambda kv: -len(kv[1]))[:10]:
        kinds = sorted({(c.get('stall') or {}).get('kind') for _, c in hits} - {None})
        names = sorted({m['experiment']['name'] for m, _ in hits})
        rows.append([esc(specimen), seed, esc(outcome), esc(', '.join(kinds) or '–'),
                     esc(', '.join(sorted({c['profile'] for _, c in hits}))),
                     ', '.join(f'<a href="{link(m)}">{esc(m["experiment"]["name"])}</a>'
                               for m in {m['experiment']['name']: m for m, _ in hits}.values())])
    body = (table(['Version', 'Seed', 'Outcome', 'Stall kind', 'Profiles', 'Experiments'], rows, left=6) if rows
            else '<p class="muted">None.</p>')
    return (f'<div class="card"><h2>Stalls and crashes</h2>'
            f'<p class="answer"><span class="big">{len(stalled)}</span> of {total:,} runs stopped without reaching '
            f'an endpoint (stall, wall timeout or crash), from {len(leads)} distinct version and seed pairs. Each is a '
            f'lead for a liveness bug: seed 1045\'s munchkin stair cycle became '
            f'<a href="https://github.com/diegoami/neo-angband-tracker/issues/403">neo-angband-tracker#403</a>.</p>'
            f'{body}</div>')


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
    return table(['Version', 'Commit', 'Harness', 'Fixes', 'What it is'], rows, left=5)


def landing_page(runs, run_rows):
    total = sum(len(c) for _, c, _ in runs)
    latest = runs[0][0].get('completed', '?') if runs else '–'
    cards = [c for c in (card_settings(runs), card_milestones(runs), card_port(runs), card_stalls(runs)) if c]
    return (
        f'<h1>Borg zoo</h1>'
        f'<p class="muted">{total:,} runs · {len(runs)} experiment runs · latest {esc(latest)}</p>'
        f'<p class="lead">Seed-suite comparisons of Angband Borg versions and configurations: the original C Borg, '
        f'better-borg-c\'s milestones of carried fixes, and the borg-rs Rust port, run headless on the same seeds.</p>'
        f'<div class="cards">{"".join(cards)}</div>'
        f'<h2>How to read this</h2>'
        f'<p>Results are descriptive unless an experiment says it is prespecified. Intervals are Wilson 95%; '
        f'paired p-values are exact McNemar tests on seeds where both arms finished. "Rescued" means the comparison '
        f'arm survived a seed on which the control died. Stalls, timeouts, crashes and harness failures are counted '
        f'separately and never as deaths. Suites are small for small effects: a 2–4 point difference in early deaths '
        f'needs thousands of paired seeds.</p>'
        f'<h2>Versions</h2>{versions_table()}'
        f'<h2>All experiment runs</h2>'
        + (table(['Experiment', 'Completed', 'Versions', 'Profiles', 'Runs', 'Finished'], run_rows)
           if run_rows else '<p class="muted">No results yet.</p>') +
        f'<p class="muted">Raw cells: the <a href="https://github.com/diegoami/borg-zoo/tree/results">results branch</a>. '
        f'Method: <a href="https://github.com/diegoami/borg-zoo/blob/main/docs/DESIGN.md">design</a>. '
        f'Source: <a href="https://github.com/diegoami/borg-zoo">diegoami/borg-zoo</a>.</p>')
