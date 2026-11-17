"""Freeze the requested two-setup saved-incident study, without running games."""
import argparse
import hashlib
from pathlib import Path
from . import encounters as native
from . import incident_bank
from .borgrs import config_text,check_config

ROOT=Path(__file__).resolve().parents[1]


def definition_plan(d,path,root):
    required={'kind','name','folder','issue','question','baseline_definition','reference','expected_cells','owner_authorization','prespecified'}
    if set(d)!=required or d['kind']!='balanced-incident-comparison-plan' or d['expected_cells']!=1998 or d['folder']!='scenario-experiments':
        raise ValueError('two-setup balanced999 comparison required')
    reference=d['reference'];directory=root/reference['inputs']
    provenance=native.read(directory/'provenance.json')
    if provenance['commit']!=reference['zoo_commit'] or provenance['run_id']!=reference['run_id']:
        raise ValueError('reference Zoo execution identity differs')
    for name,digest in provenance['files_sha256'].items():native.local(directory,name,digest)
    specimen=native.read(directory/'specimen.json');profile=native.read(directory/'profile.json')
    if specimen['ref']!=provenance['source_commit'] or profile['settings'].get('borg_param_attack_speed_fight_danger_tenths')!=30:
        raise ValueError('reference source/profile differs')
    if profile['settings'].get('borg_reborn_core')!='borg-rs' or profile['settings'].get('borg_plan')!='errands_plan.txt':
        raise ValueError('reference core/plan differs')
    if native.sha(directory/'errands_plan.txt')!=specimen['plans']['errands_plan.txt']:
        raise ValueError('pinned errands file differs')
    body=dict(d,schema='borg-zoo/balanced-incident-comparison-definition@1',definition=Path(path).resolve().relative_to(root.resolve()).as_posix(),
              reference_specimen=specimen,reference_profile=profile,reference_provenance=provenance)
    target=root/d['folder']/(d['name']+'.json');changes=[]
    if not target.exists() or native.read(target)!=body:changes.append(('experiment-update' if target.exists() else 'experiment',target.relative_to(root).as_posix(),body))
    return d,[],changes


def freeze(definition,baseline,out,root=ROOT):
    d=native.read(definition);plan=incident_bank.read_execution_plan(baseline)
    if d['schema']!='borg-zoo/balanced-incident-comparison-definition@1':raise ValueError('unsupported comparison definition')
    baseline_definition=root/d['baseline_definition']
    if native.sha(baseline_definition)!=plan['definition_sha256']:raise ValueError('baseline plan differs from requested definition')
    directory=root/d['reference']['inputs'];provenance=d['reference_provenance']
    for name,digest in provenance['files_sha256'].items():native.local(directory,name,digest)
    if native.read(directory/'profile.json')!=d['reference_profile'] or native.read(directory/'specimen.json')!=d['reference_specimen']:
        raise ValueError('reference snapshot differs')
    cases=[]
    for case in plan['cases']:
        scenario=case['scenario'];text=config_text(directory,d['reference_profile'],scenario['race_idx'],scenario['class_idx'])
        if check_config(text,d['reference_profile']):raise ValueError('reference settings not written')
        cases.append(dict(id=case['id'],class_idx=scenario['class_idx'],scenario_sha256=case['scenario_sha256'],save_sha256=scenario['save_sha256'],
            start_turn=scenario['start_turn'],historical_type=scenario['event_kind'],origin=scenario['origin'],
            candidate_borg_txt_sha256=hashlib.sha256(text.encode()).hexdigest()))
    result=dict(schema='borg-zoo/balanced-incident-comparison-plan@1',status='planned_not_executed',dispatchable=False,definition=d,
        zoo_commit=native.git(root,'rev-parse','HEAD'),definition_sha256=native.sha(definition),baseline_plan_hash=plan['plan_hash'],
        bank_artifact=plan['definition']['bank_artifact'],expected_scenarios=999,expected_cells=1998,per_class_per_arm=111,
        manifest=plan['manifest'],cases=cases,batches=plan['batches'],
        stages=[dict(id=t,cumulative_scenarios=n,cumulative_cells=2*n,cases_per_class=n//9) for t,n in incident_bank.TIERS.items()],
        arms=[dict(id='baseline',source=plan['definition']['source'],core='reborn',profile='saved default profile',execution_definition=d['baseline_definition']),
              dict(id='speed30',source=dict(repository=d['reference_specimen']['repository'],commit=d['reference_specimen']['ref']),
                   core='borg-rs',specimen=provenance['specimen'],profile=provenance['profile'],settings=d['reference_profile']['settings'],
                   errands_plan_sha256=d['reference_specimen']['plans']['errands_plan.txt'])],
        pairing='scenario/save/start/horizon/RNG match in both arms; fresh Borg memory',
        comparison_axes=['source_build','controller_core','configuration'],qualified_near_death={'coverage':'unavailable','count':None},
        gates=['two native loaded starts per class and arm before larger tiers','saved-state and game-data compatibility in both builds',
               'exact requested parameter readback, core identity and loaded errands-plan SHA',
               'no missing/invalid cells; stopped outcomes block intermediate expansion','bounded jobs at most40 cases and eight concurrent jobs'],
        execution_prerequisites=['baseline saved-state runner exists','candidate requires Zoo integration of Cemetery scenario_config.run_configured and configured receipt validation before dispatch'],
        inference='Descriptive comparison of two complete setups; cannot isolate speed30 or claim population improvement')
    result['plan_hash']=native.digest(result);native.write(out,result);return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('definition','baseline','out'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();plan=freeze(a.definition.resolve(),a.baseline.resolve(),a.out.resolve())
    print(plan['expected_cells'],'planned cells; no games executed')


if __name__=='__main__':main()
