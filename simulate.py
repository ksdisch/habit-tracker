from __future__ import annotations
import datetime as dt
from db import connect, upsert_habit, write_log

def simulate_past_days(days: int = 7) -> None:
    fake = [("123", "Meditate"), ("456", "Read 15 minutes"), ("789", "Workout")]
    start = dt.date.today() - dt.timedelta(days=days - 1)
    with connect() as con:
        for task_id, name in fake:
            upsert_habit(con, task_id, name)
        for i in range(days):
            d = start + dt.timedelta(days=i)
            for j, (task_id, _) in enumerate(fake):
                did = not ((d.day + j) % 2 == 0)
                write_log(con, d.isoformat(), task_id, did)

