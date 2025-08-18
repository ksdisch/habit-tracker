
# Don't Miss Two Days — Habit Tracker (Testing)

# This lets you **simulate** or **actually test** the core logic for the "Don't Miss Two Days in a Row" habit tracker that reads your **Todoist** recurring tasks and produces a **morning report** of habits you **missed yesterday**, plus an optional **in-danger** flag if you missed something two days in a row.

# **You can run this in two modes:**
# - **MOCK mode (default):** No API tokens needed. We generate fake habits and completions so you can see the whole flow working end-to-end.
# - **LIVE mode:** Provide your `TODOIST_TOKEN` and point to your `Next Actions` → `Next Recurring Actions` section. The notebook will pull your real tasks, log today's completions, and generate a real morning report.

## 1) Setup

from dotenv import load_dotenv
load_dotenv()  # loads variables from .env into os.environ

import os
import sqlite3
import json
import requests
import datetime as dt
from zoneinfo import ZoneInfo  # Available in Python 3.9+ (Colab is OK)
from getpass import getpass

print("✅ Imports ready")


## 2) Configuration

# - Set `USE_MOCK = True` to simulate habits and completions with fake data.
# - Set `USE_MOCK = False` for **LIVE** Todoist mode and provide your token + names.

# **Important:** In LIVE mode we only **read** completions via the Activity Log. We don't modify your tasks.


# ---- Core switches ----
USE_MOCK = True  # ← switch to False to hit Todoist for real

# ---- Timezone ----
TIMEZONE = "America/Chicago"  # change if needed
TZ = ZoneInfo(TIMEZONE)

# ---- Todoist (LIVE mode only) ----
# If you flip USE_MOCK=False, either paste your token here OR leave empty
# and you'll be prompted securely.
TODOIST_TOKEN = os.environ.get("TODOIST_TOKEN", "").strip()

PROJECT_NAME = "Next Actions"
SECTION_NAME = "Next Recurring Actions"

# ---- Database file (local to Colab runtime) ----
DB_PATH = "habits_test.db"

print(f"USE_MOCK = {USE_MOCK}")
print(f"DB_PATH  = {DB_PATH}")

## 3) Database helpers

def get_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("CREATE TABLE IF NOT EXISTS habits (task_id TEXT PRIMARY KEY, name TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS logs (log_date TEXT, task_id TEXT, completed INTEGER, PRIMARY KEY (log_date, task_id))")
    return con

def reset_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🗑️ Removed existing DB to start fresh.")
    else:
        print("ℹ️ No DB found; starting fresh.")

print("✅ DB helpers defined")

## 4) Todoist + logic helpers

API = "https://api.todoist.com"

def get_headers():
    global TODOIST_TOKEN
    if not TODOIST_TOKEN:
        TODOIST_TOKEN = getpass("Enter TODOIST_TOKEN (input hidden): ").strip()
    return {"Authorization": f"Bearer {TODOIST_TOKEN}"}

def get_project_id(project_name):
    r = requests.get(f"{API}/rest/v2/projects", headers=get_headers())
    r.raise_for_status()
    for p in r.json():
        if p["name"] == project_name:
            print(f"📁 Found project '{project_name}' → {p['id']}")
            return p["id"]
    raise ValueError(f"Project '{project_name}' not found.")

def get_section_id(project_id, section_name):
    r = requests.get(f"{API}/rest/v2/sections", params={"project_id": project_id}, headers=get_headers())
    r.raise_for_status()
    for s in r.json():
        if s["name"] == section_name:
            print(f"📑 Found section '{section_name}' → {s['id']}")
            return s["id"]
    raise ValueError(f"Section '{section_name}' not found in project {project_id}.")

def get_recurring_tasks(project_id, section_id):
    r = requests.get(f"{API}/rest/v2/tasks", params={"project_id": project_id}, headers=get_headers())
    r.raise_for_status()
    items = [t for t in r.json() if t.get("section_id")==section_id and t.get("due",{}).get("is_recurring")]
    print(f"🧾 Recurring tasks in section: {len(items)} found")
    return items

def completed_on_date(task_id, date_obj):
    # Query Todoist Activity Log for completed events between local day's bounds
    start = dt.datetime.combine(date_obj, dt.time(0,0), tzinfo=TZ).isoformat()
    end   = dt.datetime.combine(date_obj, dt.time(23,59,59), tzinfo=TZ).isoformat()

    params = {
        "event_type": "completed",
        "object_type": "item",
        "object_id": task_id,
        "limit": 100,
        "since": start,
        "until": end
    }
    r = requests.get(f"{API}/sync/v9/activity/get", params=params, headers=get_headers())
    r.raise_for_status()
    events = r.json().get("events", [])
    return len(events) > 0

def upsert_habit(con, task_id, name):
    con.execute("INSERT OR REPLACE INTO habits(task_id, name) VALUES(?,?)", (task_id, name))

def write_log(con, date_obj, task_id, completed_bool):
    con.execute("INSERT OR REPLACE INTO logs(log_date, task_id, completed) VALUES(?,?,?)",
                (date_obj.isoformat(), task_id, 1 if completed_bool else 0))

print("✅ API + logic helpers ready")

## 5) Nightly job
# Logs whether each habit was completed **today**.

def nightly_run_live():
    print("🌙 Nightly (LIVE) starting...")
    con = get_db()
    today = dt.date.today()

    pid = get_project_id(PROJECT_NAME)
    sid = get_section_id(pid, SECTION_NAME)
    tasks = get_recurring_tasks(pid, sid)

    for t in tasks:
        task_id = t["id"]
        name = t["content"]
        upsert_habit(con, task_id, name)
        did = completed_on_date(task_id, today)
        print(f"   • {name:30}  completed_today={did}")
        write_log(con, today, task_id, did)

    con.commit()
    con.close()
    print("✅ Nightly (LIVE) finished. Data written to DB.")

def nightly_run_mock():
    print("🌙 Nightly (MOCK) starting...")
    con = get_db()
    today = dt.date.today()

    # Pretend these are your three habits
    fake = [
        ("123", "Meditate"),
        ("456", "Read 15 minutes"),
        ("789", "Workout"),
    ]

    # Deterministic pattern so output is easy to follow
    for i, (task_id, name) in enumerate(fake):
        upsert_habit(con, task_id, name)
        did = (today.day % (i+2) == 0)  # simple pattern; change if you like
        print(f"   • {name:30}  completed_today={did}")
        write_log(con, today, task_id, did)

    con.commit()
    con.close()
    print("✅ Nightly (MOCK) finished. Data written to DB.")

if USE_MOCK:
    nightly_run_mock()
else:
    nightly_run_live()

## 6) Morning report
# Finds what you **missed yesterday**, and flags items missed **two days straight**.

def two_day_flag(con, task_id, yday):
    d1 = con.execute("SELECT completed FROM logs WHERE log_date=? AND task_id=?", (yday.isoformat(), task_id)).fetchone()
    d2 = con.execute("SELECT completed FROM logs WHERE log_date=? AND task_id=?", ((yday - dt.timedelta(days=1)).isoformat(), task_id)).fetchone()
    return (d1 and d1[0]==0) and (d2 and d2[0]==0)

def morning_report():
    print("🌅 Morning report starting...")
    con = get_db()
    yday = dt.date.today() - dt.timedelta(days=1)

    query = (
        "SELECT l.task_id, h.name, l.completed "
        "FROM logs l JOIN habits h ON h.task_id = l.task_id "
        "WHERE l.log_date = ? ORDER BY h.name"
    )
    rows = con.execute(query, (yday.isoformat(),)).fetchall()

    if not rows:
        print("No data for yesterday yet. Run the nightly step first (or simulate).")
        con.close()
        return

    missed = [(tid, name) for (tid, name, completed) in rows if completed == 0]
    if not missed:
        print("✅ No missed habits yesterday. Great job!")
        con.close()
        return

    print("\nYesterday’s Missed Habits:")
    for tid, name in missed:
        print(f"— {name}")

    danger = [name for (tid, name) in missed if two_day_flag(con, tid, yday)]
    if danger:
        print("\n⚠ In danger (missed 2 days straight):")
        for name in danger:
            print(f"— {name}")

    con.close()
    print("\n✅ Morning report generated. (In a real deployment, this would be emailed or pushed.)")

morning_report()

## 7) Inspect the database
# Peek at what was written.
# %pip install pandas

import pandas as pd

def show_tables():
    con = get_db()
    habits = pd.read_sql_query("SELECT * FROM habits ORDER BY name", con)
    logs = pd.read_sql_query("SELECT * FROM logs ORDER BY log_date DESC, task_id", con)
    con.close()

    print("\n=== habits ===")
    print(habits)
    print("\n=== logs ===")
    print(logs)

show_tables()


## 8) (Optional) Simulate multiple days (MOCK)

# Run this to create data for the **past N days** so you can test the **two-days-in-a-row** warning easily.


def simulate_past_days_mock(days=5):
    if not USE_MOCK:
        print("This simulator only works in MOCK mode.")
        return
    print(f"🧪 Simulating the last {days} days...")
    reset_db()
    con = get_db()

    fake = [
        ("123", "Meditate"),
        ("456", "Read 15 minutes"),
        ("789", "Workout"),
    ]
    for task_id, name in fake:
        con.execute("INSERT OR REPLACE INTO habits(task_id,name) VALUES(?,?)", (task_id, name))

    start = dt.date.today() - dt.timedelta(days=days-1)
    for d in (start + dt.timedelta(days=i) for i in range(days)):
        for i, (task_id, name) in enumerate(fake):
            # Pattern: miss alternatingly so we can see warnings
            did = not ((d.day + i) % 2 == 0)
            write_log(con, d, task_id, did)

    con.commit(); con.close()
    print("✅ Simulation done. Now re-run the Morning Report cell to see output.")

# Example: uncomment to simulate then run morning_report()
simulate_past_days_mock(days=7)

## 9) Reset database (danger)

# Run this if you want to start clean.
# reset_db()
print("Ready. (Uncomment reset_db() above if you want to wipe the DB.)")
# This is a test file for habit tracker logic, not meant to be run directly.