"""Single-owner SQLite queue. Atomic claim; one rendering worker per data directory."""

import json, sqlite3, time, uuid
from contextlib import contextmanager
from .settings import DATA


@contextmanager
def connect():
    DATA.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DATA / "scholarshorts.sqlite", timeout=30)
    c.row_factory = sqlite3.Row
    try:
        c.execute("PRAGMA journal_mode=WAL")
        c.executescript("""CREATE TABLE IF NOT EXISTS jobs (
          id TEXT PRIMARY KEY, paper_id TEXT NOT NULL, preset TEXT NOT NULL,
          status TEXT NOT NULL, stage TEXT, progress REAL DEFAULT 0,
          error TEXT, usage TEXT DEFAULT '[]', cancel_requested INTEGER DEFAULT 0,
          created_at REAL NOT NULL, updated_at REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS presets (id TEXT PRIMARY KEY, document TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS shorts (id TEXT PRIMARY KEY, document TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS flags (id TEXT PRIMARY KEY, document TEXT NOT NULL);""")
        yield c
        c.commit()
    except BaseException:
        c.rollback()
        raise
    finally:
        c.close()


def decode(row):
    if row is None:
        return None
    d = dict(row)
    d["preset"] = json.loads(d["preset"])
    d["usage"] = json.loads(d["usage"])
    return d


def create(paper_id, preset):
    jid = uuid.uuid4().hex
    now = time.time()
    with connect() as c:
        c.execute(
            "INSERT INTO jobs(id,paper_id,preset,status,created_at,updated_at) VALUES(?,?,?,?,?,?)",
            (jid, paper_id, json.dumps(preset), "queued", now, now),
        )
    return get(jid)


def get(jid):
    with connect() as c:
        return decode(c.execute("SELECT * FROM jobs WHERE id=?", (jid,)).fetchone())


def all_jobs():
    with connect() as c:
        return [
            decode(r)
            for r in c.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT 100")
        ]


def update(jid, **fields):
    allowed = {"status", "stage", "progress", "error", "usage", "cancel_requested"}
    if not set(fields) <= allowed:
        raise ValueError("Invalid update")
    if "usage" in fields:
        fields["usage"] = json.dumps(fields["usage"])
    fields["updated_at"] = time.time()
    with connect() as c:
        c.execute(
            f"UPDATE jobs SET {','.join(k + '=?' for k in fields)} WHERE id=?",
            [*fields.values(), jid],
        )


def claim():
    with connect() as c:
        c.execute("BEGIN IMMEDIATE")
        r = c.execute(
            "SELECT * FROM jobs WHERE status='queued' AND cancel_requested=0 ORDER BY created_at LIMIT 1"
        ).fetchone()
        if r:
            c.execute(
                "UPDATE jobs SET status='running',updated_at=? WHERE id=?",
                (time.time(), r["id"]),
            )
        return decode(r)


def store(table, id, doc):
    assert table in ("presets", "shorts", "flags")
    with connect() as c:
        c.execute(
            f"INSERT OR REPLACE INTO {table}(id,document) VALUES(?,?)",
            (id, json.dumps(doc)),
        )


def documents(table):
    assert table in ("presets", "shorts", "flags")
    with connect() as c:
        return [json.loads(r[0]) for r in c.execute(f"SELECT document FROM {table}")]
