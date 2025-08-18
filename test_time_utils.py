import datetime as dt
from time_utils import day_bounds_iso

def test_day_bounds_iso_format():
    s, e = day_bounds_iso(dt.date(2025, 1, 2))
    assert "2025-01-02" in s and "T00:00:00" in s
    assert "2025-01-02" in e and "T23:59:59" in e
