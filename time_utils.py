from __future__ import annotations
import datetime as dt
from zoneinfo import ZoneInfo
from config import SETTINGS

TZ = ZoneInfo(SETTINGS.TIMEZONE)

def local_now() -> dt.datetime:
    return dt.datetime.now(TZ)

def ledger_date_with_cutoff() -> dt.date:
    now = local_now()
    return (now - dt.timedelta(days=1)).date() if now.hour < SETTINGS.CUTOFF_HOUR else now.date()

def day_bounds_iso(day: dt.date) -> tuple[str, str]:
    start = dt.datetime.combine(day, dt.time(0, 0), tzinfo=TZ).isoformat()
    end   = dt.datetime.combine(day, dt.time(23, 59, 59), tzinfo=TZ).isoformat()
    return start, end
