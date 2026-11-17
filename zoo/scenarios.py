"""Pinned Cemetery scenario dispatch and paired impact reports (never population cells).

Run as python -m zoo.scenarios {plan,run,collect}. Cemetery owns generation,
execution/classification and canonical per-target reports. This module freezes
pushid resolution, journals cells and compares outcomes without requiring parity.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import html
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import math

from . import catalogue

REPO = 'diegoami/borg-reborn-rs'
BANK_REPO = 'diegoami/borg-cemetery'
COMMIT = re.compile(r'[0-9a-f]{40}')
HEX = re.compile(r'[0-9a-f]{64}')
NAME = re.compile(r'[a-zA-Z0-9][a-zA-Z0-9_.-]{0,99}')
VALID = {'death', 'survived_to_cap'}
INVALID = {'harness_failure', 'identity_mismatch', 'timeout', 'unsupported'}
ENGINE_PATHS = ['engine/angband', 'engine/patches', 'engine/frontend', 'engine/UPSTREAM']


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f'duplicate JSON key: {key}')
            out[key] = value
        return out
    return json.loads(Path(path).read_text(), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Each completed cell is durable before the next game starts. No overwrites.
    with path.open('x') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def checked_checkout(root, commit):
    if not COMMIT.fullmatch(commit) or git(root, 'rev-parse', 'HEAD') != commit or git(root, 'status', '--porcelain'):
        raise ValueError('checkout must be clean at its exact pinned commit')


def engine_hash(source):
    raw = subprocess.check_output(['git', '-C', str(source), 'ls-tree', '-r', 'HEAD', '--', *ENGINE_PATHS])
    return hashlib.sha256(raw).hexdigest()


def bank_module(bank, pin):
    checked_checkout(bank, pin['commit'])
    path = Path(bank) / 'scripts/synthetic_suite.py'
    if file_hash(path) != pin['runner_sha256']:
        raise ValueError('Cemetery runner digest mismatch')
    spec = importlib.util.spec_from_file_location('pinned_cemetery_synthetic', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def safe_file(root, relative):
    path = Path(root) / relative
    if not isinstance(relative, str) or Path(relative).is_absolute() or '..' in Path(relative).parts or not path.resolve().is_relative_to(Path(root).resolve()) or path.is_symlink():
        raise ValueError('expected a contained relative bank path')
    return path


def prepare(definition, bank, cat=None):
    """Freeze a reviewed definition and the exact catalogue resolution before play."""
    d = read(definition)
    if set(d) != {'schema', 'name', 'bank', 'pushids', 'scenario_ids', 'comparison_axis', 'engine_sha256', 'budget'} or d['schema'] != 'borg-zoo/scenario-experiment@1':
        raise ValueError('unsupported scenario experiment fields/schema')
    if not NAME.fullmatch(d['name']) or d['comparison_axis'] != ['target_build']:
        raise ValueError('this adapter supports only an explicit target_build comparison axis')
    pin = d['bank']
    if set(pin) != {'repository', 'commit', 'manifest', 'manifest_sha256', 'suite_spec_sha256', 'runner_sha256'} or pin['repository'] != BANK_REPO:
        raise ValueError('unsupported bank dependency')
    if not COMMIT.fullmatch(pin['commit']) or any(not HEX.fullmatch(pin[k]) for k in ('manifest_sha256', 'suite_spec_sha256', 'runner_sha256')):
        raise ValueError('bank must name exact commit and digests')
    module = bank_module(bank, pin)
    manifest = safe_file(bank, pin['manifest'])
    generated = module.generate(manifest)
    if generated['manifest_sha256'] != pin['manifest_sha256'] or generated['suite_spec_sha256'] != pin['suite_spec_sha256']:
        raise ValueError('bank manifest/spec digest mismatch')
    ids = d['scenario_ids']
    if not isinstance(ids, list) or not ids or len(ids) != len(set(ids)):
        raise ValueError('explicit unique scenario selection required')
    cases = {case['id']: case for case in generated['cases']}
    if set(ids) - cases.keys():
        raise ValueError('unknown scenario ID (equipment indexes are not executable scenarios)')
    selected = [cases[key] for key in ids]
    if any(c['character_build']['core'] != 'reborn' for c in selected):
        raise ValueError('this comparison adapter requires reborn effective-parameter receipts')
    specs = (cat or catalogue.catalogue())['specimens']['specimens']
    targets, seen = [], set()
    if not isinstance(d['pushids'], list) or not 2 <= len(d['pushids']) <= 4:
        raise ValueError('select two to four pushids')
    for entry in d['pushids']:
        if set(entry) != {'pushid', 'specimen'} or not NAME.fullmatch(entry['pushid']) or entry['pushid'] in seen:
            raise ValueError('invalid/duplicate pushid resolution')
        seen.add(entry['pushid'])
        spec = specs[entry['specimen']]
        if spec.get('repository') != REPO or spec.get('kind') != 'borg-rs' or spec.get('impl') != 'rust' or not COMMIT.fullmatch(spec['ref']):
            raise ValueError('pushid requires an exact supported specimen, not a moving ref')
        targets.append(dict(entry, repository=REPO, commit=spec['ref'], specimen_snapshot=spec,
                            harness=dict(repository=REPO, commit=spec['ref'])))
    if len({t['commit'] for t in targets}) != len(targets) or not HEX.fullmatch(d['engine_sha256']):
        raise ValueError('every pushid must resolve to a distinct commit; exact engine semantics digest required')
    budget = d['budget']
    if set(budget) != {'max_cells', 'max_wall_seconds', 'max_parallel'} or any(type(v) is not int for v in budget.values()) or not 2 <= budget['max_cells'] <= 32 or budget['max_parallel'] != 1:
        raise ValueError('bounded sequential smoke budget required (2..32 cells)')
    if len(selected) * len(targets) > budget['max_cells'] or not 1 <= budget['max_wall_seconds'] <= 1800 or sum(c['wall_seconds'] + 15 for c in selected) * len(targets) > budget['max_wall_seconds']:
        raise ValueError('scenario dispatch exceeds reviewed budget')
    for target in targets:
        # Ten minutes for a source build and three for checkout/artifact setup,
        # plus every selected cell's declared wall/outer-cleanup allowance.
        target['timeout_minutes'] = 13 + math.ceil(sum(c['wall_seconds'] + 15 for c in selected) / 60)
    plan = dict(schema='borg-zoo/scenario-plan@1', name=d['name'], definition=d,
                definition_sha256=file_hash(definition), targets=targets, cases=selected,
                semantics=dict(engine_sha256=d['engine_sha256'], dungeon_mode='one_way',
                               boundary='after-key', calendar='UTC-real-clock-same-execution'),
                zoo_commit=git(catalogue.ROOT, 'rev-parse', 'HEAD'),
                zoo_runner_sha256=file_hash(__file__))
    plan['plan_sha256'] = digest(plan)
    validate_plan(plan)
    return plan


def validate_plan(plan):
    body = {k: v for k, v in plan.items() if k != 'plan_sha256'}
    if plan.get('schema') != 'borg-zoo/scenario-plan@1' or digest(body) != plan.get('plan_sha256'):
        raise ValueError('frozen plan hash mismatch')
    if len({t['commit'] for t in plan['targets']}) != len(plan['targets']):
        raise ValueError('duplicate target commits in frozen plan')
    for case in plan['cases']:
        payload = {k: v for k, v in case.items() if k not in ('id', 'spec_sha256')}
        if digest(payload) != case['spec_sha256']:
            raise ValueError('scenario input hash mismatch')
    return plan


def pairing_hash(plan, case):
    return digest(dict(contract='borg-zoo/scenario-pair@1', plan=plan['plan_sha256'],
                       scenario=case, semantics=plan['semantics']))


def execution_input(plan, case, target, identity, calendar):
    return dict(plan_sha256=plan['plan_sha256'], pairing_sha256=pairing_hash(plan, case),
                scenario=case, target=target, build_receipt=identity, calendar=calendar)


def effective_settings(case, text):
    """Normalize actual settings; names/default documentation are not policy."""
    params = json.loads(text)
    if params.get('profile_sha256') != case['character_build']['profile_sha256']:
        raise ValueError('effective parameter profile digest mismatch')
    values = {}
    for entry in params.get('parameters', []):
        name, value = entry['name'], entry['value']
        if name in values or not isinstance(name, str) or type(value) is not int:
            raise ValueError('ambiguous effective parameter receipt')
        values[name] = value
    if not values:
        raise ValueError('missing effective parameters')
    return dict(core=case['character_build']['core'], profile_sha256=params['profile_sha256'], parameters=values)


def run_target(plan, bank, source, pushid, out):
    """Execute one target through the pinned Cemetery adapter, flush every cell."""
    import datetime
    validate_plan(plan)
    target = next((t for t in plan['targets'] if t['pushid'] == pushid), None)
    if target is None:
        raise ValueError('pushid is not in the frozen dispatch')
    module = bank_module(bank, plan['definition']['bank'])
    generated = module.generate(safe_file(bank, plan['definition']['bank']['manifest']))
    actual = {c['id']: c for c in generated['cases']}
    if any(actual.get(c['id']) != c for c in plan['cases']):
        raise ValueError('bank changed since dispatch')
    # The Cemetery adapter launches the harness with cwd=source. Its profile,
    # exporter destination and output arguments must survive that cwd change.
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    write(out / 'requested.json', dict(plan_sha256=plan['plan_sha256'], target=target))
    adapter = module.RebornAdapter(source)
    identity, failure = None, None
    try:
        checked_checkout(source, target['commit'])
        identity = adapter.describe(target['commit'], {c['harness_contract'] for c in plan['cases']},
                                    {c['character_build']['core'] for c in plan['cases']})
        if engine_hash(source) != plan['semantics']['engine_sha256']:
            raise module.ExecutionError('identity_mismatch', 'engine/start semantics differ from prespecified contract')
        identity['engine_sha256'] = engine_hash(source)
    except (OSError, ValueError, subprocess.SubprocessError, module.ExecutionError) as error:
        failure = (getattr(error, 'status', 'harness_failure'), str(error))
    rows = []
    for case in plan['cases']:
        attempt = out / 'attempts' / case['id']
        attempt.mkdir(parents=True)
        calendar = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
        inputs = execution_input(plan, case, target, identity, calendar)
        row = dict(schema='borg-zoo/scenario-cell@1', pushid=pushid, scenario_id=case['id'],
                   plan_sha256=plan['plan_sha256'], pairing_sha256=pairing_hash(plan, case),
                   execution_input=inputs, execution_sha256=digest(inputs), attempted=False,
                   status='harness_failure', reason='', qualified_near_death=dict(coverage='unavailable', count=None))
        row.update(terminal=None, death_cause=None, evidence={}, minimum_observed_living_hp=None,
                   candidate_screen=dict(kind='low_hp_candidate', count=None),
                   refusal_messages=dict(coverage='unavailable', nothing_happens_dot=None, nothing_happens_bang=None))
        # Publish requested identity before handing control to the game.
        write(attempt / 'requested.json', inputs)
        if failure:
            row.update(status=failure[0], reason=failure[1])
        else:
            try:
                if case['character_build']['start'] == 'record':
                    support = module.read(Path(source) / 'harness/capabilities.json').get('character_build_support', {})
                    if (case['character_build']['race_idx'] != support.get('race_idx') or
                            case['character_build']['class_idx'] != support.get('class_idx') or
                            case['expected_start']['level'] > support.get('maximum_level', 0)):
                        raise module.ExecutionError('unsupported', 'pinned harness cannot apply this character kit')
                row['attempted'] = True
                rc = adapter.run(case, generated['root'], attempt / 'run')
                result = module.classify(case, attempt / 'run', rc, identity['build']['binary_sha256'])
                if file_hash(attempt / 'profile.txt') != case['character_build']['profile_sha256']:
                    result.update(status='identity_mismatch', terminal=None, reason='applied profile changed')
                if (attempt / 'natural-registry-guard').exists():
                    # Cemetery's adapter sets BORG_DEATH_RECORDS_DIR to this
                    # directory. A mistaken natural export creates it; it is
                    # not a sentinel file or the population-results separator.
                    result.update(status='harness_failure', terminal=None, reason='synthetic run wrote a natural registry')
                row.update(result)
            except (OSError, ValueError, subprocess.SubprocessError, module.ExecutionError) as error:
                row.update(status=getattr(error, 'status', 'harness_failure'), reason=str(error))
        # Preserve original compact receipt bytes, not only hashes that become
        # unverifiable after raw gameplay artifacts expire.
        row['receipts'] = {name: (attempt / 'run' / name).read_bytes().decode('utf-8', errors='replace')
                           for name in ('summary.json', 'process.json', 'config.txt', 'params.json')
                           if (attempt / 'run' / name).is_file()}
        if row['status'] in VALID | {'stopped'}:
            try:
                row['effective_settings'] = effective_settings(case, row['receipts']['params.json'])
                profile = (attempt / 'profile.txt').read_text()
                for line in profile.splitlines():
                    line = line.split('#', 1)[0].strip()
                    if not line:
                        continue
                    match = re.fullmatch(r'([a-zA-Z0-9_]+)\s*=\s*(-?\d+)', line)
                    if not match or row['effective_settings']['parameters'].get(match[1]) != int(match[2]):
                        raise ValueError('requested profile did not take effect')
                row['evidence']['params.json'] = dict(sha256=file_hash(attempt / 'run/params.json'))
            except (ValueError, KeyError, OSError, TypeError, AttributeError) as error:
                row.update(status='identity_mismatch', reason=str(error))
        write(out / 'cells' / (case['id'] + '.json'), row)
        rows.append(row)
        print(json.dumps(dict(pushid=pushid, scenario=case['id'], status=row['status'])), flush=True)
    # Cemetery generates the canonical per-target outcome report. Zoo does not
    # treat its regression verifier (stream equality) as an impact comparator.
    canonical_report = dict(schema=module.RESULT_SCHEMA, scenario_count=len(rows), results=[dict(r, depth=c['depth'], character_build_id=c['character_build']['id'], minimum_observed_living_hp=r.get('minimum_observed_living_hp'), evidence=r.get('evidence', {}), death_cause=r.get('death_cause')) for r, c in zip(rows, plan['cases'])], suite_id=generated['manifest']['suite_id'], revision=generated['manifest']['revision'])
    (out / 'cemetery-report.md').write_text(module.report(canonical_report))
    write(out / 'cemetery-results.json', canonical_report)
    return rows


def validate_cell(plan, case, target, row):
    """Reject substituted inputs/receipts, while permitting declared target changes."""
    expected = pairing_hash(plan, case)
    inputs = row.get('execution_input', {})
    if not isinstance(inputs, dict):
        raise ValueError('malformed execution inputs')
    if (row.get('schema') != 'borg-zoo/scenario-cell@1' or row.get('plan_sha256') != plan['plan_sha256'] or
            row.get('scenario_id') != case['id'] or row.get('pushid') != target['pushid'] or
            row.get('pairing_sha256') != expected or row.get('execution_sha256') != digest(inputs) or
            inputs.get('scenario') != case or inputs.get('target') != target or
            inputs.get('plan_sha256') != plan['plan_sha256'] or inputs.get('pairing_sha256') != expected):
        raise ValueError('undeclared scenario/target/input difference')
    if row.get('status') not in VALID | INVALID | {'stopped'}:
        raise ValueError('unknown execution outcome')
    if row['status'] in VALID | {'stopped'}:
        receipt = inputs.get('build_receipt') or {}
        build = receipt.get('build') or {}
        if (receipt.get('commit') != target['commit'] or receipt.get('repository') != target['repository'] or
                receipt.get('engine_sha256') != plan['semantics']['engine_sha256'] or
                build.get('git_rev') != target['commit'] or build.get('git_dirty') != 'no' or build.get('inputs_dirty') != 'no' or
                not HEX.fullmatch(build.get('binary_sha256', '')) or not HEX.fullmatch(build.get('source_sha256', '')) or
                not row.get('attempted') or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', inputs.get('calendar', ''))):
            raise ValueError('missing/invalid source/binary/calendar receipt')
        required = {'summary.json', 'process.json', 'config.txt', 'params.json', 'keys.log', 'state.log', 'messages.log'}
        if not isinstance(row.get('evidence'), dict) or not required <= row['evidence'].keys() or any(
                not isinstance(row['evidence'][key], dict) or not HEX.fullmatch(row['evidence'][key].get('sha256', '')) for key in required):
            raise ValueError('missing classified gameplay evidence')
        for name in ('summary.json', 'process.json', 'config.txt', 'params.json'):
            receipt = row.get('receipts', {}).get(name)
            if not isinstance(receipt, str) or hashlib.sha256(receipt.encode()).hexdigest() != row['evidence'][name]['sha256']:
                raise ValueError('missing or changed compact receipt bytes')
        if row.get('effective_settings') != effective_settings(case, row['receipts']['params.json']):
            raise ValueError('effective configuration identity mismatch')
        validate_terminal_receipts(case, row, build['binary_sha256'])
    return row


def validate_terminal_receipts(case, row, binary):
    """Re-derive compact start/terminal facts, independently of the row's label.

    This detects contradictory edits, not coordinated forgery: receipts are
    unsigned assertions of the pinned execution job. Stream checks still belong
    to Cemetery's classifier and require retained raw logs to reproduce.
    """
    summary = json.loads(row['receipts']['summary.json'])
    process = json.loads(row['receipts']['process.json'])
    config = {}
    for line in row['receipts']['config.txt'].splitlines():
        if '=' in line:
            key, value = line.split('=', 1)
            if key in config:
                raise ValueError('duplicate retained configuration field')
            config[key] = value
    character = case['character_build']
    expected = dict(synthetic=True, loaded=False, seed=case['seed'], race_idx=character['race_idx'],
                    class_idx=character['class_idx'], start_depth=case['depth'], initial_depth=case['depth'],
                    initial_cave_depth=case['depth'], initial_generation_pending=False, start_build=character['start'],
                    synthetic_contract=case['harness_contract'], dungeon_mode='one_way')
    if any(type(summary.get(k)) is not type(v) or summary.get(k) != v for k, v in expected.items()):
        raise ValueError('retained summary contradicts the requested synthetic start')
    for key, actual in (('level', 'initial_clevel'), ('max_hp', 'initial_max_hp'), ('max_sp', 'initial_max_sp')):
        if key in case['expected_start'] and (type(summary.get(actual)) is not int or summary[actual] != case['expected_start'][key]):
            raise ValueError('retained character build mismatch')
    options = summary.get('game_options', {})
    if options.get('birth_force_descend') is not True or options.get('birth_no_recall') is not True:
        raise ValueError('retained one-way rules mismatch')
    fields = dict(synthetic='1', start_depth=str(case['depth']), start_build=character['start'],
                  synthetic_contract=case['harness_contract'], dungeon_mode='one_way',
                  profile_sha256=character['profile_sha256'], borg_core=character['core'])
    if any(config.get(k) != v for k, v in fields.items()):
        raise ValueError('retained configuration contradicts the scenario')
    if character['start'] == 'record' and (summary.get('start_build_sha256') != character['record_sha256'] or config.get('start_build_sha256') != character['record_sha256']):
        raise ValueError('retained kit digest mismatch')
    if (process.get('status') != 'success' or type(process.get('exit_code')) is not int or process['exit_code'] != 0 or
            process.get('timed_out') is not False or process.get('executable_sha256_before') != binary or process.get('executable_sha256_after') != binary):
        raise ValueError('retained process cannot establish a gameplay outcome')
    turn, dead, reason = summary.get('game_turns'), summary.get('dead'), summary.get('stop_reason')
    if type(turn) is not int or turn < 0 or type(dead) is not bool or not isinstance(reason, str):
        raise ValueError('malformed retained terminal facts')
    if dead and reason == 'death':
        derived = 'death'
    elif not dead and reason == 'turns' and turn >= case['turn_cap']:
        derived = 'survived_to_cap'
    elif not dead and reason not in ('death', 'turns'):
        derived = 'stopped'
    else:
        raise ValueError('contradictory retained terminal facts')
    if row['status'] != derived:
        raise ValueError('reported outcome contradicts retained terminal facts')


def compare_pair(left, right):
    if 'missing' in (left['status'], right['status']):
        return 'missing'
    if left['status'] in INVALID or right['status'] in INVALID:
        return 'invalid'
    if left['execution_input']['calendar'] != right['execution_input']['calendar']:
        return 'inconclusive'
    if left.get('effective_settings') != right.get('effective_settings'):
        return 'invalid'
    a, b = left['status'], right['status']
    if a not in VALID or b not in VALID:
        return 'inconclusive'
    return {('death', 'death'): 'both_died', ('survived_to_cap', 'survived_to_cap'): 'both_survived',
            ('death', 'survived_to_cap'): 'rescued', ('survived_to_cap', 'death'): 'newly_killed'}[(a, b)]


def collect(plan, cells, out, evidence_url=''):
    validate_plan(plan)
    targets = {t['pushid']: t for t in plan['targets']}
    cases = {c['id']: c for c in plan['cases']}
    found = {}
    for path in sorted(Path(cells).rglob('cells/*.json')):
        if path.is_symlink():
            raise ValueError('symlink cell refused')
        try:
            row = read(path)
        except (ValueError, UnicodeError):
            pushid, scenario_id = path.parent.parent.name, path.stem
            if pushid not in targets or scenario_id not in cases:
                raise ValueError('unidentifiable malformed cell')
            row = dict(pushid=pushid, scenario_id=scenario_id, status='identity_mismatch',
                       reason='malformed cell JSON', raw_sha256=file_hash(path))
        if not isinstance(row, dict):
            raise ValueError('cell must be an object')
        key = row.get('pushid'), row.get('scenario_id')
        if key[0] not in targets or key[1] not in cases or key in found:
            raise ValueError('unexpected or duplicate scenario cell')
        try:
            validate_cell(plan, cases[key[1]], targets[key[0]], row)
        except (ValueError, TypeError, KeyError, AttributeError) as error:
            row = dict(pushid=key[0], scenario_id=key[1], status='identity_mismatch',
                       reason=str(error), rejected_record=row)
        found[key] = row
    rows = []
    for t in targets:
        for c in cases:
            rows.append(found.get((t, c), dict(pushid=t, scenario_id=c, status='missing',
                        plan_sha256=plan['plan_sha256'], pairing_sha256=pairing_hash(plan, cases[c]),
                        execution_sha256=None, expected_target=targets[t],
                        reason='no completed record collected (interrupted, failed or never started)')))
    index = {(r['pushid'], r['scenario_id']): r for r in rows}
    baseline = next(iter(targets))
    pairs, groups = [], defaultdict(Counter)
    for target in list(targets)[1:]:
        for c, case in cases.items():
            a, b = index[baseline, c], index[target, c]
            outcome = compare_pair(a, b)
            build = case['character_build']
            pair = dict(baseline=baseline, candidate=target, scenario_id=c, class_idx=build['class_idx'],
                        depth=case['depth'], loadout=build['id'], outcome=outcome)
            if outcome == 'invalid' and a['status'] in VALID and b['status'] in VALID:
                pair['reason'] = 'undeclared effective-configuration difference'
            pairs.append(pair)
            groups[target, build['class_idx'], case['depth'], build['id']][outcome] += 1
    report = dict(schema='borg-zoo/scenario-comparison@1', plan=plan, cells=rows, pairs=pairs,
                  counts=dict(Counter(p['outcome'] for p in pairs)), expected_cells=len(targets)*len(cases),
                  collected_cells=len(found), evidence_url=evidence_url,
                  aggregates=[dict(candidate=k[0], class_idx=k[1], depth=k[2], loadout=k[3], expected_pairs=sum(v.values()), counts=dict(v)) for k, v in groups.items()],
                  population_eligible=False, qualified_near_death=dict(coverage='unavailable', count=None))
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    write(out / 'comparison.json', report)
    (out / 'index.html').write_text(render(report))
    return report


def render(report, base="../../../"):
    from . import landing, site
    esc = lambda x: html.escape(str(x), quote=True)
    plan = report['plan']
    bank = plan['definition']['bank']
    url = f'https://github.com/{BANK_REPO}/tree/{bank["commit"]}/{Path(bank["manifest"]).parent.as_posix()}'
    parts = [f'<h1>Borg zoo</h1>{landing.nav("scenarios/index.html", base)}',
             f'<p><a href="{base}scenarios/index.html">All scenario runs</a></p>',
             f'<h2>{esc(plan["name"])}</h2>', '<p>Synthetic scenarios. No population or improvement claim. Low HP is only a candidate screen; qualified near-death is unavailable. Repeats/checkpoints are correlated.</p>',
             f'<p><a href="{esc(url)}">Pinned Cemetery bank, catalog and evidence</a> · <a href="comparison.json">Complete comparison receipts</a></p>']
    if report.get('evidence_url', '').startswith('https://github.com/'):
        parts.append(f'<p><a href="{esc(report["evidence_url"])}">Execution artifacts and Cemetery reports</a></p>')
    parts.append('<h2>Builds compared</h2><table><tr><th>Pushid</th><th>Specimen</th><th>Source/harness commit</th><th>Binary hashes</th></tr>')
    for t in plan['targets']:
        binaries = sorted({((r.get('execution_input') or {}).get('build_receipt') or {}).get('build', {}).get('binary_sha256', 'unavailable') for r in report['cells'] if r['pushid'] == t['pushid']})
        parts.append(f'<tr><td>{esc(t["pushid"])}</td><td>{esc(t["specimen"])}</td><td><a href="https://github.com/{esc(t["repository"])}/tree/{esc(t["commit"])}">{esc(t["commit"])}</a></td><td>{esc(", ".join(binaries))}</td></tr>')
    parts.append('</table><h2>Paired outcomes</h2><table><tr><th>Scenario</th><th>Candidate</th><th>Class</th><th>Depth</th><th>Loadout</th><th>Result</th><th>Reason</th></tr>')
    for p in report['pairs']:
        values = [p['scenario_id'], p['candidate'], catalogue.CLASSES[p['class_idx']], p['depth'], p['loadout'], p['outcome'], p.get('reason', '')]
        parts.append('<tr>' + ''.join(f'<td>{esc(v)}</td>' for v in values) + '</tr>')
    parts.append('</table><h2>Class/depth/loadout denominators</h2><table><tr><th>Candidate</th><th>Class</th><th>Depth</th><th>Loadout</th><th>Expected pairs</th><th>Outcomes</th></tr>')
    for a in report['aggregates']:
        values = [a['candidate'], catalogue.CLASSES[a['class_idx']], a['depth'], a['loadout'], a['expected_pairs'], a['counts']]
        parts.append('<tr>' + ''.join(f'<td>{esc(v)}</td>' for v in values) + '</tr>')
    parts.append('</table><h2>Every requested cell</h2><table><tr><th>Pushid</th><th>Scenario</th><th>Outcome</th><th>Sampled minimum HP</th><th>Reason</th></tr>')
    for r in report['cells']:
        parts.append('<tr>'+ ''.join(f'<td>{esc(r.get(k, "unavailable"))}</td>' for k in ('pushid', 'scenario_id', 'status', 'minimum_observed_living_hp', 'reason')) + '</tr>')
    parts += ['</table>', f'<p>Collected {report["collected_cells"]}/{report["expected_cells"]} cells. {esc(report["counts"])}</p>']
    body = ''.join(parts).replace('<table>', '<div class="wrap"><table>').replace('</table>', '</table></div>')
    return site.page(f'{plan["name"]} · Scenarios · Borg zoo', body, base=base)


def build_site(results, out):
    """Separate synthetic catalogue. Never feed these rows to population stats."""
    from . import landing, site

    out = Path(out) / 'scenarios'
    out.mkdir(parents=True, exist_ok=True)
    roots = [Path(results).parent / 'scenario-results', catalogue.ROOT / 'reports/scenarios']
    rows, unavailable = [], []
    for root in roots:
        for path in sorted(root.glob('*/*/comparison.json')):
            name, run = path.parent.parent.name, path.parent.name
            try:
                report = read(path)
                if report.get('schema') != 'borg-zoo/scenario-comparison@1':
                    raise ValueError('unsupported comparison schema')
                validate_plan(report['plan'])
                if not NAME.fullmatch(name) or not NAME.fullmatch(run):
                    raise ValueError('unsafe scenario report path')
                rendered = render(report)
                plan = report["plan"]
                versions = "<br>".join(f'<code>{html.escape(t["pushid"])}</code> · {html.escape(t["specimen"])}' for t in plan["targets"])
                outcomes = ", ".join(f'{key.replace("_", " ")}: {value}' for key, value in sorted(report["counts"].items()))
            except (OSError, ValueError, TypeError, KeyError, AttributeError, IndexError) as error:
                unavailable.append(dict(report=f'{name}/{run}', reason=str(error)))
                continue
            target = out / name / run
            target.mkdir(parents=True, exist_ok=True)
            (target / 'index.html').write_text(rendered)
            (target / 'comparison.json').write_bytes(path.read_bytes())
            rows.append([f'<a href="{name}/{run}/index.html">{html.escape(name)}</a><br><span class="muted">{html.escape(run)}</span>',
                         versions, len(plan['cases']), f'{report["collected_cells"]}/{report["expected_cells"]}',
                         html.escape(outcomes) or 'No paired outcomes'])
    from . import saved_incidents
    saved_rows, saved_unavailable = saved_incidents.build_site(results, out)
    rows.extend(saved_rows)
    unavailable.extend(saved_unavailable)
    (out / 'unavailable.json').write_text(json.dumps(unavailable, indent=2) + '\n')
    columns = [('Scenario run', 'The comparison and execution run; opens the full report.'),
               ('Versions', 'The exact pushids and specimens compared in this run.'),
               ('Scenarios', 'Distinct saved or synthetic encounter starts requested per version.'),
               ('Collected / expected cells', 'Completed records collected, including failures, out of all requested version × scenario cells.'),
               ('Outcomes', 'Scenario pairs by outcome for a comparison (missing, invalid and inconclusive included); the death share for a suite run of one build.')]
    body = (f'<h1>Borg zoo</h1>{landing.nav("scenarios/index.html", "../")}'
            '<h2>Scenario runs</h2>'
            + site.explain('Saved encounters and synthetic starts from pinned Cemetery banks, compared across exact Borg setups. '
                           'These runs stay separate from natural games and population statistics. '
                           'Missing and invalid cells remain visible; these comparisons alone do not establish improvement.', columns)
            + (site.table(columns, rows, left=2) if rows else '<p class="muted">No scenario runs yet.</p>'))
    if unavailable:
        body += '<h2>Unavailable reports</h2>' + site.table(['Report', 'Reason'],
            [[html.escape(r['report']), html.escape(r['reason'])] for r in unavailable], left=2)
    (out / 'index.html').write_text(site.page('Scenarios · Borg zoo', body, base='../'))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    s = sub.add_parser('plan')
    s.add_argument('--definition', required=True)
    s.add_argument('--bank', required=True)
    s.add_argument('--out', required=True)
    s = sub.add_parser('run')
    s.add_argument('--plan', required=True)
    s.add_argument('--bank', required=True)
    s.add_argument('--source', required=True)
    s.add_argument('--pushid', required=True)
    s.add_argument('--out', required=True)
    s = sub.add_parser('collect')
    s.add_argument('--plan', required=True)
    s.add_argument('--cells', required=True)
    s.add_argument('--out', required=True)
    s.add_argument('--evidence-url', default='')
    args = p.parse_args(argv)
    try:
        if args.command == 'plan':
            write(args.out, prepare(args.definition, args.bank))
        elif args.command == 'run':
            rows = run_target(read(args.plan), args.bank, args.source, args.pushid, args.out)
            return int(any(r['status'] in INVALID for r in rows))
        else:
            collect(read(args.plan), args.cells, args.out, args.evidence_url)
        return 0
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        p.error(str(error))


if __name__ == '__main__':
    raise SystemExit(main())
