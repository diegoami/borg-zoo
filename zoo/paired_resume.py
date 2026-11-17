"""Resume a balanced paired study using the original compiled builds and cells."""
import argparse
import json
from pathlib import Path
from . import paired_incidents as paired,incident_bank as bank,encounters as n

PREVIOUS={'small':'smoke','medium':'small','big':'medium','full':'big'}


def prepare(plan_path,parent_report,cells,stage,out):
    p=paired.load(plan_path);report=n.read(parent_report)
    if stage not in PREVIOUS:raise ValueError('resume stage must follow an earlier tier')
    previous=PREVIOUS[stage]
    if report.get('plan',{}).get('plan_hash')!=p['plan_hash'] or report.get('expected_cells')!=2*bank.TIERS[previous]:raise ValueError('parent is not the immediately preceding stage of this exact study')
    if report.get('invalid_count') or report.get('stopped_count'):raise ValueError('parent stage did not pass its gate')
    if paired.collect(plan_path,cells,out/'parent-validated',tier=previous):raise ValueError('parent receipts failed independent revalidation')
    matrix=[]
    for batch in p['batches']:
        if not batch['id'].startswith(stage+'-'):continue
        for arm in p['arms']:
            matrix.append(dict(arm=arm['id'],batch=batch['id'],source=arm['source']['commit'],tools=arm['native_tools']['commit'],cemetery=p['definition']['cemetery']['commit']))
    scheduled={c for b in p['batches'] if b['id'].startswith(stage+'-') for c in b['cases']}
    if len(scheduled)!=bank.TIERS[stage]-bank.TIERS[previous]:raise ValueError('resume partition differs')
    n.write(out/'matrix.json',matrix)
    n.write(out/'resume.json',dict(parent_stage=previous,stage=stage,plan_hash=p['plan_hash'],new_scenarios=len(scheduled),new_cells=2*len(scheduled),expected_cumulative_cells=2*bank.TIERS[stage],builds_reused=True))
    return matrix


def main():
    q=argparse.ArgumentParser(description=__doc__)
    for key in ('plan','parent-report','cells','out'):q.add_argument('--'+key,type=Path,required=True)
    q.add_argument('--stage',choices=list(PREVIOUS),required=True)
    a=q.parse_args();prepare(a.plan.resolve(),a.parent_report.resolve(),a.cells.resolve(),a.stage,a.out.resolve())


if __name__=='__main__':main()
