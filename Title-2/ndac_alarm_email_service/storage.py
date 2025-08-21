import hashlib
import json
import sqlite3
from datetime import datetime
from typing import Dict, Any

class Storage:
    def __init__(self, db_path: str, logger):
        self.db_path = db_path
        self.log = logger
        self._ensure()

    def _ensure(self):
        with sqlite3.connect(self.db_path) as con:
            con.execute("""
            CREATE TABLE IF NOT EXISTS sent_alerts (
                digest TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                sent_at TEXT NOT NULL
            )
            """)
            con.commit()

    def compute_digest(self, alarm: Dict[str, Any]) -> str:
        # Stable digest across runs
        payload = json.dumps(alarm, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def already_sent(self, digest: str) -> bool:
        with sqlite3.connect(self.db_path) as con:
            cur = con.execute("SELECT 1 FROM sent_alerts WHERE digest=?", (digest,))
            return cur.fetchone() is not None

    def mark_sent(self, digest: str, alarm: Dict[str, Any]):
        with sqlite3.connect(self.db_path) as con:
            con.execute("INSERT OR REPLACE INTO sent_alerts(digest, payload, sent_at) VALUES (?, ?, ?)",
                        (digest, json.dumps(alarm, ensure_ascii=False), datetime.utcnow().isoformat()))
            con.commit()
