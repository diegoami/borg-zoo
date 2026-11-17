"""Discover frozen saved suites without treating a different build as a new bank."""
import html
import json
from pathlib import Path
from . import catalogue, site, suite_runs


def catalogue_entries(root=None):
    root=Path(root or catalogue.ROOT)
    entries=[]
    for path in sorted((root/'scenario-suites').glob('*/suite.json')):
        entry=suite_runs.suite(root,path.parent.name)
        entries.append(entry)
    return entries


def build_site(out, root=None):
    root=Path(root or catalogue.ROOT);out=Path(out)
    rows=[]
    for entry in catalogue_entries(root):
        esc=html.escape
        ident=entry['id'];name=entry['name'];bank=entry['bank']
        plan=json.loads((root/entry['cases_plan']['path']).read_text())
        cases=plan['cases']
        classes={c['scenario']['class_idx'] for c in cases}
        counts={cls:sum(c['scenario']['class_idx']==cls for c in cases) for cls in classes}
        balance=', '.join(str(v) for v in sorted(set(counts.values())))+' per class'
        url=f'https://github.com/{entry["cemetery"]["repository"]}/tree/{entry["cemetery"]["commit"]}/{bank["members"]}'
        detail=(f'<h1>Borg zoo</h1><p><a href="../../index.html">Scenarios</a></p><h2>{esc(name)}</h2>'
                f'<p><code>{esc(ident)}</code> · version {entry["version"]} · {len(cases)} saved starts · {balance}</p>'
                f'<p>{esc(entry["description"])}</p>'
                f'<p>Bank SHA-256: <code>{esc(bank["sha256"])}</code></p>'
                f'<p><a href="{url}">Pinned Cemetery inputs and provenance</a> · <a href="suite.json">Exact suite manifest</a></p>'
                '<p>New Borg builds and settings are runs of this suite. A change to its saved starts requires a new version. '
                'Compare outcomes on identical starts within one suite; differences between banks describe coverage.</p>'
                '<p>To select this suite, set <code>suite: '+esc(ident)+'</code> in a suite-run YAML definition. '
                'Generate it with <code>python3 -m zoo define definitions/NAME.yaml</code>, then dispatch '
                '<code>suite-run.yml</code> with that definition and <code>stage=smoke</code>.</p>'
                '<p><a href="https://github.com/diegoami/borg-zoo/blob/main/docs/SUITE-RUNS.md">Run and preparation guide</a></p>')
        target=out/'suites'/ident;target.mkdir(parents=True,exist_ok=True)
        (target/'index.html').write_text(site.page(name+' · Borg zoo',detail,base='../../../'))
        (target/'suite.json').write_bytes((root/'scenario-suites'/ident/'suite.json').read_bytes())
        rows.append([f'<a href="suites/{ident}/index.html">{esc(name)}</a><br><code>{esc(ident)}</code>',
                     len(cases),f'{len(classes)} classes · {balance}',f'<code>{esc(bank["sha256"][:16])}…</code>'])
    for path in sorted((root/'scenario-suites').glob('*/preparation.json')):
        if (path.parent/'suite.json').exists():continue
        prep=json.loads(path.read_text());esc=html.escape
        if prep.get('schema')!='borg-zoo/saved-suite-preparation@1' or prep['id']!=path.parent.name:
            raise ValueError('invalid suite preparation identity')
        rows.append([f'<a href="{esc(prep["run_url"],quote=True)}">{esc(prep["name"])}</a><br><code>{esc(prep["id"])}</code><br><span class="muted">Preparation blocked; not runnable</span>',
                     f'{prep["usable_cases"]} / {prep["expected_cases"]}',f'Target: {prep["per_class"]} per class',
                     'Not frozen'])
    return ('<h2>Saved encounter suites</h2>'
            '<p>A suite fixes the saved starts; a run fixes the Borg build and configuration. '
            'Every suite has its own immutable ID and bank digest.</p>'
            +site.table(['Suite','Saved starts','Class balance','Bank SHA-256'],rows,left=1)) if rows else ''
