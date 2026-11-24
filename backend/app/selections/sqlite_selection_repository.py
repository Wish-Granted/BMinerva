import sqlite3
from pathlib import Path

from .selection_repository import SelectionRepository

SCHEMA = """
CREATE TABLE IF NOT EXISTS user_selections (
    username   TEXT NOT NULL,
    student_id TEXT NOT NULL,
    called     INTEGER NOT NULL DEFAULT 0,
    added_at   TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (username, student_id)
);
CREATE TABLE IF NOT EXISTS user_prefs (
    username TEXT PRIMARY KEY,
    sort_key TEXT, sort_dir INTEGER
);
"""

class SQLiteSelectionRepository(SelectionRepository):
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def get_selection(self, username: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT student_id, called, added_at FROM user_selections "
                "WHERE username = ? ORDER BY added_at, rowid",
                (username,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_sort(self, username: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT sort_key, sort_dir FROM user_prefs WHERE username = ?",
                (username,),
            ).fetchone()
        if not row or not row["sort_key"]:
            return None
        return {"key": row["sort_key"], "dir": row["sort_dir"]}

    def replace_selection(self, username: str, student_ids: list[str], called_ids: set[str], sort: dict | None) -> None:
        with self._connect() as conn:  # commits on success, rolls back on error
            existing = {
                r["student_id"]: r["added_at"]
                for r in conn.execute(
                    "SELECT student_id, added_at FROM user_selections WHERE username = ?", (username,),
                )
            }
            conn.execute("DELETE FROM user_selections WHERE username = ?", (username,))
            for sid in student_ids:
                added_at = existing.get(sid)
                if added_at:
                    conn.execute(
                        "INSERT INTO user_selections (username, student_id, called, added_at) VALUES (?,?,?,?)",
                        (username, sid, int(sid in called_ids), added_at),
                    )
                else:
                    conn.execute(
                        "INSERT INTO user_selections (username, student_id, called) VALUES (?,?,?)",
                        (username, sid, int(sid in called_ids)),
                    )
            if sort:
                conn.execute(
                    "INSERT INTO user_prefs (username, sort_key, sort_dir) VALUES (?,?,?) "
                    "ON CONFLICT(username) DO UPDATE SET sort_key=excluded.sort_key, sort_dir=excluded.sort_dir",
                    (username, sort["key"], sort["dir"]),
                )