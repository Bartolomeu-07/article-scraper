from __future__ import annotations
import re
from datetime import datetime, time
from typing import Optional
import dateparser
from zoneinfo import ZoneInfo


WARSAW = ZoneInfo("Europe/Warsaw")

OUTPUT_FMT = "%d.%m.%Y %H:%M:%S"

# Pattern for detecting an explicit time in the raw input string
_TIME_PATTERN = re.compile(
    r"(\b\d{1,2}:\d{2}(?::\d{2})?\b)|(\b\d{1,2}\s?(am|pm)\b)",
    re.IGNORECASE
)


def parse_any_date(raw: str | None, default_tz=WARSAW)-> Optional[datetime]:
    """
    Accepts any date/time string (e.g. "2 days ago", "2024-10-14",
    "October 14, 2024") and returns a timezone-aware datetime object.
    If no time is provided in the input, sets the time to 00:00:00
    in the given timezone.
    """

    if not raw:
        return None

    settings = {
    "TIMEZONE": str(default_tz),
    "RETURN_AS_TIMEZONE_AWARE": True,
    "PREFER_DATES_FROM": "past",
    "DATE_ORDER": "DMY",
    }

    dt = dateparser.parse(raw, settings=settings)

    # If there's no date component - return None
    if dt is None:
        return None

    # If no time component is present, set the time to 00:00:00
    if dt.hour == 0 and dt.minute == 0 and dt.second == 0:

        # Check whether the time was explicitly provided in the source text — this prevents dateparser
        # from assigning a time when the input uses relative expressions like "yesterday" or "3 days ago"
        if not _TIME_PATTERN.search(raw):
            dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)

    return dt.astimezone(WARSAW)