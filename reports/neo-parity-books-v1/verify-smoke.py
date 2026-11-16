import argparse,collections,hashlib,json,pathlib,sys,tarfile
p=argparse.ArgumentParser();p.add_argument('--artifacts',type=pathlib.Path,required=True);p.add_argument('--catalogue',type=pathlib.Path,required=True);p.add_argument('--out',type=pathlib.Path,required=True);args=p.parse_args()
sys.path.insert(0,str(args.catalogue.resolve()))
from zoo import catalogue
cat=catalogue.catalogue(args.catalogue);exp=catalogue.load_experiment(str(args.catalogue/'smoke/neo-b4-parity-books-smoke-18-v1.json'),cat=cat)
planned={str(c['seed']):c for c in catalogue.cells(exp,cat)}
cells=[json.loads(line) for f in args.artifacts.glob('cells-*/*.jsonl') for line in f.read_text().splitlines()]
assert len(cells)==18 and len({c['seed'] for c in cells})==18
assert set(map(str,(c['seed'] for c in cells)))==set(planned)
byseed={str(c['seed']):c for c in cells};facts={};verified=0;archives={}
source='464a1555ca73cf662b522f020152faa9d1a2d465';engine='d27ed50f9e3b650a43cceda5a0c007d03cc321df';toolkit='638979da690891c11da1c1e780631828953b03d7'
build_archive=next(args.artifacts.glob('build-*/*.tgz'))
with tarfile.open(build_archive) as tf:
 build=json.load(tf.extractfile(next(m for m in tf.getmembers() if m.name.endswith('/zoo-build.json'))))
 bundle=tf.extractfile(next(m for m in tf.getmembers() if m.name.endswith('/bundle.mjs'))).read()
assert (build['source_commit'],build['engine_commit'],build['toolkit_commit'])==(source,engine,toolkit)
digest=hashlib.sha256(bundle).hexdigest();assert digest==build['binary_sha256']==build['bundleSha256']
assert build['borg']['manifest']['data']['version']=='1.4.0-beta.6.zoo.1'
for c in cells:
 expected=planned[str(c['seed'])]
 assert (c['race'],c['class'])==(expected['race'],expected['class'])
 assert (c['played_race'],c['played_class'])==(expected['race'],expected['class'])
 assert (c['specimen_ref'],c['engine_ref'],c['toolkit_ref'])==(source,engine,toolkit)
 assert c['binary_sha256']==digest and c['cap']==5000 and c['boundary']=='exact-tick'
 assert c['final']['turn']<=5000 and c['outcome'] in ['death','turn_cap','stalled','wall_timeout','borg_stopped','harness_failure','config_error','decision_cap']
 assert c['evidence']['complete'] and not c['evidence']['missing_required']
 assert c['birth_record']['options']['birth_no_selling'] is True
 assert c['birth_record']['options']['birth_connect_stairs'] is True
 assert c['birth_record']['options']['birth_force_descend'] is False
 settings=c['settings_effective'];assert settings['borg.selfScum'] is True
 assert all(v is False for k,v in settings.items() if k!='borg.selfScum')
for archive in sorted(args.artifacts.glob('raw-*/*.tgz')):
 sha=hashlib.sha256(archive.read_bytes()).hexdigest();assert sha==archive.with_suffix('.sha256').read_text().split()[0];archives[archive.name]=sha
 with tarfile.open(archive) as tf:
  for m in tf.getmembers():
   if not m.isfile():continue
   parts=pathlib.PurePosixPath(m.name).parts;si=parts.index('default')+1;seed=parts[si];relative='/'.join(parts[si+1:]);c=byseed[seed];data=tf.extractfile(m).read()
   f=facts.setdefault(seed,{'seed':int(seed),'class':c['class'],'race':c['race'],'outcome':c['outcome'],'cause':c.get('cause'),'files':[]})
   if relative in c['evidence']['files']:
    receipt=c['evidence']['files'][relative];assert len(data)==receipt['bytes'] and hashlib.sha256(data).hexdigest()==receipt['sha256'];f['files'].append(relative);verified+=1
   if relative=='run/run.json':
    run=json.loads(data);assert run['inputs']['birthProfile']=='c-seeded-point-buy-v2';assert run['playSha256']==c['play_sha256']
    book=next((i for i in run['birth']['inventory'] if 30<=i['tval']<=39),None)
    f.update(turn=run['turn'],cast_attempts=run['commands'].get('cast',0),retained_starting_book=None if book is None else any(i['tval']==book['tval'] and i['sval']==book['sval'] for i in run['finalInventory']),last_commands=run['lastCommands'][-12:],stall=run.get('stall'))
   if relative=='run/states.jsonl':
    rows=[json.loads(l) for l in data.splitlines()];receipts=[r for r in rows if r.get('kind')=='truth-use'];assert receipts
    entry=receipts[0]['manifest']['capabilityUse']['entries'][0];assert entry['digest']==digest and entry['version']=='1.4.0-beta.6.zoo.1' and entry['capability']=='state:monsters-actual.read'
    assert receipts[0]['manifest']['modNoscore'] is True;f['truth_receipt']=True
    align=next(r for r in rows if r.get('kind')=='alignment');assert align['profile']=='c-seeded-point-buy-v2'
   if relative=='run/messages.jsonl':
    rows=[json.loads(l) for l in data.splitlines()];f['last_messages']=rows[-20:];f['book_events']=[r for r in rows if any(s in r.get('text','') for s in ['First Spells','Novice','Into the Shadows','Lesser Charms'])]
for seed,c in byseed.items():assert set(c['evidence']['files'])==set(facts[seed]['files'])
result={'schema':'neo-parity-smoke-acceptance@1','source':source,'engine':engine,'toolkit':toolkit,'bundle_sha256':digest,'version':'1.4.0-beta.6.zoo.1','records':18,'outcomes':dict(collections.Counter(c['outcome'] for c in cells)),'inventoried_files_verified':verified,'raw_archives':archives,'all_pins_births_settings_receipts_verified':True,'cells':list(facts.values()),'acceptance':'requires explicit review of outcomes and abnormal endpoints','survival_claim':False}
args.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['cells','raw_archives']}))
