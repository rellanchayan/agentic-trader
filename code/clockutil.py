"""
clockutil.py — tiny time helpers, all in New York (Eastern) time.

The US stock market runs on New York time. Everything date/clock-related in this
project is anchored to "America/New_York" so daylight-saving time is handled for
us automatically (the zone switches between EST and EDT on its own).

Note: this module only does CLOCK MATH. The single source of truth for whether
the market is actually open (holidays, half-days) is Alpaca's own clock, fetched
via `alpaca_client.py --clock`.
"""

from __future__ import annotations

from __future__ import annotations

from datetime import datetime, time
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")

MARKET_OPEN = time(9, 30)    # 9:30 AM ET
MARKET_CLOSE = time(16, 0)   # 4:00 PM ET


def et_now() -> datetime:
    """Current time in New York."""
    return datetime.now(ET)


def et_today_str(now: datetime | None = None) -> str:
    """Today's date in New York as 'YYYY-MM-DD' — the key for the day folder."""
    return (now or et_now()).strftime("%Y-%m-%d")


def et_hhmm(now: datetime | None = None) -> str:
    """Current New York time as 'HH:MM' (24-hour)."""
    return (now or et_now()).strftime("%H:%M")


def hhmm_to_time(hhmm: str) -> time:
    """Parse 'HH:MM' into a time object."""
    h, m = hhmm.split(":")
    return time(int(h), int(m))


def is_after(hhmm: str, now: datetime | None = None) -> bool:
    """True if the current ET time is at or after the given 'HH:MM'."""
    n = (now or et_now()).timetz()
    t = hhmm_to_time(hhmm)
    return (n.hour, n.minute) >= (t.hour, t.minute)


def minutes_since_open(now: datetime | None = None) -> int:
    """How many minutes since 9:30 ET (negative before the open)."""
    n = now or et_now()
    return (n.hour * 60 + n.minute) - (MARKET_OPEN.hour * 60 + MARKET_OPEN.minute)


def within_regular_session(now: datetime | None = None) -> bool:
    """Clock-only check that we're inside 9:30–16:00 ET (NOT a holiday check)."""
    n = (now or et_now()).time()
    return MARKET_OPEN <= n <= MARKET_CLOSE
