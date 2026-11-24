"""SQLite storage for sessions, drafted actions (approvals + undo log) and watches."""
import json
import sqlite3
import os

DB = os.getenv("COUNCIL_DB", "council.db")


def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.executescript("""
    CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY, question TEXT, result TEXT);
    CREATE TABLE IF NOT EXISTS actions (id INTEGER PRIMARY KEY, session_id INT, draft TEXT, status TEXT DEFAULT 'pending');
    CREATE TABLE IF NOT EXISTS watches (id INTEGER PRIMARY KEY, session_id INT, question TEXT, phone TEXT, active INT DEFAULT 1);
    """)
    return con


def save_session(result: dict) -> int:
    con = db()
    sid = con.execute("INSERT INTO sessions (question, result) VALUES (?, ?)",
                      (result["question"], json.dumps(result))).lastrowid
    for d in result["drafts"]:
        con.execute("INSERT INTO actions (session_id, draft) VALUES (?, ?)", (sid, json.dumps(d)))
    con.commit()
    return sid


def list_actions(session_id: int) -> list[dict]:
    rows = db().execute("SELECT * FROM actions WHERE session_id=?", (session_id,)).fetchall()
    return [{"id": r["id"], "status": r["status"], **json.loads(r["draft"])} for r in rows]


def set_action(action_id: int, status: str) -> dict:
    con = db()
    con.execute("UPDATE actions SET status=? WHERE id=?", (status, action_id))
    con.commit()
    r = con.execute("SELECT * FROM actions WHERE id=?", (action_id,)).fetchone()
    return {"id": r["id"], "status": r["status"], **json.loads(r["draft"])}


def add_watch(session_id: int, question: str, phone: str | None) -> int:
    con = db()
    wid = con.execute("INSERT INTO watches (session_id, question, phone) VALUES (?, ?, ?)",
                      (session_id, question, phone)).lastrowid
    con.commit()
    return wid


def active_watches() -> list[dict]:
    return [dict(r) for r in db().execute("SELECT * FROM watches WHERE active=1").fetchall()]


def close_watch(watch_id: int):
    con = db()
    con.execute("UPDATE watches SET active=0 WHERE id=?", (watch_id,))
    con.commit()
