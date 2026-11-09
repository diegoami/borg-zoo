"""The landing page: the main questions answered from the newest runs.

Every number on the page is computed from the results store when the site is
built; nothing is written by hand. A question whose experiment has no run yet
is left out.
"""
import math
import re

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


SHAPES = ('circle', 'diamond', 'triangle', 'square', 'cross')


def mark(shape, cx, cy, cls):
    """One scatter mark. `cls` is a space-joined set of CSS modifiers:
    "hi" (the recommended setup, good color), "other" (a different game,
    never paired with the rest - muted color), "rust" (the borg-rs Rust
    port's own color, next to shape so the two lines are told apart twice
    over), "outline" (a +munchkin variant of its filled sibling: same
    shape, hollow instead of solid)."""
    if shape == 'diamond':
        return f'<polygon class="dot {cls}" points="{cx:.1f},{cy - 8:.1f} {cx + 8:.1f},{cy:.1f} ' \
               f'{cx:.1f},{cy + 8:.1f} {cx - 8:.1f},{cy:.1f}"/>'
    if shape == 'triangle':
        return f'<polygon class="dot {cls}" points="{cx:.1f},{cy - 8:.1f} {cx - 7:.1f},{cy + 6:.1f} ' \
               f'{cx + 7:.1f},{cy + 6:.1f}"/>'
    if shape == 'square':
        return f'<rect class="dot {cls}" x="{cx - 6:.1f}" y="{cy - 6:.1f}" width="12" height="12"/>'
    if shape == 'cross':
        return (f'<g class="dot cross {cls}">'
                f'<line x1="{cx - 7:.1f}" y1="{cy:.1f}" x2="{cx + 7:.1f}" y2="{cy:.1f}"/>'
                f'<line x1="{cx:.1f}" y1="{cy - 7:.1f}" x2="{cx:.1f}" y2="{cy + 7:.1f}"/></g>')
    return f'<circle class="dot {cls}" cx="{cx:.1f}" cy="{cy:.1f}" r="7"/>'


def _nice_step(vmax):
    """A round step for a plain-number axis (not a rate): the smallest of
    1/2/5/10/20/25/50/... that keeps the axis to at most 6 gridlines."""
    for step in (1, 2, 5, 10, 20, 25, 50, 100, 200, 500):
        if vmax / step <= 6:
            return step
    return 1000


def axis_limits(points, y_fmt='pct'):
    """The (x_max, y_max) scatter() would pick for these points on its own.

    Exposed so a small-multiples caller (class_grid, turn_snapshots_section)
    can compute one shared scale over every tile's points combined, then
    pass it to each tile's own scatter() call as x_max/y_max - otherwise
    each tile auto-scales to its own data and the same value draws at a
    different height in every one (review #39).
    """
    xs = [p[1] for p in points if p[1] is not None]
    ys = [p[2] for p in points if p[2] is not None]
    x_max = max(0.3, math.ceil((max(xs, default=0.3) + 0.03) * 10) / 10)
    if y_fmt == 'num':
        y_step = _nice_step(max(ys, default=10) or 1)
        y_max = max(y_step, math.ceil((max(ys, default=10) * 1.1) / y_step) * y_step)
    else:
        y_max = max(0.2, math.ceil((max(ys, default=0.2) + 0.03) * 10) / 10)
    return x_max, y_max


def scatter(points, x_label, y_label, compact=False, y_fmt='pct', x_max=None, y_max=None):
    """Survivability (x) against progress (y), a handful of named setups.

    points: (shape, x, y, cls). Marks carry no inline text: real points can
    land only a few percent apart, and any label placed beside a dot would
    collide with its neighbour. Shape (and, redundantly, color) is the only
    way to tell points apart on the chart itself; the caller renders the
    names, exact numbers and links as a legend table once, in the same order
    as `points`, shared across every compact chart that reuses the same set.

    compact: a small-multiple (one per class): smaller, coarser gridlines,
    no axis label text (the caller titles it externally).

    y_fmt: 'pct' (0-100%, the default: x always is) or 'num' - y is a plain
    combined number (not a rate), with its own round-number step and no %.

    x_max/y_max: fix the axis scale instead of fitting it to these points'
    own range (see axis_limits). Small multiples that are meant to be
    compared side by side (the per-class grid, turn snapshots) must share
    one scale, or the same value draws at a different height in every tile.
    """
    pad_l, pad_b, pad_t, size = (22, 16, 4, 110) if compact else (42, 34, 16, 300)
    x_step = 50 if compact else 10
    auto_x, auto_y = axis_limits(points, y_fmt)
    if x_max is None:
        x_max = auto_x
    if y_max is None:
        y_max = auto_y
    y_step = _nice_step(y_max) if y_fmt == 'num' else (50 if compact else 10)
    width = pad_l + size + (4 if compact else 16)
    height = pad_t + size + pad_b
    x = lambda v: pad_l + size * min(max(v, 0.0), x_max) / x_max  # noqa: E731
    y = lambda v: pad_t + size * (1 - min(max(v, 0.0), y_max) / y_max)  # noqa: E731
    cls = 'scatter compact' if compact else 'scatter'
    parts = [f'<svg class="{cls}" viewBox="0 0 {width} {height}" role="img" '
             f'aria-label="{esc(x_label)} against {esc(y_label)}, {len(points)} Borg setups, named below the chart">']
    for i in range(0, int(x_max * 100) + 1, x_step):
        xv = x(i / 100)
        parts.append(f'<line class="axis" x1="{xv:.1f}" y1="{pad_t}" x2="{xv:.1f}" y2="{pad_t + size}"/>')
        if not compact:
            parts.append(f'<text class="tick" x="{xv:.1f}" y="{pad_t + size + 14}" text-anchor="middle">{i}%</text>')
    if y_fmt == 'num':
        y_ticks = [(i, str(i)) for i in range(0, int(y_max) + 1, y_step)]
    else:
        y_ticks = [(i / 100, f'{i}%') for i in range(0, int(y_max * 100) + 1, y_step)]
    for raw, label in y_ticks:
        yv = y(raw)
        parts.append(f'<line class="axis" x1="{pad_l}" y1="{yv:.1f}" x2="{pad_l + size}" y2="{yv:.1f}"/>')
        if not compact:
            parts.append(f'<text class="tick" x="{pad_l - 6}" y="{yv + 4:.1f}" text-anchor="end">{label}</text>')
    if not compact:
        parts.append(f'<text class="head" x="{pad_l + size / 2:.1f}" y="{height - 4}" '
                     f'text-anchor="middle">{esc(x_label)}</text>')
        parts.append(f'<g transform="translate(12,{pad_t + size / 2:.1f}) rotate(-90)">'
                     f'<text class="head" text-anchor="middle">{esc(y_label)}</text></g>')
    for shape, xv, yv, mcls in points:
        if xv is None or yv is None:
            continue
        parts.append(mark(shape, x(xv), y(yv), mcls))
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


def find_arm(runs, specimen, profile, specs, cls=None):
    """The most informative run with cells for (specimen, profile[, played class]):
    the most finished runs (a smoke-suite run of a handful of seeds must never
    outrank a development-suite run of thousands just for being newer), ties
    broken by newest. (None, None) if none.

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
               and (cls is None or c.get('played_class') == cls)]
        if not arm:
            continue
        s = dict(stats.arm_summary(arm), progress_score=stats.progress_score(arm))
        key = (s['valid'], meta.get('completed', ''))
        if key > best_key:
            best_summary, best_meta, best_arm, best_key = s, meta, arm, key
    return best_summary, best_meta, best_arm


PROFILES_URL = 'https://github.com/diegoami/borg-zoo/blob/main/catalogue/profiles.json'

# Not every milestone (that is the detailed tab): where you start, the one single-setting
# win already confirmed, the owner's actual recommendation, both lines' newest milestone
# (M8) plain and with the same win tried on them, and - a different game, never paired with
# the rest - the Neo Borg. "Vanilla" is specimen 4.2.6, formerly named "pristine".
def _bbc(n, carries):
    return {'shape': 'circle', 'cls': '', 'specimen': f'4.2.6-bbc-m{n}', 'profile': 'default',
            'name': f'better-borg-c M{n}', 'note': f'{carries} carried fixes, default settings.'}


def _rs(n, carries):
    return {'shape': 'triangle', 'cls': 'rust', 'specimen': f'4.2.6-rs-m{n}', 'profile': 'default',
            'name': f'borg-rs M{n} (Rust)', 'note': f'the Rust port carrying the same {carries} fixes, '
            'default settings.'}


# Identity is by shape *group*, not one glyph per point, so adding another milestone never
# needs a new glyph: circle = the C line (better-borg-c), triangle = the Rust port, diamond =
# the one recommendation, cross = a different game entirely (Neo). Color backs shape up rather
# than repeating it: the Rust port's triangles also carry their own hue (--rust), so the two
# lines are told apart twice over, not by shape alone. "outline" (hollow instead of solid)
# marks a specimen's +munchkin sibling - dropped for any specimen whose own default already is
# the munchkin start by class (M8 on both lines: confirmed identical play/trace hashes, review
# #39), since pairing it with the munchkin-wdr profile there would just re-measure the same
# game. Exact identification is always the legend table below, by name and number, same
# mechanism regardless of how many points there are. "Vanilla" is specimen 4.2.6, formerly
# named "pristine".
EXEMPLARS = [
    {'shape': 'circle', 'cls': '', 'specimen': '4.2.6', 'profile': 'default',
     'name': 'Vanilla', 'note': 'the reference version: angband/angband e473720, no fixes, default settings.'},
    {'shape': 'circle', 'cls': 'outline', 'specimen': '4.2.6', 'profile': 'munchkin-wdr',
     'name': 'Vanilla + munchkin', 'note': 'vanilla with the munchkin start by class profile '
     f'(<code>munchkin-wdr</code>, <a href="{PROFILES_URL}">settings</a>): no other fixes.'},
    _bbc(4, 42), _bbc(5, 50), _bbc(6, 63), _bbc(7, 76),
    {'shape': 'diamond', 'cls': 'hi', 'specimen': '4.2.6-bbc-munchkin-by-class', 'profile': 'default',
     'name': 'Recommended mix', 'note': 'better-borg-c M7’s 76 carried fixes, with the munchkin start by '
     'class as the version’s own default (no profile override needed).'},
    _bbc(8, 88), _bbc(9, 98),
    _rs(4, 42), _rs(5, 50), _rs(6, 63), _rs(8, 88),
    {'shape': 'cross', 'cls': 'other', 'specimen': 'neo-b3-api2-upstream', 'profile': 'default',
     'name': 'Neo Angband (Mandos, upstream)', 'note': 'a different engine on different seeds — '
     '<strong>never paired</strong> with the C/Rust points above; shown for scale only.'},
]


def exemplar_points(runs, specs, cls=None):
    """(shape, x, y, css-class) per exemplar, x = survivability, y = progress_score
    (median max depth + character level, not a rate); cls restricts to one
    played class (for the per-class grid) or None for all."""
    points, found = [], []
    for e in EXEMPLARS:
        s, meta, arm = find_arm(runs, e['specimen'], e['profile'], specs, cls)
        x = (1 - s['death_rate']) if s and s['death_rate'] is not None else None
        yv = s['progress_score'] if s else None
        points.append((e['shape'], x, yv, e['cls']))
        found.append((s, meta, arm))
    return points, found


def card_exemplars(runs):
    specs = cat_mod.catalogue()['specimens']['specimens']
    points, found = exemplar_points(runs, specs)
    if not any(p[1] is not None for p in points):
        return None
    rows = []
    run_keys = set()
    for e, (s, meta, arm) in zip(EXEMPLARS, found):
        source = specs.get(e['specimen'], {}).get('source')
        src = f' · <a href="{esc(source)}">source</a>' if source else ''
        x = (1 - s['death_rate']) if s and s['death_rate'] is not None else None
        yv = s['progress_score'] if s else None
        badge = (f'<svg class="scatter legend-mark" width="16" height="16" viewBox="0 0 16 16">'
                 f'{mark(e["shape"], 8, 8, e["cls"])}</svg>')
        if meta:
            run_keys.add((meta['experiment']['name'], meta['experiment']['suites'][0]))
            run_cell = (f'<a href="{link(meta)}">{esc(meta["experiment"]["name"])}</a><br>'
                       f'<span class="muted">{esc(meta["experiment"]["suites"][0])} · '
                       f'{esc(meta.get("completed", "?"))}</span>')
        else:
            run_cell = '–'
        rows.append(f'<tr><td class="l">{badge} <strong>{esc(e["name"])}</strong></td>'
                    f'<td class="l">{e["note"]}{src}</td>'
                    f'<td>{pct(x) if x is not None else "–"}</td>'
                    f'<td>{num(yv) if yv is not None else "–"}</td>'
                    f'<td>{num(s["valid"]) if s else "–"}</td>'
                    f'<td class="l">{run_cell}</td></tr>')
    chart = scatter(points, x_label='Survivability — alive at the turn cap',
                    y_label='Progress — median max dungeon level + character level', y_fmt='num')
    legend = ('<div class="wrap"><table><thead><tr><th class="l">Setup</th><th class="l">What it is</th>'
              '<th>Alive at cap</th>'
              '<th title="Median, over finished runs including deaths, of max dungeon level reached + '
              'character level reached. A plain combined figure, not a calibrated score.">Depth + level</th>'
              '<th title="Cells that reached death or the turn cap; the denominator of both columns">'
              'Finished</th><th class="l">Run · suite · completed</th>'
              '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>')
    grid = class_grid(runs, specs)
    snapshots = turn_snapshots_section(found)
    cross_run = len(run_keys) > 1
    answer = (f'The <strong>recommended mix</strong> is ahead of vanilla on both axes and of vanilla + '
              f'munchkin on survival too, in the runs recorded so far — but those points are not one '
              f'controlled comparison: {"at least one of them comes from a different experiment or suite" if cross_run else ""} '
              f'(see the Run column), the gaps are a few percentage points, and no interval is shown here. '
              f'Build better-borg-c’s <code>munchkin-by-class</code> commit as-is (no profile needed) to try '
              f'it; treat it as the current lead, not a confirmed result, until a same-run comparison exists.'
              if cross_run else
              f'The <strong>recommended mix</strong> is ahead of vanilla on both axes, in the one recorded run. '
              f'Build better-borg-c’s <code>munchkin-by-class</code> commit as-is (no profile needed) to try it.')
    return (f'<div class="card wide"><h2>Which setup should I actually run?</h2>'
            f'<p class="answer">{answer}</p>{chart}{legend}'
            f'<p class="foot">Each point is the run with the most finished cells recorded for that exact '
            f'version, profile (and class, in the grid below) — not necessarily the newest, which is only '
            f'the tiebreaker; marker shape, not just color, tells them apart. "Progress" is depth + level '
            f'added unweighted, median over every finished run including deaths (how far a run got, not '
            f'just whether it survived) — gold on hand and a real net worth will join it once they exist '
            f'for more than one specimen. The Neo Angband point is never comparable with the rest: Mandos '
            f'plays a different engine on different seeds.</p>'
            f'{grid}{snapshots}</div>')


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
        if not arm:
            for i in range(len(fractions)):
                by_fraction[i].append((e['shape'], None, None, e['cls']))
            continue
        cap = arm[0]['cap']
        caps.add(cap)
        surv = stats.survival_table(arm, cap, fractions)
        prog = stats.milestone_progress_score(arm, fractions)
        for i in range(len(fractions)):
            by_fraction[i].append((e['shape'], surv[i]['alive'], prog[i]['score'], e['cls']))
    # A mark needs both coordinates (see the docstring); a fraction - or the whole section -
    # with survivability but no progress anywhere draws nothing, so do not show it as if it did.
    if not any(any(p[1] is not None and p[2] is not None for p in pts) for pts in by_fraction):
        return ''
    one_cap = caps.pop() if len(caps) == 1 else None
    shown = [i for i in range(len(fractions)) if any(p[1] is not None and p[2] is not None for p in by_fraction[i])]
    # One scale across every tile, not each fitting its own data: the whole point of this
    # section is watching progress rise from tile to tile, which a self-scaling axis per tile
    # would flatten out (the same review #39 finding the by-class grid had).
    x_max, y_max = axis_limits([p for i in shown for p in by_fraction[i]], y_fmt='num')
    cells = []
    for i in shown:
        f = fractions[i]
        label = f'{int(one_cap * f):,} turns' if one_cap else f'{int(f * 100)}% of cap'
        chart = scatter(by_fraction[i], x_label='', y_label='', compact=True, y_fmt='num', x_max=x_max, y_max=y_max)
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


def class_grid(runs, specs):
    classes = [c for c in cat_mod.CLASSES
               if any(find_arm(runs, e['specimen'], e['profile'], specs, c)[0] for e in EXEMPLARS)]
    if not classes:
        return ''
    by_class = {}
    for cls in classes:
        pts, _ = exemplar_points(runs, specs, cls)
        if any(p[1] is not None for p in pts):
            by_class[cls] = pts
    if not by_class:
        return ''
    # One scale for every cell: the grid's point is comparing classes against
    # each other, which an auto-scaled axis per cell breaks (the same value
    # would draw at a different height in every tile). Survivability is
    # always a rate (0-100% fits every tile); depth + level is a plain
    # number, so its shared max has to be computed from this grid's own data.
    x_max, y_max = axis_limits([p for pts in by_class.values() for p in pts], y_fmt='num')
    cells = [f'<div class="class-cell"><h3>{esc(cls)}</h3>'
             f'{scatter(pts, x_label="", y_label="", compact=True, y_fmt="num", x_max=x_max, y_max=y_max)}</div>'
             for cls, pts in by_class.items()]
    return (f'<h3>By class</h3><p class="foot">The same setups and marks as above, split by the class each '
            f'seed played (<code>classes-1800</code>-style suites assign 200 seeds per class). One fixed '
            f'scale for every tile — survivability left to right (0–100%), depth + level bottom to top — so '
            f'classes can be compared against each other.</p><div class="class-grid">{"".join(cells)}</div>')


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


def versions_page():
    return f'<p><a href="index.html">Borg zoo</a></p><h1>Versions</h1>{versions_table()}'


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
        f'<div class="cards">{"".join(cards)}</div>'
        f'<h2>Experiment runs</h2>'
        + (explain('Every recorded run, newest first. Each page explains its tables.', RUN_COLS)
           + table(RUN_COLS, run_rows) if run_rows else '<p class="muted">No results yet.</p>')
        + FOOTER)
