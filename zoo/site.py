"""Static statistics site generated from the results tree."""
import html
import json
import shutil
from pathlib import Path

from . import stats

CSS = """
:root{--bg:#fbfaf7;--fg:#1d1d1b;--muted:#6b6a64;--line:#dcd9cf;--head:#f0eee7;--good:#1f7a3a;--bad:#a8321e;--accent:#2f5d8a}
@media (prefers-color-scheme:dark){:root{--bg:#171715;--fg:#ecebe6;--muted:#a3a198;--line:#3a3934;--head:#24231f;--good:#6fcf8a;--bad:#f08a76;--accent:#8db7e0}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1100px;margin:0 auto;padding:24px 16px 64px}h1{font-size:1.6rem;margin:0 0 4px}h2{font-size:1.2rem;margin:32px 0 8px}h3{font-size:1rem;margin:20px 0 6px}
a{color:var(--accent)}p.note,.muted{color:var(--muted)}.wrap{overflow-x:auto;border:1px solid var(--line);border-radius:6px;margin:8px 0}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}th,td{padding:6px 10px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}
th{background:var(--head);font-weight:600}th:first-child,td:first-child,th.l,td.l{text-align:left}tr:last-child td{border-bottom:0}
.good{color:var(--good)}.bad{color:var(--bad)}code{font-size:.9em}
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


def page(title, body):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{esc(title)}</title><style>{CSS}</style></head><body><main>{body}</main></body></html>\n')


def table(headers, rows, left=1):
    head = ''.join(f'<th class="{"l" if i < left else ""}">{esc(h)}</th>' for i, h in enumerate(headers))
    body = ''.join('<tr>' + ''.join(f'<td class="{"l" if i < left else ""}">{v}</td>' for i, v in enumerate(r)) + '</tr>'
                   for r in rows)
    return f'<div class="wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


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


def run_page(meta, cells):
    exp = meta['experiment']
    analysis = stats.analyse(exp, cells)
    parts = [f'<p><a href="../../index.html">All experiments</a></p>',
             f'<h1>{esc(exp["name"])}</h1><p>{esc(exp.get("description", ""))}</p>',
             (f'<p><strong>Prespecified:</strong> {esc(exp["prespecified"])}</p>' if exp.get('prespecified') else ''),
             f'<p class="muted">Run {esc(meta["run_id"])} · completed {esc(meta.get("completed", "?"))} · '
             f'<a href="{esc(meta.get("run_url", "#"))}">workflow run</a> · <a href="cells.jsonl">raw cells (JSON lines)</a></p>',
             '<p class="note">Descriptive results from small suites. Intervals are Wilson 95%; '
             'paired p-values are exact McNemar tests on the seeds where both arms finished. '
             'Neither is a prespecified test, and nothing here is a claim of improvement. '
             f'"Goal" means alive at the turn cap having reached dungeon level {stats.DEPTH_GOAL}; '
             'the owner has not yet fixed the primary endpoint.</p>']
    for suite, rows in analysis.items():
        s = meta['catalogue']['suites'][suite]
        parts.append(f'<h2>Suite {esc(suite)}</h2><p class="muted">{esc(s["description"])} · '
                     f'{len(s["seeds"])} seeds · cap {s["cap"]:,} engine turns · birth {esc(s["birth"])}</p>')
        parts.append('<h3>Outcomes per arm</h3>')
        parts.append(table(
            ['Arm', 'Runs', 'Finished', 'Deaths', 'Death rate', '95% CI', 'Goal', 'Goal 95% CI',
             'Median max depth', 'Median max level', 'Median death turn', 'Other outcomes'],
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
            parts.append(f'<h3>{title}</h3>')
            parts.append(table(
                ['Arm', 'Pairs', 'Rescued', 'Newly killed', 'Both died', 'Both lived', 'Identical play', 'p (death)',
                 'Goal gained', 'Goal lost', 'p (goal)'],
                [[arm_label(meta, r['specimen'], r['profile']), v['pairs'],
                  f'<span class="good">{v["rescued"]}</span>', f'<span class="bad">{v["newly_killed"]}</span>',
                  v['both_died'], v['both_lived'], v['identical_traces'], pval(v['death_p']),
                  v['goal_gained'], v['goal_lost'], pval(v['goal_p'])]
                 for r in versus for v in [r[key]]]))
        unfinished = [c for c in cells if c['suite'] == suite and c['outcome'] not in stats.VALID]
        if unfinished:
            parts.append('<h3>Runs that did not finish</h3>')
            parts.append('<p class="muted">Stall kind is a heuristic over the counters: a level cycle spends '
                         'energy across level changes without game time; a zero-energy retry repeats without '
                         'spending energy. The counters and the notes are the evidence.</p>')
            rows_u = []
            for c in unfinished:
                st = c.get('stall') or {}
                top = st.get('top_notes_at_last_turn') or st.get('top_keys_at_last_turn') or []
                rows_u.append([arm_label(meta, c['specimen'], c['profile']), c['seed'], esc(c['outcome']),
                               num(st.get('last_turn', c['final'].get('turn'))), esc(st.get('kind', '–')),
                               num(st.get('decisions_delta')), num(st.get('energy_delta')),
                               num(st.get('depth_changes')),
                               esc('; '.join(f'{t} ×{n}' for t, n in top[:2])) or '–'])
            parts.append(table(['Arm', 'Seed', 'Outcome', 'Last turn', 'Stall kind', 'Decisions Δ', 'Energy Δ',
                                'Level changes', 'Most repeated at the last turn'], rows_u, left=1))
        parts.append('<h3>Share alive by engine turn</h3>')
        turns = [x['turn'] for x in rows[0]['survival']] if rows else []
        parts.append(table(['Arm'] + [f'{t:,}' for t in turns],
                           [[arm_label(meta, r['specimen'], r['profile'])] + [pct(x['alive']) for x in r['survival']]
                            for r in rows]))
        parts.append('<h3>Depth reached</h3>')
        marks = [x['depth'] for x in rows[0]['depths']] if rows else []
        parts.append(table(['Arm'] + [f'DL{m}: share · median turn' for m in marks],
                           [[arm_label(meta, r['specimen'], r['profile'])] +
                            [f'{pct(x["reached"])} · {num(x["median_turn"])}' for x in r['depths']]
                            for r in rows]))
    parts.append('<h2>Specimens and environment</h2>')
    parts.append(table(['Specimen', 'Ref', 'Carries', 'Label'],
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
    body = ('<h1>Borg zoo</h1><p>Seed-suite comparisons of Angband Borg versions and configurations. '
            'Source and method: <a href="https://github.com/diegoami/borg-zoo">diegoami/borg-zoo</a>.</p>'
            '<h2>Experiment runs</h2>' +
            (table(['Experiment', 'Completed', 'Specimens', 'Profiles', 'Runs', 'Finished'], rows)
             if rows else '<p class="muted">No results yet.</p>'))
    (out / 'index.html').write_text(page('Borg zoo', body))
    (out / '.nojekyll').write_text('')
    return len(runs)
