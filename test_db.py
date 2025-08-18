import os
from config import SETTINGS
from db import connect

def test_db_schema_exists(tmp_path, monkeypatch):
    db = tmp_path / "t.db"
    monkeypatch.setenv("DB_PATH", str(db))
    from importlib import reload
    import config as cfg
    reload(cfg)
    with connect() as con:
        cur = con.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {r[0] for r in cur.fetchall()}
        assert {"habits", "logs"}.issubset(tables)
