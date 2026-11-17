"""Publish saved-encounter comparisons separately from natural-run statistics."""
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import re

SCHEMA='borg-zoo/saved-incident-comparison@1'
CLASSES=['Warrior','Mage','Druid','Priest','Necromancer','Paladin','Rogue','Ranger','Blackguard']
VALID={'death','survived_horizon','stopped'}
NAME=re.compile(r'[a-zA-Z0-9][a-zA-Z0-9_-]*')


def pairing(a,b):
    if a not in VALID or b not in VALID:return 'invalid'
    if 'stopped' in (a,b):return 'inconclusive'
    return {('death','death'):'both_died',('death','survived_horizon'):'rescued',('survived_horizon','death'):'newly_killed',('survived_horizon','survived_horizon'):'both_survived'}[a,b]


def roles(r):
    """(reference, candidate, counted arms); legacy records are baseline against speed30."""
    c=r.get('comparison') or dict(reference='baseline',candidate='speed30')
    return c['reference'],c['candidate'],r.get('counted_arms') or [a['id'] for a in r['arms']]


def compact(report,tier,evidence_url,howto_url,artifact=None,parent_run=None):
    if report.get('schema')!='borg-zoo/paired-incident-results@1':raise ValueError('not a paired saved-incident report')
    p=report['plan'];size=report['expected_cells']//2
    if report['expected_cells']!=size*2 or len(report['cells'])!=size*2:raise ValueError('incomplete report denominator')
    rows={(r['arm'],r['id']):r for r in report['cells']}
    if len(rows)!=len(report['cells']):raise ValueError('duplicate native cell')
    cases=[]
    for index,case in enumerate(p['cases'][:size]):
        s=case['scenario'];outcomes={};details={}
        for arm in p['arms']:
            row=rows[arm['id'],case['id']];cell=row.get('cell') or {};raw=cell.get('receipts',{})
            if row['status'] in VALID and not cell.get('execution_hash'):raise ValueError('valid cell lacks native identity')
            if cell.get('execution_hash'):
                body={k:v for k,v in cell.items() if k not in ('execution_hash','elapsed_seconds','validation_error')}
                if hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':')).encode()).hexdigest()!=cell['execution_hash']:raise ValueError('native cell identity differs')
            summary=json.loads(raw['run/summary.json']) if 'run/summary.json' in raw else {}
            outcomes[arm['id']]=row['status'];details[arm['id']]=dict(status=row['status'],summary=summary,streams=cell.get('streams',{}),cell_execution_hash=cell.get('execution_hash'),elapsed_seconds=cell.get('elapsed_seconds'),reason=cell.get('validation_error',cell.get('reason')))
        cases.append(dict(id=case['id'],class_idx=s['class_idx'],race_idx=s['race_idx'],birth_seed=s['birth_seed'],start_turn=s['start_turn'],
            historical_type=s['event_kind'],selection=s['selection'],coverage=s['coverage'],origin=s['origin'],
            scenario_sha256=case['scenario_sha256'],save_sha256=s['save_sha256'],suite=f'synthetic/balanced-999-incidents/generated/shards/{index//8:03d}.json',
            outcomes=outcomes,details=details,pair=pairing(outcomes['baseline'],outcomes['speed30'])))
    result=dict(schema=SCHEMA,name='balanced999-baseline-vs-speed30',tier=tier,run_url=report['run_url'],parent_run=parent_run,
        plan_hash=p['plan_hash'],definition=p['definition'],arms=p['arms'],manifest=p['manifest'],expected_cells=report['expected_cells'],
        collected_cells=sum(r.get('cell') is not None for r in report['cells']),invalid_count=report['invalid_count'],stopped_count=report['stopped_count'],
        pairs=report['pairs'],per_class=report['per_class'],cases=cases,bank_artifact=p['bank_artifact'],evidence_url=evidence_url,howto_url=howto_url,
        raw_report_artifact=artifact,independent_life=False,qualified_near_death={'coverage':'unavailable','count':None})
    validate(result);return result


def validate(r):
    if r.get('schema')!=SCHEMA or not NAME.fullmatch(r['name']):raise ValueError('unsupported saved comparison')
    for key in ('run_url','evidence_url','howto_url'):
        if not r[key].startswith('https://github.com/'):raise ValueError('saved report links must use public GitHub HTTPS URLs')
    cases=r['cases'];n=len(cases)
    reference,candidate,counted=roles(r);ids=[a['id'] for a in r['arms']]
    if len(set(ids))!=len(ids) or reference not in ids or candidate not in ids or not set(counted)<=set(ids):raise ValueError('saved comparison arms differ')
    if 'comparison' not in r and set(ids)!={'baseline','speed30'}:raise ValueError('saved comparison arms differ')
    if n not in [18,90,360,900,999] or r['expected_cells']!=len(counted)*n or len({c['id'] for c in cases})!=n:raise ValueError('saved comparison count differs')
    if Counter(c['class_idx'] for c in cases)!=Counter({i:n//9 for i in range(9)}):raise ValueError('saved comparison lost class balance')
    counts=Counter();by_reference={a:Counter() for a in r.get('pairs_by_reference',{})};invalid=stopped=0
    for c in cases:
        if not NAME.fullmatch(c['id']):raise ValueError('unsafe case ID')
        result=pairing(c['outcomes'][reference],c['outcomes'][candidate])
        if c['pair']!=result:raise ValueError('paired outcome differs')
        for ref in by_reference:
            if c['pair_by_reference'][ref]!=pairing(c['outcomes'][ref],c['outcomes'][candidate]):raise ValueError('paired outcome differs')
            by_reference[ref][c['pair_by_reference'][ref]]+=1
        counts[result]+=1;own=[c['outcomes'][a] for a in counted];invalid+=sum(s not in VALID for s in own);stopped+=sum(s=='stopped' for s in own)
    if counts!=Counter(r['pairs']) or invalid!=r['invalid_count'] or stopped!=r['stopped_count']:raise ValueError('saved outcome totals differ')
    if any(by_reference[a]!=Counter(v) for a,v in r.get('pairs_by_reference',{}).items()):raise ValueError('saved outcome totals differ')
    for a in r['arms']:
        if not re.fullmatch('[0-9a-f]{40}',a['source']['commit']):raise ValueError('exact source commit missing')
    return r


def esc(v):return html.escape(str(v))


def links(r):
    return '<p>'+ ' · '.join(f'<a href="{esc(r[k])}">{label}</a>' for k,label in [('run_url','Zoo execution'),('evidence_url','Cemetery evidence'),('howto_url','Run one scenario')] if r.get(k))+'</p>'


def builds(r):
    rows=[]
    for a in r['arms']:
        commit=a['source']['commit'];profile=a.get('profile','saved default profile')
        rows.append('<tr>'+''.join('<td>'+v+'</td>' for v in [esc(a['id']),esc(a['core']),esc(profile),f'<a href="https://github.com/{esc(a["source"]["repository"])}/tree/{commit}"><code>{commit}</code></a>',f'<code>{esc(a["build"]["binary_sha256"])}</code>'])+'</tr>')
    details=''.join('<details><summary>Complete '+esc(a['id'])+' settings and errands-file identity</summary><pre>'+esc(json.dumps(dict(settings=a['settings'],errands_plan_sha256=a.get('errands_plan_sha256'),inputs=a.get('inputs')),indent=2))+'</pre></details>' for a in r['arms'] if 'settings' in a)
    return '<h2>Builds and configuration</h2><div class="table-wrap"><table><tr><th>Setup</th><th>Core</th><th>Profile</th><th>Source</th><th>Binary SHA-256</th></tr>'+''.join(rows)+'</table></div>'+details


def case_page(r,c):
    from . import site,landing
    body='<h1>'+esc(c['id'])+'</h1>'+landing.nav('scenarios/index.html','../../../../../../')+'<p><a href="../../index.html">Back to comparison</a></p>'+links(r)
    body+='<p>'+esc(CLASSES[c['class_idx']])+f' · race index{c["race_idx"]} · level{c["coverage"]["level"]} · depth{c["coverage"]["depth"]} · start turn{c["start_turn"]} · '+esc(c['pair'].replace('_',' '))+'</p>'
    body+='<h2>Initial equipment and inventory</h2><pre>'+esc(json.dumps(c['coverage'],indent=2))+'</pre>'
    body+='<h2>Run this scenario</h2><p>Build or restore the exact source and its native tools once, unpack the Cemetery bank, then run from that Cemetery checkout. See the linked guide for all setup commands. Choose a fresh output directory for every attempt.</p>'
    for a in r['arms']:
        command=f"python3 scripts/single_encounter.py --suite {c['suite']} --case {c['id']} --source ../borg-{a['id']} --source-commit {a['source']['commit']} --core {a['core']} --native-tools ../tools-{a['id']} --out /tmp/{c['id']}-{a['id']}"
        if a['id']=='speed30' and 'comparison' not in r:command+=' --borg-txt studies/balanced999-speed30/borg.txt --errands-plan studies/balanced999-speed30/errands_plan.txt'
        elif a.get('inputs'):
            command+=f" --borg-txt <borg-zoo>/{a['inputs']['path']}/borg.txt"+(f" --errands-plan <borg-zoo>/{a['inputs']['path']}/errands_plan.txt" if a.get('errands_plan_sha256') else '')
        body+='<h3>'+esc(a['id'])+'</h3><pre>'+esc(command)+'</pre>'
    body+='<h2>Outcomes and reproduction hashes</h2><pre>'+esc(json.dumps(dict(save_sha256=c['save_sha256'],scenario_sha256=c['scenario_sha256'],selection=c['selection'],origin=c['origin'],details=c['details']),indent=2))+'</pre>'
    return site.page(c['id']+' · saved scenario',body,base='../../../../../../')


def render(r):
    from . import site,landing
    n=len(r['cases']);reference,candidate,counted=roles(r);title=r.get('title','Balanced999: baseline vs speed30');ids=[a['id'] for a in r['arms']]
    body='<h1>'+esc(title)+'</h1>'+landing.nav('scenarios/index.html','../../../../')
    body+=f'<h2>{esc(r["tier"])} stage: {n} scenarios, {r["expected_cells"]} cells</h2><p>{n//9} starts per class per setup. Invalid/missing: {r["invalid_count"]}; stopped: {r["stopped_count"]}.</p>'+links(r)
    if 'comparison' in r:body+=f'<p>{esc(candidate)} ran {n} saved encounters of {esc(r["suite"]["name"])}; the other setups are earlier published runs of the same suite, reused, not rerun. '
    else:body+='<p>'
    body+='Saved encounters with fresh Borg memory and saved engine RNG, an exact 2,000-engine-turn horizon and 5-second wall limit. Sources, cores and configuration differ between setups; these results do not isolate one setting or establish population improvement. Encounters from one life remain correlated. Historical critical-HP recoveries are a screen, not qualified counterfactual near-deaths.</p>'
    shares=[]
    for a in r['arms']:
        deaths=sum(c['outcomes'][a['id']]=='death' for c in r['cases'])
        label=esc(a['id'])+f' <span class="muted">{esc(a["source"]["commit"][:8])}, {esc(a.get("core",""))}</span>'
        shares.append([label,f'{100*deaths/n:.1f}% <span class="muted">({deaths} of {n})</span>'])
    body+='<h2>Deaths per build</h2>'+site.table(['Build','Deaths'],shares)
    tables=r.get('pairs_by_reference') or {reference:r['pairs']}
    for ref,pairs in tables.items():
        body+=f'<h2>Paired outcomes: {esc(candidate)} against {esc(ref)}</h2>'+site.table(['Outcome','Scenarios'],[[esc(k.replace('_',' ')),v] for k,v in sorted(pairs.items())])
    rows=[]
    for i,name in enumerate(CLASSES):
        group=[c for c in r['cases'] if c['class_idx']==i];pairs=Counter(c['pair'] for c in group);row=[name,len(group)]
        for a in ids:
            got=Counter(c['outcomes'][a] for c in group);row+=[got['death'],got['survived_horizon']]
        rows.append(row+[pairs['rescued'],pairs['newly_killed']])
    head=['Class','Starts/setup']+[h for a in ids for h in (a+' deaths',a+' survived')]+[f'Rescued vs {reference}',f'Newly killed vs {reference}']
    body+='<h2>Class balance and outcomes</h2>'+site.table(head,rows)
    body+=builds(r)
    body+='<h2>Every scenario</h2><p>Open a scenario for its initial equipment, exact outcomes, hashes and single-scenario commands.</p><label>Filter <input id="saved-filter" placeholder="class, outcome or scenario ID"></label><table id="saved-cases"><thead><tr><th>Scenario</th><th>Class</th><th>Level/depth</th><th>Historical incident</th>'+''.join('<th>'+esc(a)+'</th>' for a in ids)+f'<th>Pair vs {esc(reference)}</th></tr></thead><tbody>'
    for c in r['cases']:
        vals=[f'<a href="cases/{c["id"]}/index.html">{esc(c["id"])}</a>',esc(CLASSES[c['class_idx']]),f'{c["coverage"]["level"]}/{c["coverage"]["depth"]}',esc(c['historical_type'].replace('_',' '))]+[esc(c['outcomes'][a]) for a in ids]+[esc(c['pair'].replace('_',' '))]
        body+='<tr>'+''.join('<td>'+v+'</td>' for v in vals)+'</tr>'
    body+='</tbody></table><p><a href="comparison.json">Download the compact report</a>. Native source receipts and stream evidence are linked in Cemetery and the Zoo workflow artifacts.</p><script>document.getElementById("saved-filter").addEventListener("input",function(){const q=this.value.toLowerCase();document.querySelectorAll("#saved-cases tbody tr").forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(q));});</script>'
    return site.page('Saved incidents · '+title,body,base='../../../../')


def build_site(results,out):
    roots=[Path(results).parent/'saved-incident-results'];rows=[];unavailable=[]
    for root in roots:
        for path in sorted(root.glob('*/*/comparison.json')):
            name,run=path.parent.parent.name,path.parent.name
            try:
                if not NAME.fullmatch(name) or not NAME.fullmatch(run):raise ValueError('unsafe saved report path')
                r=validate(json.loads(path.read_text()));target=Path(out)/'saved'/name/run;target.mkdir(parents=True,exist_ok=True)
                (target/'index.html').write_text(render(r));(target/'comparison.json').write_bytes(path.read_bytes())
                for case in r['cases']:
                    dest=target/'cases'/case['id'];dest.mkdir(parents=True,exist_ok=True);(dest/'index.html').write_text(case_page(r,case))
                versions='<br>'.join(esc(a.get('specimen',a['id']))+' · <code>'+esc(a['source']['commit'][:12])+'</code>' for a in r['arms'])
                rows.append([f'<a href="saved/{name}/{run}/index.html">{esc(name)}</a><br><span class="muted">Saved encounters · {esc(r["tier"])} · {esc(run)}</span>',versions,len(r['cases']),f'{r["collected_cells"]}/{r["expected_cells"]}',esc(', '.join(k.replace('_',' ')+': '+str(v) for k,v in sorted(r['pairs'].items())))])
            except (OSError,ValueError,KeyError,TypeError,AttributeError) as error:unavailable.append(dict(report=f'{name}/{run}',reason=str(error)))
    return rows,unavailable


def main():
    import argparse
    q=argparse.ArgumentParser(description=__doc__)
    q.add_argument('--input',type=Path,required=True);q.add_argument('--out',type=Path,required=True);q.add_argument('--tier',required=True)
    q.add_argument('--evidence-url',required=True);q.add_argument('--howto-url',required=True)
    q.add_argument('--parent-run',type=int)
    a=q.parse_args()
    if a.out.exists():raise ValueError('fresh compact output directory required')
    report=compact(json.loads(a.input.read_text()),a.tier,a.evidence_url,a.howto_url,parent_run=a.parent_run)
    report['raw_report_sha256']=hashlib.sha256(a.input.read_bytes()).hexdigest()
    a.out.mkdir(parents=True);(a.out/'comparison.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    (a.out/'index.html').write_text(render(report))


if __name__=='__main__':main()
