from __future__ import annotations
import datetime as dt
from config import SETTINGS
from time_utils import ledger_date_with_cutoff, day_bounds_iso
from db import connect, upsert_habit, write_log
from todoist_api import get_project_id, get_section_id, get_recurring_tasks, completed_on_date

def nightly_live() -> None:
    day = ledger_date_with_cutoff()
    with connect() as con:
        pid = get_project_id(SETTINGS.PROJECT_NAME)
        sid = get_section_id(pid, SETTINGS.SECTION_NAME)
        tasks = get_recurring_tasks(pid, sid)
        for t in tasks:
            task_id, name = str(t["id"]), t["content"]
            upsert_habit(con, task_id, name)
            did = completed_on_date(task_id, day_bounds_iso(day))
            write_log(con, day.isoformat(), task_id, did)

def nightly_mock() -> None:
    day = ledger_date_with_cutoff()
    fake = [("123", "Meditate"), ("456", "Read 15 minutes"), ("789", "Workout")]
    with connect() as con:
        for i, (task_id, name) in enumerate(fake):
            upsert_habit(con, task_id, name)
            did = (day.day % (i + 2) == 0)
            write_log(con, day.isoformat(), task_id, did)

def two_day_flag(con, task_id: str, yday: dt.date) -> bool:
    d1 = con.execute("SELECT completed FROM logs WHERE log_date=? AND task_id=?", (yday.isoformat(), task_id)).fetchone()
    d0 = con.execute("SELECT completed FROM logs WHERE log_date=? AND task_id=?", ((yday - dt.timedelta(days=1)).isoformat(), task_id)).fetchone()

    def missed(row):
        if row is None:
            return 1 if SETTINGS.COUNT_MISSING_AS_MISS else None
        return 1 - int(row[0])

    m1, m0 = missed(d1), missed(d0)
    return (m1 == 1) and (m0 == 1)

def morning_report() -> str:
    yday = ledger_date_with_cutoff() - dt.timedelta(days=1)
    lines = [f"Morning report for {yday}"]
    with connect() as con:
        rows = con.execute("""
            SELECT l.task_id, h.name, l.completed
            FROM logs l JOIN habits h ON h.task_id = l.task_id
            WHERE l.log_date = ?
            ORDER BY h.name
        """, (yday.isoformat(),)).fetchall()
        if not rows:
            return f"No data for {yday}. Run nightly first."
        missed = [(tid, name) for (tid, name, done) in rows if done == 0]
        if not missed:
            return "✅ No missed habits yesterday."
        lines.append("\nYesterday’s Missed Habits:")
        for tid, name in missed:
            lines.append(f"— {name}")
        danger = [name for (tid, name) in missed if two_day_flag(con, tid, yday)]
        if danger:
            lines.append("\n⚠ In danger (missed 2 days straight):")
            lines.extend([f"— {n}" for n in danger])
    return "\n".join(lines)
