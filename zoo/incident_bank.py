"""Balanced nine-class incident preparation and full saved-bank orchestration."""
import json
from pathlib import Path
import re


def definition_plan(d, path, root):
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
