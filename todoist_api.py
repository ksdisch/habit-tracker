from __future__ import annotations
import time, requests
from config import SETTINGS

API = "https://api.todoist.com"
SESSION = requests.Session()

def _headers() -> dict:
    if SETTINGS.MODE.upper() == "MOCK":
        raise RuntimeError("Todoist called in MOCK mode.")
    if not SETTINGS.TODOIST_TOKEN:
        raise ValueError("TODOIST_TOKEN missing.")
    return {"Authorization": f"Bearer {SETTINGS.TODOIST_TOKEN}"}

def _get(path: str, *, params: dict | None = None, max_retries: int = 3):
    url = f"{API}{path}"
    for attempt in range(max_retries):
        r = SESSION.get(url, headers=_headers(), params=params or {}, timeout=SETTINGS.REQUEST_TIMEOUT_S)
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep((2 ** attempt) * 0.5)
            continue
        r.raise_for_status()
        return r
    r.raise_for_status()  # type: ignore

def get_project_id(project_name: str) -> str:
    for p in _get("/rest/v2/projects").json():
        if p.get("name") == project_name:
            return str(p["id"])
    raise ValueError(f"Project {project_name!r} not found.")

def get_section_id(project_id: str, section_name: str) -> str:
    for s in _get("/rest/v2/sections", params={"project_id": project_id}).json():
        if s.get("name") == section_name:
            return str(s["id"])
    raise ValueError(f"Section {section_name!r} not in project {project_id}.")

def get_recurring_tasks(project_id: str, section_id: str) -> list[dict]:
    items = _get("/rest/v2/tasks", params={"project_id": project_id}).json()
    return [t for t in items if str(t.get("section_id")) == section_id and t.get("due", {}).get("is_recurring")]

def completed_on_date(task_id: str, day_bounds: tuple[str, str]) -> bool:
    after, before = day_bounds
    for since_key, until_key in (("after", "before"), ("since", "until")):
        params = {
            "event_type": "completed",
            "object_type": "item",
            "object_id": task_id,
            "limit": 100,
            since_key: after,
            until_key: before,
        }
        data = _get("/sync/v9/activity/get", params=params).json()
        if data.get("events") is not None:
            return len(data["events"]) > 0
    return False
