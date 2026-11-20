#!/usr/bin/env python3
"""Fill the report template with recorded deaths and the session's findings.

    page.py FRAMES_JSON --out PAGE.html --title "Ranger Deaths on fde8025a" --pack fde8-rangers
            --header header.html --findings findings.html --footer footer.html
            [--classes classes.json] [--cases cases.json]

header.html, findings.html and footer.html are HTML fragments the session writes from what
it read in the deaths (see SKILL.md). classes.json, when given, is a list of
{"cls", "before", "after"} rows for the per-class bar table; findings.html must then contain
a <table id="cls"> with a <tbody></tbody>. cases.json maps seed (or a death's dir, when one seed
died twice) -> cemetery dossier id (D-<sha>) for the per-death dossier link. An optional
`note` on a death in FRAMES_JSON (e.g. which arms played it) is shown with it.
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('frames', type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--title', required=True)
    ap.add_argument('--pack', required=True)
    ap.add_argument('--header', required=True, type=Path)
    ap.add_argument('--findings', required=True, type=Path)
    ap.add_argument('--footer', required=True, type=Path)
    ap.add_argument('--classes', type=Path)
    ap.add_argument('--cases', type=Path)
    a = ap.parse_args()
    data = json.loads(a.frames.read_text())
    cases = json.loads(a.cases.read_text()) if a.cases else {}
    for d in data:
        d['case'] = cases.get(d['dir']) or cases.get(str(d['seed']), '')
    classes = json.loads(a.classes.read_text()) if a.classes else []
    js = lambda o: json.dumps(o, separators=(',', ':')).replace('</', '<\\/')
    t = (HERE / 'template.html').read_text()
    for k, v in (('__TITLE__', a.title), ('__HEADER__', a.header.read_text()), ('__FINDINGS__', a.findings.read_text()),
                 ('__FOOTER__', a.footer.read_text()), ('__PACK__', a.pack), ('__FIRSTDIR__', data[0]['dir']),
                 ('__DATA__', js(data)), ('__CLASSES__', js(classes))):
        t = t.replace(k, v)
    a.out.write_text(t)
    print(f'{a.out} ({len(t) // 1024} KB, {len(data)} deaths)')


if __name__ == '__main__':
    main()
