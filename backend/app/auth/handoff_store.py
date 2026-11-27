import sqlite3
import time
from pathlib import Path

from ..utils.crypto import encrypt_json, decrypt_json

SCHEMA = """
CREATE TABLE IF NOT EXISTS handoff (
    token TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    expires_at REAL NOT NULL
);
"""

#eminerva cookie store
class HandoffStore: 
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(SCHEMA)

    def _connect(self):
        return sqlite3.connect(self.db_path, timeout=10)

    def put(self, token: str, payload: dict, ttl: int):
        now = time.time()
        with self._connect() as conn:
            conn.execute("DELETE FROM handoff WHERE expires_at < ?", (now,))  # cleanup
            conn.execute(
                "INSERT INTO handoff (token, payload, expires_at) VALUES (?, ?, ?)",
                (token, encrypt_json(payload), now + ttl),
            )

    def claim(self, token: str) -> dict | None:
        """atomically fetch and delete. Returns None if missing, used, or expired."""
        with self._connect() as conn:
            row = conn.execute(
                "DELETE FROM handoff WHERE token = ? AND expires_at > ? RETURNING payload",
                (token, time.time()),
            ).fetchone()
        return decrypt_json(row[0]) if row else None