"""Zoo execution/reporting for the bounded mixed-class saved-encounter smoke.

Cemetery owns saved inputs and native execution. This baseline is deliberately
separate from generated births, natural seed suites and paired-impact reports.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import html
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SHA = re.compile('[0-9a-f]{40}')
HEX = re.compile('[0-9a-f]{64}')
VALID = {'death', 'survived_horizon', 'stopped'}
CLASSES = {1: 'Mage', 2: 'Druid', 3: 'Priest', 4: 'Necromancer'}
STATE = re.compile(r'^(\d+) -?\d+,-?\d+ d(\d+)/(\d+) hp(-?\d+)/(\d+) sp(-?\d+)/(\d+)(?: |$)')


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True).strip()


def checked_checkout(path, commit):
    if not SHA.fullmatch(commit) or git(path, 'rev-parse', 'HEAD') != commit or git(path, 'status', '--porcelain', '--untracked-files=no'):
        raise ValueError('checkout differs from clean immutable pin')


def local(root, name, expected):
    path = (root / name).resolve()
    path.relative_to(root.resolve())
    if not HEX.fullmatch(expected) or sha(path) != expected:
        raise ValueError('input digest differs: ' + name)
    return path


def validate_yaml(value):
    keys = {'kind', 'name', 'folder', 'issue', 'question', 'specimen', 'bank', 'native_tools', 'owner_authorization', 'prespecified'}
    if set(value) != keys or value['kind'] != 'saved-encounter-smoke' or value['folder'] != 'scenario-experiments':
        raise ValueError('unsupported saved-encounter definition keys/kind/folder')
    if not re.fullmatch('[a-z0-9][a-z0-9-]{0,99}', value['name']) or not isinstance(value['issue'], int):
        raise ValueError('invalid definition identity')
    for pin in (value['bank'], value['native_tools']):
        if pin['repository'] != 'diegoami/borg-cemetery' or not SHA.fullmatch(pin['commit']):
            raise ValueError('Cemetery requires an exact pin')
    if not HEX.fullmatch(value['bank']['manifest_sha256']) or not value['bank']['runner_sha256']:
        raise ValueError('missing bank/runner digests')
    for path, expected in value['bank']['runner_sha256'].items():
        if Path(path).is_absolute() or '..' in Path(path).parts or not HEX.fullmatch(expected):
            raise ValueError('invalid runner reference')


def definition_plan(value, path, root):
    validate_yaml(value)
    specimen = read(root / 'catalogue/specimens.json')['specimens'][value['specimen']]
    if specimen['repository'] != 'diegoami/borg-reborn-rs' or not SHA.fullmatch(specimen['ref']):
        raise ValueError('only exact reborn source pins qualified')
    body = dict(value, schema='borg-zoo/saved-encounter-smoke@1', definition=Path(path).resolve().relative_to(root.resolve()).as_posix(),
                source=dict(repository=specimen['repository'], commit=specimen['ref'], specimen=value['specimen'], snapshot=specimen),
                core='reborn', expected_cells=8, comparison_axis=[], executor='zoo', independent_life=False)
    target = root / value['folder'] / (value['name'] + '.json')
    changes = []
    if not target.exists() or read(target) != body:
        changes.append(('experiment-update' if target.exists() else 'experiment', target.relative_to(root).as_posix(), body))
    return value, [], changes


def bank_cases(bank, definition):
    checked_checkout(bank, definition['bank']['commit'])
    for name, expected in definition['bank']['runner_sha256'].items():
        local(bank, name, expected)
    manifest = local(bank, definition['bank']['manifest'], definition['bank']['manifest_sha256'])
    # Delegate the authoritative suite qualification to exactly pinned Cemetery.
    code = """import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.argv[1])/'scripts'))
from encounter_suite import prepare
m,c=prepare(Path(sys.argv[2]),Path(sys.argv[1]))
print(json.dumps({'manifest':m,'cases':[{'id':n,'scenario':str((d/'scenario.json').relative_to(Path(sys.argv[1])))} for n,d,p in c]}))
"""
    data = json.loads(subprocess.check_output([sys.executable, '-c', code, str(bank), str(manifest)], text=True))
    cases = []
    for item in data['cases']:
        scenario_path = bank / item['scenario']
        scenario = read(scenario_path)
        cases.append(dict(id=item['id'], scenario_path=item['scenario'], scenario_sha256=sha(scenario_path), scenario=scenario,
                          profile_text=(scenario_path.parent / scenario['baseline_profile']).read_text()))
    counts = Counter(c['scenario']['class_idx'] for c in cases)
    if counts != Counter({1: 2, 2: 2, 3: 2, 4: 2}) or len({c['scenario']['save_sha256'] for c in cases}) != 8:
        raise ValueError('smoke requires eight distinct starts, two per caster class')
    return data['manifest'], cases


def plan(definition_path, bank, source, tools, output):
    definition = read(definition_path)
    if definition.get('schema') != 'borg-zoo/saved-encounter-smoke@1' or definition.get('core') != 'reborn' or definition.get('comparison_axis') != []:
        raise ValueError('unsupported saved-state baseline contract')
    checked_checkout(source, definition['source']['commit'])
    checked_checkout(tools, definition['native_tools']['commit'])
    if (source / 'death-tools-pin.txt').read_text().strip() != definition['native_tools']['commit']:
        raise ValueError('source native-tools pin differs')
    manifest, cases = bank_cases(bank, definition)
    upstream = dict(line.split('=', 1) for line in (source / 'engine/UPSTREAM').read_text().splitlines() if '=' in line)
    if upstream.get('commit') != manifest['engine_commit'] or manifest['horizon_engine_turns'] > 1000 or manifest['wall_seconds'] > 5:
        raise ValueError('engine or smoke budget differs')
    source_sha = subprocess.check_output(['bash', str(source / 'harness/identity.sh'), 'source-hash', 'rust'], text=True).strip()
    value = dict(schema='borg-zoo/saved-encounter-plan@1', definition=definition, definition_sha256=sha(definition_path),
                 zoo_commit=git(ROOT, 'rev-parse', 'HEAD'), runner_sha256=sha(Path(__file__)), manifest=manifest,
                 zoo_inputs_dirty=bool(git(ROOT, 'status', '--porcelain', '--', 'zoo/encounters.py', 'zoo/define.py', definition['definition'])),
                 source_sha256=source_sha, cases=cases, expected_cells=8)
    value['plan_hash'] = digest(value)
    write(output, value)
    return value


def load_plan(path):
    value = read(path)
    expected = value.pop('plan_hash')
    if value.get('schema') != 'borg-zoo/saved-encounter-plan@1' or digest(value) != expected:
        raise ValueError('plan identity differs')
    value['plan_hash'] = expected
    if (value['expected_cells'] != 8 or len(value['cases']) != 8
            or Counter(c['scenario']['class_idx'] for c in value['cases']) != Counter({1: 2, 2: 2, 3: 2, 4: 2})
            or len({c['id'] for c in value['cases']}) != 8
            or len({c['scenario']['save_sha256'] for c in value['cases']}) != 8):
        raise ValueError('plan lost the eight-cell mixed-class contract')
    return value


def kv(text):
    return dict(line.split('=', 1) for line in text.splitlines() if '=' in line)


def validate_receipts(plan_value, case, receipts):
    trial = json.loads(receipts['trial.json'])
    scenario = case['scenario']
    definition = plan_value['definition']
    expected = dict(source_commit=definition['source']['commit'], scenario_sha256=case['scenario_sha256'],
                    save_sha256=scenario['save_sha256'], startup_contract='fresh_borg_saved_engine_rng',
                    borg_memory_restored=False, start_turn=scenario['start_turn'],
                    horizon_engine_turns=plan_value['manifest']['horizon_engine_turns'],
                    cap_turn=scenario['start_turn'] + plan_value['manifest']['horizon_engine_turns'])
    if any(trial.get(k) != v for k, v in expected.items()):
        raise ValueError('trial input/start identity differs')
    status = trial['status']
    if status not in VALID:
        return status
    build, process, summary = trial['build'], trial['process'], trial['summary']
    if (trial.get('exit_code') != 0 or build.get('git_rev') != definition['source']['commit']
            or build.get('source_sha256') != plan_value['source_sha256'] or build.get('inputs_dirty') != 'no'
            or build.get('impl') != 'rust' or not HEX.fullmatch(str(build.get('binary_sha256', '')))
            or build.get('engine_upstream') != plan_value['manifest']['engine_commit']
            or process.get('status') != 'success' or process.get('exit_code') != 0
            or process.get('executable_sha256_before') != build.get('binary_sha256')
            or process.get('executable_sha256_after') != build.get('binary_sha256')
            or json.loads(receipts['summary.json']) != summary or json.loads(receipts['process.json']) != process):
        raise ValueError('native process/build receipt differs')
    identity = dict(loaded=True, calendar='fixed', loaded_turn=scenario['start_turn'], seed=scenario['birth_seed'], race_idx=scenario['race_idx'], class_idx=scenario['class_idx'])
    if any(summary.get(k) != v for k, v in identity.items()):
        raise ValueError('native loaded identity differs')
    if any(v for k, v in summary.get('game_options', {}).items() if k.startswith('cheat_')):
        raise ValueError('cheat option enabled')
    config = kv(receipts['config.txt'])
    if (config.get('borg_core') != 'reborn' or 'keep-load-rng' not in config.get('flags', '').split(',')
            or config.get('save_sha256') != scenario['save_sha256']
            or trial.get('profile_sha256') != scenario['baseline_profile_sha256']
            or config.get('profile_sha256') != scenario['baseline_profile_sha256']):
        raise ValueError('core/profile/saved-RNG configuration differs')
    effective = {p['name']: p['value'] for p in json.loads(receipts['params.json'])['parameters']}
    for raw in case['profile_text'].splitlines():
        line = raw.split('#', 1)[0].strip()
        if line:
            name, value = (part.strip() for part in line.split('=', 1))
            if effective.get(name) != int(value):
                raise ValueError('profile value not effective: ' + name)
    state = STATE.match(receipts['initial-state'])
    expected_state = [scenario['start_turn'], scenario['checkpoint']['depth'], scenario['checkpoint']['max_depth']] + [scenario['initial_observed'][k] for k in ('hp', 'max_hp', 'sp', 'max_sp')]
    if not state or list(map(int, state.groups())) != expected_state:
        raise ValueError('native initial state differs')
    if status == 'death' and (summary.get('dead') is not True or summary.get('stop_reason') != 'death'):
        raise ValueError('death facts differ')
    if status == 'survived_horizon' and (summary.get('dead') is not False or summary.get('stop_reason') != 'turns' or summary.get('game_turns', 0) < expected['cap_turn']):
        raise ValueError('horizon facts differ')
    return status


def make_cell(plan_value, case, directory):
    receipts = {'trial.json': (directory / 'trial.json').read_text()}
    trial = json.loads(receipts['trial.json'])
    if trial.get('status') in ('preparing', 'running'):
        return None
    for name in ('summary.json', 'process.json', 'config.txt', 'params.json'):
        if (directory / 'run' / name).exists():
            receipts[name] = (directory / 'run' / name).read_text()
    if (directory / 'run/state.log').exists():
        with (directory / 'run/state.log').open() as stream:
            receipts['initial-state'] = next(stream, '')
    cell = dict(schema='borg-zoo/saved-encounter-cell@1', id=case['id'], plan_hash=plan_value['plan_hash'],
                receipts=receipts, receipts_sha256={k: hashlib.sha256(v.encode()).hexdigest() for k, v in receipts.items()},
                independent_life=False, origin=case['scenario']['origin'])
    try:
        cell['status'] = validate_receipts(plan_value, case, receipts)
    except (ValueError, KeyError, TypeError, AttributeError, IndexError) as error:
        cell.update(status='invalid_receipt', reason=str(error))
    cell['execution_hash'] = digest(dict(plan=plan_value['plan_hash'], scenario=case['scenario_sha256'],
                                        build=trial.get('build'), receipts=cell['receipts_sha256']))
    return cell


def execute(plan_path, bank, source, tools, output):
    value = load_plan(plan_path)
    if output.exists():
        raise ValueError('use a fresh attempt directory')
    if sha(Path(__file__)) != value['runner_sha256']:
        raise ValueError('Zoo runner changed since plan')
    checked_checkout(source, value['definition']['source']['commit'])
    checked_checkout(tools, value['definition']['native_tools']['commit'])
    manifest, cases = bank_cases(bank, value['definition'])
    if cases != value['cases'] or manifest != value['manifest']:
        raise ValueError('bank inputs changed since plan')
    output.mkdir(parents=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith(('BORG_', 'ANGBAND_')) and k not in ('BORGH_DATA_ROOT', 'SAVE_ROOT', 'STALL_TIMEOUT_SECONDS')}
    env.update(BORG_CEMETERY_DIR=str(tools))
    command = [sys.executable, str(bank / 'scripts/encounter_suite.py'), '--manifest', str(bank / value['definition']['bank']['manifest']),
               '--source', str(source), '--out', str(output / 'native')]
    tick = time.monotonic()
    pending = {c['id']: c for c in cases}
    timed_out = False
    def journal():
        for name, case in list(pending.items()):
            trial = output / 'native' / name / 'trial.json'
            if trial.exists():
                try:
                    cell = make_cell(value, case, trial.parent)
                    if cell is not None:
                        write(output / 'cells' / (name + '.json'), cell)
                        del pending[name]
                except (json.JSONDecodeError, OSError):
                    pass  # Writer may be between truncation and flush.
    with (output / 'launcher.log').open('w') as log:
        process = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        while True:
            journal()
            if process.poll() is not None:
                journal()  # Include a last cell completed between scan and exit.
                break
            if time.monotonic() - tick > 360:
                timed_out = True
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                break
            time.sleep(0.2)
    write(output / 'execution.json', dict(command=command, returncode=process.returncode,
        timed_out=timed_out, elapsed_seconds=time.monotonic() - tick, pending=list(pending)))
    return int(process.returncode != 0 or bool(pending) or any(
        read(path)['status'] not in VALID for path in (output / 'cells').glob('*.json')))


def collect(plan_path, attempt, output, run_url=''):
    value = load_plan(plan_path)
    if output.exists():
        raise ValueError('use a fresh report directory')
    cells, counts = [], defaultdict(Counter)
    for case in value['cases']:
        path = attempt / 'cells' / (case['id'] + '.json')
        row = dict(id=case['id'], class_name=CLASSES[case['scenario']['class_idx']], origin=case['scenario']['origin'], status='missing')
        if path.exists():
            try:
                cell = read(path)
                if cell['id'] != case['id'] or cell['plan_hash'] != value['plan_hash']:
                    raise ValueError('cell identity differs')
                for name, raw in cell['receipts'].items():
                    if hashlib.sha256(raw.encode()).hexdigest() != cell['receipts_sha256'].get(name):
                        raise ValueError('receipt digest differs')
                status = validate_receipts(value, case, cell['receipts'])
                trial = json.loads(cell['receipts']['trial.json'])
                expected_execution = digest(dict(plan=value['plan_hash'], scenario=case['scenario_sha256'],
                    build=trial.get('build'), receipts=cell['receipts_sha256']))
                if expected_execution != cell['execution_hash'] or cell['status'] != status:
                    raise ValueError('execution/outcome differs')
                row.update(status=status, execution_hash=cell['execution_hash'], summary=trial.get('summary'), build=trial.get('build'), cell=cell)
            except (ValueError, KeyError, TypeError, OSError, AttributeError, IndexError) as error:
                row.update(status='invalid_receipt', reason=str(error))
        counts[row['class_name']][row['status']] += 1
        cells.append(row)
    report = dict(schema='borg-zoo/saved-encounter-results@1', name=value['definition']['name'], executor='zoo',
        run_url=run_url, plan=value, expected_cells=8, cells=cells, per_class=dict(counts),
        invalid_count=sum(c['status'] not in VALID for c in cells), independent_life=False,
        qualified_near_death=dict(coverage='unavailable', count=None))
    output.mkdir(parents=True)
    write(output / 'comparison.json', report)
    lines = ['# Zoo mixed-class saved-encounter smoke', '', 'Eight saved starts; fixed reborn build; fresh Borg memory and saved engine RNG.', '',
             f"Source: `{value['definition']['source']['commit']}`. Cemetery: `{value['definition']['bank']['commit']}`.", '',
             'This is a baseline execution check, with no paired impact or population claim.', '',
             '| Class | Scenario | Outcome | End HP | End depth |', '|---|---|---|---:|---:|']
    for cell in cells:
        summary = cell.get('summary') or {}
        lines.append('| ' + ' | '.join(str(v) for v in (cell['class_name'], cell['id'], cell['status'], summary.get('hp', '—'), summary.get('depth', '—'))) + ' |')
    lines += ['', f"Expected cells: 8. Invalid/missing: {report['invalid_count']}.", '',
              'Shared-life encounters stay correlated. Survival is to the finite horizon only. No qualified near-death diagnostic.', '',
              f"[Issue](https://github.com/diegoami/borg-zoo/issues/{value['definition']['issue']}) · [YAML definition](https://github.com/diegoami/borg-zoo/blob/{value['zoo_commit']}/{value['definition']['definition']}) · [Zoo run]({run_url})"]
    text = '\n'.join(lines) + '\n'
    (output / 'comparison.md').write_text(text)
    (output / 'comparison.html').write_text('<!doctype html><meta charset="utf-8"><title>Zoo caster encounters</title><pre>' + html.escape(text) + '</pre>')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    p = commands.add_parser('plan')
    for name in ('definition', 'bank', 'source', 'tools', 'out'):
        p.add_argument('--' + name, type=Path, required=True)
    p = commands.add_parser('run')
    for name in ('plan', 'bank', 'source', 'tools', 'out'):
        p.add_argument('--' + name, type=Path, required=True)
    p = commands.add_parser('collect')
    for name in ('plan', 'attempt', 'out'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--run-url', default='')
    args = parser.parse_args()
    if args.action == 'plan':
        plan(args.definition.resolve(), args.bank.resolve(), args.source.resolve(), args.tools.resolve(), args.out.resolve())
    elif args.action == 'run':
        return execute(args.plan.resolve(), args.bank.resolve(), args.source.resolve(), args.tools.resolve(), args.out.resolve())
    else:
        result = collect(args.plan.resolve(), args.attempt.resolve(), args.out.resolve(), args.run_url)
        print(f"8 expected cells, {result['invalid_count']} invalid/missing")
        return int(bool(result['invalid_count']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
