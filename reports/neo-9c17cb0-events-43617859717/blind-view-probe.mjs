// Read-only Core reproducer: Node 26, built pinned engine, composed pack.
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
import { loadPack } from './pack.ts';
const [engine, pack] = process.argv.slice(2);
if (!engine || !pack) throw new Error('Usage: node blind-view-probe.mjs ENGINE_CHECKOUT PACK_DIRECTORY');
const core = await import(pathToFileURL(resolve(engine, 'packages/core/dist/index.js')));
const game = core.startGame(loadPack(pack), {seed:303, depth:0, raceName:'High-Elf', className:'Blackguard'});
const s=game.state,p=s.actor.player,eff=s.world.timedTable[core.TMD.BLIND],hooks=s.world.timedHooks;
const sample=()=>({blind:p.timed[core.TMD.BLIND],seen:s.chunk.sqinfoHas(s.actor.grid,core.SQUARE.SEEN),light:s.actor.light});
s.updateFov(s);const before=sample();
core.playerIncTimed(p,eff,10,true,true,false,hooks);const during=sample();
core.playerClearTimed(p,eff,true,true,hooks);const after=sample();
s.updateFov(s);const refreshed=sample();
console.log(JSON.stringify({before,during,after,refreshed},null,2));
if (!(before.seen && during.blind>0 && during.seen && after.blind===0 && !after.seen && refreshed.seen)) throw new Error('Pinned failure signature changed');
