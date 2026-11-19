"""Run one Borg build and configuration on a frozen saved-encounter suite.

A suite (scenario-suites/ID/suite.json) is a frozen bank of saved starts with its
execution protocol. A run is one build (an exact borg-reborn-rs commit, by default
main's HEAD) with its own harness/borg.txt, unchanged unless the owner asks for a
profile on top. It is a sanity check of that build: the run is reported alone, with
no other arm. Runs grow in the suite's nested stages without replaying earlier cells.

    python3 -m zoo.suite_runs snapshot --source CHECKOUT --name NAME [--profile P]
    python3 -m zoo.suite_runs prepare|stage|run|collect ...   (the suite-run workflow)
"""
import argparse
from collections import Counter
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from . import encounters as n, incident_bank as bank, saved_incidents as saved
from .borgrs import config_text

ROOT=Path(__file__).resolve().parents[1]
SCHEMA='borg-zoo/suite-run-plan@1'
CELL='borg-zoo/suite-run-cell@1'
KEYS={'kind','name','folder','issue','question','suite','source','settings','inputs','native_tools','owner_authorization','prespecified'}
PREVIOUS={'small':'smoke','medium':'small','big':'medium','full':'big'}
FILES=['trial.json','run/summary.json','run/process.json','run/config.txt','run/params-core.json','run/configuration.json','run/user/borg.txt','run/errands_plan.txt']
SETTING=re.compile(r'^[ \t]*(borg_[a-z0-9_]+)[ \t]*=[ \t]*([^\n#]*?)[ \t]*(?:#[^\n]*)?$',re.MULTILINE)


def digest_text(text):return hashlib.sha256(text.encode()).hexdigest()


def settings_of(text):return dict(SETTING.findall(text))


def suite(root,suite_id):
    m=n.read(root/'scenario-suites'/suite_id/'suite.json')
    if m.get('schema')!='borg-zoo/saved-suite@1' or m['id']!=suite_id:raise ValueError('unknown saved suite: '+suite_id)
    n.local(root,m['cases_plan']['path'],m['cases_plan']['sha256']);n.local(root,m['gear']['path'],m['gear']['sha256'])
    return m


def snapshot(source,name,profile=None,root=ROOT):
    """Freeze a checkout's harness/borg.txt (and its plan, if it names one) as the run's inputs."""
    commit=n.git(source,'rev-parse','HEAD');n.checked_checkout(source,commit)
    out=root/'scenario-inputs'/name
    if out.exists():raise ValueError('inputs already exist: '+str(out.relative_to(root)))
    text=(source/'harness/borg.txt').read_text();chosen={}
    if profile:chosen=json.loads((root/'catalogue/profiles.json').read_text())['profiles'][profile]['settings']
    merged=dict(settings_of(text));merged.update({k:str(v) for k,v in chosen.items()})
    if merged.get('borg_reborn_core') not in ('borg-rs','1'):raise ValueError('the saved-state runner drives the borg-rs core only')
    if merged.get('borg_reborn_errand','none')!='none':raise ValueError('errands are not supported by the saved-state runner')
    out.mkdir(parents=True);(out/'borg.txt').write_text(text);files={'borg.txt':n.sha(out/'borg.txt')}
    plan=merged.get('borg_plan')
    if plan:
        (out/'errands_plan.txt').write_bytes((source/'harness/plans'/plan).read_bytes());files['errands_plan.txt']=n.sha(out/'errands_plan.txt')
    scary=merged.get('borg_scary_list')
    if scary:
        # The saved-state runner stages only borg.txt and the plan in user/; the frozen
        # scary list is read by absolute path instead (see template).
        if '/' in scary:raise ValueError('borg_scary_list must name a file in harness/')
        (out/scary).write_bytes((source/'harness'/scary).read_bytes());files[scary]=n.sha(out/scary)
    tools=(source/'death-tools-pin.txt').read_text().strip()
    settings=dict(stock=True) if not profile else dict(profile=profile,values=chosen)
    n.write(out/'provenance.json',dict(source=dict(repository='diegoami/borg-reborn-rs',commit=commit),settings=settings,native_tools=tools,files_sha256=files,
                                       source_sha256=subprocess.check_output(['bash',str(source/'harness/identity.sh'),'source-hash','rust'],text=True).strip()))
    files['provenance.json']=n.sha(out/'provenance.json')
    return dict(name=name,source=commit,native_tools=tools,settings=settings,inputs=dict(path=str(out.relative_to(root)),files=files))


def definition_plan(d,path,root):
    if set(d)!=KEYS or d['kind']!='suite-run' or d['folder']!='scenario-experiments' or not saved.NAME.fullmatch(d['name']):raise ValueError('unsupported suite run definition')
    for key in ('question','prespecified','owner_authorization'):
        if not isinstance(d[key],str) or not d[key].strip():raise ValueError('suite run needs '+key)
    suite(root,d['suite'])
    for pin,repo in ((d['source'],'diegoami/borg-reborn-rs'),(d['native_tools'],'diegoami/borg-cemetery')):
        if pin['repository']!=repo or not n.SHA.fullmatch(pin['commit']):raise ValueError('exact pin required: '+repo)
    s=d['settings']
    if s!='stock' and (not isinstance(s,dict) or set(s)!={'profile'}):raise ValueError("settings is 'stock' or {profile: NAME}")
    inputs=root/d['inputs']['path']
    for name,value in d['inputs']['files'].items():n.local(inputs,name,value)
    prov=n.read(inputs/'provenance.json')
    if prov['source']['commit']!=d['source']['commit'] or prov['native_tools']!=d['native_tools']['commit']:raise ValueError('inputs were frozen from another source')
    if (s=='stock')!=bool(prov['settings'].get('stock')) or (s!='stock' and prov['settings'].get('profile')!=s['profile']):raise ValueError('inputs were frozen with other settings')
    body=dict(d,schema='borg-zoo/suite-run-definition@1',definition=Path(path).resolve().relative_to(root.resolve()).as_posix())
    target=root/d['folder']/(d['name']+'.json');changes=[]
    if not target.exists() or n.read(target)!=body:changes.append(('experiment-update' if target.exists() else 'experiment',target.relative_to(root).as_posix(),body))
    return d,[],changes


def prepare(definition,cemetery,source,build,archive,out):
    d=n.read(definition)
    if d.get('schema')!='borg-zoo/suite-run-definition@1':raise ValueError('not a suite run definition')
    m=suite(ROOT,d['suite']);base=bank.read_execution_plan(ROOT/m['cases_plan']['path']);gear=n.read(ROOT/m['gear']['path'])['cases']
    if [c['id'] for c in base['cases']]!=list(gear):raise ValueError('gear reference does not cover the suite')
    n.checked_checkout(cemetery,m['cemetery']['commit']);n.checked_checkout(source,d['source']['commit'])
    if n.sha(archive)!=m['bank']['sha256']:raise ValueError('prepared archive differs')
    sys.path.insert(0,str(cemetery/'scripts'))
    from encounter_bank import prepare_bank
    prepare_bank(cemetery/m['bank']['manifest'],cemetery)
    for case in base['cases']:n.local(cemetery,case['scenario_path'],case['scenario_sha256'])
    if (source/'death-tools-pin.txt').read_text().strip()!=d['native_tools']['commit']:raise ValueError('source requires a different death-export tools pin')
    upstream=dict(line.split('=',1) for line in (source/'engine/UPSTREAM').read_text().splitlines() if '=' in line)
    if upstream['commit']!=m['protocol']['engine_commit']:raise ValueError('the suite was saved by another engine')
    source_sha=subprocess.check_output(['bash',str(source/'harness/identity.sh'),'source-hash','rust'],text=True).strip()
    built=n.read(build)
    if built['git_rev']!=d['source']['commit'] or built['source_sha256']!=source_sha or built['inputs_dirty']!='no':raise ValueError('build inputs differ')
    inputs=ROOT/d['inputs']['path']
    for name,value in d['inputs']['files'].items():n.local(inputs,name,value)
    profile={} if d['settings']=='stock' else json.loads((ROOT/'catalogue/profiles.json').read_text())['profiles'][d['settings']['profile']]['settings']
    plan_file=inputs/'errands_plan.txt'
    arm=dict(id=d['name'],source=d['source'],source_sha256=source_sha,core='borg-rs',native_tools=d['native_tools'],build=built,settings=profile,
             settings_label='stock' if d['settings']=='stock' else d['settings']['profile'],inputs=d['inputs'],errands_plan_sha256=n.sha(plan_file) if plan_file.exists() else None,
             scary_list=scary_list_of(inputs,d['inputs']['files']))
    plan=dict(schema=SCHEMA,definition=d,definition_sha256=n.sha(definition),runner_sha256=n.sha(Path(__file__)),zoo_commit=n.git(ROOT,'rev-parse','HEAD'),
              suite=m,cases=base['cases'],batches=base['batches'],manifest=dict(base['manifest'],wall_seconds=m['protocol']['wall_seconds']),gear=gear,arm=arm,expected_cells=len(base['cases']),exact_turns=True)
    plan['plan_hash']=n.digest(plan);n.write(out,plan);return plan


def load(path):
    p=n.read(path)
    if p.get('schema')!=SCHEMA or n.digest({k:v for k,v in p.items() if k!='plan_hash'})!=p['plan_hash']:raise ValueError('execution plan changed')
    expected=[(name,[c['id'] for c in group]) for name,group in bank.execution_groups(p['cases'])]
    if [(b['id'],b['cases']) for b in p['batches']]!=expected:raise ValueError('nested stage partition differs')
    if p['manifest']['horizon_engine_turns']!=p['suite']['protocol']['horizon_engine_turns'] or p['manifest']['wall_seconds']!=p['suite']['protocol']['wall_seconds']:raise ValueError('execution budget differs')
    return p


SCARY_SETTING=re.compile(r'^[ \t]*borg_scary_list[ \t]*=.*$',re.M)


def scary_list_of(inputs,files):
    """{name, sha256} of the frozen scary list the inputs' borg.txt names, or None."""
    name=settings_of((inputs/'borg.txt').read_text()).get('borg_scary_list')
    if not name:return None
    if name not in files:raise ValueError('borg.txt names a scary list the inputs did not freeze: '+name)
    return dict(name=name,sha256=files[name])


def template(plan,case):
    text=config_text(ROOT/plan['arm']['inputs']['path'],dict(settings=plan['arm']['settings']),case['scenario']['race_idx'],case['scenario']['class_idx'])
    scary=plan['arm'].get('scary_list')
    if scary:
        # borg-reborn-rs resolves an absolute borg_scary_list as it is (scary_list.rs).
        path=n.local(ROOT/plan['arm']['inputs']['path'],scary['name'],scary['sha256'])
        text=SCARY_SETTING.sub('borg_scary_list = '+str(path.resolve()),text)
    return text


CLASSES=('warrior','mage','druid','priest','necromancer','paladin','rogue','ranger','blackguard')


def effective_row(params,name):
    """The receipt row for a borg.txt parameter name. borg-reborn-rs #520 keeps per-class values
    (`<name>@<class>`, the legacy `<name>_<class>` and `attack_preference_<class>_<family>_permille`)
    as class_values of the general parameter; those come back as {value, origin, class}."""
    if name in params:return params[name]
    base=cls=None
    if '@' in name:base,cls=name.split('@',1)
    else:
        m=re.fullmatch(r'attack_preference_([a-z]+)_([a-z]+)_permille',name)
        if m and m.group(1) in CLASSES:base,cls='attack_preference_'+m.group(2)+'_permille',m.group(1)
        else:
            cls=next((c for c in CLASSES if name.endswith('_'+c)),None)
            base=name[:-len(cls)-1] if cls else None
    entry=(params.get(base) or {}).get('class_values',{}).get(cls) if base else None
    return dict(entry,**{'class':cls}) if entry else {}


def validate(plan,case,receipts,streams):
    arm=plan['arm'];t=json.loads(receipts['trial.json']);s=case['scenario'];summary=json.loads(receipts['run/summary.json']);process=json.loads(receipts['run/process.json'])
    horizon=plan['manifest']['horizon_engine_turns']
    expected=dict(source_commit=arm['source']['commit'],scenario_sha256=case['scenario_sha256'],save_sha256=s['save_sha256'],start_turn=s['start_turn'],
                  cap_turn=s['start_turn']+horizon,horizon_engine_turns=horizon,startup_contract='fresh_borg_saved_engine_rng',borg_memory_restored=False,exit_code=0)
    if any(t.get(k)!=v for k,v in expected.items()):raise ValueError('native trial identity differs')
    if t['build']!=arm['build'] or t['summary']!=summary or t['process']!=process:raise ValueError('native trial/process/build differs')
    if process.get('status')!='success' or process.get('exit_code')!=0 or any(process.get(k)!=arm['build']['binary_sha256'] for k in ('executable_sha256_before','executable_sha256_after')):raise ValueError('executed binary differs')
    identity=dict(loaded=True,loaded_turn=s['start_turn'],seed=s['birth_seed'],race_idx=s['race_idx'],class_idx=s['class_idx'],calendar='fixed')
    if any(summary.get(k)!=v for k,v in identity.items()):raise ValueError('loaded state identity differs')
    if any(v for k,v in summary.get('game_options',{}).items() if k.startswith('cheat_')):raise ValueError('cheat option enabled')
    state=n.STATE.match(receipts['initial-state']);expected_state=[s['start_turn'],s['checkpoint']['depth'],s['checkpoint']['max_depth']]+[s['initial_observed'][k] for k in ('hp','max_hp','sp','max_sp')]
    if not state or list(map(int,state.groups()))!=expected_state:raise ValueError('initial resources/depth differ')
    gear=re.search(r' p([0-9a-f]{16}) e([0-9a-f]{16}) r([0-9a-f]{16})(?:\s|$)',receipts['initial-state'])
    if not gear or list(gear.groups())!=plan['gear'][case['id']]:raise ValueError('initial pack/equipment/runes differ from the suite')
    if set(streams)!={'keys.log','state.log','messages.log'} or any(not n.HEX.fullmatch(v) for v in streams.values()):raise ValueError('missing native streams')
    cfg=n.kv(receipts['run/config.txt'])
    if cfg.get('borg_core')!='borg-rs' or cfg.get('save_sha256')!=s['save_sha256'] or 'keep-load-rng' not in cfg.get('flags','').split(','):raise ValueError('core/save/RNG differs')
    text=receipts['run/user/borg.txt'];proof=json.loads(receipts['run/configuration.json']);requested=template(plan,case)
    if proof!=t.get('configuration') or proof.get('core')!='borg-rs' or cfg.get('borg_core_overrides')!='on':raise ValueError('configuration proof differs')
    if proof.get('template_sha256')!=digest_text(requested) or proof.get('applied_borg_txt_sha256')!=digest_text(text) or cfg.get('borg_txt_sha256')!=digest_text(text):raise ValueError('borg.txt differs')
    plan_sha=arm['errands_plan_sha256'];wanted=settings_of(requested)
    wanted.update(borg_reborn_core='FALSE',borg_respawn_race=str(s['race_idx']),borg_respawn_class=str(s['class_idx']),borg_cheat_death='FALSE',borg_respawn_winners='FALSE')
    if plan_sha:wanted['borg_plan']='selected-plan.txt'
    elif 'borg_plan' in wanted:raise ValueError('borg.txt names a plan the run did not freeze')
    actual=settings_of(text)
    if any(actual.get(k)!=v for k,v in wanted.items()):raise ValueError('classic input setting differs')
    params={r['name']:r for r in json.loads(receipts['run/params-core.json'])}
    if cfg.get('params_core_sha256')!=digest_text(receipts['run/params-core.json']):raise ValueError('parameter receipt changed')
    for name,value in wanted.items():
        if name.startswith('borg_param_'):
            row=effective_row(params,name.removeprefix('borg_param_'))
            named=proof['named_parameters'].get(name)
            # A class line (#520) is effective as a class value; a runner that predates
            # class values does not list it among the named parameters.
            if str(row.get('value'))!=value or row.get('origin')!='borg.txt' or (named is None and not row.get('class')) or (named is not None and str(named)!=value):raise ValueError('parameter not effective: '+name)
    if plan_sha:
        if proof.get('plan_sha256')!=plan_sha or proof.get('loaded_plan_sha256')!=plan_sha or digest_text(receipts['run/errands_plan.txt'])!=plan_sha or cfg.get('borg_errands_plan_sha256')!=plan_sha:raise ValueError('errands file not loaded')
    elif proof.get('plan_sha256') is not None or 'run/errands_plan.txt' in receipts:raise ValueError('a plan was loaded though none was frozen')
    status=t['status']
    if status=='death':
        if summary.get('dead') is not True or summary.get('stop_reason')!='death':raise ValueError('death endpoint differs')
    elif status=='survived_horizon':
        if summary.get('dead') is not False or summary.get('stop_reason')!='turns' or summary.get('game_turns')!=expected['cap_turn']:raise ValueError('exact horizon differs')
    elif status!='stopped':raise ValueError('invalid native outcome: '+str(status))
    return status


def make_cell(plan,case,directory):
    receipts={name:(directory/name).read_text() for name in FILES if (directory/name).is_file()}
    with (directory/'run/state.log').open() as f:receipts['initial-state']=next(f,'')
    streams={name:n.sha(directory/'run'/name) for name in ('keys.log','state.log','messages.log')}
    cell=dict(schema=CELL,id=case['id'],arm=plan['arm']['id'],plan_hash=plan['plan_hash'],receipts=receipts,
              receipts_sha256={k:digest_text(v) for k,v in receipts.items()},streams=streams,independent_life=False)
    trial=json.loads(receipts.get('trial.json','{}'))
    if trial.get('status')=='timeout':  # the native wall limit cut the game short: no outcome, and the gate fails
        cell.update(status='wall_timeout',reason=f"stopped by the {plan['manifest']['wall_seconds']} s wall limit before the horizon")
    else:
        try:cell['status']=validate(plan,case,receipts,streams)
        except (ValueError,KeyError,TypeError,IndexError,AttributeError) as e:cell.update(status='invalid_receipt',reason=str(e))
    cell['execution_hash']=n.digest({k:v for k,v in cell.items() if k!='execution_hash'});return cell


def run(plan_path,cemetery,source,tools,batch_id,out):
    p=load(plan_path);arm=p['arm'];batch=next(b for b in p['batches'] if b['id']==batch_id)
    if n.sha(Path(__file__))!=p['runner_sha256']:raise ValueError('runner changed')
    for directory,pin in [(cemetery,p['suite']['cemetery']['commit']),(tools,arm['native_tools']['commit']),(source,arm['source']['commit'])]:n.checked_checkout(directory,pin)
    if out.exists():raise ValueError('fresh attempt directory required')
    out.mkdir(parents=True)
    sys.path.insert(0,str(cemetery/'scripts'))
    from scenario_config import run_configured
    plan_file=ROOT/arm['inputs']['path']/'errands_plan.txt' if arm['errands_plan_sha256'] else None
    old=dict(os.environ)
    try:
        for key in list(os.environ):
            if key.startswith(('BORG_','ANGBAND_','BORGH_')) or key in ('SAVE_ROOT','STALL_TIMEOUT_SECONDS'):os.environ.pop(key)
        os.environ.update(BORG_CEMETERY_DIR=str(tools),BORG_CORE='borg-rs')
        with open('/tmp/angband-validation.lock','a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            for case in p['cases']:
                if case['id'] not in batch['cases']:continue
                dest=out/'native'/case['id'];tick=time.monotonic()
                try:
                    scenario=n.local(cemetery,case['scenario_path'],case['scenario_sha256']).parent
                    text=out/'templates'/(case['id']+'.txt');text.parent.mkdir(exist_ok=True);text.write_text(template(p,case))
                    run_configured(source,scenario,dest,text,plan_file,p['manifest']['horizon_engine_turns'],p['manifest']['wall_seconds'],exact_turns=True)
                    cell=make_cell(p,case,dest)
                except Exception as e:
                    cell=dict(schema=CELL,id=case['id'],arm=arm['id'],plan_hash=p['plan_hash'],status='harness_failure',reason=str(e))
                    cell['execution_hash']=n.digest(cell)
                cell['elapsed_seconds']=time.monotonic()-tick  # descriptive, outside the execution identity
                n.write(out/'cells'/(case['id']+'.json'),cell)
    finally:
        os.environ.clear();os.environ.update(old)
    return 0


def cells_of(plan,inputs,selected):
    expected={c['id'] for c in selected};found={}
    for path in inputs.rglob('*.json'):
        try:cell=n.read(path)
        except (ValueError,OSError) as error:
            if path.stem not in expected:raise ValueError('unidentified malformed cell') from error
            cell=dict(schema=CELL,id=path.stem,status='malformed',reason=str(error))
        if cell.get('schema')!=CELL:continue
        if cell.get('id') not in expected or cell['id'] in found:raise ValueError('unknown or repeated cell: '+str(cell.get('id')))
        found[cell['id']]=cell
    return found


def checked(plan,case,cell):
    if not cell:return 'missing',cell
    try:
        body={k:v for k,v in cell.items() if k not in ('execution_hash','elapsed_seconds')}
        if cell['plan_hash']!=plan['plan_hash'] or n.digest(body)!=cell['execution_hash']:raise ValueError('cell execution identity changed')
        for name,text in cell.get('receipts',{}).items():
            if digest_text(text)!=cell['receipts_sha256'][name]:raise ValueError('receipt changed')
        trial=json.loads(cell['receipts'].get('trial.json','{}'))
        status='wall_timeout' if trial.get('status')=='timeout' else validate(plan,case,cell['receipts'],cell['streams'])
        if status!=cell['status'] and not (status=='wall_timeout' and cell['status']=='invalid_receipt'):raise ValueError('reported outcome differs')
        return status,cell
    except (ValueError,KeyError,TypeError,IndexError,AttributeError) as e:return 'invalid_receipt',dict(cell,validation_error=str(e))


def collect(plan_path,inputs,out,tier='smoke',run_url=''):
    p=load(plan_path)
    if out.exists():raise ValueError('fresh report directory required')
    selected=p['cases'][:bank.TIERS[tier]];found=cells_of(p,inputs,selected);rows=[]
    for case in selected:
        status,cell=checked(p,case,found.get(case['id']))
        rows.append(dict(id=case['id'],arm=p['arm']['id'],class_name=bank.CLASSES[case['scenario']['class_idx']],status=status,cell=cell))
    c=Counter(r['status'] for r in rows);invalid=sum(v for k,v in c.items() if k not in n.VALID)
    report=dict(schema='borg-zoo/suite-run-results@1',plan=p,tier=tier,expected_cells=len(rows),cells=rows,outcomes=dict(c),
                per_class={name:dict(Counter(r['status'] for r in rows if r['class_name']==name)) for name in bank.CLASSES.values()},
                invalid_count=invalid,stopped_count=c['stopped'],run_url=run_url)
    n.write(out/'comparison.json',report)
    lines=['# '+p['arm']['id']+' on '+p['suite']['name'],'',f"{tier}: {len(rows)} scenarios; deaths {c['death']}, survived the horizon {c['survived_horizon']}, stopped {c['stopped']}, cut off by the wall limit {c['wall_timeout']}, invalid or missing {invalid-c['wall_timeout']}.",'',f'[Zoo run]({run_url})']
    (out/'comparison.md').write_text('\n'.join(lines)+'\n');return int(bool(invalid or c['stopped']))


def stage(plan_path,parent_report,cells,stage_name,out):
    """Gate the parent stage and list the batches the next stage adds."""
    p=load(plan_path)
    if stage_name=='smoke':previous=None
    elif stage_name in PREVIOUS:previous=PREVIOUS[stage_name]
    else:raise ValueError('unknown stage')
    if previous:
        report=n.read(parent_report)
        if report.get('plan',{}).get('plan_hash')!=p['plan_hash'] or report.get('tier')!=previous or report.get('expected_cells')!=bank.TIERS[previous]:raise ValueError('parent is not the preceding stage of this run')
        if report.get('invalid_count') or report.get('stopped_count'):raise ValueError('parent stage did not pass its gate')
        if collect(plan_path,cells,out/'parent-validated',tier=previous):raise ValueError('parent receipts failed independent revalidation')
    prefix='smoke' if stage_name=='smoke' else stage_name+'-'
    batches=[b['id'] for b in p['batches'] if b['id']==prefix or b['id'].startswith(prefix)]
    added=sum(len(b['cases']) for b in p['batches'] if b['id'] in batches)
    if added!=bank.TIERS[stage_name]-(bank.TIERS[previous] if previous else 0):raise ValueError('stage partition differs')
    n.write(out/'matrix.json',[dict(batch=b) for b in batches]);return batches


def compact(report,evidence_url,howto_url,parent_run=None):
    """The dashboard record of the run alone: its build, its configuration and every scenario's outcome."""
    p=report['plan'];arm=p['arm'];rows={r['id']:r for r in report['cells']};cases=[]
    for index,case in enumerate(p['cases'][:report['expected_cells']]):
        s=case['scenario'];row=rows[case['id']];cell=row.get('cell') or {};raw=cell.get('receipts',{})
        summary=json.loads(raw['run/summary.json']) if 'run/summary.json' in raw else {}
        details={arm['id']:dict(status=row['status'],summary=summary,streams=cell.get('streams',{}),cell_execution_hash=cell.get('execution_hash'),elapsed_seconds=cell.get('elapsed_seconds'),reason=cell.get('validation_error',cell.get('reason')))}
        cases.append(dict(id=case['id'],class_idx=s['class_idx'],race_idx=s['race_idx'],birth_seed=s['birth_seed'],start_turn=s['start_turn'],
            historical_type=s['event_kind'],selection=s['selection'],coverage=s['coverage'],origin=s['origin'],scenario_sha256=case['scenario_sha256'],save_sha256=s['save_sha256'],
            suite=f'synthetic/balanced-999-incidents/generated/shards/{index//8:03d}.json',outcomes={arm['id']:row['status']},details=details,pair=None))
    run_arm=dict(id=arm['id'],core=arm['core'],source=arm['source'],build=arm['build'],native_tools=arm['native_tools'],profile=arm['settings_label'],
                 settings=arm['settings'],errands_plan_sha256=arm['errands_plan_sha256'],inputs=arm['inputs'])
    result=dict(schema=saved.SCHEMA,name=p['definition']['name'],title=arm['id']+' on '+p['suite']['name'],suite=dict(id=p['suite']['id'],name=p['suite']['name']),
        tier=report['tier'],run_url=report['run_url'],parent_run=parent_run,plan_hash=p['plan_hash'],definition=p['definition'],arms=[run_arm],
        comparison=dict(reference=None,candidate=arm['id']),counted_arms=[arm['id']],manifest=p['manifest'],expected_cells=report['expected_cells'],
        collected_cells=sum(r.get('cell') is not None for r in report['cells']),invalid_count=report['invalid_count'],stopped_count=report['stopped_count'],
        pairs={},per_class=report['per_class'],cases=cases,bank_artifact=p['suite']['bank'],evidence_url=evidence_url,howto_url=howto_url,
        independent_life=False,qualified_near_death={'coverage':'unavailable','count':None})
    saved.validate(result);return result


def main():
    q=argparse.ArgumentParser(description=__doc__.splitlines()[0]);sub=q.add_subparsers(dest='action',required=True)
    a=sub.add_parser('snapshot');a.add_argument('--source',type=Path,required=True);a.add_argument('--name',required=True);a.add_argument('--profile')
    a=sub.add_parser('prepare')
    for key in ('definition','cemetery','source','build','archive','out'):a.add_argument('--'+key,type=Path,required=True)
    a=sub.add_parser('stage')
    for key in ('plan','out'):a.add_argument('--'+key,type=Path,required=True)
    a.add_argument('--parent-report',type=Path);a.add_argument('--cells',type=Path)
    a.add_argument('--stage',choices=list(bank.TIERS),required=True)
    a=sub.add_parser('run')
    for key in ('plan','cemetery','source','tools','out'):a.add_argument('--'+key,type=Path,required=True)
    a.add_argument('--batch',required=True)
    a=sub.add_parser('collect')
    for key in ('plan','inputs','out'):a.add_argument('--'+key,type=Path,required=True)
    a.add_argument('--tier',choices=list(bank.TIERS),default='smoke');a.add_argument('--run-url',default='')
    a=sub.add_parser('compact')
    for key in ('input','out'):a.add_argument('--'+key,type=Path,required=True)
    a.add_argument('--evidence-url',required=True);a.add_argument('--howto-url',required=True);a.add_argument('--parent-run',type=int)
    a=q.parse_args()
    if a.action=='snapshot':print(json.dumps(snapshot(a.source.resolve(),a.name,a.profile),indent=2));return 0
    if a.action=='prepare':prepare(a.definition.resolve(),a.cemetery.resolve(),a.source.resolve(),a.build.resolve(),a.archive.resolve(),a.out.resolve());return 0
    if a.action=='stage':
        if a.stage!='smoke' and not (a.parent_report and a.cells):raise ValueError('a later stage needs the parent report and cells')
        stage(a.plan.resolve(),a.parent_report and a.parent_report.resolve(),a.cells and a.cells.resolve(),a.stage,a.out.resolve());return 0
    if a.action=='run':return run(a.plan.resolve(),a.cemetery.resolve(),a.source.resolve(),a.tools.resolve(),a.batch,a.out.resolve())
    if a.action=='collect':return collect(a.plan.resolve(),a.inputs.resolve(),a.out.resolve(),a.tier,a.run_url)
    if a.out.exists():raise ValueError('fresh compact output directory required')
    raw=a.input.resolve();r=compact(n.read(raw),a.evidence_url,a.howto_url,a.parent_run)
    r['raw_report_sha256']=n.sha(raw);a.out.mkdir(parents=True);(a.out/'comparison.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    (a.out/'index.html').write_text(saved.render(r));return 0


if __name__=='__main__':raise SystemExit(main())
