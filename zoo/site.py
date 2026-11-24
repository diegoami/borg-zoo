"""Static statistics site generated from the results tree."""
import gzip
import html
import re
import json
import shutil
from functools import lru_cache
from statistics import mean
from pathlib import Path

from . import catalogue as cat_mod
from . import stats, configuration
from .briefs import question, profile_label

# Raw cell files are not copied into Pages: together they are about as large
# as the whole results branch (991 MB on 2026-11-15, against Pages' 1 GB
# limit, borg-zoo#114 T0). The results branch is append-only, so the file a
# run wrote stays at the same path there and a link to it is permanent.
RESULTS_RAW = 'https://raw.githubusercontent.com/diegoami/borg-zoo/results/results'


def raw_cells_url(results_path):
    """Link to a run's cells.jsonl on the results branch ('<experiment>/<run>')."""
    return f'{RESULTS_RAW}/{results_path}/cells.jsonl'


def results_path(src):
    return f'{Path(src).parent.name}/{Path(src).name}'

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
.experiment-brief{margin:16px 0;overflow-wrap:anywhere}.experiment-brief dl{display:grid;grid-template-columns:8rem 1fr;gap:8px 16px;margin:12px 0}
.experiment-brief dt{font-weight:600}.experiment-brief dd{margin:0;overflow-wrap:anywhere}
.experiment-brief ul{padding-left:20px;margin:0}.experiment-brief .question{font-size:1.25rem;max-width:55rem;margin:8px 0 16px}
details.background{margin:16px 0}details.background summary{cursor:pointer;color:var(--accent)}
@media(max-width:600px){.experiment-brief dl{grid-template-columns:1fr;gap:4px}.experiment-brief dd{margin-bottom:8px}}
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
p.tabs{display:flex;flex-wrap:wrap;gap:4px;margin:8px 0 18px;border-bottom:1px solid var(--line)}
p.tabs .tab{padding:6px 14px;color:var(--muted);text-decoration:none;border-bottom:2px solid transparent}
p.tabs .tab.active{color:var(--fg);font-weight:600;border-bottom-color:var(--accent)}
th{white-space:normal;vertical-align:bottom}th[title]{text-decoration:underline dotted;text-underline-offset:3px;cursor:help}
p.how{max-width:62rem;margin:4px 0}p.example{max-width:62rem;margin:4px 0;padding:6px 10px;border-left:3px solid var(--accent);background:var(--card)}
details.cols{margin:4px 0 12px;max-width:62rem}details.cols summary{cursor:pointer;color:var(--accent)}
details.cols dl{margin:6px 0;display:grid;grid-template-columns:minmax(8rem,max-content) 1fr;gap:4px 12px}
details.cols dt{font-weight:600}details.cols dd{margin:0}
@media (max-width:600px){details.cols dl{grid-template-columns:1fr}details.cols dd{margin:0 0 6px}}
details.fold{margin:20px 0;border:1px solid var(--line);border-radius:8px;background:var(--card);padding:2px 14px 10px}
details.fold>summary{cursor:pointer;font-weight:700;font-size:1.15rem;padding:8px 0}
details.fold>summary:hover{color:var(--accent)}details.fold[open]>summary{margin-bottom:8px;border-bottom:1px solid var(--line)}
.subtitle{color:var(--muted);font-size:1.05rem;margin:0 0 10px}
.facts{margin:10px 0}.facts dl{display:grid;grid-template-columns:max-content 1fr;gap:3px 16px;margin:0}.facts dt{color:var(--muted);white-space:nowrap}.facts dd{margin:0}
details.fold dl{display:grid;grid-template-columns:max-content 1fr;gap:3px 16px;margin:8px 0}details.fold dt{color:var(--muted)}details.fold dd{margin:0}
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


def fold(title, inner):
    """A page section that starts collapsed; the heading is the summary (owner, 2026-11-24)."""
    return f'<details class="fold"><summary>{title}</summary>{inner}</details>'


def explain_folded(how, columns=(), example=None):
    """The how-to-read text behind one closed fold: the table shows first (owner, 2026-11-24)."""
    out = f'<p class="how">{how}</p>'
    if example:
        out += f'<p class="example"><strong>Example:</strong> {example}</p>'
    described = [c for c in columns if isinstance(c, tuple)]
    if described:
        out += '<dl>' + ''.join(f'<dt>{esc(n)}</dt><dd>{esc(m)}</dd>' for n, m in described) + '</dl>'
    return f'<details class="cols"><summary>How to read this table</summary>{out}</details>' 


VERSION_COL = ('Version', 'The Borg version, and the settings profile when the experiment varies it. '
                          'In brackets: how many fixes from the tracker it carries.')
OUTCOME_COLS = [
    VERSION_COL,
    ('Runs', 'Seeds played: one game per seed.'),
    ('Finished', 'Runs that reached an endpoint: the character died, or was alive at the turn cap. '
                 'Only these count in the rates.'),
    ('Deaths', 'Finished runs in which the character died before the cap.'),
    ('CL5 by 100,000', 'Share of runs with known attainment that reached character level 5 by turn '
                       '100,000, including characters that later died or stopped. The primary progress '
                       'endpoint (Rule 22, #758).'),
    ('Median max depth', 'The middle value, over finished runs, of the deepest dungeon level reached (0 = town). '
                         'A diagnostic; depth is not the success criterion.'),
    ('Median max level', 'The middle value of the highest character level reached. A diagnostic.'),
    ('Median death turn', 'The middle engine turn at which the dying runs died. Lower means earlier deaths.'),
    ('Death rate', 'Deaths divided by finished runs.'),
    ('Alive at 100,000 with CL5', 'Count known to have reached CL5 and still be alive at turn 100,000.'),
    ('Other outcomes', 'Runs with no endpoint, by kind: stalled (game time stopped advancing), wall_timeout '
                       '(out of real time), crash, harness_failure, config_error (the settings did not take '
                       'effect). Never counted as deaths.'),
]
PAIRED_COLS = [
    VERSION_COL,
    ('CL5 pairs', 'Seeds with known CL5 attainment in both arms.'),
    ('CL5 gained', 'Seeds where this arm reached CL5 by 100,000 and the control did not.'),
    ('CL5 lost', 'Seeds where the control reached CL5 by 100,000 and this arm did not.'),
    ('p (CL5)', 'Exact McNemar test on CL5 gains and losses. The primary endpoint (Rule 22, #758).'),
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
    name = arm_label(meta, r['specimen'], r['profile'])
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
    if key == 'vs_version':
        control = arm_label(meta, control_specimen, r['profile'])
    else:
        control = arm_label(meta, r['specimen'], control_profile)
    return paired_example(meta, r, r[key], control)


def load_runs(results):
    runs = []
    for meta_path in sorted(Path(results).glob('*/*/meta.json')):
        meta = json.loads(meta_path.read_text())
        cells_path = meta_path.parent / 'cells.jsonl'
        cells = [json.loads(line) for line in cells_path.read_text().splitlines() if line.strip()]
        runs.append((meta, cells, meta_path.parent))
    runs = consolidate(runs)
    runs.sort(key=lambda r: r[0].get('completed', ''), reverse=True)
    return runs


def consolidate(runs):
    """Merge the single-arm runs of one experiment tag into one run.

    A run started with `--arm` holds one specimen x profile of an experiment
    and keeps the experiment name as its tag. Here every such run of a tag
    becomes one run of the experiment, so the tables, pairing and landing
    page work as for a whole-experiment run. Whole-experiment runs pass
    through unchanged. When a cell appears in more than one arm run of the
    tag (an arm re-run), the newest wins. The merged meta lists its parts,
    because arms from different workflow runs may differ in compiler,
    machine, date or harness commit (RULES.md 7)."""
    groups, out = {}, []
    for run in runs:
        exp = run[0]['experiment']
        if exp.get('arm') and exp.get('full'):
            groups.setdefault(exp['name'], []).append(run)
        else:
            out.append(run)
    for name, parts in groups.items():
        parts.sort(key=lambda r: r[0].get('completed', ''))
        full = parts[-1][0]['experiment']['full']
        present = {tuple(p[0]['experiment']['arm'].split(':', 1)) for p in parts}
        specimens = [x for x in full['specimens'] if any(x == a[0] for a in present)]
        profiles = [x for x in full['profiles'] if any(x == a[1] for a in present)]
        control = full['control'] if full['control'] in specimens else specimens[0]
        cprofile = full.get('control_profile', full['profiles'][0])
        if cprofile not in profiles:
            cprofile = profiles[0]
        cells, catalogue = {}, {'specimens': {}, 'profiles': {}, 'suites': {}}
        for meta, part_cells, _ in parts:
            for c in part_cells:
                cells[cat_mod.cell_key(c)] = c
            for k in catalogue:
                catalogue[k].update(meta['catalogue'].get(k, {}))
            catalogue['harness'] = meta['catalogue'].get('harness')
        newest = parts[-1][0]
        meta = {**newest,
                'experiment': {**full, 'specimens': specimens, 'profiles': profiles, 'control': control,
                               'control_profile': cprofile},
                'catalogue': catalogue,
                'run_id': '+'.join(p[0]['run_id'] for p in parts),
                'environment': {k: sorted({v for p in parts for v in p[0].get('environment', {}).get(k, [])})
                                for k in ('compilers', 'platforms', 'arg_orders')},
                'missing_cells': sum(p[0].get('missing_cells', 0) for p in parts),
                'consolidated_runs': [{'run_id': p[0]['run_id'], 'run_url': p[0].get('run_url', ''),
                                       'results_path': results_path(p[2]),
                                       'arm': p[0]['experiment']['arm'], 'completed': p[0].get('completed', ''),
                                       'zoo_commit': p[0].get('zoo_commit', ''),
                                       'harness': (p[0]['catalogue'].get('harness') or {}).get('commit', '')}
                                      for p in parts]}
        order = {(sp, pr): i for i, (sp, pr) in enumerate(
            (a, b) for a in specimens for b in profiles)}
        merged = sorted(cells.values(), key=lambda c: (c['suite'], order.get((c['specimen'], c['profile']), 0),
                                                       c['seed']))
        out.append((meta, merged, parts[-1][2]))
    return out


@lru_cache(maxsize=1)
def study_presentation():
    # Display metadata only. Never replace the frozen settings or results.
    path = Path(__file__).resolve().parents[1] / 'catalogue/study-presentation.json'
    return json.loads(path.read_text()) if path.exists() else {'profiles': {}, 'experiments': {}}


def study_info(meta):
    return study_presentation()['experiments'].get(meta['experiment']['name'])


def tested_settings(meta):
    if not study_info(meta):
        return ''
    rows = []
    repaired = study_info(meta).get('coverage_repaired', False)
    profiles = meta['catalogue'].get('profiles', {})
    for name in meta['experiment']['profiles']:
        cfg = profiles.get(name, {}).get('settings', {})
        live = cfg.get('borg_town_plan') == 1
        trip = cfg.get('borg_trip_policy') == 1
        row = [esc(study_presentation()['profiles'].get(name, name)),
                     'New shopper — ON' if live else 'Existing shopper',
                     'New trip policy — ON' if trip else 'Existing return rules',
                     f"{cfg.get('borg_town_risk', 1000) / 1000:g}x forecast risk" if live else 'Existing supply rules',
                     (f"{cfg.get('borg_trip_pack_slack', 2)} free spaces / "
                      + ('learning returns off' if cfg.get('borg_trip_unknown_stacks', 4) == 0 else
                         f"{cfg.get('borg_trip_unknown_stacks', 4)} {'eligible unknown stacks' if repaired else 'unknown gear stacks'}")) if trip else 'Existing triggers']
        if repaired:
            row.append(f"Attack {cfg.get('borg_town_w_attack', 100)} / support {cfg.get('borg_town_w_support', 50)} / learning {cfg.get('borg_town_w_knowledge', 25)}" if live else 'Existing priorities')
        rows.append(row)
    ids = ''.join(f'<li><code>{esc(name)}</code>: {esc(study_presentation()["profiles"].get(name, name))}</li>' for name in meta['experiment']['profiles'])
    return fold('What is being tested? (study details)', '<p>The new shopper makes actual purchases, sales and Home transfers. '
            'The trip policy decides when to go home. The risk multiplier changes supply planning; '
            'it does not make the character fight more recklessly. Other declared settings stay the same.</p>'
            + ('<p>This build includes expanded object capabilities and the all-item learning-return fix. The inventory coverage gate accounts for all 104 ordinary shop kinds, including contextual exclusions. Unknown food and mushrooms can contribute; unchanged unresolved items do not repeatedly trigger returns by themselves. ' + esc(study_info(meta).get('scope_note', 'This compares both policies together.')) + '</p>' if repaired else '<p>These are the frozen runs of the original, limited shopping model. The object-coverage fixes now being developed are not included.</p>')
            + table(['Choice', 'Shopping', 'Dungeon returns', 'Supply planning', 'Return triggers'] + (['Purchase priorities'] if repaired else []), rows)
            + '<p><strong>Primary endpoint: CL5 by 100,000 turns (Rule 22, #758);</strong> deaths, character level and depth are reported alongside. '
              'Putting an unknown object in the Home frees space but does not identify it.</p>'
            + '<details><summary>Exact identifiers and statistical plan</summary><ul>' + ids + '</ul><p>'
            + esc(meta['experiment'].get('prespecified', '')) + '</p></details>')


def study_identity_table(meta, cells):
    """The study's identities in one compact table.

    A reader must be able to answer four questions without reverse-engineering
    catalogue identifiers: which configuration was tested, which experiment it
    came from, which repository supplied it, and which exact build was used.
    The death percentage is included here because it is the primary endpoint of
    these policy studies.
    """
    exp = meta['experiment']
    specimens = meta['catalogue'].get('specimens', {})
    rows = []
    for specimen in exp['specimens']:
        spec = specimens.get(specimen, {})
        repo = spec.get('repository', '–')
        repo_url = repository_url(repo)
        build = spec.get('ref', '–')
        source = specimen_source(spec)
        source_link = (f'<a href="{esc(source)}">exact source</a>' if source else '–')
        repo_cell = (f'<a href="{esc(repo_url)}">{esc(repo)}</a>' if repo_url else esc(repo))
        for profile in exp['profiles']:
            selected = [c for c in cells if c.get('specimen') == specimen and c.get('profile') == profile]
            finished = [c for c in selected if c.get('outcome') in stats.VALID]
            deaths = sum(c.get('outcome') == 'death' for c in finished)
            death_rate = f'{100 * deaths / len(finished):.1f}%' if finished else '–'
            choice = study_presentation()['profiles'].get(profile, profile)
            cfg = meta['catalogue'].get('profiles', {}).get(profile, {})
            values = cfg.get('settings', {})
            changed = []
            for key in sorted(values):
                value = values[key]
                if value in (0, False):
                    changed.append(f'{key} off')
                elif value in (1, True):
                    changed.append(f'{key} on')
                else:
                    changed.append(f'{key} {value}')
            difference = '; '.join(changed) if changed else 'build defaults'
            rows.append([esc(choice), difference, esc(exp['name']), repo_cell,
                         f'<code>{esc(build)}</code><br>{source_link}', death_rate])
    return table(['Choice', 'Configuration difference', 'Experiment ID', 'Repository', 'Build', 'Deaths'], rows)


def study_summary(meta, cells, suite):
    if not study_info(meta):
        return ''
    rows = []
    for specimen in meta['experiment']['specimens']:
        for profile in meta['experiment']['profiles']:
            selected = [c for c in cells if c['suite'] == suite and c['specimen'] == specimen and c['profile'] == profile]
            finished = [c for c in selected if c['outcome'] in stats.VALID]
            levels = [c['final']['level'] for c in finished if c.get('final', {}).get('level') is not None]
            depths = [c['final']['max_depth'] for c in finished if c.get('final', {}).get('max_depth') is not None]
            att = stats.cl5_summary(selected)
            rows.append([arm_label(meta, specimen, profile), len(selected), len(finished),
                         sum(c['outcome'] == 'death' for c in finished),
                         f'{att["cl5_reached"]} / {att["cl5_known"]}',
                         f'{mean(levels):.2f}' if levels else '—', f'{mean(depths):.2f}' if depths else '—',
                         sum(d >= 3 for d in depths), len(selected) - len(finished)])
    verdict = ''
    compare = {}
    repaired = study_info(meta).get('coverage_repaired', False)
    default_comparison = ('rs-kit-trip-control', 'rs-kit-trip-default') if repaired else ('rs-joint-old-control', 'rs-joint-risk2000')
    control, candidate = study_info(meta).get('comparison_profiles', default_comparison)
    candidate_name = study_info(meta).get('candidate_label', 'integrated-default candidate' if repaired else '2x-forecast candidate')
    for profile in (control, candidate):
        group = [c for c in cells if c['suite'] == suite and c['profile'] == profile]
        if group and all(c['outcome'] in stats.VALID for c in group):
            compare[profile] = group
    if len(compare) == 2 and len(compare[control]) == len(compare[candidate]):
        delta = sum(c['outcome'] == 'death' for c in compare[candidate]) - sum(c['outcome'] == 'death' for c in compare[control])
        if delta > 0:
            verdict = f'<p><strong>On these cases, the {candidate_name} had {delta} more deaths than the existing rules. It did not reduce deaths in this comparison.</strong></p>'
        elif delta < 0:
            verdict = f'<p><strong>On these cases, the {candidate_name} had {-delta} fewer deaths than the existing rules.</strong> The paired analysis below shows the uncertainty.</p>'
        else:
            verdict = '<p>The candidate and existing rules had the same death count.</p>'
    return ('<h3>Plain summary</h3>' + verdict + '<p>Means include every finished character, including those that died. '
            'Progress is CL5: character level 5 reached by 100,000 engine turns (Rule 22, #758); '
            '“Reached DL3+” is a diagnostic that counts characters reaching dungeon level 3 or deeper. '
            'Incomplete games are shown separately and are not counted as deaths or survivors.</p>'
            + '<h4>Experiment and build identity</h4>'
            + '<p>Use this table to identify each choice, its experiment, source repository, exact build and primary death result.</p>'
            + study_identity_table(meta, cells)
            + table(['Choice', 'Games', 'Finished', 'Deaths', 'Death %', 'CL5 by cap (of known)',
                     'Mean character level', 'Mean deepest level', 'Reached DL3+ (diagnostic)', 'Incomplete'],
                    [[r[0], r[1], r[2], r[3], f'{100 * r[3] / r[2]:.1f}%' if r[2] else '–', r[4], r[5], r[6], r[7], r[8]]
                     for r in rows])
            + '<h3>Detailed statistics</h3><p>The tables below add uncertainty ranges, paired comparisons and medians. '
              'The primary endpoint throughout is CL5: character level 5 reached by 100,000 engine turns '
              '(Rule 22, #758); dungeon level appears only as a diagnostic.</p>')


def arm_label(meta, specimen, profile):
    spec = meta['catalogue']['specimens'].get(specimen, {})
    friendly = study_presentation()['profiles'].get(profile) if study_info(meta) else None
    if friendly:
        return f'<span title="{esc(specimen)} · {esc(profile)}">{esc(friendly)}</span>'
    if len(meta['experiment']['specimens']) == 1:
        return esc(profile)  # one version: the profile alone identifies the arm (owner, 2026-11-24)
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


def raw_cells_link(meta):
    if meta.get('consolidated_runs'):
        return ('<a href="cells.jsonl.gz">merged cells (gzipped JSON lines)</a>; '
                'each arm run\'s raw cells are linked below')
    if meta.get('results_path'):
        return f'<a href="{esc(raw_cells_url(meta["results_path"]))}">raw cells (JSON lines, results branch)</a>'
    return 'raw cells on the results branch'


def consolidated_note(meta):
    parts = meta.get('consolidated_runs')
    if not parts:
        return ''
    rows = ''.join(f'<li><a href="{esc(p["run_url"] or "#")}">{esc(p["arm"])}</a> · {esc(p["completed"])} · '
                   f'harness {esc(p["harness"][:8])} · zoo {esc(p["zoo_commit"][:8])}'
                   + (f' · <a href="{esc(raw_cells_url(p["results_path"]))}">raw cells</a>' if p.get('results_path') else '')
                   + '</li>' for p in parts)
    env = meta.get('environment', {})
    differ = []
    if len({p['completed'][:10] for p in parts}) > 1:
        differ.append('calendar date')
    if len({p['harness'] for p in parts}) > 1:
        differ.append('harness commit')
    if len(env.get('compilers', [])) > 1:
        differ.append('compiler')
    if len(env.get('platforms', [])) > 1:
        differ.append('platform')
    if len(env.get('arg_orders', [])) > 1 or 'ltr' in env.get('arg_orders', []):
        # borg-reborn-rs #855: an `ltr` compiler plays other games from the same seed, so arms built with different
        # argument orders (or any `ltr` build) are not the same game and a pairing of them says nothing.
        differ.append('argument order (arg_order, borg-reborn-rs #855)')
    what = ('They differ in: ' + ', '.join(differ) + '.') if differ else 'They share date, harness commit, compiler and platform.'
    return ('<p class="note">This experiment was run one arm per workflow run and consolidated here. '
            f'{what} Each arm plays the same seeds. Where the arms differ in any of these, a paired comparison '
            f'between them is not a controlled one.</p><details><summary>The {len(parts)} runs</summary>'
            f'<ul>{rows}</ul></details>')


def repository_url(repository):
    """Return the public GitHub URL for an owner/repository catalogue value."""
    if not repository:
        return ''
    if '/' not in repository:
        return ''
    return f'https://github.com/{repository}'


def specimen_source(spec):
    """A direct link to the exact source used by a specimen.

    Prefer the specimen's pinned commit over a branch or tag URL. The source
    field is allowed to point at design documentation, so it is only a
    fallback.
    """
    repo_url = repository_url(spec.get('repository'))
    ref = spec.get('ref')
    if repo_url and ref:
        return f'{repo_url}/tree/{ref}'
    return spec.get('source', '')


def experiment_brief(meta, compact=False):
    """Describe the recorded design, including historical settings, before the data."""
    exp = meta['experiment']
    snapshot = meta['catalogue']
    versions = ', '.join(exp['specimens'])
    profiles = '; '.join(profile_label(name) for name in exp['profiles'])
    limits = []
    for name in exp['suites']:
        suite = snapshot['suites'][name]
        birth = {'fixed': 'fixed Human Warrior', 'random': 'race and class chosen by seed',
                 'assigned': 'assigned race and class'}.get(suite['birth'], suite['birth'])
        limits.append(f'{len(suite["seeds"]):,} seeds · {suite["cap"]:,} turns per game · {birth}')
    if compact:
        def choices(label, names, rendered):
            if len(names) > 3:
                return (f'<details><summary>{len(names)} {label.lower()} compared</summary>'
                        f'<p>{esc(rendered)}</p></details>')
            return f'<p><strong>{label}:</strong> {esc(rendered)}</p>'
        build_rows = []
        for name in exp['specimens']:
            spec = snapshot['specimens'].get(name, {})
            source = specimen_source(spec)
            link = (f'<a href="{esc(source)}">source</a>' if source else '–')
            build_rows.append([esc(name), esc(spec.get('repository', '–')),
                               f'<code>{esc(spec.get("ref", "–"))}</code>', link])
        return (choices('Versions', exp['specimens'], versions)
                + choices('Settings', exp['profiles'], profiles)
                + f'<p>{esc("; ".join(limits))}</p>'
                + '<details><summary>Builds compared</summary>'
                + table(['Specimen', 'Repository', 'Exact commit', 'Source'], build_rows)
                + '</details>')
    settings = []
    for name in exp['profiles']:
        profile = snapshot.get('profiles', {}).get(name, {})
        values = profile.get('settings', {})
        written = ', '.join(f'{key} = {value}' for key, value in values.items())
        base = 'version’s shipped configuration' if profile.get('base') == 'shipped' else 'build defaults'
        settings.append(f'<li><strong>{esc(name)}</strong>: {esc(written or base)}'
                        + (f' (other settings use {esc(base)})' if written else '') + '</li>')
    control = (f'{exp["control"]} · {profile_label(exp.get("control_profile", exp["profiles"][0]))}'
               if len(exp['specimens']) > 1 else profile_label(exp.get("control_profile", exp["profiles"][0])))
    comparison = ('Versions and settings both vary.' if len(exp['specimens']) > 1 and len(exp['profiles']) > 1
                  else 'Same version; settings vary.' if len(exp['profiles']) > 1
                  else 'Same settings profile; versions vary.' if len(exp['specimens']) > 1
                  else 'One configuration measured; no within-study comparison.')
    build_rows = []
    for name in exp['specimens']:
        spec = snapshot['specimens'].get(name, {})
        source = specimen_source(spec)
        link = (f'<a href="{esc(source)}">exact source</a>' if source else '–')
        build_rows.append([esc(name), esc(spec.get('repository', '–')),
                           f'<code>{esc(spec.get("ref", "–"))}</code>', link])
    return (f'<p class="question">{esc(question(exp))}</p><dl>'
            f'<dt>Comparison</dt><dd>{esc(comparison)}</dd>'
            f'<dt>Versions</dt><dd>{esc(versions)}</dd>'
            f'<dt>Settings</dt><dd>{esc(profiles)}</dd>'
            f'<dt>Baseline</dt><dd>{esc(control)}</dd>'
            f'<dt>Test conditions</dt><dd>{"<br>".join(esc(x) for x in limits)}</dd>'
            f'<dt>Study type</dt><dd>{"Prespecified; the study plan below defines the endpoints." if exp.get("prespecified") else "Descriptive; no prespecified primary endpoint recorded."}</dd>'
            '<dt>Results shown</dt><dd>CL5 by 100,000 turns; deaths before the cap; depth and level as diagnostics. '
            'Stalls, timeouts and errors are reported separately.</dd></dl>'
            '<details class="background"><summary>Builds compared</summary>'
            + table(['Specimen', 'Repository', 'Exact commit', 'Source'], build_rows)
            + '</details>'
            '<details class="background"><summary>Exact settings used</summary><ul>'
            + ''.join(settings) + '</ul></details>')
def town_shadow_table(meta, cells):
    if not any(meta['catalogue']['specimens'].get(s, {}).get('town_shadow_records')
               for s in meta['experiment']['specimens']):
        return ''
    from .town_shadow import QUALIFICATION
    groups = {}
    rows = []
    for cell in cells:
        char = cat_mod.character(meta['catalogue']['suites'][cell['suite']], cell['seed'])
        cls = cell.get('played_class') or (char[1] if char else '?')
        groups[cls] = groups.get(cls, 0) + 1
        shadow = cell.get('town_shadow') or {}
        vector = shadow.get('effective_vector')
        identity = ('<details><summary>Parsed parameters</summary><pre>'
                    + esc(json.dumps(vector, indent=2)) + '</pre></details>') if vector else 'Unavailable'
        rows.append([esc(cls), cell['seed'], esc(cell['profile']),
                     esc(cell.get('profile_applied', '?')), esc(cell['outcome']),
                     esc(cell.get('observed_outcome', cell['outcome'])),
                     esc(shadow.get('status', 'unavailable')), num(shadow.get('checked_records')),
                     num(shadow.get('median_planned_spending')), num(shadow.get('median_retained_gold')),
                     esc(json.dumps(shadow.get('planned_supply_copies_by_stack_class', {}))),
                     esc(json.dumps(shadow.get('snapshot_home_dispositions', {}))),
                     esc(cell.get('config_sha256', '?')), identity, esc(shadow.get('error') or '')])
    return fold('Shadow town diagnostics', '<p>' + esc(QUALIFICATION) + '</p>'
            '<p>All attempted outcomes are included. Spending and retained gold are medians over '
            'snapshots within that cell after the urgent-purchase budget has been deducted; supply copies '
            'and Home dispositions count proposals in those snapshots. An empty stream means no consultation '
            'observed, not verified identical planning.</p>'
            + table(['Class', 'Attempted games'], [[esc(cls), groups.get(cls, 0)] for cls in cat_mod.CLASSES])
            + table(['Class', 'Seed', 'Selector', 'Applied profile', 'Outcome', 'Native outcome', 'Record check', 'Snapshots',
                     'Planned spending (median)', 'Retained gold (median)', 'Planned supply copies by stack class',
                     'Snapshot Home dispositions', 'Config SHA-256', 'Native parameter vector', 'Error'], rows, left=4))


def provenance_line(exp):
    """The experiment-definition YAML, closed by default; the ticket lives in the header facts."""
    definition = cat_mod.definition_of(exp)
    if not definition:
        return ''
    text = (cat_mod.ROOT / definition).read_text()
    return (f'<details class="definition"><summary>Experiment definition: <code>{esc(definition)}</code>'
            f'</summary><pre>{esc(text)}</pre></details>')


WORLD_LABELS = {
    'breeders-x4': 'Breeders ×4', 'breeders-x8': 'Breeders ×8',
    'patches-x8': 'Patches ×8', 'poison-x8': 'Poison ×8', 'eyes-x8': 'Eyes ×8',
    'archers-x4': 'Archers ×4', 'archers-x8': 'Archers ×8',
    'jellies-x4': 'Jellies ×4', 'jellies-x8': 'Jellies ×8',
    'white-worm-mass-x4': 'White worm mass ×4',
}


def world_type(exp, snapshot):
    """The worlds the arms play, from the recorded profile settings."""
    worlds = []
    for name in exp['profiles']:
        w = ((snapshot.get('profiles') or {}).get(name) or {}).get('settings', {}).get('borg_world')
        worlds.append(WORLD_LABELS.get(w, w.replace('-', ' ').capitalize() if w else 'Normal'))
    return ' · '.join(dict.fromkeys(worlds))


QUESTION_RE = re.compile(r'On (?P<pin>[^,]+), what do (?:the )?(?P<subject>[^(]+?) '
                          r'\((?P<ref>[^:)]+): (?P<detail>[^)]+)\) change[^,]*, (?P<mode>[^?]+)\?')


def question_title(exp):
    """The h1: the question's detail - 'Cure Critical Wounds copies and the poison
    remedy at 40 percent.' (owner, 2026-11-24, two-line title). Falls back to the
    question verbatim when it has another shape."""
    q = exp.get('question') or ''
    m = QUESTION_RE.match(q)
    if not m:
        return q or exp.get('name', '')
    return f"{m['detail'].strip()}."


def subject_mode(exp):
    """The second title line: 'Dear-cure rows, switched on and off.' The pin and
    tracker ref live in the facts card (build, tickets). None for other shapes."""
    m = QUESTION_RE.match(exp.get('question') or '')
    if not m:
        return None
    mode = m['mode'].strip()
    if re.fullmatch(r'switched \w+', mode):
        mode = 'switched on and off'
    return f"{m['subject'].strip().capitalize()}, {mode}."


def upstream_ticket(exp, snapshot):
    """The upstream tracker reference the question names — "(#1134: ...)" —
    linked to the specimens' repository (owner, 2026-11-24: both tickets in the header)."""
    m = QUESTION_RE.match(exp.get('question') or '')
    if not m:
        return None
    num = m['ref'].lstrip('#').strip()
    if not num.isdigit():
        return None
    repo = next((snapshot['specimens'].get(s, {}).get('repository', '')
                 for s in exp['specimens']
                 if snapshot['specimens'].get(s, {}).get('repository')), '')
    if not repo:
        return None
    return f'<a href="https://github.com/{esc(repo)}/issues/{num}">{esc(repo.split("/")[-1])} #{num}</a>'


def header_facts(exp, snapshot):
    """The compact facts block heading every report (owner, 2026-11-24): ticket
    reference, samples, arms, world type, and the build, prominently."""
    issue = cat_mod.issue_of(exp)
    refs = [f'<a href="{cat_mod.ISSUES_URL}{issue}">borg-zoo #{issue}</a>'] if issue else []
    up = upstream_ticket(exp, snapshot)
    if up:
        refs.append(up)
    ticket = ' · '.join(refs) if refs else '–'
    n_arms = len(exp['specimens']) * len(exp['profiles'])
    suite_lines = []
    for name in exp['suites']:
        suite = snapshot['suites'][name]
        suite_lines.append(f'{len(suite["seeds"]) * n_arms:,} games '
                           f'({len(suite["seeds"]):,} seeds × {n_arms} arms, cap {suite["cap"]:,} turns)')
    meta = {'experiment': exp, 'catalogue': snapshot}
    arms = ', '.join(arm_label(meta, s, p)
                     for s in exp['specimens'] for p in exp['profiles'])
    builds = []
    for name in exp['specimens']:
        spec = snapshot['specimens'].get(name, {})
        repo, ref = spec.get('repository', ''), spec.get('ref', '')
        link = (f'<a href="https://github.com/{esc(repo)}/commit/{esc(ref)}"><code>{esc(ref[:9])}</code></a>'
                if repo and ref else f'<code>{esc(ref[:9] or "–")}</code>')
        carries = f' · {spec["carries"]} carries' if spec.get('carries') is not None else ''
        builds.append(f'{esc(name)} · {esc(repo or "?")} {link}{carries}')
    return (f'<div class="card facts"><dl>'
            f'<dt>Ticket reference</dt><dd>{ticket}</dd>'
            f'<dt>Samples</dt><dd>{"<br>".join(suite_lines)}</dd>'
            f'<dt>Arms</dt><dd>{n_arms}: {arms}</dd>'
            f'<dt>World type</dt><dd>{world_type(exp, snapshot)}</dd>'
            f'<dt>Build</dt><dd>{"<br>".join(builds)}</dd>'
            f'</dl></div>')


def build_used(meta, cells):
    """What executed the games: per specimen, the exact source, binary and
    toolchain the records report, and the zoo commit and Actions run."""
    rows = []
    for name in meta['experiment']['specimens']:
        spec = meta['catalogue']['specimens'].get(name, {})
        mine = [c for c in cells if c.get('specimen') == name]

        def seen(key):
            vals = sorted({c.get(key) for c in mine if c.get(key)})
            if not vals:
                return '–'
            text = '<br>'.join(f'<code>{esc(v)}</code>' for v in vals)
            return text + (f' <strong>({len(vals)} different)</strong>' if len(vals) > 1 else '')
        repo, ref = spec.get('repository', ''), spec.get('ref', '')
        commit = (f'<a href="https://github.com/{esc(repo)}/commit/{esc(ref)}"><code>{esc(ref)}</code></a>'
                  if repo and ref else f'<code>{esc(ref or "–")}</code>')
        rows.append([esc(name), esc(repo or '–'), commit, seen('engine_upstream'), seen('source_sha256'), seen('binary_sha256'),
                     seen('compiler'), seen('rustc'), seen('platform')])
    zoo = meta.get('zoo_commit')
    zoo_link = (f'<a href="https://github.com/diegoami/borg-zoo/commit/{esc(zoo)}"><code>{esc(zoo[:12])}</code></a>'
                if zoo else '–')
    run = (f'<a href="{esc(meta["run_url"])}">Actions run {esc(meta.get("run_id", ""))}</a>'
           if meta.get('run_url') else esc(meta.get('run_id', '–')))
    return ('<details class="build-used"><summary>Build used to run it</summary>'
            + table(['Specimen', 'Repository', 'Commit', 'Engine (upstream Angband)', 'Source hash', 'Binary SHA-256', 'Compiler', 'rustc', 'Platform'],
                    rows)
            + f'<p class="muted">Zoo {zoo_link} · {run}. The values are what the game records report; a source '
              'hash is recorded for borg-rs builds from 2026-11-16 on, the engine from 2026-11-20 on (borg-zoo#473).</p></details>')


def run_page(meta, cells):
    exp = meta['experiment']
    specimens = meta['catalogue']['specimens']
    analysis = stats.analyse(exp, cells, specimens)
    class_pairs = stats.paired_by_class(exp, cells, specimens)
    display = study_info(meta)
    page_title = display['title'] if display else exp['name']
    intro = display['intro'] if display else exp.get('description', '')
    header_title = display['title'] if display else question_title(exp)
    sub = None if display else subject_mode(exp)
    headline, diagnostics = [], []
    parts = [f'<p><a href="../../index.html">All experiments</a></p>',
             f'<h1>{esc(header_title)}</h1>',
             (f'<p class="subtitle">{esc(sub)}</p>' if sub else ''),
             header_facts(exp, meta['catalogue'])]
    meta_parts = [provenance_line(exp),
             build_used(meta, cells),
             fold('What is being tested?',
                  (f'<p class="lead">{esc(intro)}</p>' if intro else '') + experiment_brief(meta)),
             configuration.summary(meta),
             tested_settings(meta),
             '<details class="background"><summary>Background and study plan</summary>'
             f'<p>{esc(exp.get("description", ""))}</p>'
             + (f'<p><strong>Prespecified:</strong> {esc(exp["prespecified"])}</p>'
                if exp.get('prespecified') and not display else '')
             + '</details>',
             f'<p class="muted">Run {esc(meta["run_id"])} · completed {esc(meta.get("completed", "?"))} · '
             f'<a href="{esc(meta.get("run_url", "#"))}">workflow run</a> · {raw_cells_link(meta)}</p>',
             consolidated_note(meta),
             '<details class="background"><summary>How to read the statistics</summary><p class="note">An <em>arm</em> is one Borg version run with one settings profile; every arm plays '
             'the same seeds, one game per seed. Results are descriptive unless the experiment says it is '
             'prespecified above. Ranges are Wilson 95% intervals; paired p-values are exact McNemar tests on the '
             'seeds with known outcomes for that endpoint. Deaths are measured before the run cap. '
             'Progress is reaching <strong>character level 5 by 100,000 engine turns</strong>. '
             'For historical prespecified studies, see the original endpoints in the study plan.</p>'
             + '</details>']
    for suite, rows in analysis.items():
        s = meta['catalogue']['suites'][suite]
        headline.append(fold(f'Suite {esc(suite)}',
                          f'<p class="muted">{esc(s["description"])} · '
                          f'{len(s["seeds"])} seeds · cap {s["cap"]:,} engine turns · birth {esc(s["birth"])}</p>'))
        headline.append(study_summary(meta, cells, suite))
        headline.append('<h3>Outcomes per arm</h3>')
        first = rows[0]['summary'] if rows else None
        headline.append(explain_folded(
            'One row per arm: a Borg version, with a settings profile when the experiment varies it. Every arm '
            'plays the same seeds. The primary figure is CL5 \u2014 character level 5 reached by 100,000 engine '
            'turns (Rule 22, #758); deaths and the death rate sit alongside it, and depth is a diagnostic.',
            OUTCOME_COLS,
            (f'{arm_label(meta, rows[0]["specimen"], rows[0]["profile"])}: {first["valid"]:,} of {first["cells"]:,} runs finished and '
             f'{first["deaths"]:,} died ({pct(first["death_rate"])}); with this many seeds the true death rate '
             f'is most likely {ci(first["death_ci"])}.') if first and first['valid'] else None))
        headline.append(table(
            OUTCOME_COLS,
            [[arm_label(meta, r['specimen'], r['profile']), r['summary']['cells'], r['summary']['valid'],
              r['summary']['deaths'], pct(r['summary']['cl5_rate']),
              num(r['summary']['median_max_depth']), num(r['summary']['median_max_level']),
              num(r['summary']['median_death_turn']),
              pct(r['summary']['death_rate']), r['summary']['cl5_alive'],
              esc(', '.join(f'{k} {v}' for k, v in r['summary']['counts'].items()
                            if v and k not in stats.VALID)) or '–']
             for r in rows]))
        control_profile = exp.get('control_profile', exp['profiles'][0])
        for key, title in (('vs_version', f'Paired against {esc(exp["control"])}, same profile'),
                           ('vs_profile', f'Paired against {esc(study_presentation()["profiles"].get(control_profile, control_profile))}, same version')):
            versus = [r for r in rows if r[key]]
            if not versus:
                continue
            control = esc(exp['control']) if key == 'vs_version' else f'profile {esc(control_profile)}'
            headline.append(f'<h3>{title}</h3>')
            headline.append(explain_folded(
                f'Each row compares one arm with the control ({control}) seed by seed. The primary endpoint is '
                'CL5: gained against lost, tested by exact McNemar over the seeds with known attainment in '
                'both arms. Deaths are read the same way: seeds where both died or both lived cannot tell the '
                'arms apart; the comparison rests on <span class="good">Rescued</span> (only the control died) '
                'against <span class="bad">Newly killed</span> (only this arm died).',
                PAIRED_COLS,
                example_for(meta, versus, key, exp['control'], control_profile)))
            headline.append(table(
                PAIRED_COLS,
                [[arm_label(meta, r['specimen'], r['profile']),
                  v['cl5_pairs'], v['cl5_gained'], v['cl5_lost'], pval(v['cl5_p']),
                  v['pairs'],
                  f'<span class="good">{v["rescued"]}</span>', f'<span class="bad">{v["newly_killed"]}</span>',
                  v['both_died'], v['both_lived'], v['identical_traces'], pval(v['death_p'])]
                 for r in versus for v in [r[key]]]))
        unfinished = [c for c in cells if c['suite'] == suite and c['outcome'] not in stats.VALID]
        if unfinished:
            unfinished_inner = [explain(
                'Runs that reached neither death nor the turn cap, one row each. Verified CL5 attainment can '
                'still contribute to progress. A stall usually means the Borg loops while game time stands still; each one is a '
                'lead for a liveness bug. Stall kind is a heuristic label; the counters and the notes are the '
                'evidence.', UNFINISHED_COLS)]
            rows_u = []
            for c in unfinished:
                st = c.get('stall') or {}
                top = st.get('top_notes_at_last_turn') or st.get('top_keys_at_last_turn') or []
                rows_u.append([arm_label(meta, c['specimen'], c['profile']), c['seed'], esc(c['outcome']),
                               num(st.get('last_turn', c['final'].get('turn'))), esc(st.get('kind', '–')),
                               num(st.get('decisions_delta')), num(st.get('energy_delta')),
                               num(st.get('depth_changes')),
                               esc('; '.join(f'{t} ×{n}' for t, n in top[:2])) or '–'])
            unfinished_inner.append(table(UNFINISHED_COLS, rows_u, left=1))
            diagnostics.append(fold('Runs that did not finish', ''.join(unfinished_inner)))
        for field, title in (('class', 'Deaths by class'), ('race', 'Deaths by race')):
            per = stats.by_character(exp, cells, field).get(suite)
            many = {'class': 'classes', 'race': 'races'}[field]
            if not per or len(per) < 2:
                continue
            arms = [a['arm'] for a in per[0]['arms']]
            diagnostics.append(fold(title, explain(
                f'One row per {field}, one column per arm. Each cell is deaths / finished runs (death rate) for '
                f'characters of that {field}. Read down a column to see which {many} die most; read across a row '
                f'to see whether a version changed that {field}\'s risk. Cells hold a few hundred runs or fewer, '
                'so read the pattern, not single values.')
                + table([field.capitalize()] + [arm_label(meta, s_, p_) for s_, p_ in arms],
                        [[esc(r['value'])] + [f'{a["deaths"]}/{a["n"]} ({pct(a["rate"])})' if a['n'] else '–'
                                              for a in r['arms']] for r in per])))
        if class_pairs.get(suite):
            diagnostics.append(fold('Paired deaths by class',
                              explain('Each row pairs seeds within the class actually played. Only pairs where '
                                      'both arms finished contribute to rescued/newly killed counts; unfinished '
                                      'attempts remain reported separately. These are descriptive comparisons: '
                                      'testing nine classes and several arms can produce small p-values by chance. '
                                      'A class-specific improvement or regression needs fresh confirmation.')
                              + table(['Class', 'Arm', 'Compared with', 'Pairs', 'Rescued', 'Newly killed',
                                       'Both died', 'Both lived', 'Identical play', 'p', 'Arm unfinished'],
                                      [[esc(r['class']), arm_label(meta, r['specimen'], r['profile']),
                                        arm_label(meta, r['control_specimen'], r['control_profile']),
                                        *[num(r['paired'][k]) for k in ('pairs', 'rescued', 'newly_killed',
                                                                       'both_died', 'both_lived', 'identical_traces')],
                                        pval(r['paired']['death_p']), num(r['unfinished'])]
                                      for r in class_pairs[suite]], left=3)))
        cz = stats.by_cause(exp, cells).get(suite)
        if cz:
            label = lambda a: arm_label(meta, a[0], a[1])
            cause_inner = [explain(
                'What killed the characters that died, per arm. The harness records the cause as free text, so '
                'it is grouped: <strong>Poison</strong>, <strong>Hunger</strong> (starvation), '
                '<strong>Lava</strong>, and <strong>Monster</strong> for every other named killer. Counts are '
                'deaths among finished runs; the share is of that arm\'s deaths.')]
            cause_inner.append(table(['Arm', 'Deaths'] + list(stats.CAUSE_GROUPS),
                               [[esc(label(r['arm'])), num(r['deaths'])] +
                                [f'{r["groups"][g]} ({pct(r["groups"][g] / r["deaths"]) if r["deaths"] else "–"})'
                                 for g in stats.CAUSE_GROUPS] for r in cz['per_arm']]))
            if cz['common']:
                cause_inner.append('<h4>Most frequent named causes</h4>')
                cause_inner.append(explain('The eight most frequent causes over all arms (a leading "a" or "an" is '
                                           'dropped), with the count per arm.'))
                cause_inner.append(table(['Cause'] + [esc(label(r['arm'])) for r in cz['per_arm']],
                                         [[esc(n)] + [num(r['named'][n]) for r in cz['per_arm']] for n in cz['common']]))
            if cz['paired']:
                cause_inner.append('<h4>Cause groups against the control, seed by seed</h4>')
                cause_inner.append(explain(
                    'For each arm and cause group: <strong>New</strong> is the seeds where only this arm died of '
                    'that cause, <strong>Fewer</strong> where only the control did. A seed counts when both arms '
                    'finished it. p is the exact McNemar test on those two numbers. Four groups are tested per '
                    'arm, so a single p near 0.05 is weak evidence.'))
                cause_inner.append(table(['Arm', 'Cause', 'Pairs', 'New', 'Fewer', 'p'],
                                         [[esc(label(r['arm'])), esc(r['group']), num(r['pairs']), num(r['new']),
                                           num(r['fewer']), pval(r['p']) if r['p'] is not None else '–']
                                          for r in cz['paired']], left=2))
            diagnostics.append(fold('Deaths by cause', ''.join(cause_inner)))
        turns = [x['turn'] for x in rows[0]['survival']] if rows else []
        diagnostics.append(fold('Share alive by engine turn', explain(
            'For each arm, the share of finished runs whose character was still alive at each engine turn (the '
            'last column is the turn cap). Read along a row to see when the deaths happen: an arm with fewer '
            'early deaths keeps a higher share in the first columns.')
            + table(['Version'] + [f'{t:,}' for t in turns],
                    [[arm_label(meta, r['specimen'], r['profile'])] + [pct(x['alive']) for x in r['survival']]
                     for r in rows])))
        marks = [x['depth'] for x in rows[0]['depths']] if rows else []
        no_marks = {k for k, v in meta['catalogue']['specimens'].items() if v.get('kind') == 'borg-rs'}
        diagnostics.append(fold('Depth reached (diagnostic)', explain(
            'For each arm and dungeon level (DL): the share of finished runs that ever reached that level, then '
            'the median engine turn at which they first got there. A higher share reached sooner means faster '
            'descent, which is not the same as safer play.'
            + (' borg-rs runs record no depth by turn, so their cells are empty.' if no_marks & set(exp['specimens'])
               else ''))
        + table(['Version'] + [f'DL{m}: share · median turn' for m in marks],
                [[arm_label(meta, r['specimen'], r['profile'])] +
                 (['not recorded'] * len(marks) if r['specimen'] in no_marks else
                  [f'{pct(x["reached"])} · {num(x["median_turn"])}' for x in r['depths']])
                 for r in rows])))
        has_milestones = any(x['n'] for r in rows for x in r['milestones'])
        if has_milestones:
            has_gold = any(x.get('median_gold') is not None for r in rows for x in r['milestones'])
            milestone_inner = [explain(
                'For each arm, at 25/50/75% of the cap and at the cap itself: the median character level and '
                'the median max depth over finished runs that recorded it, among those still going at that '
                'turn (a death before it is simply excluded, not substituted). Gold on hand is shown only '
                'where the harness logs it; it is not a net worth — inventory and equipment are hashed, not '
                'valued (docs/DESIGN.md, "Open questions").' if has_gold else
                'For each arm, at 25/50/75% of the cap and at the cap itself: the median character level and '
                'the median max depth over finished runs that recorded it, among those still going at that '
                'turn (a death before it is simply excluded, not substituted). This harness logs no gold or '
                'item value, so there is no net-worth column (docs/DESIGN.md, "Open questions").')]
            m_turns = [x['turn'] for x in rows[0]['milestones']] if rows else []

            def fmt_milestone(x):
                if not x['n']:
                    return '–'
                cell_ = f'lv {num(x["median_level"])} · DL{num(x["median_max_depth"])}'
                return cell_ + (f' · {num(x["median_gold"])}g' if has_gold and x.get('median_gold') is not None
                               else '')
            milestone_inner.append(table(['Version'] + [f'{t:,}' if t is not None else '–' for t in m_turns],
                                             [[arm_label(meta, r['specimen'], r['profile'])] +
                                              [fmt_milestone(x) for x in r['milestones']] for r in rows]))
            diagnostics.append(fold('Level, max depth and gold by engine turn', ''.join(milestone_inner)))
    parts += headline + meta_parts
    parts.append(cutoff_note(exp, specimens, meta.get('completed', ''),
                             (meta.get('catalogue') or {}).get('harness', {}).get('commit', '')))
    parts += diagnostics
    returns_by_profile = {}
    for cell in cells:
        activity = cell.get('return_activity')
        if activity is not None:
            totals = returns_by_profile.setdefault(cell['profile'], [0] * 13)
            for i, name in enumerate(('town_arrivals', 'new_custom_return_goals', 'arrivals_after_custom_goal',
                                      'arrivals_with_selling_note', 'unfinished_journeys_with_custom_goal',
                                      'sampled_town_turns', 'sampled_dungeon_turns')):
                totals[i] += activity.get(name, 0)
            totals[7] += not activity.get('state_available', False)
            totals[8] += activity.get('invalid_trip_records', 0)
            for i, name in enumerate(('application_records', 'already_rising_applications', 'new_return_goals', 'return_recommendation_records'), 9):
                totals[i] += activity.get(name, 0)
    if returns_by_profile:
        parts.append(fold('What actually sent the Borg home?',
                          '<p>Native arrivals are separate from return requests. '
                          'An application record can show that the policy newly set the return goal, or found it already set. '
                          'A later arrival after such a goal is an association, not proof it would never return otherwise. '
                          'Selling notes can overlap. Custom goals exclude shared restocking. Time is sampled from native states.</p>'
                          + table(['Profile', 'Town arrivals', 'New custom goals', 'Arrivals after custom goal',
                                   'Arrivals with selling note', 'Unfinished trips with custom goal', 'Sampled time in town', 'Missing states / invalid trip rows'],
                                  [[esc(profile), *totals[:5],
                                    f'{100 * totals[5] / (totals[5] + totals[6]):.1f}%' if totals[5] + totals[6] else '—', f'{totals[7]} / {totals[8]}']
                                   for profile, totals in sorted(returns_by_profile.items())])
                          + table(['Profile', 'Policy applications', 'Calls already homeward', 'New return goals',
                                   'Custom subset of new goals', 'Recommendation records'],
                                  [[esc(profile), totals[9], totals[10], totals[11], totals[1], totals[12]]
                                   for profile, totals in sorted(returns_by_profile.items())])))
    shopping = {}
    for cell in cells:
        for item in (cell.get('town_activity') or {}).get('items', []):
            key = (cell['profile'], cell.get('played_class') or '?', item['item'])
            total = shopping.setdefault(key, [0, 0, 0])
            total[0] += item['transactions']
            total[1] += item['units']
            total[2] += item['gold']
    if any('town_activity' in cell for cell in cells):
        parts.append(fold('Observed town purchases',
                          '<p>Native retail receipts, grouped by profile, class and item. '
                          'Counts include all recorded attempts. Planned buys and Home transfers are excluded. '
                          'Full messages and policy records are in the workflow raw evidence artifacts (90-day retention).</p>'
                          + table(['Profile', 'Class', 'Item', 'Transactions', 'Units', 'Gold spent'],
                                  [[esc(profile), esc(cls), esc(item), *totals]
                                   for (profile, cls, item), totals in sorted(shopping.items())])))
    parts.append(town_shadow_table(meta, cells))
    parts.append(fold('Specimens and environment',
                      explain('The Borg versions in this experiment, each built from the commit shown.')
                      + table(['Specimen', ('Ref', 'The commit that was built.'),
                               ('Carries', 'Fixes from the tracker carried by this version.'), 'Label'],
                              [[esc(k), f'<code>{esc(v["ref"][:12])}</code>', num(v.get('carries')), esc(v.get('label', ''))]
                               for k in exp['specimens'] for v in [meta['catalogue']['specimens'][k]]])))
    builds_inner = [explain('Every arm below uses the listed repository at the exact commit shown. '
                            'The source link opens that immutable tree.')]
    build_rows = []
    for name in exp['specimens']:
        spec = meta['catalogue']['specimens'][name]
        source = specimen_source(spec)
        link = (f'<a href="{esc(source)}">exact source</a>' if source else '–')
        build_rows.append([esc(name), esc(spec.get('repository', '–')),
                           f'<code>{esc(spec.get("ref", "–"))}</code>', num(spec.get('carries')),
                           esc(spec.get('label', '')), link])
    builds_inner.append(table(['Specimen', 'Repository', 'Exact commit', ('Carries', 'Fixes from the tracker carried by this version.'),
                               'Label', 'Source'], build_rows))
    env = meta.get('environment', {})
    harness = meta['catalogue'].get('harness', {})
    harness_url = repository_url(harness.get('repository'))
    harness_link = (f'<a href="{esc(harness_url)}">{esc(harness.get("repository"))}</a>'
                    if harness_url else esc(harness.get('repository', '–')))
    builds_inner.append(f'<p class="muted">Harness {harness_link} '
                        f'<code>{esc(harness.get("commit", "–"))}</code> · '
                        f'compilers {esc(", ".join(env.get("compilers", [])))} · platforms {esc(", ".join(env.get("platforms", [])))} · '
                        f'calendar: native clock, all arms in one workflow run</p>')
    parts.append(fold('Builds compared and environment', ''.join(builds_inner)))
    return page(f'{page_title} · borg-zoo', ''.join(parts))


def build_site(results, out):
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    every = load_runs(results) if Path(results).exists() else []
    smoke = cat_mod.smoke_names()
    # The analysis pages see every run: a setup with nothing bigger than a
    # smoke run is still listed, marked "smoke-scale only - not plotted", and a
    # full run always outranks a smoke one. Smoke checks are not listed on the
    # Full runs tab at all, and there is no smoke tab (owner, 2026-11-24).
    runs = every
    rows = []
    from . import landing
    for meta, cells, src in every:
        target = out / 'runs' / meta['experiment']['name'] / meta['run_id']
        target.mkdir(parents=True, exist_ok=True)
        if not meta.get('consolidated_runs'):
            meta = {**meta, 'results_path': results_path(src)}
        configuration.build_inspector(meta, cells, src, target)
        (target / 'index.html').write_text(run_page(meta, cells))
        if meta.get('consolidated_runs'):
            # The merged set exists nowhere else, so it is published, gzipped.
            # mtime=0 keeps the bytes reproducible across rebuilds.
            merged = ''.join(json.dumps(c, sort_keys=True) + '\n' for c in cells).encode()
            (target / 'cells.jsonl.gz').write_bytes(gzip.compress(merged, 6, mtime=0))
            (target / 'meta.json').write_text(json.dumps(meta, indent=2, sort_keys=True) + '\n')
        else:
            shutil.copy(src / 'meta.json', target / 'meta.json')
        if meta['experiment']['name'] in smoke:
            continue
        finished = sum(1 for c in cells if c['outcome'] in stats.VALID)
        death_ivs = landing.arm_intervals(cells, lambda c: c['outcome'] == 'death')
        cl5_ivs = landing.arm_intervals(cells, lambda c: stats.cl5_reached(c) is True,
                                        known=lambda c: stats.cl5_reached(c))
        rows.append([f'<a href="runs/{esc(meta["experiment"]["name"])}/{esc(meta["run_id"])}/index.html">'
                     f'{esc((study_info(meta) or {}).get("title", meta["experiment"]["name"]))}</a>',
                     (f'<a href="{cat_mod.ISSUES_URL}{issue}">#{issue}</a>' if (issue := cat_mod.issue_of(meta['experiment'])) else '–'),
                     esc(meta.get('completed', '?')),
                     len(meta['experiment']['specimens']), len(meta['experiment']['profiles']),
                     len(cells), finished,
                     landing.range_cell(list(reversed(death_ivs))),
                     landing.range_cell(cl5_ivs)])
    from . import landing
    shutil.copy(Path(__file__).parent / 'assets' / 'echarts.min.js', out / 'echarts.min.js')
    (out / 'overview.html').write_text(page('Borg comparisons · borg-zoo', landing.overview_page(runs), charts=True))
    from . import scenarios
    scenarios.build_site(results, out)
    from . import settings_page
    settings_page.build(runs, out, page)
    # The /runs/ directory contains per-run report folders, not a page of its
    # own. Publish an index there so the directory URL is useful instead of
    # returning 404/503, and point it at the Detailed experiment catalogue.
    runs_index = out / 'runs'
    runs_index.mkdir(exist_ok=True)
    (runs_index / 'index.html').write_text(page(
        'Experiment runs · borg zoo',
        '<h1>Experiment runs</h1><p><a href="../detailed.html">Browse all experiment reports</a></p>'
        '<p class="muted">Each experiment also has its own permanent report under this directory.</p>'))
    for policy in landing.POLICIES:
        (out / f'{policy["slug"]}.html').write_text(
            page(f'{policy["title"]} · borg-zoo', landing.comparison_page(runs, policy), charts=True))
    full = page('Full runs · borg-zoo', landing.landing_page(runs, rows))
    (out / 'index.html').write_text(full)
    (out / 'detailed.html').write_text(full)  # older links
    (out / 'stalls.html').write_text(page('Stalls and crashes · borg-zoo', landing.stalls_page(runs)))
    (out / 'versions.html').write_text(page('Versions · borg-zoo', landing.versions_page()))
    (out / '.nojekyll').write_text('')
    for slug, title, body in landing.class_pages(runs):
        (out / 'classes').mkdir(exist_ok=True)
        (out / 'classes' / f'{slug}.html').write_text(page(title, body, base='../', charts=True))
    return len(every)
