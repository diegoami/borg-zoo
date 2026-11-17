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
    if n not in [18,90,360,900,999] or r['expected_cells']!=2*n or len({c['id'] for c in cases})!=n:raise ValueError('saved comparison count differs')
    if Counter(c['class_idx'] for c in cases)!=Counter({i:n//9 for i in range(9)}):raise ValueError('saved comparison lost class balance')
    if {a['id'] for a in r['arms']}!={'baseline','speed30'}:raise ValueError('saved comparison arms differ')
    counts=Counter();invalid=stopped=0
    for c in cases:
        if not NAME.fullmatch(c['id']):raise ValueError('unsafe case ID')
        a,b=c['outcomes']['baseline'],c['outcomes']['speed30'];result=pairing(a,b)
        if c['pair']!=result:raise ValueError('paired outcome differs')
        counts[result]+=1;invalid+=sum(s not in VALID for s in (a,b));stopped+=sum(s=='stopped' for s in (a,b))
    if counts!=Counter(r['pairs']) or invalid!=r['invalid_count'] or stopped!=r['stopped_count']:raise ValueError('saved outcome totals differ')
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
    settings=next(a for a in r['arms'] if a['id']=='speed30')
    return '<h2>Builds and configuration</h2><div class="table-wrap"><table><tr><th>Setup</th><th>Core</th><th>Profile</th><th>Source</th><th>Binary SHA-256</th></tr>'+''.join(rows)+'</table></div><details><summary>Complete speed30 settings and errands-file identity</summary><pre>'+esc(json.dumps(dict(settings=settings['settings'],errands_plan_sha256=settings['errands_plan_sha256']),indent=2))+'</pre></details>'


def case_page(r,c):
    from . import site,landing
    body='<h1>'+esc(c['id'])+'</h1>'+landing.nav('scenarios/index.html','../../../../../../')+'<p><a href="../../index.html">Back to comparison</a></p>'+links(r)
    body+='<p>'+esc(CLASSES[c['class_idx']])+f' · race index{c["race_idx"]} · level{c["coverage"]["level"]} · depth{c["coverage"]["depth"]} · start turn{c["start_turn"]} · '+esc(c['pair'].replace('_',' '))+'</p>'
    body+='<h2>Initial equipment and inventory</h2><pre>'+esc(json.dumps(c['coverage'],indent=2))+'</pre>'
    body+='<h2>Run this scenario</h2><p>Build or restore the exact source and its native tools once, unpack the Cemetery bank, then run from that Cemetery checkout. See the linked guide for all setup commands. Choose a fresh output directory for every attempt.</p>'
    candidate=next(a for a in r['arms'] if a['id']=='speed30');base=next(a for a in r['arms'] if a['id']=='baseline')
    for a in [base,candidate]:
        command=f"python3 scripts/single_encounter.py --suite {c['suite']} --case {c['id']} --source ../borg-{a['id']} --source-commit {a['source']['commit']} --core {a['core']} --native-tools ../tools-{a['id']} --out /tmp/{c['id']}-{a['id']}"
        if a['id']=='speed30':command+=' --borg-txt studies/balanced999-speed30/borg.txt --errands-plan studies/balanced999-speed30/errands_plan.txt'
        body+='<h3>'+esc(a['id'])+'</h3><pre>'+esc(command)+'</pre>'
    body+='<h2>Outcomes and reproduction hashes</h2><pre>'+esc(json.dumps(dict(save_sha256=c['save_sha256'],scenario_sha256=c['scenario_sha256'],selection=c['selection'],origin=c['origin'],details=c['details']),indent=2))+'</pre>'
    return site.page(c['id']+' · saved scenario',body,base='../../../../../../')


def render(r):
    from . import site,landing
    n=len(r['cases']);body='<h1>Balanced999: baseline vs speed30</h1>'+landing.nav('scenarios/index.html','../../../../')
    body+=f'<h2>{esc(r["tier"])} stage: {n} scenarios, {r["expected_cells"]} cells</h2><p>{n//9} starts per class per setup. Invalid/missing: {r["invalid_count"]}; stopped: {r["stopped_count"]}.</p>'+links(r)
    body+='<p>Saved encounters with fresh Borg memory and saved engine RNG. Both setups use an exact2,000-engine-turn horizon and5-second wall limit. Sources, cores and configuration differ; these results do not isolate speed30 or establish population improvement. Encounters from one life remain correlated. Historical critical-HP recoveries are a screen, not qualified counterfactual near-deaths.</p>'
    body+='<h2>Paired outcomes</h2>'+site.table(['Outcome','Scenarios'],[[esc(k.replace('_',' ')),v] for k,v in sorted(r['pairs'].items())])
    rows=[]
    for i,name in enumerate(CLASSES):
        group=[c for c in r['cases'] if c['class_idx']==i];a=Counter(c['outcomes']['baseline'] for c in group);b=Counter(c['outcomes']['speed30'] for c in group)
        pairs=Counter(c['pair'] for c in group)
        rows.append([name,len(group),a['death'],a['survived_horizon'],b['death'],b['survived_horizon'],pairs['rescued'],pairs['newly_killed']])
    body+='<h2>Class balance and outcomes</h2>'+site.table(['Class','Starts/setup','Baseline deaths','Baseline survived','Speed30 deaths','Speed30 survived','Rescued','Newly killed'],rows)
    body+=builds(r)
    body+='<h2>Every scenario</h2><p>Open a scenario for its initial equipment, exact outcomes, hashes and single-scenario commands.</p><label>Filter <input id="saved-filter" placeholder="class, outcome or scenario ID"></label><table id="saved-cases"><thead><tr><th>Scenario</th><th>Class</th><th>Level/depth</th><th>Historical incident</th><th>Baseline</th><th>Speed30</th><th>Pair</th></tr></thead><tbody>'
    for c in r['cases']:
        vals=[f'<a href="cases/{c["id"]}/index.html">{esc(c["id"])}</a>',esc(CLASSES[c['class_idx']]),f'{c["coverage"]["level"]}/{c["coverage"]["depth"]}',esc(c['historical_type'].replace('_',' ')),esc(c['outcomes']['baseline']),esc(c['outcomes']['speed30']),esc(c['pair'].replace('_',' '))]
        body+='<tr>'+''.join('<td>'+v+'</td>' for v in vals)+'</tr>'
    body+='</tbody></table><p><a href="comparison.json">Download the compact report</a>. Native source receipts and stream evidence are linked in Cemetery and the Zoo workflow artifacts.</p><script>document.getElementById("saved-filter").addEventListener("input",function(){const q=this.value.toLowerCase();document.querySelectorAll("#saved-cases tbody tr").forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(q));});</script>'
    return site.page('Saved incidents · baseline vs speed30',body,base='../../../../')


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
