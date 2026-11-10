"""Static statistics site generated from the results tree."""
import html
import json
import shutil
from pathlib import Path

from . import catalogue as cat_mod
from . import stats

CSS = """
:root{--card:#ffffff;--bg:#fbfaf7;--fg:#1d1d1b;--muted:#6b6a64;--line:#dcd9cf;--head:#f0eee7;--good:#1f7a3a;--bad:#a8321e;--accent:#2f5d8a;--rust:#b58700}
@media (prefers-color-scheme:dark){:root{--card:#1f1e1b;--bg:#171715;--fg:#ecebe6;--muted:#a3a198;--line:#3a3934;--head:#24231f;--good:#6fcf8a;--bad:#f08a76;--accent:#8db7e0;--rust:#b08a1e}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1100px;margin:0 auto;padding:24px 16px 64px}h1{font-size:1.6rem;margin:0 0 4px}h2{font-size:1.2rem;margin:32px 0 8px}h3{font-size:1rem;margin:20px 0 6px}
a{color:var(--accent)}p.note,.muted{color:var(--muted)}.wrap{overflow-x:auto;border:1px solid var(--line);border-radius:6px;margin:8px 0}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}th,td{padding:6px 10px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}
th{background:var(--head);font-weight:600}th:first-child,td:first-child,th.l,td.l{text-align:left}tr:last-child td{border-bottom:0}
.good{color:var(--good)}.bad{color:var(--bad)}code{font-size:.9em;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"DejaVu Sans Mono","Liberation Mono",monospace}
.lead{font-size:1.05rem;max-width:62rem}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,30rem),1fr));gap:16px;margin:16px 0}
.card{border:1px solid var(--line);border-radius:8px;padding:16px;background:var(--card)}
.card.wide{grid-column:1/-1}.chart{max-width:640px;overflow-x:auto}.chart svg{min-width:420px}.card td{white-space:normal}.card h2{margin:0 0 4px;font-size:1.1rem}.card .answer{margin:4px 0 10px}
.card .foot{font-size:.85rem;color:var(--muted);margin-top:8px}
svg.forest{width:100%;height:auto;display:block}
svg.forest text{fill:var(--fg);font:13px system-ui,-apple-system,Segoe UI,sans-serif}
svg.forest .axis{stroke:var(--line)}svg.forest .tick{fill:var(--muted);font-size:11px}
svg.forest .ci{stroke:var(--muted);stroke-width:2}svg.forest .dot{fill:var(--accent)}
svg.forest .dot.hi{fill:var(--good)}svg.forest .val{fill:var(--muted)}svg.forest .head{font-weight:600;font-size:12px}
.big{font-size:2rem;font-weight:650;line-height:1.1}.pair{display:flex;flex-wrap:wrap;gap:16px}.pair .wrap{flex:1 1 14rem}
svg.port{width:100%;height:auto;display:block}svg.port text{fill:var(--fg);font:12px system-ui,-apple-system,Segoe UI,sans-serif}
svg.port .small{font-size:10.5px;fill:var(--muted)}svg.port .head,svg.port .lane{font-weight:600}svg.port .lane.sub{font-weight:400;fill:var(--muted);font-size:10.5px}
svg.port rect.c{fill:var(--head);stroke:var(--line)}svg.port .link{stroke:var(--line);stroke-width:2}
svg.port rect.r{stroke:var(--line);fill:var(--card)}svg.port rect.identical{fill:var(--good);fill-opacity:.18;stroke:var(--good)}
svg.port rect.differs{fill:var(--bad);fill-opacity:.15;stroke:var(--bad)}svg.port rect.unmeasured{stroke:var(--accent)}
svg.port rect.skipped{stroke-dasharray:4 3;fill:none}svg.port rect.not_yet{fill:none;stroke:var(--line)}
svg.scatter{width:100%;height:auto;display:block}
svg.scatter text{fill:var(--fg);font:13px system-ui,-apple-system,Segoe UI,sans-serif}
svg.scatter .axis{stroke:var(--line)}svg.scatter .tick{fill:var(--muted);font-size:11px}
svg.scatter .head{font-weight:600;font-size:12px}
svg.scatter .dot{stroke:var(--card);stroke-width:1.5}
svg.scatter .lbl{fill:var(--fg);font:600 11px system-ui,-apple-system,Segoe UI,sans-serif;
 paint-order:stroke;stroke:var(--card);stroke-width:3px;stroke-linejoin:round}
svg.scatter.compact{max-width:140px}
.legend-mark{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:3px;vertical-align:-1px}
.chip{display:inline-block;padding:3px 10px;margin:2px 4px 2px 0;border:1px solid var(--line);border-radius:999px;text-decoration:none;color:var(--fg)}
.chip:hover{border-color:var(--accent)}
.class-links .chip{font-size:1rem;padding:7px 16px;border-color:var(--accent);font-weight:600}
.big-chip{display:inline-block;padding:11px 20px;margin:4px 10px 4px 0;border:1px solid var(--accent);border-radius:8px;font-weight:600;text-decoration:none}
.big-chip:hover{background:var(--accent);color:#fff}
.policy-switch{margin:6px 0 14px}
.links-head{margin-top:18px}
.chart-echarts{width:100%;max-width:680px}
.class-cell .chart-echarts{max-width:none}
.class-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(9rem,1fr));gap:12px;margin:8px 0}
.class-cell{border:1px solid var(--line);border-radius:6px;padding:8px;text-align:center}
.class-cell h3{margin:0 0 4px;font-size:.85rem}
/* The generic .chart rule below is sized for the big charts (a 420px floor
   so they don't get squished on mobile) and wraps every chart, this small
   one included; without this override each class tile fought its own box
   for width and scrolled individually instead of just... fitting. */
.class-cell .chart{max-width:none;overflow-x:visible}
.class-cell .chart svg{min-width:0;max-width:100%}
p.tabs{display:flex;gap:4px;margin:8px 0 18px;border-bottom:1px solid var(--line)}
p.tabs .tab{padding:6px 14px;color:var(--muted);text-decoration:none;border-bottom:2px solid transparent}
p.tabs .tab.active{color:var(--fg);font-weight:600;border-bottom-color:var(--accent)}
th{white-space:normal;vertical-align:bottom}th[title]{text-decoration:underline dotted;text-underline-offset:3px;cursor:help}
p.how{max-width:62rem;margin:4px 0}p.example{max-width:62rem;margin:4px 0;padding:6px 10px;border-left:3px solid var(--accent);background:var(--card)}
details.cols{margin:4px 0 12px;max-width:62rem}details.cols summary{cursor:pointer;color:var(--accent)}
details.cols dl{margin:6px 0;display:grid;grid-template-columns:minmax(8rem,max-content) 1fr;gap:4px 12px}
details.cols dt{font-weight:600}details.cols dd{margin:0}
@media (max-width:600px){details.cols dl{grid-template-columns:1fr}details.cols dd{margin:0 0 6px}}
"""


def esc(x):
    return html.escape(str(x))


def pct(x):
    return '–' if x is None else f'{100 * x:.0f}%'


def ci(pair):
    lo, hi = pair
    return '–' if lo is None else f'{100 * lo:.0f}–{100 * hi:.0f}%'


def num(x):
    return '–' if x is None else (f'{x:,.0f}' if isinstance(x, (int, float)) else esc(x))


def pval(p):
    return '–' if p is None else (f'{p:.3f}' if p >= 0.001 else '<0.001')


def page(title, body, base='', charts=False):
    """Wrap a page body. `base` is the relative prefix for assets (classes/
    pages live one level down); `charts` includes the vendored ECharts
    library (deferred: chart init code waits for DOMContentLoaded)."""
    lib = '<script src="{}echarts.min.js" defer></script>'.format(base) if charts else ''
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{esc(title)}</title>{lib}<style>{CSS}</style></head><body><main>{body}</main></body></html>\n')


def table(headers, rows, left=1):
    """headers: names, or (name, meaning) pairs; a meaning becomes the header's tooltip."""
    head = ''.join(f'<th class="{"l" if i < left else ""}"' + (f' title="{esc(h[1])}"' if isinstance(h, tuple) else '')
                   + f'>{esc(h[0] if isinstance(h, tuple) else h)}</th>' for i, h in enumerate(headers))
    body = ''.join('<tr>' + ''.join(f'<td class="{"l" if i < left else ""}">{v}</td>' for i, v in enumerate(r)) + '</tr>'
                   for r in rows)
    return f'<div class="wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def explain(how, columns=(), example=None, open_=False):
    """How to read a table: a sentence or two, a worked example, and what each column means."""
    out = f'<p class="how">{how}</p>'
    if example:
        out += f'<p class="example"><strong>Example:</strong> {example}</p>'
    described = [c for c in columns if isinstance(c, tuple)]
    if described:
        out += (f'<details class="cols"{" open" if open_ else ""}><summary>What each column means</summary><dl>'
                + ''.join(f'<dt>{esc(name)}</dt><dd>{esc(meaning)}</dd>' for name, meaning in described)
                + '</dl></details>')
    return out


VERSION_COL = ('Version', 'The Borg version, and the settings profile when the experiment varies it. '
                          'In brackets: how many fixes from the tracker it carries.')
OUTCOME_COLS = [
    VERSION_COL,
    ('Runs', 'Seeds played: one game per seed.'),
    ('Finished', 'Runs that reached an endpoint: the character died, or was alive at the turn cap. '
                 'Only these count in the rates.'),
    ('Deaths', 'Finished runs in which the character died before the cap.'),
    ('Death rate', 'Deaths divided by finished runs.'),
    ('Death rate range', 'The 95% range (Wilson interval) for the death rate: with this many seeds, the true '
                         'rate most likely lies in it. Two versions whose ranges overlap widely may not differ.'),
    (f'Alive at cap, reached DL{stats.DEPTH_GOAL}', 'Share of finished runs that were alive at the turn cap and '
                                                    f'had reached dungeon level {stats.DEPTH_GOAL} on the way: '
                                                    'survived and made progress. Staying shallow to survive '
                                                    'does not count.'),
    ('Its range', 'The 95% range for the previous column.'),
    ('Median max depth', 'The middle value, over finished runs, of the deepest dungeon level reached (0 = town).'),
    ('Median max level', 'The middle value of the highest character level reached.'),
    ('Median death turn', 'The middle engine turn at which the dying runs died. Lower means earlier deaths.'),
    ('Other outcomes', 'Runs with no endpoint, by kind: stalled (game time stopped advancing), wall_timeout '
                       '(out of real time), crash, harness_failure, config_error (the settings did not take '
                       'effect). Never counted as deaths.'),
]
PAIRED_COLS = [
    VERSION_COL,
    ('Pairs', 'Seeds on which both this arm and the control finished. Both start from the same seed and '
              'character, so the two games are compared seed by seed.'),
    ('Rescued', 'Seeds where the control died and this arm was alive at the cap.'),
    ('Newly killed', 'Seeds where the control was alive at the cap and this arm died.'),
    ('Both died', 'Seeds where both died. They say nothing about which is better.'),
    ('Both lived', 'Seeds where both were alive at the cap. They say nothing about which is better.'),
    ('Identical play', 'Seeds where both games were the same move for move. When it equals Pairs, the '
                       'difference between the arms never changed play on this suite.'),
    ('p (death)', 'Exact McNemar test of Rescued against Newly killed: the chance of a split at least this '
                  'uneven if both arms were equally deadly. Below 0.05 suggests a real difference; with many '
                  'rows, some low values turn up by chance.'),
    (f'DL{stats.DEPTH_GOAL} alive: gained', f'Seeds where this arm was alive at the cap having reached '
                                            f'DL{stats.DEPTH_GOAL}, and the control was not.'),
    (f'DL{stats.DEPTH_GOAL} alive: lost', f'Seeds where the control was alive at the cap having reached '
                                          f'DL{stats.DEPTH_GOAL}, and this arm was not.'),
    (f'p (DL{stats.DEPTH_GOAL} alive)', 'The same test on gained against lost.'),
]
UNFINISHED_COLS = [
    VERSION_COL,
    ('Seed', 'The seed of the run; rerunning it reproduces the stop.'),
    ('Outcome', 'Why the run has no endpoint: stalled, wall_timeout, crash, harness_failure or config_error.'),
    ('Last turn', 'The engine turn at which the game stopped advancing.'),
    ('Stall kind', 'A heuristic label over the counters: level_cycle (changes level without game time passing), '
                   'zero_energy_retry (repeats without spending energy), energy_without_time (energy rises, the '
                   'clock does not), no_decisions (the Borg stopped deciding), keys_without_time (borgh: keys '
                   'sent while the turn stays frozen).'),
    ('Decisions Δ', 'Borg decisions made while the game turn stayed at Last turn.'),
    ('Energy Δ', 'Player energy gained over the same span.'),
    ('Level changes (sampled)', 'Level changes seen at the frozen turn. States are sampled every 100 decisions, '
                                'so this is a lower bound.'),
    ('Most repeated at the last turn', 'The Borg notes, or keys, repeated most often at the frozen turn.'),
]


def paired_example(meta, r, v, control):
    """A worked reading of one paired row; control names the arm it is paired with."""
    if not v['pairs']:
        return None
    name = esc(r['specimen']) + (f' · {esc(r["profile"])}' if len(meta['experiment']['profiles']) > 1 else '')
    same = (f' {v["identical_traces"]:,} of the {v["pairs"]:,} games were identical move for move.'
            if v['identical_traces'] else '')
    if v['identical_traces'] == v['pairs']:
        verdict = 'every game was the same, so the two cannot differ on this suite'
    elif v['death_p'] is not None and v['death_p'] < 0.05:
        verdict = 'a split this uneven is unlikely by chance'
    else:
        verdict = 'a split like this happens easily by chance, so no difference is shown'
    return (f'on the {v["pairs"]:,} seeds that both {name} and {control} finished, {name} survived '
            f'{v["rescued"]} seeds on which {control} died, and died on {v["newly_killed"]} seeds that {control} '
            f'survived. The other {v["both_died"] + v["both_lived"]:,} seeds ended the same way for both '
            f'({v["both_died"]:,} both died, {v["both_lived"]:,} both lived).{same} p (death) = {pval(v["death_p"])}: '
            f'{verdict}.')


def example_for(meta, versus, key, control_specimen, control_profile):
    """The paired row with the smallest p, read out in words."""
    r = min(versus, key=lambda r: r[key]['death_p'] if r[key]['death_p'] is not None else 2)
    many = len(meta['experiment']['profiles']) > 1
    if key == 'vs_version':
        control = esc(control_specimen) + (f' · {esc(r["profile"])}' if many else '')
    else:
        control = f'{esc(r["specimen"])} · {esc(control_profile)}'
    return paired_example(meta, r, r[key], control)


def load_runs(results):
    runs = []
    for meta_path in sorted(Path(results).glob('*/*/meta.json')):
        meta = json.loads(meta_path.read_text())
        cells_path = meta_path.parent / 'cells.jsonl'
        cells = [json.loads(line) for line in cells_path.read_text().splitlines() if line.strip()]
        runs.append((meta, cells, meta_path.parent))
    runs.sort(key=lambda r: r[0].get('completed', ''), reverse=True)
    return runs


def arm_label(meta, specimen, profile):
    spec = meta['catalogue']['specimens'].get(specimen, {})
    label = esc(specimen)
    if spec.get('carries') is not None:
        label += f' <span class="muted">({spec["carries"]} carries)</span>'
    if len(meta['experiment']['profiles']) > 1:
        label += f' · {esc(profile)}'
    return label


def run_cutoff(exp, specimens, completed, harness_commit=''):
    """(pre_cutoff, straddles) for one recorded run: pre_cutoff is true when
    the run was recorded before the mode cutoff (borg-zoo#54) - before
    2026-11-10, or that same day on the pre-restart harness pin (runs
    collected on the cutoff date itself, e.g. classes-m9-m10 run
    42816432188). straddles, when the experiment's better-borg-c arms sit on
    both sides of the cutoff, so the same profile name is a different game
    across arms and the cross-version pairings are suppressed."""
    sides = {name: cat_mod.mode_side(specimens.get(name, {})) for name in exp['specimens']}
    present = {side for side in sides.values() if side}
    pre = (bool(exp.get('pre_cutoff')) or completed[:10] < cat_mod.MODE_CUTOFF_DATE
           or (completed[:10] == cat_mod.MODE_CUTOFF_DATE
               and harness_commit and harness_commit != cat_mod.MODE_CUTOFF_HARNESS))
    return pre, len(present) > 1


def cutoff_note(exp, specimens, completed, harness_commit=''):
    """The one-paragraph mode-cutoff statement a run page shows: the cutoff
    itself, a pre-cutoff label when the run predates it, and what that does
    to its comparisons."""
    pre, straddles = run_cutoff(exp, specimens, completed, harness_commit)
    if not pre and not straddles:
        return ''
    cut = cat_mod.MODE_CUTOFF[:9]
    lines = [f'<p class="note"><strong>Mode cutoff {cut} (better-borg-c PR 302, '
             f'{cat_mod.MODE_CUTOFF_DATE}, borg-zoo#54):</strong> from that commit '
             '<code>borg_munchkin_by_class</code> defaults to TRUE, so specimens before it do not carry the '
             'class rule and the same profile name plays a different game on either side. Version pairings '
             'across the cutoff are not computed.']
    if pre:
        lines.append(' <strong>These results are pre-cutoff:</strong> recorded before the explicit mode profiles '
                     '(<code>normal</code>, <code>munchkin-class</code>, <code>munchkin-on</code>, '
                     '<code>lunal</code>) existed; their <code>default</code> arms mean whatever each build\'s '
                     'own defaults said. Kept as recorded, excluded from comparisons that straddle the cutoff.')
    lines.append('</p>')
    return ''.join(lines)


def run_page(meta, cells):
    exp = meta['experiment']
    specimens = meta['catalogue']['specimens']
    analysis = stats.analyse(exp, cells, specimens)
    parts = [f'<p><a href="../../index.html">All experiments</a></p>',
             f'<h1>{esc(exp["name"])}</h1><p>{esc(exp.get("description", ""))}</p>',
             (f'<p><strong>Prespecified:</strong> {esc(exp["prespecified"])}</p>' if exp.get('prespecified') else ''),
             f'<p class="muted">Run {esc(meta["run_id"])} · completed {esc(meta.get("completed", "?"))} · '
             f'<a href="{esc(meta.get("run_url", "#"))}">workflow run</a> · <a href="cells.jsonl">raw cells (JSON lines)</a></p>',
             '<p class="note">An <em>arm</em> is one Borg version run with one settings profile; every arm plays '
             'the same seeds, one game per seed. Results are descriptive unless the experiment says it is '
             'prespecified above. Ranges are Wilson 95% intervals; paired p-values are exact McNemar tests on the '
             'seeds where both arms finished. Two outcomes are measured: <strong>death</strong> before the turn '
             f'cap, and <strong>alive at the cap having reached dungeon level {stats.DEPTH_GOAL}</strong> '
             '(survived and made progress). The owner has not yet chosen which one is primary.</p>']
    parts.append(cutoff_note(exp, specimens, meta.get('completed', ''),
                             (meta.get('catalogue') or {}).get('harness', {}).get('commit', '')))
    for suite, rows in analysis.items():
        s = meta['catalogue']['suites'][suite]
        parts.append(f'<h2>Suite {esc(suite)}</h2><p class="muted">{esc(s["description"])} · '
                     f'{len(s["seeds"])} seeds · cap {s["cap"]:,} engine turns · birth {esc(s["birth"])}</p>')
        parts.append('<h3>Outcomes per arm</h3>')
        first = rows[0]['summary'] if rows else None
        parts.append(explain(
            'One row per arm: a Borg version, with a settings profile when the experiment varies it. Every arm '
            'plays the same seeds. The main figure is the death rate before the turn cap, with its 95% range.',
            OUTCOME_COLS,
            (f'{esc(rows[0]["specimen"])}: {first["valid"]:,} of {first["cells"]:,} runs finished and '
             f'{first["deaths"]:,} died ({pct(first["death_rate"])}); with this many seeds the true death rate '
             f'is most likely {ci(first["death_ci"])}.') if first and first['valid'] else None,
            open_=True))
        parts.append(table(
            OUTCOME_COLS,
            [[arm_label(meta, r['specimen'], r['profile']), r['summary']['cells'], r['summary']['valid'],
              r['summary']['deaths'], pct(r['summary']['death_rate']), ci(r['summary']['death_ci']),
              pct(r['summary']['goal_rate']), ci(r['summary']['goal_ci']),
              num(r['summary']['median_max_depth']), num(r['summary']['median_max_level']),
              num(r['summary']['median_death_turn']),
              esc(', '.join(f'{k} {v}' for k, v in r['summary']['counts'].items()
                            if v and k not in stats.VALID)) or '–']
             for r in rows]))
        control_profile = exp.get('control_profile', exp['profiles'][0])
        for key, title in (('vs_version', f'Paired against {esc(exp["control"])}, same profile'),
                           ('vs_profile', f'Paired against profile {esc(control_profile)}, same version')):
            versus = [r for r in rows if r[key]]
            if not versus:
                continue
            control = esc(exp['control']) if key == 'vs_version' else f'profile {esc(control_profile)}'
            parts.append(f'<h3>{title}</h3>')
            parts.append(explain(
                f'Each row compares one arm with the control ({control}) seed by seed. Seeds where both died or '
                'both lived cannot tell them apart; the comparison rests on the seeds that ended differently: '
                '<span class="good">Rescued</span> (only the control died) against '
                '<span class="bad">Newly killed</span> (only this arm died). If the change made no difference, '
                'those two would be about equal.',
                PAIRED_COLS,
                example_for(meta, versus, key, exp['control'], control_profile),
                open_=True))
            parts.append(table(
                PAIRED_COLS,
                [[arm_label(meta, r['specimen'], r['profile']), v['pairs'],
                  f'<span class="good">{v["rescued"]}</span>', f'<span class="bad">{v["newly_killed"]}</span>',
                  v['both_died'], v['both_lived'], v['identical_traces'], pval(v['death_p']),
                  v['goal_gained'], v['goal_lost'], pval(v['goal_p'])]
                 for r in versus for v in [r[key]]]))
        unfinished = [c for c in cells if c['suite'] == suite and c['outcome'] not in stats.VALID]
        if unfinished:
            parts.append('<h3>Runs that did not finish</h3>')
            parts.append(explain(
                'Runs that reached neither death nor the turn cap, one row each. They are left out of every '
                'rate above. A stall usually means the Borg loops while game time stands still; each one is a '
                'lead for a liveness bug. Stall kind is a heuristic label; the counters and the notes are the '
                'evidence.', UNFINISHED_COLS))
            rows_u = []
            for c in unfinished:
                st = c.get('stall') or {}
                top = st.get('top_notes_at_last_turn') or st.get('top_keys_at_last_turn') or []
                rows_u.append([arm_label(meta, c['specimen'], c['profile']), c['seed'], esc(c['outcome']),
                               num(st.get('last_turn', c['final'].get('turn'))), esc(st.get('kind', '–')),
                               num(st.get('decisions_delta')), num(st.get('energy_delta')),
                               num(st.get('depth_changes')),
                               esc('; '.join(f'{t} ×{n}' for t, n in top[:2])) or '–'])
            parts.append(table(UNFINISHED_COLS, rows_u, left=1))
        for field, title in (('class', 'Deaths by class'), ('race', 'Deaths by race')):
            per = stats.by_character(exp, cells, field).get(suite)
            many = {'class': 'classes', 'race': 'races'}[field]
            if not per or len(per) < 2:
                continue
            arms = [a['arm'] for a in per[0]['arms']]
            parts.append(f'<h3>{title}</h3>')
            parts.append(explain(
                f'One row per {field}, one column per arm. Each cell is deaths / finished runs (death rate) for '
                f'characters of that {field}. Read down a column to see which {many} die most; read across a row '
                f'to see whether a version changed that {field}\'s risk. Cells hold a few hundred runs or fewer, '
                'so read the pattern, not single values.'))
            parts.append(table([field.capitalize()] + [s_ if len(exp['profiles']) == 1 else f'{s_} · {p_}'
                                                       for s_, p_ in arms],
                               [[esc(r['value'])] + [f'{a["deaths"]}/{a["n"]} ({pct(a["rate"])})' if a['n'] else '–'
                                                      for a in r['arms']] for r in per]))
        parts.append('<h3>Share alive by engine turn</h3>')
        parts.append(explain(
            'For each arm, the share of finished runs whose character was still alive at each engine turn (the '
            'last column is the turn cap). Read along a row to see when the deaths happen: an arm with fewer '
            'early deaths keeps a higher share in the first columns.'))
        turns = [x['turn'] for x in rows[0]['survival']] if rows else []
        parts.append(table(['Version'] + [f'{t:,}' for t in turns],
                           [[arm_label(meta, r['specimen'], r['profile'])] + [pct(x['alive']) for x in r['survival']]
                            for r in rows]))
        parts.append('<h3>Depth reached</h3>')
        marks = [x['depth'] for x in rows[0]['depths']] if rows else []
        no_marks = {k for k, v in meta['catalogue']['specimens'].items() if v.get('kind') == 'borg-rs'}
        parts.append(explain(
            'For each arm and dungeon level (DL): the share of finished runs that ever reached that level, then '
            'the median engine turn at which they first got there. A higher share reached sooner means faster '
            'descent, which is not the same as safer play.'
            + (' borg-rs runs record no depth by turn, so their cells are empty.' if no_marks & set(exp['specimens'])
               else '')))
        parts.append(table(['Version'] + [f'DL{m}: share · median turn' for m in marks],
                           [[arm_label(meta, r['specimen'], r['profile'])] +
                            (['not recorded'] * len(marks) if r['specimen'] in no_marks else
                             [f'{pct(x["reached"])} · {num(x["median_turn"])}' for x in r['depths']])
                            for r in rows]))
        has_milestones = any(x['n'] for r in rows for x in r['milestones'])
        if has_milestones:
            parts.append('<h3>Level, max depth and gold by engine turn</h3>')
            has_gold = any(x.get('median_gold') is not None for r in rows for x in r['milestones'])
            parts.append(explain(
                'For each arm, at 25/50/75% of the cap and at the cap itself: the median character level and '
                'the median max depth over finished runs that recorded it, among those still going at that '
                'turn (a death before it is simply excluded, not substituted). Gold on hand is shown only '
                'where the harness logs it; it is not a net worth — inventory and equipment are hashed, not '
                'valued (docs/DESIGN.md, "Open questions").' if has_gold else
                'For each arm, at 25/50/75% of the cap and at the cap itself: the median character level and '
                'the median max depth over finished runs that recorded it, among those still going at that '
                'turn (a death before it is simply excluded, not substituted). This harness logs no gold or '
                'item value, so there is no net-worth column (docs/DESIGN.md, "Open questions").'))
            m_turns = [x['turn'] for x in rows[0]['milestones']] if rows else []

            def fmt_milestone(x):
                if not x['n']:
                    return '–'
                cell_ = f'lv {num(x["median_level"])} · DL{num(x["median_max_depth"])}'
                return cell_ + (f' · {num(x["median_gold"])}g' if has_gold and x.get('median_gold') is not None
                               else '')
            parts.append(table(['Version'] + [f'{t:,}' if t is not None else '–' for t in m_turns],
                               [[arm_label(meta, r['specimen'], r['profile'])] +
                                [fmt_milestone(x) for x in r['milestones']] for r in rows]))
    parts.append('<h2>Specimens and environment</h2>')
    parts.append(explain('The Borg versions in this experiment, each built from the commit shown.'))
    parts.append(table(['Specimen', ('Ref', 'The commit that was built.'),
                        ('Carries', 'Fixes from the tracker carried by this version.'), 'Label'],
                       [[esc(k), f'<code>{esc(v["ref"][:12])}</code>', num(v.get('carries')), esc(v.get('label', ''))]
                        for k in exp['specimens'] for v in [meta['catalogue']['specimens'][k]]]))
    env = meta.get('environment', {})
    parts.append(f'<p class="muted">Harness {esc(meta["catalogue"]["harness"]["repository"])} '
                 f'<code>{esc(meta["catalogue"]["harness"]["commit"][:12])}</code> · '
                 f'compilers {esc(", ".join(env.get("compilers", [])))} · platforms {esc(", ".join(env.get("platforms", [])))} · '
                 f'calendar: native clock, all arms in one workflow run</p>')
    return page(f'{exp["name"]} · borg-zoo', ''.join(parts))


def build_site(results, out):
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    runs = load_runs(results) if Path(results).exists() else []
    rows = []
    for meta, cells, src in runs:
        target = out / 'runs' / meta['experiment']['name'] / meta['run_id']
        target.mkdir(parents=True, exist_ok=True)
        (target / 'index.html').write_text(run_page(meta, cells))
        shutil.copy(src / 'cells.jsonl', target / 'cells.jsonl')
        shutil.copy(src / 'meta.json', target / 'meta.json')
        finished = sum(1 for c in cells if c['outcome'] in stats.VALID)
        rows.append([f'<a href="runs/{esc(meta["experiment"]["name"])}/{esc(meta["run_id"])}/index.html">'
                     f'{esc(meta["experiment"]["name"])}</a>', esc(meta.get('completed', '?')),
                     len(meta['experiment']['specimens']), len(meta['experiment']['profiles']),
                     len(cells), finished])
    from . import landing
    shutil.copy(Path(__file__).parent / 'assets' / 'echarts.min.js', out / 'echarts.min.js')
    (out / 'index.html').write_text(page('Borg zoo', landing.overview_page(runs), charts=True))
    for policy in landing.POLICIES:
        (out / f'{policy["slug"]}.html').write_text(
            page(f'{policy["title"]} · borg-zoo', landing.comparison_page(runs, policy), charts=True))
    (out / 'detailed.html').write_text(page('Detailed · borg-zoo', landing.landing_page(runs, rows)))
    (out / 'stalls.html').write_text(page('Stalls and crashes · borg-zoo', landing.stalls_page(runs)))
    (out / 'versions.html').write_text(page('Versions · borg-zoo', landing.versions_page()))
    (out / '.nojekyll').write_text('')
    for slug, title, body in landing.class_pages(runs):
        (out / 'classes').mkdir(exist_ok=True)
        (out / 'classes' / f'{slug}.html').write_text(page(title, body, base='../', charts=True))
    return len(runs)
