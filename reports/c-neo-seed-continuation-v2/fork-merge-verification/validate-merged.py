import os,subprocess,pathlib,json
root=pathlib.Path('/workspace/work/seed-alignment');engine=root/'merged-engine';toolkit=root/'merged-toolkit';out=root/'merge-receipts';node='/workspace/work/runtime/node_modules/.bin/node'
steps=[('install',['pnpm','install','--frozen-lockfile'],engine),('build',['pnpm','exec','tsc','-b','packages/core','packages/mod-sdk','packages/content'],engine),('tests',['pnpm','exec','vitest','run','packages/core/src/store','packages/core/src/agent/loadout.test.ts','packages/core/src/player/bind.test.ts','packages/core/src/game/gear.test.ts','packages/core/src/agent/known-world.test.ts','packages/core/src/monclass.upstream.test.ts'],engine)]
for name,cmd,cwd in steps:
 with (out/f'merged-{name}.log').open('w') as f:r=subprocess.run(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT)
 print(name,r.returncode,flush=True)
 if r.returncode:raise SystemExit(r.returncode)
epin=subprocess.check_output(['git','rev-parse','HEAD'],cwd=engine,text=True).strip();bpin=subprocess.check_output(['git','rev-parse','HEAD'],cwd=toolkit,text=True).strip()
commands=[('bundle',[node,str(toolkit/'tools/zoo/build.mjs'),'--engine-dir',str(engine),'--borg-dir',str(toolkit),'--engine-pin',epin,'--borg-pin',bpin,'--alignment-probes','true','--exact-tick-cap','true','--c-seed-startup','true','--c-gcc-coordinate-order','true','--out',str(root/'merged-build')]),('game',[node,str(toolkit/'tools/zoo/run.mjs'),'--bundle',str(root/'merged-build/bundle.mjs'),'--seed','303','--race','Human','--class','Warrior','--birth-profile','c-seeded-point-buy-v2','--turns','2000','--out',str(root/'merged-neo-303')])]
for name,cmd in commands:
 with (out/f'merged-{name}.log').open('w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 print(name,r.returncode,flush=True)
 if r.returncode:raise SystemExit(r.returncode)
pairs=out/'merged-pairs.json';pairs.write_text(json.dumps({'cases':[{'seed':303,'native':'../verified-c-303','neo':'../merged-neo-303','bodySlots':12}]}))
with (out/'merged-startup-comparison.json').open('w') as f:subprocess.run([node,str(toolkit/'tools/zoo/alignment/compare-startup.mjs'),str(pairs)],stdout=f,check=True)
print('initial-state-comparison pass',flush=True)
