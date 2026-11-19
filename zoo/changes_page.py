"""The Plausible changes page of the Settings tab (RULES 18).

Every value an experiment tried against its control, ranked by how good it
looks and how well it was tested, so the owner can pick changes he prefers
even when they do not save games. "Good" means fewer deaths, or at least not
more: a change with no measurable cost is safe to adopt.

Each change is one non-control arm of a study (its tiers pooled), compared
with that study's control on the same starts:

- **helpful**: fewer deaths than the control, exact McNemar p < 0.05;
- **leaning better**: fewer deaths, p < 0.25;
- **neutral**: no measurable difference (safe to adopt if preferred);
- **leaning worse**: more deaths, p < 0.25;
- **harmful**: more deaths, p < 0.05.

Within a bin, the most-tested changes come first. A second table lists the
settings the shipped borg-reborn-rs borg.txt writes out that no experiment
has varied yet.
"""
import re

from . import setting_descriptions
from .settings_page import fmt, head_row, run_link, slug, SORT_SCRIPT
from .site import esc, pval, table

BINS = ['helpful', 'leaning better', 'neutral', 'leaning worse', 'harmful']
BIN_NOTE = {
    'helpful': 'Fewer deaths than the control, p < 0.05.',
    'leaning better': 'Fewer deaths than the control, p < 0.25: a lead, not yet shown.',
    'neutral': 'No measurable difference in deaths: safe to adopt if preferred.',
    'leaning worse': 'More deaths than the control, p < 0.25: adopt only with a reason, or test further.',
    'harmful': 'More deaths than the control, p < 0.05.',
}


def classify(arm):
    pr = arm['paired']
    better = pr['rescued'] - pr['newly_killed']
    p = pr['death_p'] if pr['death_p'] is not None else 1.0
    if better > 0:
        return 'helpful' if p < 0.05 else 'leaning better' if p < 0.25 else 'neutral'
    if better < 0:
        return 'harmful' if p < 0.05 else 'leaning worse' if p < 0.25 else 'neutral'
    return 'neutral'


def changes(found):
    """One entry per non-control arm of every study (each study once)."""
    seen, out = set(), []
    for studies in found.values():
        for study in studies:
            if id(study) in seen:
                continue
            seen.add(id(study))
            row = head_row(study)
            ctl = next(a for a in row['arms'] if a['profile'] == row['control'])
            for arm in row['arms']:
                if arm['profile'] == row['control'] or not arm['paired'] or not arm['n']:
                    continue
                # An arm that leaves a setting unwritten where the control writes it out plays
                # the build's value: not a change of its own.
                diff = {k: v for k, v in arm['values'].items()
                        if repr(v) != repr(ctl['values'].get(k)) and v is not None}
                out.append({'row': row, 'study': study, 'arm': arm, 'ctl': ctl, 'diff': diff, 'bin': classify(arm)})
    out.sort(key=lambda c: (BINS.index(c['bin']), -c['arm']['n'],
                            c['arm']['deaths'] / c['arm']['n'] - c['ctl']['deaths'] / max(1, c['ctl']['n'])))
    return out


def study_name(study):
    meta = study['runs'][0]['metas'][0]
    name = meta['experiment']['name']
    return re.sub(r'-(pilot|verysmall|small-rest|small|medium|big|full|1800)$', '', name) if study['pooled'] else name


COLS = [('Change', 'The settings this arm sets differently from its control (the setting links to its page).'),
        ('Verdict', 'helpful / leaning better / neutral / leaning worse / harmful; see the legend.'),
        ('Starts', 'Starts per arm, every tier of the study pooled.'),
        ('Deaths: change / control', 'Deaths in this arm and in the control on the same starts.'),
        ('Δ death rate', 'Change minus control, in percentage points; negative is better.'),
        ('Saved / lost', 'Starts where only the control died / only this arm died.'),
        ('p', 'Exact McNemar test on saved against lost.'),
        ('Δ level', 'Mean character level reached, change minus control.'),
        ('Study', 'The study, its tiers and build; the link opens its newest run.')]


def change_row(c):
    arm, ctl, row = c['arm'], c['ctl'], c['row']
    meta = c['study']['runs'][0]['metas'][0]
    change = '<br>'.join(f'<a href="{slug(k)}.html"><code>{esc(k)}</code></a> = <code>{esc(fmt(v))}</code>'
                         f' <span class="muted">(control {esc(fmt(ctl["values"].get(k)))})</span>'
                         for k, v in sorted(c['diff'].items())) or f'<code>{esc(arm["profile"])}</code>'
    d = 100 * (arm['deaths'] / arm['n'] - ctl['deaths'] / max(1, ctl['n']))
    lv = (arm['level'] - ctl['level']) if arm.get('level') is not None and ctl.get('level') is not None else None
    pr = arm['paired']
    return [change,
            f'<span data-sort="{BINS.index(c["bin"])}">{esc(c["bin"])}</span>',
            f'{arm["n"]:,}',
            f'{arm["deaths"]} / {ctl["deaths"]}',
            f'{d:+.1f}',
            f'{pr["rescued"]} / {pr["newly_killed"]}',
            esc(pval(pr['death_p'])),
            '–' if lv is None else f'{lv:+.2f}',
            f'<a href="{run_link(meta, "../")}">{esc(study_name(c["study"]))}</a><br>'
            f'<span class="muted">{esc(row["tier"])} · {esc(row["specimen"].rsplit("-", 1)[-1])}</span>']


CURRENT = '4.2.6-reborn-rust-'
# Settings that run the harness rather than shape play: not candidates for a change.
OPERATIONAL = re.compile(r'autosave|cheat|delay|dump|verbose|respawn|save_death|stop_|_log|record|graphics|screen')


def untested(found):
    """Settings the shipped borg-reborn-rs borg.txt documents that no experiment varied."""
    described = setting_descriptions.load()
    out = []
    for key, d in sorted(described.items()):
        if (d.get('source', '').endswith('harness/borg.txt') and 'borg-reborn-rs' in d.get('source', '')
                and key not in found and not OPERATIONAL.search(key)):
            first = re.split(r'(?<=\.)\s', d['text'], maxsplit=1)[0]
            out.append([f'<code>{esc(key)}</code>', esc(first if len(first) <= 240 else first[:237] + '...')])
    return out


def page_body(found):
    from .landing import nav
    every = changes(found)
    rows = [c for c in every if c['row']['specimen'].startswith(CURRENT)]
    older = [c for c in every if not c['row']['specimen'].startswith(CURRENT)]
    counts = {b: sum(c['bin'] == b for c in rows) for b in BINS}
    legend = ''.join(f'<li><strong>{esc(b)}</strong> ({counts[b]}): {esc(BIN_NOTE[b])}</li>' for b in BINS)
    pending = untested(found)
    return (f'<h1>Borg zoo</h1>{nav("settings/index.html", "../")}'
            '<p><a href="index.html">All settings</a></p>'
            '<h2>Plausible changes</h2>'
            '<p>Every value an experiment tried against its control. '
            'A change does not have to save games to be worth adopting: one with no measurable cost is a '
            'valid choice if it plays a way the owner prefers (RULES 18). Ordered by verdict, then by how many '
            'starts tested it. Results on different builds are not interchangeable.</p>'
            f'<ul>{legend}</ul>'
            '<p class="muted">Click a column heading to sort by it.</p>'
            + '<h3>borg-reborn-rs builds</h3>'
            + table(COLS, [change_row(c) for c in rows])
            + f'<details><summary>Older Borgs and historical builds ({len(older)} changes: the C Borg, better-borg-c '
              'milestones, borg-rs before the reborn shell)</summary>'
            + table(COLS, [change_row(c) for c in older]) + '</details>'
            + '<h2>Plausible but not yet tested</h2>'
            f'<p>The {len(pending)} settings that the shipped borg-reborn-rs <code>harness/borg.txt</code> writes out '
            'with a comment, which no experiment has varied. The text is the first sentence of that comment.</p>'
            + table([('Setting', 'The exact borg.txt key.'), ('What it does', 'From the shipped borg.txt.')],
                    pending, left=2)
            + SORT_SCRIPT)
