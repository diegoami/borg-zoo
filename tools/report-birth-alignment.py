#!/usr/bin/env python3
"""Validate a bounded C/Neo birth pilot; never label shared integers paired worlds."""

import argparse, json, pathlib, hashlib, collections


def read_native(directory):
    lines = (directory / "trace.txt").read_text().splitlines()
    tagged = lambda key: [
        json.loads(l[len(key) + 1 :]) for l in lines if l.startswith(key + " ")
    ]
    opts = lambda key: {
        k: bool(int(v))
        for k, v in (
            s.split("=")
            for s in next(l for l in lines if l.startswith(key + " ")).split()[1:]
        )
    }
    return {
        "birth": tagged("ALIGN_BIRTH")[0],
        "options": opts("OPTIONS"),
        "activeOptions": opts("ACTIVE_OPTIONS"),
        "rng": tagged("ALIGN_RNG"),
        "terrain": tagged("ALIGN_TERRAIN")[0],
        "result": json.load(open(directory / "result.json")),
        "trace_sha256": hashlib.sha256(
            (directory / "trace.txt").read_bytes()
        ).hexdigest(),
    }


def read_neo(directory):
    states = [json.loads(l) for l in open(directory / "states.jsonl")]
    a = next(s for s in states if s["kind"] == "alignment")
    active = next(s for s in states if s["kind"] == "alignment-active")
    return {
        "birth": a["birth"],
        "options": a["options"]["values"],
        "activeOptions": active["options"]["values"],
        "rng": a["rngObservations"],
        "worldRng": a["worldRng"],
        "terrain": a["terrain"],
        "result": json.load(open(directory / "run.json")),
        "commands_sha256": hashlib.sha256(
            (directory / "commands.jsonl").read_bytes()
        ).hexdigest(),
    }


def active_rng(s):
    return (s["quick"], s["stateI"], s["state"], s["value"] if s["quick"] else None)


def gear(items):
    # This pilot is Human only: the pinned humanoid body has 12 equipment slots.
    # C object_slot returns body.count for a pack item; Neo returns -1.
    assert all(x.get("slot", -1) <= 12 for x in items)
    keys = [
        "tval",
        "sval",
        "number",
        "weight",
        "slot",
        "timeout",
        "dd",
        "ds",
        "toH",
        "toD",
        "toA",
    ]
    return sorted(
        tuple(
            (-1 if x.get(k, 0) == 12 else x.get(k, 0)) if k == "slot" else x.get(k, 0)
            for k in keys
        )
        for x in items
    )


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--work", type=pathlib.Path, required=True)
    p.add_argument("--plan", type=pathlib.Path, required=True)
    p.add_argument("--out", type=pathlib.Path, required=True)
    a = p.parse_args()
    plan = json.load(open(a.plan))
    out = {"schema": "borg-zoo/birth-alignment-review@1", "plan": plan, "pairs": []}
    for cell in plan["cells"]:
        assert cell["race"] == "Human"
        tail = f"Human-{cell['class']}-{cell['seed']}"
        c = read_native(a.work / ("c-" + tail))
        n = read_neo(a.work / (plan.get("neo_directory_prefix", "neo-") + tail))
        cb, nb = c["birth"], n["birth"]
        pair = {
            "cell": cell,
            "native": c,
            "neo": n,
            "checks": {
                "requested_identity": (cb["race"], cb["class"])
                == (cell["race"], cell["class"])
                == (nb["race"], nb["class"]),
                "natural_stats_equal": cb["stats"] == nb["stats"],
                "initial_hp_equal": (cb["hp"], cb["maxHp"]) == (nb["hp"], nb["maxHp"]),
                "initial_sp_equal": (cb["sp"], cb["maxSp"]) == (nb["sp"], nb["maxSp"]),
                "initial_options_equal": c["options"] == n["options"],
                "active_options_equal": c["activeOptions"] == n["activeOptions"],
                "seeded_rng_equal": active_rng(c["rng"][0]) == active_rng(n["rng"][0]),
                "gear_equal": gear(cb["inventory"]) == gear(nb["inventory"]),
                "gold_equal": cb["gold"] == nb["gold"],
                "town_equal": c["terrain"] == n["terrain"],
                "placement_equal": cb["grid"] == [nb["grid"]["x"], nb["grid"]["y"]],
            },
        }
        for k in [
            "requested_identity",
            "natural_stats_equal",
            "initial_hp_equal",
            "initial_sp_equal",
            "initial_options_equal",
            "active_options_equal",
            "seeded_rng_equal",
        ]:
            assert pair["checks"][k], (cell, k)
        if plan.get("require_exact_ticks"):
            exact = n["result"]["turnCap"]
            assert n["result"]["turn"] == plan["cap_ticks"]
            assert exact["guaranteedExact"] and exact["boundary"] == "exact-tick"
            assert c["result"]["states"][-1]["turn"] == plan["cap_ticks"]
        out["pairs"].append(pair)
    r = plan["repeat_control"]
    tail = f"{r['race']}-{r['class']}-{r['seed']}"
    c1, c2 = read_native(a.work / ("c-" + tail)), read_native(
        a.work / ("c-" + tail + "-repeat")
    )
    n1, n2 = read_neo(
        a.work / (plan.get("neo_directory_prefix", "neo-") + tail)
    ), read_neo(a.work / (plan.get("neo_directory_prefix", "neo-") + tail + "-repeat"))
    out["repeat_controls"] = {
        "C_birth_equal": c1["birth"] == c2["birth"],
        "C_rng_checkpoints_equal": c1["rng"] == c2["rng"],
        "C_terminal_states_equal": c1["result"]["states"] == c2["result"]["states"],
        "Neo_command_hash_equal": n1["commands_sha256"] == n2["commands_sha256"],
        "Neo_birth_equal": n1["birth"] == n2["birth"],
    }
    assert all(out["repeat_controls"].values())
    out["check_counts"] = {
        k: sum(x["checks"][k] for x in out["pairs"]) for k in out["pairs"][0]["checks"]
    }
    out["outcomes"] = {
        e: dict(
            collections.Counter(
                [x[e]["result"]["outcome"] for x in out["pairs"]]
                + [(c2 if e == "native" else n2)["result"]["outcome"]]
            )
        )
        for e in ["native", "neo"]
    }
    out["comparison"] = (
        "Birth policy/options aligned; shared-seed worlds not aligned. No mortality effect estimate."
    )
    # Full states/maps/provenance stay in the sealed raw archive. Keep this
    # review compact instead of repeating each finalKnownWorld grid twice.
    result_keys = {
        "outcome",
        "turn",
        "depth",
        "maxDepth",
        "level",
        "maxLevel",
        "hp",
        "maxHp",
        "turnCap",
        "playSha256",
        "settings",
        "cfg",
        "crossModFlags",
    }
    for pair in out["pairs"]:
        pair["neo"]["result"] = {
            k: v for k, v in pair["neo"]["result"].items() if k in result_keys
        }
        for engine in ["native", "neo"]:
            terrain = pair[engine]["terrain"]
            pair[engine]["terrain"] = {
                "height": terrain["height"],
                "width": terrain["width"],
                "sha256": hashlib.sha256(
                    json.dumps(terrain["terrain"], separators=(",", ":")).encode()
                ).hexdigest(),
            }
    a.out.write_text(json.dumps(out, indent=2) + "\n")
    print(
        json.dumps(
            {
                "checks": out["check_counts"],
                "repeats": out["repeat_controls"],
                "outcomes": out["outcomes"],
            }
        )
    )


if __name__ == "__main__":
    main()
