from __future__ import annotations
import sqlite3
from contextlib import contextmanager
from config import SETTINGS

@contextmanager
def connect():
    con = sqlite3.connect(SETTINGS.DB_PATH)
    try:
        con.execute("PRAGMA foreign_keys=ON;")
        con.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                task_id TEXT PRIMARY KEY,
                name    TEXT NOT NULL
            );
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                log_date  TEXT NOT NULL,
                task_id   TEXT NOT NULL,
                completed INTEGER NOT NULL,
                PRIMARY KEY (log_date, task_id),
                FOREIGN KEY (task_id) REFERENCES habits(task_id)
            );
        """)
        con.execute("CREATE INDEX IF NOT EXISTS idx_logs_date ON logs(log_date);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_logs_task ON logs(task_id);")
        yield con
        con.commit()
    finally:
        con.close()

def upsert_habit(con, task_id: str, name: str) -> None:
    con.execute("INSERT OR REPLACE INTO habits(task_id, name) VALUES(?,?)", (task_id, name))

def write_log(con, log_date: str, task_id: str, completed: bool) -> None:
    con.execute("INSERT OR REPLACE INTO logs(log_date, task_id, completed) VALUES(?,?,?)",
                (log_date, task_id, 1 if completed else 0))
