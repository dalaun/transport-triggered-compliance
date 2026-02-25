"""
dispute_store.py — SQLite-backed A2A dispute persistence
Replaces in-memory _disputes dict. Survives restarts.
"""
import sqlite3, json, time, os

DB_PATH = os.path.join(os.path.dirname(__file__), "disputes.db")

def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS disputes (
                id              TEXT PRIMARY KEY,
                created         REAL NOT NULL,
                domain          TEXT NOT NULL,
                scope_boundary  TEXT DEFAULT '',
                fiduciary_moment TEXT DEFAULT '',
                evidence_standard TEXT DEFAULT '',
                metadata        TEXT DEFAULT '{}',
                positions       TEXT DEFAULT '[]',
                status          TEXT DEFAULT 'open',
                result          TEXT DEFAULT NULL
            )
        """)
        conn.commit()

def put(dispute_id, dispute):
    with _conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO disputes
            (id, created, domain, scope_boundary, fiduciary_moment,
             evidence_standard, metadata, positions, status, result)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            dispute_id,
            dispute.get("created", time.time()),
            dispute.get("domain", ""),
            dispute.get("scope_boundary", ""),
            dispute.get("fiduciary_moment", ""),
            dispute.get("evidence_standard", ""),
            json.dumps(dispute.get("metadata", {})),
            json.dumps(dispute.get("positions", [])),
            dispute.get("status", "open"),
            json.dumps(dispute["result"]) if dispute.get("result") else None
        ))
        conn.commit()

def get(dispute_id):
    with _conn() as conn:
        row = conn.execute("SELECT * FROM disputes WHERE id=?", (dispute_id,)).fetchone()
    if not row:
        return None
    return _row_to_dict(row)

def list_open():
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM disputes WHERE status='open' ORDER BY created DESC"
        ).fetchall()
    return [_row_to_dict(r) for r in rows]

def prune(ttl=3600):
    cutoff = time.time() - ttl
    with _conn() as conn:
        conn.execute("DELETE FROM disputes WHERE created < ?", (cutoff,))
        conn.commit()

def _row_to_dict(row):
    d = dict(row)
    d["metadata"]  = json.loads(d["metadata"] or "{}")
    d["positions"] = json.loads(d["positions"] or "[]")
    d["result"]    = json.loads(d["result"]) if d.get("result") else None
    return d

# Initialize on import
init_db()
