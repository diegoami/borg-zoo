"""Execute pinned saved incidents through both requested Borg controllers."""
import argparse
from collections import Counter
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from . import encounters as n, incident_bank as bank
from .borgrs import config_text

ROOT=Path(__file__).resolve().parents[1]
SCHEMA='borg-zoo/paired-incident-execution@1'
FILES=['trial.json','run/summary.json','run/process.json','run/config.txt','run/params.json',
       'run/params-core.json','run/configuration.json','run/user/borg.txt','run/errands_plan.txt']


def definition_plan(d,path,root):
    required={'kind','name','folder','issue','question','comparison_plan','baseline_plan','cemetery','native_tools','owner_authorization','prespecified','expected_cells'}
    if set(d)!=required or d['kind']!='paired-incident-execution' or d['expected_cells']!=1998 or d['folder']!='scenario-experiments':raise ValueError('unsupported paired execution definition')
    for key in ('comparison_plan','baseline_plan'):n.local(root,d[key]['path'],d[key]['sha256'])
    pins=[d['cemetery']]
    tools=d['native_tools']
    pins += [tools] if 'commit' in tools else [tools[a] for a in ('baseline','speed30')]
    for pin in pins:
        if pin['repository']!='diegoami/borg-cemetery' or not n.SHA.fullmatch(pin['commit']):raise ValueError('exact Cemetery pin required')
    body=dict(d,schema='borg-zoo/paired-incident-definition@1',definition=Path(path).resolve().relative_to(root.resolve()).as_posix())
    target=root/d['folder']/(d['name']+'.json');changes=[]
    if not target.exists() or n.read(target)!=body:changes.append(('experiment-update' if target.exists() else 'experiment',target.relative_to(root).as_posix(),body))
    return d,[],changes


def prepare(definition,cemetery,sources,builds,archive,out):
    d=n.read(definition);base=bank.read_execution_plan(n.local(ROOT,d['baseline_plan']['path'],d['baseline_plan']['sha256']))
    previous=n.read(n.local(ROOT,d['comparison_plan']['path'],d['comparison_plan']['sha256']))
    if n.digest({k:v for k,v in previous.items() if k!='plan_hash'})!=previous['plan_hash'] or previous['baseline_plan_hash']!=base['plan_hash']:raise ValueError('paired planning identity differs')
    n.checked_checkout(cemetery,d['cemetery']['commit'])
    if n.sha(archive)!=base['definition']['bank_artifact']['sha256']:raise ValueError('prepared archive differs')
    sys.path.insert(0,str(cemetery/'scripts'))
    from encounter_bank import prepare_bank
    prepare_bank(cemetery/base['definition']['bank_manifest'],cemetery)
    for case in base['cases']:n.local(cemetery,case['scenario_path'],case['scenario_sha256'])
    arms=[]
    for arm in previous['arms']:
        arm=dict(arm);source=sources/arm['id'];n.checked_checkout(source,arm['source']['commit'])
        arm['native_tools']=d['native_tools'].get(arm['id'],d['native_tools'])
        if (source/'death-tools-pin.txt').read_text().strip()!=arm['native_tools']['commit']:raise ValueError('source requires a different death-export tools pin')
        upstream=dict(line.split('=',1) for line in (source/'engine/UPSTREAM').read_text().splitlines() if '=' in line)
        if upstream['commit']!=base['manifest']['engine_commit']:raise ValueError('save engine is incompatible')
        arm['source_sha256']=subprocess.check_output(['bash',str(source/'harness/identity.sh'),'source-hash','rust'],text=True).strip()
        arm['build']=n.read(builds/('build-'+arm['id']+'.json'))
        if arm['build']['git_rev']!=arm['source']['commit'] or arm['build']['source_sha256']!=arm['source_sha256'] or arm['build']['inputs_dirty']!='no':raise ValueError('build inputs differ')
        arms.append(arm)
    reference=previous['definition']['reference'];provenance=previous['definition']['reference_provenance']
    for name,digest in provenance['files_sha256'].items():n.local(ROOT/reference['inputs'],name,digest)
    plan=dict(schema=SCHEMA,definition=d,definition_sha256=n.sha(definition),runner_sha256=n.sha(Path(__file__)),zoo_commit=n.git(ROOT,'rev-parse','HEAD'),
              comparison_plan_hash=previous['plan_hash'],cases=base['cases'],batches=base['batches'],manifest=base['manifest'],arms=arms,
              reference=previous['definition'],expected_cells=1998,exact_turns=True,bank_artifact=base['definition']['bank_artifact'])
    plan['plan_hash']=n.digest(plan);n.write(out,plan);return plan


def load(path):
    p=n.read(path)
    if p.get('schema')!=SCHEMA or n.digest({k:v for k,v in p.items() if k!='plan_hash'})!=p['plan_hash']:raise ValueError('execution plan changed')
    if len(p['cases'])!=999 or Counter(c['scenario']['class_idx'] for c in p['cases'])!=Counter({i:111 for i in range(9)}):raise ValueError('class quotas differ')
    expected=[(name,[c['id'] for c in group]) for name,group in bank.execution_groups(p['cases'])]
    if [(b['id'],b['cases']) for b in p['batches']]!=expected:raise ValueError('nested stage partition differs')
    if {a['id'] for a in p['arms']}!={'baseline','speed30'} or p['manifest']['horizon_engine_turns']!=2000 or p['manifest']['wall_seconds']!=5 or p['expected_cells']!=1998:raise ValueError('execution budget/arms differ')
    return p


def candidate_text(plan,case):
    directory=ROOT/plan['reference']['reference']['inputs']
    return config_text(directory,plan['reference']['reference_profile'],case['scenario']['race_idx'],case['scenario']['class_idx'])


def gear_state(line):
    import re
    match=re.search(r' p([0-9a-f]{16}) e([0-9a-f]{16}) r([0-9a-f]{16})(?:\s|$)',line)
    if not match:raise ValueError('missing native pack/equipment/rune hashes')
    return match.groups()


def validate(plan,case,arm,receipts,streams):
    t=json.loads(receipts['trial.json']);s=case['scenario'];summary=json.loads(receipts['run/summary.json']);process=json.loads(receipts['run/process.json'])
    expected=dict(source_commit=arm['source']['commit'],scenario_sha256=case['scenario_sha256'],save_sha256=s['save_sha256'],
                  start_turn=s['start_turn'],cap_turn=s['start_turn']+2000,horizon_engine_turns=2000,startup_contract='fresh_borg_saved_engine_rng',borg_memory_restored=False,exit_code=0)
    if any(t.get(k)!=v for k,v in expected.items()):raise ValueError('native trial identity differs')
    if t['build']!=arm['build'] or t['summary']!=summary or t['process']!=process:raise ValueError('native trial/process/build differs')
    if process.get('status')!='success' or process.get('exit_code')!=0 or any(process.get(k)!=arm['build']['binary_sha256'] for k in ('executable_sha256_before','executable_sha256_after')):raise ValueError('executed binary differs')
    identity=dict(loaded=True,loaded_turn=s['start_turn'],seed=s['birth_seed'],race_idx=s['race_idx'],class_idx=s['class_idx'],calendar='fixed')
    if any(summary.get(k)!=v for k,v in identity.items()):raise ValueError('loaded state identity differs')
    if any(v for k,v in summary.get('game_options',{}).items() if k.startswith('cheat_')):raise ValueError('cheat option enabled')
    state=n.STATE.match(receipts['initial-state']);expected_state=[s['start_turn'],s['checkpoint']['depth'],s['checkpoint']['max_depth']]+[s['initial_observed'][k] for k in ('hp','max_hp','sp','max_sp')]
    if not state or list(map(int,state.groups()))!=expected_state:raise ValueError('initial resources/depth differ')
    if set(streams)!={'keys.log','state.log','messages.log'} or any(not n.HEX.fullmatch(v) for v in streams.values()):raise ValueError('missing native streams')
    gear_state(receipts['initial-state'])
    if arm['id']=='baseline':
        coverage=json.loads(receipts['initial-coverage'])
        for key in ('level','depth','equipment_kind_signature','inventory'):
            if coverage[key]!=s['coverage'][key]:raise ValueError('initial equipment/inventory differs')
    cfg=n.kv(receipts['run/config.txt'])
    if cfg.get('borg_core')!=arm['core'] or cfg.get('save_sha256')!=s['save_sha256'] or 'keep-load-rng' not in cfg.get('flags','').split(','):raise ValueError('core/save/RNG differs')
    if arm['id']=='baseline':
        if cfg.get('profile_sha256')!=s['baseline_profile_sha256'] or t.get('profile_sha256')!=s['baseline_profile_sha256']:raise ValueError('baseline profile differs')
        actual={r['name']:r['value'] for r in json.loads(receipts['run/params.json'])['parameters']}
        for line in case['profile_text'].splitlines():
            line=line.split('#',1)[0].strip()
            if line:
                name,value=(x.strip() for x in line.split('=',1))
                if actual.get(name)!=int(value):raise ValueError('baseline parameter differs')
    else:
        text=receipts['run/user/borg.txt'];proof=json.loads(receipts['run/configuration.json'])
        if proof!=t.get('configuration') or proof.get('core')!='borg-rs' or cfg.get('borg_core_overrides')!='on':raise ValueError('candidate configuration proof differs')
        digest=lambda x:hashlib.sha256(x.encode()).hexdigest()
        if proof.get('template_sha256')!=digest(candidate_text(plan,case)) or proof.get('applied_borg_txt_sha256')!=digest(text) or cfg.get('borg_txt_sha256')!=digest(text):raise ValueError('candidate borg.txt differs')
        from .catalogue import setting_value
        def settings(text):
            import re
            return dict(re.findall(r'^\s*(borg_[a-z0-9_]+)\s*=\s*([^\n#]*?)\s*$',text,flags=re.MULTILINE))
        actual_settings=settings(text)
        fixed={'borg_reborn_core':'FALSE','borg_plan':'selected-plan.txt','borg_respawn_race':str(s['race_idx']),'borg_respawn_class':str(s['class_idx']),'borg_cheat_death':'FALSE','borg_respawn_winners':'FALSE'}
        expected_settings={k:setting_value(v) for k,v in arm['settings'].items()};expected_settings.update(fixed)
        if any(actual_settings.get(k)!=v for k,v in expected_settings.items()):raise ValueError('candidate classic input setting differs')
        actual={r['name']:r for r in json.loads(receipts['run/params-core.json'])}
        if cfg.get('params_core_sha256')!=digest(receipts['run/params-core.json']):raise ValueError('parameter receipt changed')
        for name,value in arm['settings'].items():
            if name.startswith('borg_param_'):
                row=actual.get(name.removeprefix('borg_param_'),{})
                if row.get('value')!=value or row.get('origin')!='borg.txt' or proof['named_parameters'].get(name)!=value:raise ValueError('candidate parameter not effective: '+name)
        plan_hash=arm['errands_plan_sha256']
        if proof.get('plan_sha256')!=plan_hash or proof.get('loaded_plan_sha256')!=plan_hash or digest(receipts['run/errands_plan.txt'])!=plan_hash or cfg.get('borg_errands_plan_sha256')!=plan_hash:raise ValueError('errands file not loaded')
    status=t['status']
    if status=='death':
        if summary.get('dead') is not True or summary.get('stop_reason')!='death':raise ValueError('death endpoint differs')
    elif status=='survived_horizon':
        if summary.get('dead') is not False or summary.get('stop_reason')!='turns' or summary.get('game_turns')!=expected['cap_turn']:raise ValueError('exact horizon differs')
    elif status!='stopped':raise ValueError('invalid native outcome: '+str(status))
    return status


def make_cell(plan,case,arm,directory):
    receipts={name:(directory/name).read_text() for name in FILES if (directory/name).is_file()}
    with (directory/'run/state.log').open() as f:receipts['initial-state']=next(f,'')
    if arm['id']=='baseline':
        with (directory/'run/observations.jsonl').open() as f:initial=json.loads(next(f))
        from curate_encounters import coverage
        receipts['initial-coverage']=json.dumps(coverage(initial),sort_keys=True)
    streams={name:n.sha(directory/'run'/name) for name in ('keys.log','state.log','messages.log')}
    cell=dict(schema='borg-zoo/paired-incident-cell@1',id=case['id'],arm=arm['id'],plan_hash=plan['plan_hash'],receipts=receipts,
              receipts_sha256={k:hashlib.sha256(v.encode()).hexdigest() for k,v in receipts.items()},streams=streams,independent_life=False)
    try:cell['status']=validate(plan,case,arm,receipts,streams)
    except (ValueError,KeyError,TypeError,IndexError,AttributeError) as e:cell.update(status='invalid_receipt',reason=str(e))
    cell['execution_hash']=n.digest({k:v for k,v in cell.items() if k!='execution_hash'});return cell


def run(plan_path,cemetery,source,tools,arm_id,batch_id,out):
    p=load(plan_path);arm=next(a for a in p['arms'] if a['id']==arm_id);batch=next(b for b in p['batches'] if b['id']==batch_id)
    if n.sha(Path(__file__))!=p['runner_sha256']:raise ValueError('runner changed')
    for directory,pin in [(cemetery,p['definition']['cemetery']['commit']),(tools,arm['native_tools']['commit']),(source,arm['source']['commit'])]:n.checked_checkout(directory,pin)
    if out.exists():raise ValueError('fresh attempt directory required')
    out.mkdir(parents=True)
    sys.path.insert(0,str(cemetery/'scripts'))
    from run_scenario import run_scenario
    from scenario_config import run_configured
    from run_batch import command
    # Both arms use the same exact engine-turn budget. Native tools own game execution.
    def exact_baseline(src,binary,raw,save,scenario,cap,env,wall):
        return command(['bash','harness/run.sh',str(raw),str(scenario['birth_seed']),str(scenario['race_idx']),str(scenario['class_idx']),str(cap),
                        'menu,exact,keep-load-rng,save=input.save'],cwd=src,env=env,log=raw.parent/'launcher.log',timeout=wall+30)
    old=dict(os.environ)
    try:
        for key in list(os.environ):
            if key.startswith(('BORG_','ANGBAND_','BORGH_')) or key in ('SAVE_ROOT','STALL_TIMEOUT_SECONDS'):os.environ.pop(key)
        os.environ.update(BORG_CEMETERY_DIR=str(tools),BORG_CORE=arm['core'])
        with open('/tmp/angband-validation.lock','a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            for case in p['cases']:
                if case['id'] not in batch['cases']:continue
                dest=out/'native'/case['id'];tick=time.monotonic()
                try:
                    scenario=n.local(cemetery,case['scenario_path'],case['scenario_sha256']).parent
                    if arm_id=='baseline':run_scenario(source,scenario,dest,2000,5,profile=scenario/'profile.txt',execution_adapter=exact_baseline)
                    else:
                        template=out/'templates'/(case['id']+'.txt');template.parent.mkdir(exist_ok=True);template.write_text(candidate_text(p,case))
                        run_configured(source,scenario,dest,template,ROOT/p['reference']['reference']['inputs']/'errands_plan.txt',2000,5,exact_turns=True)
                    cell=make_cell(p,case,arm,dest)
                except Exception as e:
                    cell=dict(schema='borg-zoo/paired-incident-cell@1',id=case['id'],arm=arm_id,plan_hash=p['plan_hash'],status='harness_failure',reason=str(e))
                    cell['execution_hash']=n.digest(cell)
                cell['elapsed_seconds']=time.monotonic()-tick
                # Timing is descriptive and excluded from execution identity.
                n.write(out/'cells'/(arm_id+'--'+case['id']+'.json'),cell)
    finally:
        os.environ.clear();os.environ.update(old)
    return 0


def collect(plan_path,inputs,out,tier='smoke',run_url=''):
    p=load(plan_path)
    if out.exists():raise ValueError('fresh report directory required')
    selected=p['cases'][:bank.TIERS[tier]];expected={(a['id'],c['id']) for a in p['arms'] for c in selected};found={}
    for path in inputs.rglob('*.json'):
        try:cell=n.read(path)
        except (ValueError,OSError) as error:
            parts=path.stem.split('--',1)
            if len(parts)!=2 or tuple(parts) not in expected:raise ValueError('unidentified malformed cell') from error
            cell=dict(schema='borg-zoo/paired-incident-cell@1',arm=parts[0],id=parts[1],status='malformed',reason=str(error))
        if cell.get('schema')!='borg-zoo/paired-incident-cell@1':continue
        key=(cell.get('arm'),cell.get('id'))
        if key not in expected or key in found:raise ValueError('unknown or repeated cell')
        found[key]=cell
    rows=[];by_class={name:Counter() for name in bank.CLASSES.values()};pairs=Counter()
    for case in selected:
        statuses=[]
        for arm in p['arms']:
            key=(arm['id'],case['id']);cell=found.get(key);status='missing'
            if cell:
                try:
                    body={k:v for k,v in cell.items() if k not in ('execution_hash','elapsed_seconds')}
                    if cell['plan_hash']!=p['plan_hash'] or n.digest(body)!=cell['execution_hash']:raise ValueError('cell execution identity changed')
                    for name,text in cell.get('receipts',{}).items():
                        if hashlib.sha256(text.encode()).hexdigest()!=cell['receipts_sha256'][name]:raise ValueError('receipt changed')
                    status=validate(p,case,arm,cell['receipts'],cell['streams'])
                    if status!=cell['status']:raise ValueError('reported outcome differs')
                except (ValueError,KeyError,TypeError,IndexError,AttributeError) as e:status='invalid_receipt';cell=dict(cell,validation_error=str(e))
            statuses.append(status)
            rows.append(dict(id=case['id'],arm=arm['id'],class_name=bank.CLASSES[case['scenario']['class_idx']],status=status,cell=cell))
        if all(s in n.VALID for s in statuses):
            a,b=(r['cell']['receipts']['initial-state'] for r in rows[-2:])
            if gear_state(a)!=gear_state(b):
                for r in rows[-2:]:r['status']='invalid_pairing'
                statuses=['invalid_pairing']*2
        elif statuses[1] in n.VALID:
            rows[-1]['status']='unverified_pairing';statuses[1]='unverified_pairing'
        for row in rows[-2:]:by_class[row['class_name']][row['arm']+':'+row['status']]+=1
        pair='invalid' if any(s not in n.VALID for s in statuses) else 'inconclusive' if 'stopped' in statuses else {('death','death'):'both_died',('death','survived_horizon'):'rescued',('survived_horizon','death'):'newly_killed',('survived_horizon','survived_horizon'):'both_survived'}[tuple(statuses)]
        pairs[pair]+=1
    invalid=sum(r['status'] not in n.VALID for r in rows);stopped=sum(r['status']=='stopped' for r in rows)
    n.write(out/'comparison.json',dict(schema='borg-zoo/paired-incident-results@1',plan=p,expected_cells=len(rows),cells=rows,pairs=dict(pairs),per_class=by_class,invalid_count=invalid,stopped_count=stopped,run_url=run_url))
    lines=['# Paired saved incidents','',f'{len(rows)} expected cells; invalid/missing {invalid}; stopped {stopped}.',f'[Zoo run]({run_url})','',
           '| Arm | Deaths | Horizon survival | Stopped | Invalid/missing |','|---|---:|---:|---:|---:|']
    for arm in p['arms']:
        c=Counter(r['status'] for r in rows if r['arm']==arm['id']);lines.append(f"| {arm['id']} | {c['death']} | {c['survived_horizon']} | {c['stopped']} | {sum(v for k,v in c.items() if k not in n.VALID)} |")
    lines+=['',json.dumps(dict(pairs),sort_keys=True),'','Both setups share saved states, exact2000 engine-turn and5-second wall bounds, fresh Borg memory and saved RNG. Sources/cores/configuration differ; results do not isolate speed30. Shared-life cases are correlated. Baseline observations validate loaded gear; candidate native pack/equipment/rune hashes must match the baseline. Classic settings are input-file verified; named parameters and loaded plan have native readbacks.']
    (out/'comparison.md').write_text('\n'.join(lines)+'\n');return int(bool(invalid or stopped))


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
    q=sub.add_parser('prepare')
    for key in ('definition','cemetery','sources','builds','archive','out'):q.add_argument('--'+key,type=Path,required=True)
    q=sub.add_parser('run')
    for key in ('plan','cemetery','source','tools','out'):q.add_argument('--'+key,type=Path,required=True)
    q.add_argument('--arm',choices=['baseline','speed30'],required=True);q.add_argument('--batch',required=True)
    q=sub.add_parser('collect')
    for key in ('plan','inputs','out'):q.add_argument('--'+key,type=Path,required=True)
    q.add_argument('--tier',choices=list(bank.TIERS),default='smoke');q.add_argument('--run-url',default='')
    a=parser.parse_args()
    if a.action=='prepare':prepare(a.definition.resolve(),a.cemetery.resolve(),a.sources.resolve(),a.builds.resolve(),a.archive.resolve(),a.out.resolve());return 0
    if a.action=='run':return run(a.plan.resolve(),a.cemetery.resolve(),a.source.resolve(),a.tools.resolve(),a.arm,a.batch,a.out.resolve())
    return collect(a.plan.resolve(),a.inputs.resolve(),a.out.resolve(),a.tier,a.run_url)


if __name__=='__main__':raise SystemExit(main())
