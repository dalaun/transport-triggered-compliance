"""
challenge_store.py — SQLite persistence for Canon Challenges
A challenge is a merit-based attack on a frozen canon invariant.
Valid grounds: new evidence, scope misapplication, oracle error.
Invalid grounds: positional arguments, re-litigation of same evidence.
"""

import sqlite3, json, time, os, re

DB_PATH = os.path.join(os.path.dirname(__file__), "challenges.db")

# Words that signal positional argument (invalid grounds)
POSITIONAL_SIGNALS = [
    "i didn't intend", "i submitted", "my position", "i meant",
    "i said", "that was my claim", "i didn't mean", "i was trying to",
    "i never said", "my argument was", "i believe i", "i thought i",
    "on behalf of", "i am the", "representing",
    "as the maker", "as the seller", "as the buyer", "as the owner",
    "my intention was", "i never meant"
]

def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS challenges (
                id                  TEXT PRIMARY KEY,
                created             REAL NOT NULL,
                challenger_id       TEXT NOT NULL,
                canon_hash          TEXT NOT NULL,
                canon_domain        TEXT DEFAULT '',
                grounds             TEXT NOT NULL,
                new_evidence        TEXT DEFAULT '',
                scope_argument      TEXT DEFAULT '',
                challenger_claims   TEXT DEFAULT '[]',
                status              TEXT DEFAULT 'pending',
                validity            TEXT DEFAULT NULL,
                validity_reason     TEXT DEFAULT NULL,
                result_canon_hash   TEXT DEFAULT NULL,
                result_canon_status TEXT DEFAULT NULL,
                outcome             TEXT DEFAULT NULL
            )
        """)
        conn.commit()

def validate_grounds(grounds, challenger_claims):
    """
    Returns (valid: bool, reason: str)
    Blocks positional arguments before CMP runs.
    """
    combined = (grounds + " " + " ".join(challenger_claims)).lower()
    for signal in POSITIONAL_SIGNALS:
        if signal in combined:
            return False, (
                f"Challenge blocked: positional argument detected ('{signal}'). "
                "Positional Independence requires challenges engage the invariant "
                "on its merits only. You cannot argue intent, authorship, or "
                "what you meant when you submitted a claim."
            )
    if len(grounds.strip()) < 30:
        return False, "Challenge blocked: grounds too thin. State specific new evidence or scope argument."
    return True, "Grounds accepted for CMP."

def put(challenge_id, challenge):
    with _conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO challenges
            (id, created, challenger_id, canon_hash, canon_domain,
             grounds, new_evidence, scope_argument, challenger_claims,
             status, validity, validity_reason,
             result_canon_hash, result_canon_status, outcome)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            challenge_id,
            challenge.get("created", time.time()),
            challenge.get("challenger_id", ""),
            challenge.get("canon_hash", ""),
            challenge.get("canon_domain", ""),
            challenge.get("grounds", ""),
            challenge.get("new_evidence", ""),
            challenge.get("scope_argument", ""),
            json.dumps(challenge.get("challenger_claims", [])),
            challenge.get("status", "pending"),
            challenge.get("validity"),
            challenge.get("validity_reason"),
            challenge.get("result_canon_hash"),
            challenge.get("result_canon_status"),
            challenge.get("outcome")
        ))
        conn.commit()

def get(challenge_id):
    with _conn() as conn:
        row = conn.execute(
            "SELECT * FROM challenges WHERE id=?", (challenge_id,)
        ).fetchone()
    return _row_to_dict(row) if row else None

def list_all():
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM challenges ORDER BY created DESC"
        ).fetchall()
    return [_row_to_dict(r) for r in rows]

def _row_to_dict(row):
    d = dict(row)
    d["challenger_claims"] = json.loads(d.get("challenger_claims") or "[]")
    return d

init_db()
