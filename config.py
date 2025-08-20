from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    MODE: str = os.getenv("MODE", "LIVE")  # "MOCK" or "LIVE"
    TIMEZONE: str = os.getenv("TIMEZONE", "America/Chicago")
    CUTOFF_HOUR: int = int(os.getenv("CUTOFF_HOUR", "3"))
    DB_PATH: str = os.getenv("DB_PATH", "habits.db")
    REQUEST_TIMEOUT_S: int = int(os.getenv("REQUEST_TIMEOUT_S", "10"))
    COUNT_MISSING_AS_MISS: bool = os.getenv("COUNT_MISSING_AS_MISS", "false").lower() == "true"

    TODOIST_TOKEN: str = os.getenv("TODOIST_TOKEN", "")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Next Actions")
    SECTION_NAME: str = os.getenv("SECTION_NAME", "Next Recurring Actions")

SETTINGS = Settings()
