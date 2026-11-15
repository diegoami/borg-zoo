/* Keep bytes for copy/download; never regenerate configuration from settings. */
(async () => {
  const $ = id => document.getElementById(id);
  let bytes = null, serial = 0;
  const status = message => { $('status').textContent = message; };
  const show = value => value == null ? 'Unavailable in the recorded evidence.' : JSON.stringify(value, null, 2);
  try {
    const response = await fetch('games.json');
    if (!response.ok) throw new Error('Game index unavailable');
    const {games, names} = await response.json();
    for (const key of ['seed', 'specimen', 'profile', 'suite']) {
      const values = [...new Set(games.map(g => String(g[key])))];
      for (const value of values) {
        const option = document.createElement('option'); option.value = value;
        option.textContent = key === 'profile' ? `${names[value] || value} (${value})` : value;
        $(key === 'seed' ? 'seeds' : key).append(option);
      }
    }
    $('seed').value = String(games[0]?.seed || '');
    async function select(event) {
      event?.preventDefault();
      const ticket = ++serial;
      bytes = null; $('copy').disabled = $('download').disabled = true; $('file').textContent = '';
      const cell = games.find(g => ['seed', 'specimen', 'profile', 'suite'].every(k => String(g[k]) === $(k).value));
      $('identity').replaceChildren(); $('requested').textContent = $('native').textContent = '';
      if (!cell) return status('No recorded game matches that seed, version, choice and suite.');
      for (const [key, value] of Object.entries(cell)) {
        if (['requested_overrides', 'native_effective_settings', 'file'].includes(key)) continue;
        const dt = document.createElement('dt'), dd = document.createElement('dd');
        dt.textContent = key.replaceAll('_', ' '); dd.textContent = value ?? 'Unavailable';
        $('identity').append(dt, dd);
      }
      $('requested').textContent = show(cell.requested_overrides);
      $('native').textContent = show(cell.native_effective_settings);
      if (!cell.file) return status('Original borg.txt unavailable in retained evidence. Recorded overrides and native settings are shown separately below.');
      status('Checking original file SHA-256…');
      const fileResponse = await fetch(cell.file);
      if (!fileResponse.ok) throw new Error('Original file could not be downloaded');
      const raw = new Uint8Array(await fileResponse.arrayBuffer());
      const digest = [...new Uint8Array(await crypto.subtle.digest('SHA-256', raw))].map(x => x.toString(16).padStart(2, '0')).join('');
      if (ticket !== serial) return;
      if (digest !== cell.config_sha256) throw new Error('SHA-256 mismatch: refusing to display, copy or download these bytes');
      const decoded = new TextDecoder('utf-8', {fatal: true, ignoreBOM: true}).decode(raw);
      // Clipboard text must round-trip the complete file (including CRLF/BOM).
      const encoded = new TextEncoder().encode(decoded);
      const copyable = encoded.length === raw.length && encoded.every((x, i) => x === raw[i]);
      bytes = raw; $('file').textContent = decoded;
      $('copy').disabled = !copyable; $('download').disabled = false;
      status('Verified original borg.txt. Displayed bytes match the recorded SHA-256.');
    }
    $('choose').addEventListener('submit', event => select(event).catch(error => { bytes = null; $('copy').disabled = $('download').disabled = true; status(error.message); }));
    $('copy').addEventListener('click', async () => {
      try { await navigator.clipboard.writeText(new TextDecoder('utf-8', {fatal: true, ignoreBOM: true}).decode(bytes)); status('Original file copied.'); }
      catch { status('Clipboard unavailable. Download preserves the exact original bytes.'); }
    });
    $('download').addEventListener('click', () => {
      const url = URL.createObjectURL(new Blob([bytes], {type: 'application/octet-stream'}));
      const a = document.createElement('a'); a.href = url; a.download = 'borg.txt'; a.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
    await select();
  } catch (error) { status(error.message); }
})();
