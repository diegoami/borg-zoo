/** Assemble the ordinary published GamePack; no Borg policy or replay path. */
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import type { GamePack } from "@rpgm-tools/neo-angband-core";
export function loadPack(dir: string): GamePack {
	const json = <T>(name: string): T =>
		JSON.parse(readFileSync(join(dir, `${name}.json`), "utf8")) as T;
	const records = <T>(name: string): T[] =>
		json<{ records: T[] }>(name).records;
	const optionalRecords = <T>(name: string): T[] =>
		existsSync(join(dir, `${name}.json`)) ? records<T>(name) : [];
	return {
		constants: json("constants"),
		terrain: records("terrain"),
		roomTemplates: records("room_template"),
		vaults: records("vault"),
		dungeonProfiles: records("dungeon_profile"),
		// Complete ordinary Core input, including store/world/quest records.
		chestTraps: records("chest_trap"),
		world: records("world"),
		projection: records("projection"),
		trap: records("trap"),
		messageTypes: optionalRecords("message_type"),
		tvals: optionalRecords("tval"),
		monsterSpells: records<{ type?: unknown }>("monster_spell").filter(
			(record) => typeof record.type === "string",
		),
		names: records("names"),
		store: records("store"),
		quest: records("quest"),
		uiKnowledge: records("ui_knowledge"),
		hints: records("hints"),
		obj: {
			objectBase: json("object_base"),
			object: json("object"),
			egoItem: json("ego_item"),
			artifact: json("artifact"),
			curse: json("curse"),
			brand: json("brand"),
			slay: json("slay"),
			activation: json("activation"),
			objectProperty: json("object_property"),
			flavor: json("flavor"),
		} as GamePack["obj"],
		mon: {
			pain: records("pain"),
			blowMethods: records("blow_methods"),
			blowEffects: records("blow_effects"),
			monsterSpells: records("monster_spell"),
			monsterBases: records("monster_base"),
			monsters: records("monster"),
			summons: records("summon"),
			pits: records("pit"),
		},
		player: {
			races: records("p_race"),
			classes: records("class"),
			properties: records("player_property"),
			timed: records("player_timed"),
			shapes: records("shape"),
			bodies: records("body"),
			history: records("history"),
			realms: records("realm"),
		},
	} as unknown as GamePack;
}
