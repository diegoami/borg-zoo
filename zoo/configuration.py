"""Exact configuration evidence, separate from requested/native settings."""
import gzip
import hashlib
import html
import json
import os
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verified_bytes(path, digest):
    if not digest or not path.is_file():
        return None
    try:
        data = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
    except (OSError, EOFError):
        return None
    return data if hashlib.sha256(data).hexdigest() == digest else None


def capture(record, work, blobs):
    path = Path(work) / 'user/borg.txt'
    digest = record.get('config_sha256')
    data = verified_bytes(path, digest)
    if data is None:
        record['configuration_file'] = {'status': 'unavailable',
            'reason': 'Original borg.txt unavailable or does not match the recorded SHA-256.'}
        return
    blobs = Path(blobs)
    blobs.mkdir(parents=True, exist_ok=True)
    target = blobs / f'{digest}.txt'
    # Cells that share a borg.txt share its blob and run side by side: write the whole blob under a private name and
    # link it into place, so a second cell never finds a half-written file (borg-zoo#548: a dogs10 cell failed with
    # "configuration evidence hash mismatch" when it opened the blob while another cell was still writing it).
    tmp = blobs / f'.{digest}.{os.getpid()}.{threading.get_ident()}.tmp'
    try:
        tmp.write_bytes(data)
        try:
            os.link(tmp, target)
        except FileExistsError:
            pass
    finally:
        tmp.unlink(missing_ok=True)
    if verified_bytes(target, digest) is None:
        raise ValueError(f'configuration evidence hash mismatch: {digest}')
    record['configuration_file'] = {'status': 'verified', 'sha256': digest,
        'path': f'configurations/{digest}.txt', 'source': 'Written user/borg.txt from this attempt'}


def collect(records, cells, target):
    """Copy only hash-verified blobs referenced by collected records."""
    copied = set()
    for record in records:
        info = record.get('configuration_file') or {}
        if info.get('status') != 'verified':
            continue
        digest = record.get('config_sha256')
        if info.get('sha256') != digest or not valid_digest(digest):
            raise ValueError('configuration evidence identity mismatch')
        if digest in copied:
            continue
        candidates = Path(cells).rglob(f'{digest}.txt')
        data = next((data for path in candidates if
                     (data := verified_bytes(path, digest)) is not None), None)
        if data is None:
            raise ValueError(f'missing verified configuration blob: {digest}')
        out = Path(target) / 'configurations' / f'{digest}.txt'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        copied.add(digest)


def valid_digest(digest):
    return isinstance(digest, str) and len(digest) == 64 and all(c in '0123456789abcdef' for c in digest)


def choices(meta, cells):
    """Use recorded snapshots for requested overrides, including class selectors."""
    profiles = meta['catalogue'].get('profiles', {})
    values = {key: profile.get('settings', {}) for key, profile in profiles.items()}
    return values


def arm_names(meta):
    display = json.loads((ROOT / 'catalogue/study-presentation.json').read_text())['profiles']
    from .briefs import profile_label
    return {p: display.get(p, profile_label(p)) for p in meta['experiment']['profiles']}


def summary(meta):
    esc = html.escape
    profiles = choices(meta, [])
    names = arm_names(meta)
    all_keys = set().union(*(set(v) for v in profiles.values())) if profiles else set()
    varied = sorted(k for k in all_keys if len({json.dumps(v.get(k, 'inherited')) for v in profiles.values()}) > 1)
    fixed = sorted(k for k in all_keys if k not in varied)
    rows = []
    for specimen in meta['experiment']['specimens']:
        for profile in meta['experiment']['profiles']:
            cfg = profiles.get(profile, {})
            details = '; '.join(explain(k, cfg.get(k)) for k in varied) or 'Same recorded overrides as the other arms.'
            selector = meta['catalogue'].get('profiles', {}).get(profile, {})
            if selector.get('by_class'):
                details += ' Class-specific overrides apply; inspect the selected game for its applied profile.'
            rows.append(f'<tr><td>{esc(specimen)}</td><td>{esc(names[profile])}</td><td>{esc(details)}</td></tr>')
    fixed_text = '; '.join(explain(k, profiles[next(iter(profiles))].get(k)) for k in fixed) if profiles else ''
    return ('<section class="card"><details class="fold"><summary>Configurations compared</summary>'
        '<p><a href="configurations/index.html"><strong>View borg.txt for any game</strong></a> '
        '— choose a seed and arm to inspect, copy or download its original file.</p>'
        '<p>Requested profile overrides, the actual file, and native-reported effective settings are separate evidence. '
        'Settings inherited from the build may differ between versions.</p>'
        '<div class="wrap"><table><tr><th>Version</th><th>Choice</th><th>What differs</th></tr>'
        + ''.join(rows) + '</table></div>'
        + '<details><summary>Settings held fixed in the recorded profiles</summary><p>'
        + esc(fixed_text or 'No common explicit overrides recorded; build defaults remain unspecified.')
        + '</p></details><p>Pack slack 0 means wait until the pack is full. Unknown stacks 0 disables learning-driven returns.</p></details></section>')


def explain(key, value):
    if value is None:
        return f'{key}: inherited from the build (not specified here)'
    if key == 'borg_trip_pack_slack':
        return 'Return when the pack is full (pack slack 0)' if value == 0 else f'Return with {value} pack spaces remaining'
    if key == 'borg_trip_unknown_stacks':
        return 'Learning-driven returns disabled (unknown stacks 0)' if value == 0 else f'Return at {value} eligible unknown stacks'
    if key == 'borg_town_risk':
        return f'Supply planning uses {value / 1000:g}× forecast risk'
    descriptions = {'borg_town_plan': 'New shopping policy', 'borg_trip_policy': 'New return policy',
        'borg_town_no_stores': 'Avoid shops', 'borg_buy_identify': 'Buy identification',
        'borg_munchkin_by_class': 'Stair-climbing start for Warrior, Druid and Ranger',
        'borg_munchkin_start': 'Stair-climbing start', 'borg_self_lunal': 'Permit Lunal mode'}
    if key in descriptions:
        return f'{descriptions[key]}: {"on" if value else "off"}'
    return f'{key.removeprefix("borg_").replace("_", " ")}: {value}'


def build_inspector(meta, cells, source, target):
    target = Path(target) / 'configurations'
    target.mkdir(parents=True, exist_ok=True)
    recovered = ROOT / 'reports/configuration-evidence'
    origins = json.loads((recovered / 'manifest.json').read_text()) if (recovered / 'manifest.json').exists() else {}
    rows = []
    written = set()
    consolidated_blobs = {}
    if meta.get('consolidated_runs'):
        # Index once: scanning the complete results tree for every game makes
        # historical consolidated reports needlessly expensive to publish.
        for path in Path(source).parent.parent.rglob('configurations/*.txt'):
            consolidated_blobs.setdefault(path.stem, path)
    cache = {}
    for cell in cells:
        digest = cell.get('config_sha256')
        data, origin = None, None
        if digest in cache:
            data, origin = cache[digest]
        elif valid_digest(digest):
            candidates = [Path(source) / 'configurations' / f'{digest}.txt', recovered / f'{digest}.txt.gz']
            # Consolidated reports can include blobs from several workflow runs.
            if digest in consolidated_blobs:
                candidates.append(consolidated_blobs[digest])
            for candidate in candidates:
                data = verified_bytes(candidate, digest)
                if data is not None:
                    origin = origins.get(digest, {}).get('source', 'Captured written user/borg.txt from the recorded attempt')
                    break
            cache[digest] = data, origin
        filename = None
        if data is not None:
            # Published gzipped: 586,936 cells of borg.txt text pushed the site
            # artifact past GitHub Pages' 1 GB deploy limit (2026-11-24); the
            # inspector inflates with DecompressionStream, the bytes stay exact.
            filename = f'{digest}.txt.gz'
            if filename not in written:
                (target / filename).write_bytes(gzip.compress(data, 6))
                written.add(filename)
        applied = cell.get('profile_applied', cell['profile'])
        profile = meta['catalogue'].get('profiles', {}).get(applied)
        requested = cell.get('requested_profile_settings', profile.get('settings') if profile else None)
        rows.append({**{k: cell.get(k) for k in ('suite', 'specimen', 'profile', 'seed', 'outcome', 'config_sha256')},
            'race': cell.get('played_race') or cell.get('race'),
            'class': cell.get('played_class') or cell.get('class'),
            'applied_profile': applied, 'source_commit': cell.get('specimen_ref') or
                meta['catalogue']['specimens'].get(cell['specimen'], {}).get('ref'),
            'requested_overrides': requested,
            'native_effective_settings': cell.get('native_reported_settings') or (cell.get('effective_settings') if cell.get('effective_settings') is not None else cell.get('effective_options')),
            'file': filename, 'file_source': origin})
    (target / 'games.json').write_text(json.dumps({'games': rows, 'names': arm_names(meta)}, ensure_ascii=False))
    from .site import page
    body = (ROOT / 'zoo/assets/configuration-inspector.html').read_text()
    (target / 'index.html').write_text(page('View borg.txt · borg-zoo', body))
    (target / 'inspector.js').write_bytes((ROOT / 'zoo/assets/configuration-inspector.js').read_bytes())
