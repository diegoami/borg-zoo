"""Bounded zoo#114 index benchmark: load every results-branch cell into SQLite
(scalar fields + content-addressed full record) and time dashboard-shaped queries.

These are query *workloads*, not the zoo's statistics: the paired query keeps
only finished games of one harness kind, as zoo/stats.py does, but it does not
apply every pairing rule (command-stream profile, mode cutoff)."""
import glob, gzip, hashlib, json, os, sqlite3, sys, time

root, db = sys.argv[1], sys.argv[2]
if os.path.exists(db):
    os.remove(db)
con = sqlite3.connect(db)
con.executescript("""
PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;
CREATE TABLE run(run_id TEXT PRIMARY KEY, experiment TEXT, meta_sha256 TEXT);
CREATE TABLE blob(sha256 TEXT PRIMARY KEY, bytes INTEGER, gz BLOB);
CREATE TABLE cell(
  run_id TEXT NOT NULL REFERENCES run, ordinal INTEGER NOT NULL,
  suite TEXT, specimen TEXT, profile TEXT, seed INTEGER, class TEXT, race TEXT,
  harness_kind TEXT, outcome TEXT, cause TEXT, cap INTEGER, max_depth INTEGER,
  level INTEGER, final_turn INTEGER, config_sha256 TEXT, binary_sha256 TEXT,
  play_sha256 TEXT, wall_seconds REAL, record_sha256 TEXT NOT NULL REFERENCES blob,
  PRIMARY KEY(run_id, ordinal));
""")
t0 = time.perf_counter(); n = 0; raw = 0
for meta in sorted(glob.glob(os.path.join(root, '*/*/meta.json'))):
    d = os.path.dirname(meta); run_id = os.path.basename(d); exp = os.path.basename(os.path.dirname(d))
    mb = open(meta, 'rb').read()
    con.execute('INSERT INTO run VALUES(?,?,?)', (exp + '/' + run_id, exp, hashlib.sha256(mb).hexdigest()))
    rows, blobs = [], []
    with open(os.path.join(d, 'cells.jsonl'), 'rb') as f:
        for i, line in enumerate(f):
            line = line.rstrip(b'\n')
            if not line:
                continue
            raw += len(line); c = json.loads(line); fin = c.get('final') or {}
            h = hashlib.sha256(line).hexdigest()
            blobs.append((h, len(line), gzip.compress(line, 6)))
            rows.append((exp + '/' + run_id, i, c.get('suite'), c.get('specimen'), c.get('profile'), c.get('seed'),
                         c.get('played_class') or c.get('class'), c.get('played_race') or c.get('race'),
                         c.get('harness_kind'), c.get('outcome'), c.get('cause'), c.get('cap'),
                         fin.get('max_depth'), fin.get('level') or fin.get('max_level'), fin.get('turn'),
                         c.get('config_sha256'), c.get('binary_sha256'), c.get('play_sha256'),
                         c.get('wall_seconds'), h))
    con.executemany('INSERT OR IGNORE INTO blob VALUES(?,?,?)', blobs)
    con.executemany('INSERT INTO cell VALUES(' + ','.join('?' * 20) + ')', rows)
    n += len(rows)
con.commit(); load = time.perf_counter() - t0
t0 = time.perf_counter()
con.executescript("""
CREATE INDEX cell_arm ON cell(run_id, specimen, profile);
CREATE INDEX cell_seed ON cell(suite, seed, specimen, profile);
CREATE INDEX cell_cfg ON cell(config_sha256);
""")
con.commit(); idx = time.perf_counter() - t0

Q = {
 'per-arm outcome summary (all runs)': """SELECT run_id, specimen, profile, COUNT(*), SUM(outcome='death'),
     AVG(max_depth) FROM cell GROUP BY run_id, specimen, profile""",
 'per-class summary, one run': """SELECT class, COUNT(*), SUM(outcome='death') FROM cell
     WHERE run_id=(SELECT run_id FROM cell GROUP BY run_id ORDER BY COUNT(*) DESC LIMIT 1) GROUP BY class""",
 'paired rescued/newly-killed, one run, two arms': """WITH r AS (SELECT run_id FROM cell GROUP BY run_id
     HAVING COUNT(DISTINCT specimen||profile)>1 ORDER BY COUNT(*) DESC LIMIT 1),
     arms AS (SELECT DISTINCT specimen, profile FROM cell WHERE run_id=(SELECT run_id FROM r) LIMIT 2),
     a AS (SELECT * FROM arms LIMIT 1), b AS (SELECT * FROM arms LIMIT 1 OFFSET 1)
     SELECT SUM(x.outcome='death' AND y.outcome<>'death'), SUM(x.outcome<>'death' AND y.outcome='death'), COUNT(*)
     FROM cell x JOIN cell y ON x.run_id=y.run_id AND x.suite=y.suite AND x.seed=y.seed
     WHERE x.run_id=(SELECT run_id FROM r) AND x.specimen=(SELECT specimen FROM a) AND x.profile=(SELECT profile FROM a)
       AND y.specimen=(SELECT specimen FROM b) AND y.profile=(SELECT profile FROM b)
       AND x.harness_kind IS y.harness_kind
       AND x.outcome IN ('death','turn_cap','completion') AND y.outcome IN ('death','turn_cap','completion')""",
 'per-seed history across all runs': """SELECT run_id, specimen, profile, outcome, max_depth FROM cell
     WHERE suite='classes-1800' AND seed=(SELECT seed FROM cell WHERE suite='classes-1800' LIMIT 1)""",
 'runs sharing one exact configuration': """SELECT run_id, COUNT(*) FROM cell WHERE config_sha256=
     (SELECT config_sha256 FROM cell WHERE config_sha256 IS NOT NULL LIMIT 1 OFFSET 1000) GROUP BY run_id""",
 'fetch + inflate one full record': """SELECT gz FROM blob WHERE sha256=(SELECT record_sha256 FROM cell LIMIT 1 OFFSET 123456)""",
}
res = {}
for name, q in Q.items():
    t0 = time.perf_counter(); out = con.execute(q).fetchall()
    if name.startswith('fetch'):
        json.loads(gzip.decompress(out[0][0]))
    res[name] = {'ms': round((time.perf_counter() - t0) * 1000, 1), 'rows': len(out)}
con.close()
print(json.dumps({'cells': n, 'raw_record_bytes': raw, 'load_s': round(load, 1), 'index_s': round(idx, 1),
                  'db_bytes': os.path.getsize(db), 'queries': res}, indent=1))
