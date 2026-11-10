"""The landing page: the main questions answered from the newest runs.

Every number on the page is computed from the results store when the site is
built; nothing is written by hand. A question whose experiment has no run yet
is left out.
"""
import hashlib
import json
import math
import re

_CHART_SEEN = {}  # emitted option hashes -> how many times, so identical
                  # tiles still get distinct element ids on one page

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


def _nice_step(vmax):
    """A round step for a plain-number axis (not a rate): the smallest of
    1/2/5/10/20/25/50/... that keeps the axis to at most 6 gridlines."""
    for step in (1, 2, 5, 10, 20, 25, 50, 100, 200, 500):
        if vmax / step <= 6:
            return step
    return 1000


def axis_limits(points, y_fmt='pct'):
    """The (x_max, y_max) scatter() would pick for these points on its own.

    Exposed so a small-multiples caller (turn_snapshots_section, class
    pages) can compute one shared scale over every tile's points combined,
    then pass it to each chart's own scatter() call as x_max/y_max -
    otherwise each tile auto-scales to its own data and the same value
    draws at a different height in every one (review #39).
    """
    xs = [p[0] for p in points if p[0] is not None]
    ys = [p[1] for p in points if p[1] is not None]
    x_max = max(0.3, math.ceil((max(xs, default=0.3) + 0.03) * 10) / 10)
    if y_fmt == 'num':
        y_step = _nice_step(max(ys, default=10) or 1)
        y_max = max(y_step, math.ceil((max(ys, default=10) * 1.1) / y_step) * y_step)
    else:
        y_max = max(0.2, math.ceil((max(ys, default=0.2) + 0.03) * 10) / 10)
    return x_max, y_max


def echarts_scatter(points, x_label, y_label, compact=False, y_fmt='pct', x_max=None, y_max=None):
    """Survivability (x) against progress (y), rendered by ECharts.

    points: (x, y, label, color, title). Every mark is a dot in the setup's
    own color; on the full-size charts each dot carries its short name right
    beside it. Label placement is computed here and shipped as explicit
    offsets, because ECharts' own moveOverlap does nothing in server-side
    rendering (verified) and the hand-rolled SVG this replaced dropped
    labels outright (review, 2026-11-10): the library draws, the packer
    places, and both the browser and the render-and-look step show the
    same chart. The compact
    tiles (turn snapshots) draw colored dots without labels: their color is
    the identity, keyed by the labeled chart and the table next to them.
    Every dot carries its full title in the hover tooltip.

    compact: a small-multiple (one per turn fraction): smaller, no axis
    label text (the caller titles it externally).

    y_fmt: 'pct' (0-100%, the default: x always is) or 'num' - y is a plain
    combined number (not a rate).

    x_max/y_max: fix the axis scale instead of fitting it to these points'
    own range (see axis_limits). Charts that are meant to be compared across
    tiles or pages (turn snapshots, the per-class pages) must share one
    scale, or the same value draws at a different height in each.

    The element id is content-addressed (a hash of the option), so charts
    render identically no matter what else was built before them in the
    same process - tests included.
    """
    auto_x, auto_y = axis_limits(points, y_fmt)
    x_top = round(x_max if x_max is not None else auto_x, 4)
    y_top = round(y_max if y_max is not None else auto_y, 4)
    labeled = not compact
    # ECharts' own labelLayout.moveOverlap does nothing in server-side
    # rendering (verified: identical SVG with it on or off), so label
    # placement is computed here, once, and shipped as explicit per-label
    # offsets - identical in the browser and in the render-and-look step.
    # The plot-area approximation matches the grid below within a few px.
    width, height = (210, 130) if compact else (680, 430)
    plot_l, plot_t = 46, 14
    plot_w = width - plot_l - (110 if labeled else 16)
    plot_h = height - plot_t - (46 if labeled else 26)
    px = lambda v: plot_l + (100 * v) / max(x_top, 1e-9) * plot_w / 100  # noqa: E731
    py = lambda v: plot_t + (1 - min(max(v, 0.0), y_top) / y_top) * plot_h  # noqa: E731
    placed, out, data = [], [], []
    for xv, yv, label, color, title in points:
        if xv is None or yv is None:
            continue
        out.append([(px(xv), py(yv)), label, color, title, None, (xv, yv)])
    # Setups whose runs played identically land on the exact same pixel: fan
    # such groups out along a short diagonal so every dot stays visible.
    groups = {}
    for i, entry in enumerate(out):
        groups.setdefault(entry[0], []).append(i)
    for indices in groups.values():
        for k, i in enumerate(indices[1:]):
            dot = out[i][0]
            out[i][0] = (dot[0] + 9 * k, dot[1] - 9 * k)
    # Dots are obstacles, not just labels: a label may not be drawn across
    # another setup's dot (in the dense 60-70% cluster the neighbours' dots
    # sat on top of "Vanilla", which reads as a rendering glitch, not a
    # label). Occupancy is 2D; labels always run to the right of their dot
    # into the chart's right margin, and when the spot is taken they step
    # away vertically - nearest first, because a label two gridlines from
    # its dot reads as someone else's.
    text_px = lambda label: 3 + 7.6 * len(label)  # noqa: E731  (11px semibold sans)

    def rect(lx, ly, text_w):
        return (lx, lx + text_w, ly - 8, ly + 6)

    def collisions(r):
        return sum(1 for o in placed
                   if not (r[1] <= o[0] or o[1] <= r[0] or r[3] <= o[2] or o[3] <= r[2]))

    dot_pad = 8  # symbolSize 10 (r=5) plus a little air
    placed = [(d[0] - dot_pad, d[0] + dot_pad, d[1] - dot_pad, d[1] + dot_pad)
              for d, *_rest in out]
    for i, (dot, label, color, title, _side, (xv, yv)) in enumerate(out):
        px0, py0 = dot
        offset = None
        if labeled and label:
            text_w = text_px(label)
            # the right margin is sized for labels: keep the whole word inside
            lx = min(px0 + 10, width - 2 - text_w)
            ladder = [0]
            step = 0
            while step + 15 < plot_h / 2:
                step += 15
                ladder += [step, -step]
            scored = []
            for off in ladder:
                ly = py0 + off
                if ly - 8 < plot_t or ly + 6 > plot_t + plot_h:
                    continue
                r = rect(lx, ly, text_w)
                n = collisions(r)
                if not n:
                    scored = [(0, abs(off), ly, r)]
                    break
                scored.append((n, abs(off), ly, r))
            if scored:
                _, _, ly, r = min(scored)
                placed.append(r)
                offset = [round(lx - px0, 1), round(ly - py0, 1)]
        data.append({'value': [round(100 * xv, 2), round(yv, 3)], 'name': label,
                     'itemStyle': {'color': color}, 't': title,
                     'label': {'offset': offset or [8, 0]}})
    option = {
        'animation': False,
        'backgroundColor': 'transparent',
        'grid': {'left': plot_l, 'right': width - plot_l - plot_w, 'top': plot_t,
                 'bottom': height - plot_t - plot_h},
        'xAxis': {'type': 'value', 'min': 0, 'max': round(100 * x_top, 4),
                  'axisLabel': {'color': '#808080', 'formatter': '{value}%'},
                  'splitLine': {'lineStyle': {'color': 'rgba(128,128,128,0.25)'}},
                  'name': x_label, 'nameGap': 18,
                  'nameTextStyle': {'color': '#808080', 'fontSize': 11},
                  'nameLocation': 'middle'},
        'yAxis': {'type': 'value', 'min': 0, 'max': y_top,
                  'axisLabel': {'color': '#808080'},
                  'splitLine': {'lineStyle': {'color': 'rgba(128,128,128,0.25)'}},
                  'name': y_label, 'nameGap': 14,
                  'nameTextStyle': {'color': '#808080', 'fontSize': 11, 'align': 'left'},
                  'nameLocation': 'middle', 'nameRotate': -90},
        'tooltip': {'trigger': 'item'},
        'series': [
            # dots first, labels second: ECharts draws series in order, so
            # every label sits above every dot - in a cluster the dots of
            # later items would otherwise cover earlier setups' names
            {'type': 'scatter', 'data': data, 'symbolSize': 10 if labeled else 7,
             'label': {'show': False}, 'z': 2, 'emphasis': {'scale': 1.3}},
            {'type': 'scatter', 'data': data, 'symbolSize': 0, 'silent': True,
             'label': {'show': labeled, 'position': 'right', 'formatter': '{b}',
                       'fontSize': 11, 'fontWeight': 600, 'color': '#808080'},
             'z': 3},
        ],
    }
    # the tooltip wants a formatter function, which JSON cannot carry: the
    # wrapper reads the pure-JSON option (also what tools/render-chart.js
    # feeds to ECharts' SSR for the render-and-look step) and adds it
    cfg = json.dumps(option).replace('</', '<\\/')
    h = hashlib.sha1(cfg.encode()).hexdigest()[:10]
    # two tiles can hold identical data (same values at every fraction):
    # same content, same hash, but they still need their own element
    n = _CHART_SEEN.get(h, 0)
    _CHART_SEEN[h] = n + 1
    dom = h if n == 0 else f'{h}-{n}'
    # the JS literals go through json.dumps, not hand-written quotes: the
    # selector carries its own quotes, and building it by hand shipped
    # querySelector("script[data-chart="h"]") - a syntax error that killed
    # every init script on the page and left all charts empty (live bug,
    # 2026-11-10). json.dumps escapes for JS, so this cannot recur.
    sel = json.dumps(f'script[data-chart="{dom}"]')
    dom_lit = json.dumps(dom)
    renderer = json.dumps({'renderer': 'svg'})
    return (f'<div id="{dom}" class="chart-echarts" style="width:{width}px;height:{height}px"></div>'
            f'<script type="application/json" data-chart="{dom}">{cfg}</script>'
            f'<script>window.addEventListener("DOMContentLoaded", () => {{'
            f'const cfg = JSON.parse(document.querySelector({sel}).textContent);'
            f'cfg.tooltip.formatter = p => (p.data && p.data.t) || p.name;'
            f'echarts.init(document.getElementById({dom_lit}), null, {renderer}).setOption(cfg);'
            f'}});</script>')


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
    return suite, meta['catalogue']['suites'][suite], stats.analyse(exp, cells, meta['catalogue']['specimens'])[suite]


def find_arm(runs, specimen, profile, specs, cls=None, cap=None):
    """The most informative run with cells for (specimen, profile[, played class
   ][, turn cap]): the most finished runs (a smoke-suite run of a handful of
    seeds must never outrank a development-suite run of thousands just for
    being newer), ties broken by newest. (None, None) if none.

    cap pins the comparison to one turn cap. Two runs of the same suite name
    can differ there (classes-1800 is 100,000 turns, classes-1800-200k is
    200,000), and a 200k arm survives longer by construction - mixing them in
    one chart compares the cap, not the Borg.

    Also matches any of the specimen's earlier names (catalogue "formerly"):
    results recorded before the 2026-11-08 rename use them (e.g. "pristine"
    for 4.2.6, "bbc-m4" for 4.2.6-bbc-m4), and missing them silently drops
    real runs - sometimes the only run at development-suite scale for that
    specimen, in favour of a much smaller one that happens to use the
    current name.
    """
    aliases = {specimen, *specs.get(specimen, {}).get('formerly', ())}
    best_summary, best_meta, best_arm, best_key = None, None, None, (-1, '')
    for meta, cells, _ in runs:
        arm = [c for c in cells if c['specimen'] in aliases and c['profile'] == profile
               and (cls is None or c.get('played_class') == cls)
               and (cap is None or c.get('cap') == cap)]
        if not arm:
            continue
        s = dict(stats.arm_summary(arm), progress_score=stats.progress_score(arm))
        key = (s['valid'], meta.get('completed', ''))
        if key > best_key:
            best_summary, best_meta, best_arm, best_key = s, meta, arm, key
    return best_summary, best_meta, best_arm



PROFILES_URL = 'https://github.com/diegoami/borg-zoo/blob/main/catalogue/profiles.json'

# Five points, not a roster: the plain Angband 4.2.6 borg, the same game with
# the munchkin start, the best measured setup of each line, and - a different
# engine, never paired with the rest - the Neo Borg. Better-borg-c and borg-rs
# have eleven and ten milestones; plotting each one made the chart a cloud of
# near-identical points (owner direction, 2026-11-10: "just have the best
# there proved by the fully full run").
#
# Every C/Rust point is read under ONE policy - the munchkin start for Warrior,
# Druid and Ranger, everything else ordinary - because that is the only policy
# with full class runs on both sides of the mode cutoff. Comparing a shipped
# "default" across the cutoff compared the mode defaults, not the Borg: M10's
# default already gives those three classes the munchkin start (by_class TRUE
# since fd683ced) while Angband 4.2.6's default does not, and its apparent
# survival lead was that policy, not better play (owner's challenge: "are we
# cheating with the munchkin mix?", 2026-11-10).
#
# "Angband 4.2.6" is specimen 4.2.6, formerly named "pristine" and "Vanilla".
C_COLOR = '#2f5d8a'    # the better-borg-c line (the site's --accent blue)
RUST_COLOR = '#b58700'  # the borg-rs line (the site's --rust amber)

MUNCHKIN_MODES = ('munchkin start for Warrior, Druid and Ranger; every other class '
                  'plays the ordinary game')

EXEMPLARS = [
    {'specimen': '4.2.6', 'profile': 'default', 'name': 'Angband 4.2.6', 'short': 'Angband 4.2.6',
     'color': '#757575', 'modes': 'no munchkin start, no Lunal',
     'note': 'the C Borg as Angband 4.2.6 ships it (angband/angband e473720), no fixes '
     'and default settings: the baseline everything else is read against.'},
    {'specimen': '4.2.6', 'profile': 'munchkin-wdr', 'name': 'Angband 4.2.6 + munchkin',
     'short': '4.2.6+munch', 'color': '#0097a7', 'modes': MUNCHKIN_MODES,
     'note': 'Angband 4.2.6 with the munchkin start by class profile '
     f'(<code>munchkin-wdr</code>, <a href="{PROFILES_URL}">settings</a>): no other fixes.'},
    {'specimen': '4.2.6-bbc-m8', 'profile': 'munchkin-wdr',
     'name': 'better-borg-c M8 (best C)', 'short': 'BBC M8', 'color': C_COLOR,
     'modes': MUNCHKIN_MODES,
     'note': 'the best-measured better-borg-c milestone under that policy: 88 carried fixes. '
     'M9 and M10 have no full run under it (their "default" arms already include the class '
     'rule, so they are not comparable with the pre-cutoff baseline), and M11 (116 carries, '
     'tag 4.2.6-impact-v11) has only a smoke run.'},
    {'specimen': '4.2.6-rs-m8', 'profile': 'munchkin-wdr',
     'name': 'borg-rs M8 (best Rust)', 'short': 'RS M8', 'color': RUST_COLOR,
     'modes': MUNCHKIN_MODES,
     'note': 'the best-measured Rust milestone under the same policy: the port carrying '
     'better-borg-c M8\'s 88 fixes. M9 and M10 exist but have no full run under it.'},
    {'specimen': 'neo-b3-api2-upstream', 'profile': 'default',
     'name': 'Neo Angband (Mandos, upstream)', 'short': 'Neo', 'color': '#6d4c41',
     'modes': 'its own engine defaults',
     'note': 'a different engine on different seeds — '
     '<strong>never paired</strong> with the C/Rust points above; shown for scale only.'},
]

# A dashboard point needs a real sample behind it: a smoke run (3 seeds) is
# a build sanity check, not evidence, and an 18-seed pilot is not much more.
# Setups whose best recorded run is below this stay off the charts (the
# legend row says so); they come back automatically once a real suite runs.
DASHBOARD_MIN_CELLS = 50

# ... and every point is read at one turn cap. classes-1800 is 100,000 turns;
# classes-1800-200k is 200,000, and a 200k arm survives longer by construction.
DASHBOARD_CAP = 100000


def chart_configs(html):
    """The ECharts option dicts embedded in a page or card fragment, keyed
    by their chart id - the same JSON tools/render-chart.js feeds to
    ECharts' server-side renderer for the render-and-look step (DESIGN.md)."""
    out = {}
    for m in re.finditer(r'<script type="application/json" data-chart="([^"]+)">(.*?)</script>', html, re.S):
        out[m.group(1)] = json.loads(m.group(2).replace('<\\/', '</'))
    return out


def dashboard_plotted(s):
    """True when a setup's best run carries enough cells to be a dashboard
    point (DASHBOARD_MIN_CELLS): smoke-scale checks stay off the charts."""
    return s is not None and s['valid'] >= DASHBOARD_MIN_CELLS


def exemplar_points(runs, specs, cls=None):
    """(x, y, label, color, title) per exemplar, x = survivability, y = progress_score
    (median max depth + character level, not a rate); cls restricts to one
    played class (for the per-class pages) or None for all. Setups whose
    best run is smoke-scale (DASHBOARD_MIN_CELLS) get no point at all - the
    chart reads as evidence, and a 3-seed sanity check is not that."""
    points, found = [], []
    for e in EXEMPLARS:
        s, meta, arm = find_arm(runs, e['specimen'], e['profile'], specs, cls,
                                cap=DASHBOARD_CAP)
        plotted = s is not None and s['valid'] >= DASHBOARD_MIN_CELLS
        x = (1 - s['death_rate']) if plotted and s['death_rate'] is not None else None
        yv = s['progress_score'] if plotted else None
        title = (f"{e['name']} — alive at cap {100 * (1 - s['death_rate']):.0f}%, "
                 f"depth+level {s['progress_score']:.0f}, {s['valid']} finished"
                 if plotted and s['death_rate'] is not None and s['progress_score'] is not None
                 else e['name'])
        points.append((x, yv, e['short'], e['color'], title))
        found.append((s, meta, arm))
    return points, found


def exemplar_table(found, specs):
    """The legend table under the chart: color swatch, full name, note,
    numbers, and the run each point came from. Also returns the set of
    (experiment, suite) keys behind the rows, for the cross-run caveat."""
    rows = []
    run_keys = set()
    for e, (s, meta, arm) in zip(EXEMPLARS, found):
        source = specs.get(e['specimen'], {}).get('source')
        src = f' · <a href="{esc(source)}">source</a>' if source else ''
        x = (1 - s['death_rate']) if s and s['death_rate'] is not None else None
        yv = s['progress_score'] if s else None
        badge = f'<span class="legend-mark" style="background:{e["color"]}"></span>'
        thin = ('<br><span class="muted">no run yet · not plotted</span>' if s is None
                else '<br><span class="muted">smoke-scale only — not plotted</span>'
                if not dashboard_plotted(s) else '')
        if meta:
            run_keys.add((meta['experiment']['name'], meta['experiment']['suites'][0]))
            run_cell = (f'<a href="{link(meta)}">{esc(meta["experiment"]["name"])}</a><br>'
                        f'<span class="muted">{esc(meta["experiment"]["suites"][0])} · '
                        f'{esc(meta.get("completed", "?"))}</span>')
        else:
            run_cell = '–'
        rows.append(f'<tr><td class="l">{badge} <strong>{esc(e["name"])}</strong></td>'
                    f'<td class="l">{e["note"]}{src}{thin}</td>'
                    f'<td class="l"><span class="muted">{esc(e.get("modes", ""))}</span></td>'
                    f'<td>{pct(x) if x is not None else "–"}</td>'
                    f'<td>{num(yv) if yv is not None else "–"}</td>'
                    f'<td>{num(s["valid"]) if s else "–"}</td>'
                    f'<td class="l">{run_cell}</td></tr>')
    legend = ('<div class="wrap"><table><thead><tr><th class="l">Setup</th><th class="l">What it is</th>'
              '<th class="l">Modes</th><th>Alive at cap</th>'
              '<th title="Median, over finished runs including deaths, of max dungeon level reached + '
              'character level reached. A plain combined figure, not a calibrated score.">Depth + level</th>'
              '<th title="Cells that reached death or the turn cap; the denominator of both columns">'
              'Finished</th><th class="l">Run · suite · completed</th>'
              '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>')
    return legend, run_keys


def card_exemplars(runs):
    specs = cat_mod.catalogue()['specimens']['specimens']
    points, found = exemplar_points(runs, specs)
    if not any(p[0] is not None for p in points):
        return None
    chart = echarts_scatter(points, x_label='Survivability — alive at the turn cap',
                            y_label='Progress — median max dungeon level + character level', y_fmt='num')
    legend, run_keys = exemplar_table(found, specs)
    links = class_links(runs, specs)
    snapshots = turn_snapshots_section(found)
    cross_run = len(run_keys) > 1
    measured = [(e, s) for e, (s, _meta, _arm) in zip(EXEMPLARS, found)
                if s is not None and dashboard_plotted(s) and s.get('death_rate') is not None]

    def best(prefix):
        cand = [(e, s) for e, s in measured if e['specimen'].startswith(prefix)]
        return max(cand, key=lambda es: 1 - es[1]['death_rate']) if cand else (None, None)

    base = next((s for e, s in measured
                 if e['specimen'] == '4.2.6' and e['profile'] == 'default'), None)
    mk = next((s for e, s in measured
               if e['specimen'] == '4.2.6' and e['profile'] == 'munchkin-wdr'), None)
    bc, bs = best('4.2.6-bbc')
    rc, rs = best('4.2.6-rs')
    parts = []
    if base:
        parts.append(f'plain <strong>Angband 4.2.6</strong> loses {pct(base["death_rate"])} of its runs by the cap')
    if mk:
        parts.append(f'the same game with the munchkin start (Warrior, Druid and Ranger only; the other six '
                     f'classes play exactly the baseline game, identical on every paired seed) loses '
                     f'{pct(mk["death_rate"])}')
    if bc:
        parts.append(f'the best better-borg-c milestone under that same policy loses {pct(bs["death_rate"])}')
    if rc:
        parts.append(f'the best Rust one {pct(rs["death_rate"])}')
    answer = (f'Read at one turn cap and one mode policy, {"; ".join(parts)}. '
              f'The three munchkin arms sit within a point or two of each other, so on the full runs recorded '
              f'so far the code milestones add no measurable survival over vanilla with the same policy. '
              f'M9 and M10 are not plotted because their shipped default already includes the same class rule '
              f'for those three classes, and no full run of them plays with the modes pinned: comparing their '
              f'default with the pre-cutoff baseline compared the munchkin policy, not the Borg. '
              + ('These points are not one controlled comparison — the arms come from different '
                 'experiments and none carries an interval, so treat the order as a lead, not a '
                 'confirmed result.' if cross_run else 'The arms come from one experiment.'))
    return (f'<div class="card wide"><h2>Which setup should I actually run?</h2>'
            f'<p class="answer">{answer}</p>{chart}{legend}'
            f'<p class="foot">Each point is the run with the most finished cells recorded for that exact '
            f'version and profile — not necessarily the newest, which is only the tiebreaker — and carries '
            f'its name on the chart. One point per line, the best with a full class run: every other '
            f'milestone keeps its catalogue entry, its run page and the Detailed tab, and a setup with '
            f'only smoke-scale runs is left off the chart entirely. "Progress" is depth + level '
            f'added unweighted, median over every finished run including deaths (how far a run got, not '
            f'just whether it survived) — gold on hand and a real net worth will join it once they exist '
            f'for more than one specimen. The Neo Angband point is never comparable with the rest: Mandos '
            f'plays a different engine on different seeds.</p>'
            f'{links}{snapshots}</div>')

def turn_snapshots_section(found):
    """A scatter chart per turn fraction of the cap (25/50/75/100%): every
    exemplar's survivability and progress AT that turn, not just at the end
    - the same per-cell `milestones` data the Detailed tab's own turn table
    reads. A mark needs both an x (survivability) and a y (progress): an
    exemplar whose arm has no milestones (a borg-rs specimen without
    depth_stream) has its alive rate computed but no progress figure, so it
    draws no mark at all here rather than a half-drawn one at a guessed y.

    Labelled with the actual turn each fraction lands on, which needs every
    contributing arm to share one cap; with more than one cap in play, the
    label falls back to the fraction itself and says so.
    """
    fractions = (0.25, 0.5, 0.75, 1.0)
    by_fraction = [[] for _ in fractions]
    caps = set()
    for e, (s, meta, arm) in zip(EXEMPLARS, found):
        if not arm or not dashboard_plotted(s):
            for i in range(len(fractions)):
                by_fraction[i].append((None, None, e['short'], e['color'], e['name']))
            continue
        cap = arm[0]['cap']
        caps.add(cap)
        surv = stats.survival_table(arm, cap, fractions)
        prog = stats.milestone_progress_score(arm, fractions)
        for i in range(len(fractions)):
            by_fraction[i].append((surv[i]['alive'], prog[i]['score'], e['short'], e['color'], e['name']))
    # A mark needs both coordinates (see the docstring); a fraction - or the whole section -
    # with survivability but no progress anywhere draws nothing, so do not show it as if it did.
    if not any(any(p[0] is not None and p[1] is not None for p in pts) for pts in by_fraction):
        return ''
    one_cap = caps.pop() if len(caps) == 1 else None
    shown = [i for i in range(len(fractions)) if any(p[0] is not None and p[1] is not None for p in by_fraction[i])]
    # One scale across every tile, not each fitting its own data: the whole point of this
    # section is watching progress rise from tile to tile, which a self-scaling axis per tile
    # would flatten out (the same review #39 finding the by-class grid had).
    x_max, y_max = axis_limits([p for i in shown for p in by_fraction[i]], y_fmt='num')
    cells = []
    for i in shown:
        f = fractions[i]
        label = f'{int(one_cap * f):,} turns' if one_cap else f'{int(f * 100)}% of cap'
        chart = echarts_scatter(by_fraction[i], x_label='', y_label='', compact=True, y_fmt='num', x_max=x_max, y_max=y_max)
        cells.append(f'<div class="class-cell"><h3>{esc(label)}</h3>{chart}</div>')
    caption = (f'the same setups, at {", ".join(f"{int(one_cap * f):,}" for f in fractions)} turns.'
              if one_cap else
              'the same setups, at 25/50/75/100% of each one’s own cap (more than one cap is in play, '
              'so turns are not directly comparable across tiles).')
    return (f'<h3>Progress over turns</h3><p class="foot">Not just the end state: {caption} Survivability '
            f'runs left to right, 0–100%; depth + level runs bottom to top, one fixed scale across every '
            f'tile. A tile with only some marks means the rest had no per-turn data recorded '
            f'(no <code>depth_stream</code>, for a borg-rs specimen) or had already died by then.</p>'
            f'<div class="class-grid">{"".join(cells)}</div>')


def dashboard_classes(runs, specs):
    """The classes that have at least one dashboard-worthy setup on record:
    the per-class pages exist only for these (the others would be empty)."""
    return [c for c in cat_mod.CLASSES
            if any(dashboard_plotted(find_arm(runs, e['specimen'], e['profile'], specs, c,
                                              cap=DASHBOARD_CAP)[0])
                   for e in EXEMPLARS)]


def class_links(runs, specs):
    """The overview card's row of per-class page links (full charts, one
    page per class - the old nine-remotes-wide tile grid was too small to
    read anything out of)."""
    classes = dashboard_classes(runs, specs)
    if not classes:
        return ''
    chips = ' · '.join(f'<a href="classes/{esc(cls)}.html">{esc(cls)}</a>' for cls in classes)
    return (f'<h3>By class</h3><p class="foot">The same setups, split by the class each seed played '
            f'(<code>classes-1800</code>-style suites assign 200 seeds per class), one full chart per '
            f'class page: {chips}.</p>')


def class_pages(runs):
    """One page per class: a full-size labeled chart (the same setups as the
    overview card, restricted to the seeds that played this class) and the
    same numbers table. Returns (slug, title, body) per class with data;
    every page shares one scale, so a Warrior/Mage difference reads the same
    on both pages."""
    specs = cat_mod.catalogue()['specimens']['specimens']
    classes = dashboard_classes(runs, specs)
    per_class = {}
    for cls in classes:
        points, _ = exemplar_points(runs, specs, cls)
        if any(p[0] is not None for p in points):
            per_class[cls] = points
    if not per_class:
        return []
    x_max, y_max = axis_limits([p for pts in per_class.values() for p in pts], y_fmt='num')
    pages = []
    for cls, points in per_class.items():
        points, found = exemplar_points(runs, specs, cls)
        chart = echarts_scatter(points, x_label='Survivability — alive at the turn cap',
                        y_label='Progress — median max dungeon level + character level',
                        y_fmt='num', x_max=x_max, y_max=y_max)
        legend, _ = exemplar_table(found, specs)
        body = (f'<p><a href="../index.html">Borg zoo</a></p>'
                f'<h1>{esc(cls)}</h1>'
                f'<p class="lead">The dashboard setups, on the seeds that played {esc(cls)}. '
                f'Same scale on every class page, so classes can be compared against each other; '
                f'each dot is labelled, and the table has the numbers and the run behind each point.</p>'
                f'{chart}{legend}')
        pages.append((cls, f'{cls} · borg-zoo', body))
    return pages


def card_milestones(runs):
    meta, cells = newest(runs, ['classes-m7', 'classes-m6', 'classes-m5', 'milestones-wide', 'milestones-early'])
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


NAME = re.compile(r'^(?P<engine>\d+\.\d+\.\d+)(?:-(?P<line>bbc|rs)-m(?P<n>\d+))?(?P<c>-c)?$')


def milestone_number(name, line):
    """Milestone of a version name such as 4.2.6 (0), 4.2.6-bbc-m5 or 4.2.6-rs-m3, on one line."""
    m = NAME.match(name)
    if not m or m['c']:
        return None
    if line == 'bbc' and not m['line']:
        return 0
    return int(m['n']) if m['line'] == line else None


def identity(runs, rust, twin, specs):
    """Best evidence that a Rust specimen plays like its C twin: (identical, pairs, meta).

    Older runs may name either one by a name listed under `formerly`.
    """
    best = (0, 0, None)
    alias = {old: new for new in (rust, twin) for old in (new, *specs[new].get('formerly', ()))}
    for meta, cells, _ in runs:
        present = {alias[s] for s in meta['experiment']['specimens'] if s in alias}
        if present != {rust, twin}:
            continue
        play = {}
        for c in cells:
            if c['outcome'] in stats.VALID and c.get('play_sha256'):
                who = alias.get(c['specimen'], c['specimen'])
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
        same, pairs, meta = identity(runs, name, twin, specs) if twin else (0, 0, None)
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
    lane_w, col_w, box_w, top, box_h, gap = 92, 108, 100, 22, 46, 30
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


def mode_cutoff_note():
    """The standing statement of the mode cutoff (borg-zoo#54): what changed
    at better-borg-c fd683ced, and what the zoo does about it. Shown on the
    Detailed and Versions tabs; each run page says how it applies to that
    run's own results."""
    cut = cat_mod.MODE_CUTOFF[:9]
    return (f'<p class="note"><strong>Mode cutoff {cut} (better-borg-c PR 302, {cat_mod.MODE_CUTOFF_DATE}, '
            f'borg-zoo#54):</strong> from that commit <code>borg_munchkin_by_class</code> defaults to TRUE, so '
            'better-borg-c specimens before it do not carry the class rule and the profile named '
            '<code>default</code> plays a different game on either side. Runs recorded before '
            f'{cat_mod.MODE_CUTOFF_DATE} are labelled pre-cutoff on their pages, and version pairings that '
            'straddle the cutoff are not computed. Every experiment measured now names a mode profile '
            '(<code>normal</code>, <code>munchkin-class</code>, <code>munchkin-on</code>, <code>lunal</code>); '
            '<code>default</code> stays only as a compatibility alias for pre-cutoff experiments, and the '
            'catalogue refuses it anywhere the cutoff applies.</p>')


def versions_page():
    return (f'<p><a href="index.html">Borg zoo</a></p><h1>Versions</h1>{mode_cutoff_note()}{versions_table()}')


RUN_COLS = [('Experiment', 'The question being asked; the link opens its tables.'),
            ('Completed', 'When the run finished (UTC).'),
            ('Versions', 'How many Borg versions it compares.'),
            ('Profiles', 'How many settings profiles it compares.'),
            ('Runs', 'Games played: versions × profiles × seeds.'),
            ('Finished', 'Games that reached an endpoint (death or the turn cap); the rest stalled, timed out '
                         'or failed.')]


def nav(active):
    tabs = [('index.html', 'Overview'), ('detailed.html', 'Detailed')]
    return ('<p class="tabs">' +
            ''.join(f'<a class="tab{" active" if href == active else ""}" href="{href}">{esc(label)}</a>'
                    for href, label in tabs) + '</p>')


FOOTER = (f'<p class="muted"><a href="versions.html">Versions</a> · <a href="stalls.html">Stalls and crashes</a> · '
          f'<a href="https://github.com/diegoami/borg-zoo/blob/main/docs/DESIGN.md">Method</a> · '
          f'<a href="https://github.com/diegoami/borg-zoo/tree/results">Raw results</a> · '
          f'<a href="https://github.com/diegoami/borg-zoo">Source</a></p>')


def add_your_borg_section():
    """Static, not derived from results: what a Borg needs to enter the catalogue.

    Sourced from this repo's own rules (AGENTS.md, RULES.md, docs/DESIGN.md), not
    aspirational: every requirement named here is already enforced somewhere in
    zoo/catalogue.py or an adapter, or is a standing project rule.
    """
    return (
        '<h2>Add your Borg to the zoo</h2>'
        '<p class="lead">Adding a specimen, profile, suite or experiment is a catalogue change with a pull '
        'request to <a href="https://github.com/diegoami/borg-zoo">this repository</a> — the zoo never edits '
        'another repository\'s code or issues.</p>'
        '<ol>'
        '<li>Your Borg lives in its own repository and is pinned by a full commit SHA; the zoo reads it there '
        'and never changes it. A Borg source change or a new Borg parameter belongs in your repository, not '
        'here — a parameter enters the zoo as a profile once your repository exposes it with a default that '
        'reproduces the original behaviour.</li>'
        '<li>It needs a way to run headless, deterministically, on a seed and a turn cap, that one of the '
        'zoo\'s adapters already speaks: the better-borg-c observer harness, borg-rs\'s own '
        '<code>harness/build.sh</code> and <code>borgh</code> frontend, or Mandos\'s headless entry point '
        '(<code>tools/zoo-run.mjs</code>, record schema <code>mandos/zoo-run@1</code>). A genuinely new shape '
        'needs a new adapter in <code>zoo/</code> — more work, but the same catalogue-PR process.</li>'
        '<li>The catalogue entry itself: repository, the pinned commit, how many fixes it carries from the '
        'tracker (0 for an original), and a short label.</li>'
        '<li>Starting a large experiment on it is the owner\'s call, same as for every existing specimen.</li>'
        '</ol>'
        '<p>The clearest real example: borg-reborn-rs wrote up its own '
        '<a href="https://github.com/diegoami/borg-reborn-rs/blob/main/docs/ZOO-CHANGE-REQUEST.md">change '
        'request</a> — what already worked unchanged against the zoo\'s own adapter, the specific catalogue '
        'and adapter changes it needed, and a ready prompt for the session that would do the work. The owner '
        'routed it in as <a href="https://github.com/diegoami/borg-zoo/issues/30">issue #30</a>, and it landed '
        'in <a href="https://github.com/diegoami/borg-zoo/pull/32">PR #32</a>.</p>')


def overview_page(runs):
    total = sum(len(c) for _, c, _ in runs)
    latest = runs[0][0].get('completed', '?') if runs else '–'
    exemplars = card_exemplars(runs)
    return (
        f'<h1>Borg zoo</h1>{nav("index.html")}'
        f'<p class="muted">{total:,} runs · {len(runs)} experiment runs · latest {esc(latest)}</p>'
        f'<p class="lead">Angband Borg versions played headless on the same seeds: the original C Borg, '
        f'better-borg-c\'s milestones of carried fixes, and the borg-rs Rust port.</p>'
        + (f'<div class="cards">{exemplars}</div>' if exemplars else '<p class="muted">No results yet.</p>')
        + f'<p class="muted">Every milestone, the Rust port and the open stalls are on the '
        f'<a href="detailed.html">Detailed</a> tab.</p>'
        + add_your_borg_section() + FOOTER)


def landing_page(runs, run_rows):
    cards = [c for c in (card_milestones(runs), card_port(runs), card_stalls(runs)) if c]
    return (
        f'<h1>Borg zoo</h1>{nav("detailed.html")}'
        f'{mode_cutoff_note()}'
        f'<div class="cards">{"".join(cards)}</div>'
        f'<h2>Experiment runs</h2>'
        + (explain('Every recorded run, newest first. Each page explains its tables.', RUN_COLS)
           + table(RUN_COLS, run_rows) if run_rows else '<p class="muted">No results yet.</p>')
        + FOOTER)
