"""Balanced nine-class incident preparation and full saved-bank orchestration."""
import json
from pathlib import Path
import re


def definition_plan(d, path, root):
    if d.get('kind')=='balanced-incident-execution':
        return execution_definition_plan(d,path,root)
    keys={'kind','name','folder','issue','question','cemetery','preparation_source','native_tools','baseline_specimen','expected_cells','classes','per_class','parallel_jobs','owner_authorization','prespecified'}
    if set(d)!=keys or d['kind']!='balanced-incident-harvest' or d['folder']!='scenario-experiments':
        raise ValueError('unsupported balanced harvest definition')
    if d['expected_cells']!=999 or d['classes']!=list(range(9)) or d['per_class']!=111 or not 1<=d['parallel_jobs']<=9:
        raise ValueError('equal111-per-class contract required')
    for key,repo in [('cemetery','diegoami/borg-cemetery'),('native_tools','diegoami/borg-cemetery'),('preparation_source','diegoami/borg-reborn-rs')]:
        if d[key]['repository']!=repo or not re.fullmatch('[0-9a-f]{40}',d[key]['commit']):raise ValueError('immutable repository pins required')
    if not re.fullmatch('[0-9a-f]{64}',d['cemetery']['spec_sha256']) or not isinstance(d['issue'],int) or d['issue']<=0:
        raise ValueError('spec digest and tracking issue required')
    specimen=json.loads((root/'catalogue/specimens.json').read_text())['specimens'][d['baseline_specimen']]
    body=dict(d,schema='borg-zoo/balanced-incident-harvest@1',definition=Path(path).resolve().relative_to(root.resolve()).as_posix(),baseline=dict(repository=specimen['repository'],commit=specimen['ref'],specimen=d['baseline_specimen']))
    target=root/d['folder']/(d['name']+'.json');changes=[]
    if not target.exists() or json.loads(target.read_text())!=body:changes.append(('experiment-update' if target.exists() else 'experiment',target.relative_to(root).as_posix(),body))
    return d,[],changes

# Saved-bank execution uses the existing native receipt validator, while its
# own plan schema permits all nine balanced classes and a bounded batch matrix.
import argparse
from collections import Counter, defaultdict
import hashlib
import os
import signal
import subprocess
import sys
import tarfile
import time
from . import encounters as native

CLASSES={0:'Warrior',1:'Mage',2:'Druid',3:'Priest',4:'Necromancer',5:'Paladin',6:'Rogue',7:'Ranger',8:'Blackguard'}
ROOT=Path(__file__).resolve().parents[1]
TIERS={'smoke':18,'small':90,'medium':360,'big':900,'full':999}


def execution_groups(cases):
    groups=[];start=0
    for tier,end in TIERS.items():
        for offset in range(start,end,40):
            groups.append((tier+f'-{(offset-start)//40:03d}' if tier!='smoke' else tier,cases[offset:min(offset+40,end)]))
        start=end
    return groups


def execution_definition_plan(d,path,root):
    required={'kind','name','folder','issue','question','cemetery','native_tools','source','bank_artifact','bank_manifest','expected_cells','per_class','owner_authorization','prespecified'}
    if set(d)!=required or d['kind']!='balanced-incident-execution' or d['expected_cells']!=999 or d['per_class']!=111:
        raise ValueError('balanced999 execution definition required')
    for key,repo in [('cemetery','diegoami/borg-cemetery'),('native_tools','diegoami/borg-cemetery'),('source','diegoami/borg-reborn-rs')]:
        if d[key]['repository']!=repo or not re.fullmatch('[0-9a-f]{40}',d[key]['commit']):raise ValueError('immutable execution pins required')
    artifact=d['bank_artifact']
    if not re.fullmatch('[0-9a-f]{64}',artifact['sha256']) or not isinstance(artifact['id'],int) or artifact['id']<=0 or not isinstance(artifact['run_id'],int) or artifact['run_id']<=0:
        raise ValueError('exact prepared bank artifact required')
    if d['folder']!='scenario-experiments':raise ValueError('scenario namespace required')
    body=dict(d,schema='borg-zoo/balanced-incident-execution@1',definition=Path(path).resolve().relative_to(root.resolve()).as_posix())
    target=root/d['folder']/(d['name']+'.json');changes=[]
    if not target.exists() or json.loads(target.read_text())!=body:changes.append(('experiment-update' if target.exists() else 'experiment',target.relative_to(root).as_posix(),body))
    return d,[],changes


def prepare_execution(definition_path, bank, source, output, archive):
    definition=native.read(definition_path)
    if definition.get('schema')!='borg-zoo/balanced-incident-execution@1':raise ValueError('unsupported execution definition')
    native.checked_checkout(bank,definition['cemetery']['commit'])
    native.checked_checkout(source,definition['source']['commit'])
    if native.sha(archive)!=definition['bank_artifact']['sha256']:raise ValueError('bank artifact changed')
    sys.path.insert(0,str(bank/'scripts'))
    from encounter_bank import prepare_bank
    manifest=bank/definition['bank_manifest']
    bank_info,shards=prepare_bank(manifest,bank)
    cases=[]
    for path,_ in shards:
        leaf=native.read(path)
        for entry in leaf['scenarios']:
            p=native.local(bank,entry['scenario'],entry['sha256']);scenario=native.read(p)
            if scenario['event_kind'] not in ('death','observed_critical_recovery'):raise ValueError('not an incident case')
            incident=scenario['historical_incident']
            if incident['type']=='observed_critical_recovery':
                w=incident['witness'];low=w['minimum'];recovery=w['recovery']
                if not 0<=low['hp']<=low['max_hp']*.25 or recovery['hp']<recovery['max_hp']*.5 or recovery['turn']<=low['turn']:
                    raise ValueError('critical recovery witness differs')
            cases.append(dict(id=entry['id'],scenario_path=entry['scenario'],scenario_sha256=entry['sha256'],scenario=scenario,
                              profile_text=(p.parent/scenario['baseline_profile']).read_text()))
    if len(cases)!=999 or Counter(c['scenario']['class_idx'] for c in cases)!=Counter({i:111 for i in range(9)}):
        raise ValueError('bank is not exactly balanced999')
    source_sha=subprocess.check_output(['bash',str(source/'harness/identity.sh'),'source-hash','rust'],text=True).strip()
    plan=dict(schema='borg-zoo/balanced-incident-execution-plan@1',definition=definition,definition_sha256=native.sha(definition_path),
              zoo_commit=native.git(ROOT,'rev-parse','HEAD'),runner_sha256=native.sha(Path(__file__)),source_sha256=source_sha,
              manifest=dict(horizon_engine_turns=2000,wall_seconds=5,engine_commit='42cd156ac9f95ddf4311e88dd7ad462292d6d1d6'),
              cases=cases,expected_cells=999,batches=[])
    # Smoke cases are not executed again in the full stage. Together they are999.
    groups=execution_groups(cases)
    for name,group in groups:
        refs=[]
        for offset in range(0,len(group),8):
            path=bank/'synthetic/balanced-999-incidents/generated/execution'/name/f'{offset//8}.json'
            body=dict(schema='borg-cemetery/saved-encounter-suite@1',suite_id=name+f'-{offset//8}',core='reborn',baseline_source_commit=definition['source']['commit'],
                      **plan['manifest'],scenarios=[dict(id=c['id'],scenario=c['scenario_path'],sha256=c['scenario_sha256']) for c in group[offset:offset+8]])
            native.write(path,body);refs.append(dict(manifest=path.relative_to(bank).as_posix(),sha256=native.sha(path)))
            for c in group[offset:offset+8]:c['native_relative']=f'shard-{offset//8+1}/'+c['id']
        path=bank/'synthetic/balanced-999-incidents/generated/execution'/name/'bank.json'
        native.write(path,dict(schema='borg-cemetery/encounter-bank@1',id=name,expected_cases=len(group),shards=refs))
        plan['batches'].append(dict(id=name,cases=[c['id'] for c in group],manifest=path.relative_to(bank).as_posix(),manifest_sha256=native.sha(path)))
    plan['plan_hash']=native.digest(plan)
    native.write(output,plan)
    return plan


def read_execution_plan(path):
    plan=native.read(path);body={k:v for k,v in plan.items() if k!='plan_hash'}
    if plan.get('schema')!='borg-zoo/balanced-incident-execution-plan@1' or native.digest(body)!=plan['plan_hash']:raise ValueError('execution plan changed')
    if len(plan['cases'])!=999 or Counter(c['scenario']['class_idx'] for c in plan['cases'])!=Counter({i:111 for i in range(9)}):raise ValueError('class balance changed')
    if plan.get('expected_cells')!=999 or plan['manifest'].get('horizon_engine_turns')!=2000 or plan['manifest'].get('wall_seconds')!=5:
        raise ValueError('execution budget differs')
    if len({b['id'] for b in plan['batches']})!=len(plan['batches']) or any(not 1<=len(b['cases'])<=40 for b in plan['batches']):
        raise ValueError('batch budget/identity differs')
    if plan['batches'][0]['id']!='smoke' or len(plan['batches'][0]['cases'])!=18:
        raise ValueError('mixed18-case smoke required before full bank')
    by_id={c['id']:c for c in plan['cases']}
    if Counter(by_id[i]['scenario']['class_idx'] for i in plan['batches'][0]['cases'])!=Counter({i:2 for i in range(9)}):
        raise ValueError('smoke lost its two-per-class mix')
    expected_groups=execution_groups(plan['cases'])
    if [(b['id'],b['cases']) for b in plan['batches']]!=[(name,[c['id'] for c in group]) for name,group in expected_groups]:
        raise ValueError('nested tier order changed')
    ids=[c for batch in plan['batches'] for c in batch['cases']]
    if len(ids)!=999 or len(set(ids))!=999 or set(ids)!={c['id'] for c in plan['cases']}:raise ValueError('duplicate or missing scheduled case')
    return plan


def execute_batch(plan_path,bank,source,tools,batch_id,out):
    plan=read_execution_plan(plan_path)
    if native.sha(Path(__file__))!=plan['runner_sha256']:raise ValueError('Zoo runner changed')
    native.checked_checkout(bank,plan['definition']['cemetery']['commit'])
    native.checked_checkout(source,plan['definition']['source']['commit'])
    native.checked_checkout(tools,plan['definition']['native_tools']['commit'])
    batch=next(b for b in plan['batches'] if b['id']==batch_id)
    path=native.local(bank,batch['manifest'],batch['manifest_sha256'])
    if out.exists():raise ValueError('fresh attempt directory required')
    out.mkdir(parents=True)
    env={k:v for k,v in os.environ.items() if not k.startswith(('BORG_','ANGBAND_','BORGH_')) and k not in ('SAVE_ROOT','STALL_TIMEOUT_SECONDS')}
    env['BORG_CEMETERY_DIR']=str(tools)
    command=[sys.executable,str(bank/'scripts/encounter_bank.py'),'--manifest',str(path),'--source',str(source),'--out',str(out/'native')]
    remaining={c['id']:c for c in plan['cases'] if c['id'] in batch['cases']}
    def journal():
        for name,case in list(remaining.items()):
            directory=out/'native'/case['native_relative']
            if not(directory/'trial.json').exists():continue
            try:
                cell=native.make_cell(plan,case,directory)
                if cell is not None:native.write(out/'cells'/(name+'.json'),cell);del remaining[name]
            except (ValueError,OSError):pass
    tick=time.monotonic();timed_out=False
    with(out/'launcher.log').open('w') as log:
        process=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        while True:
            journal()
            if process.poll() is not None:journal();break
            if time.monotonic()-tick>len(batch['cases'])*35+60:
                timed_out=True;os.killpg(process.pid,signal.SIGTERM)
                try:process.wait(timeout=10)
                except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
                journal();break
            time.sleep(.2)
    native.write(out/'execution.json',dict(batch=batch_id,returncode=process.returncode,timed_out=timed_out,remaining=list(remaining),elapsed_seconds=time.monotonic()-tick))
    return int(process.returncode!=0 or bool(remaining))


def collect_execution(plan_path,inputs,out,run_url='',smoke_only=False,tier='full'):
    plan=read_execution_plan(plan_path)
    if out.exists():raise ValueError('fresh report directory required')
    paths={}
    expected_ids={c['id'] for c in plan['cases']}
    for path in inputs.rglob('*.json'):
        try:
            data=native.read(path)
            if data.get('schema')!='borg-zoo/saved-encounter-cell@1' and path.stem not in expected_ids:continue
            name=data.get('id',path.stem)
        except (ValueError,AttributeError):
            if path.stem not in expected_ids:continue
            name=path.stem
        if name not in expected_ids:raise ValueError('unknown case attempt: '+name)
        if name in paths:raise ValueError('duplicate case attempt: '+name)
        paths[name]=path
    cases=plan['cases'][:TIERS['smoke' if smoke_only else tier]]
    counts=defaultdict(Counter);rows=[]
    for case in cases:
        s=case['scenario'];row=dict(id=case['id'],class_name=CLASSES[s['class_idx']],historical_type=s['event_kind'],origin=s['origin'],status='missing')
        if case['id'] in paths:
            try:
                cell=native.read(paths[case['id']])
                if cell.get('schema')!='borg-zoo/saved-encounter-cell@1' or cell['id']!=case['id'] or cell['plan_hash']!=plan['plan_hash']:raise ValueError('cell identity changed')
                for name,text in cell['receipts'].items():
                    if hashlib.sha256(text.encode()).hexdigest()!=cell['receipts_sha256'][name]:raise ValueError('receipt changed')
                status=native.validate_receipts(plan,case,cell['receipts']);trial=json.loads(cell['receipts']['trial.json'])
                execution=native.digest(dict(plan=plan['plan_hash'],scenario=case['scenario_sha256'],build=trial.get('build'),receipts=cell['receipts_sha256']))
                if execution!=cell['execution_hash'] or status!=cell['status']:raise ValueError('execution or outcome changed')
                row.update(status=status,summary=trial.get('summary'),build=trial.get('build'),cell=cell)
            except (ValueError,KeyError,TypeError,OSError,AttributeError) as error:row.update(status='invalid_receipt',reason=str(error))
        counts[row['class_name']][row['status']]+=1;rows.append(row)
    invalid=sum(r['status'] not in native.VALID for r in rows)
    report=dict(schema='borg-zoo/balanced-incident-results@1',expected_cells=len(cases),cells=rows,per_class=dict(counts),invalid_count=invalid,
                plan=plan,run_url=run_url,independent_life=False,qualified_near_death=dict(coverage='unavailable',count=None))
    native.write(out/'comparison.json',report)
    lines=['# Zoo balanced incident bank','',f'{len(cases)} requested cases. Invalid/missing: {invalid}.',
           f"Source: `{plan['definition']['source']['commit']}`; bank artifact: `{plan['definition']['bank_artifact']['sha256']}`.",'',
           '| Class | Death | Horizon survival | Stopped | Invalid/missing |','|---|---:|---:|---:|---:|']
    for cls,name in CLASSES.items():
        c=counts[name];lines.append(f"| {name} | {c['death']} | {c['survived_horizon']} | {c['stopped']} | {sum(v for k,v in c.items() if k not in native.VALID)} |")
    lines +=['','Historical incidents are actual deaths or observed loss to≤25% HP followed by recovery≥50%. This is not qualified counterfactual lethality.','',
             'Shared-life events remain correlated. Horizon survival is not an eventual win or an improvement finding.','',f'[Zoo run]({run_url})']
    (out/'comparison.md').write_text('\n'.join(lines)+'\n')
    return int(bool(invalid) or (smoke_only or tier!='full') and any(r['status']=='stopped' for r in rows))


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    a=sub.add_parser('plan')
    for name in ('definition','bank','source','out','archive'):a.add_argument('--'+name,type=Path,required=True)
    a=sub.add_parser('run')
    for name in ('plan','bank','source','tools','out'):a.add_argument('--'+name,type=Path,required=True)
    a.add_argument('--batch',required=True)
    a=sub.add_parser('collect')
    for name in ('plan','inputs','out'):a.add_argument('--'+name,type=Path,required=True)
    a.add_argument('--run-url',default='');a.add_argument('--smoke-only',action='store_true');a.add_argument('--tier',choices=list(TIERS),default='full')
    args=p.parse_args()
    if args.action=='plan':prepare_execution(args.definition.resolve(),args.bank.resolve(),args.source.resolve(),args.out.resolve(),args.archive.resolve());return 0
    if args.action=='run':return execute_batch(args.plan.resolve(),args.bank.resolve(),args.source.resolve(),args.tools.resolve(),args.batch,args.out.resolve())
    return collect_execution(args.plan.resolve(),args.inputs.resolve(),args.out.resolve(),args.run_url,args.smoke_only,args.tier)


if __name__=='__main__':raise SystemExit(main())
