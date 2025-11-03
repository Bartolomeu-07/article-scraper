import pytest
from datetime import datetime
from zoneinfo import ZoneInfo
from freezegun import freeze_time

from app.utils.date_utils import parse_any_date, WARSAW


@pytest.mark.parametrize(
    "frozen_iso, raw, expected",
    [
        (
            "2024-11-05 15:45:10+01:00",
            "yesterday",
            datetime(2024, 11, 4, 0, 0, 0, tzinfo=WARSAW),
        ),
        (
            "2024-11-05 15:45:10+01:00",
            "2 days ago",
            datetime(2024, 11, 3, 15, 45, 10, tzinfo=WARSAW),
        ),
        (
            "2024-11-05 15:45:10+01:00",
            "14.10.2024",
            datetime(2024, 10, 14, 0, 0, 0, tzinfo=WARSAW),
        ),
        (
            "2024-11-05 15:45:10+01:00",
            "October 14, 2024",
            datetime(2024, 10, 14, 0, 0, 0, tzinfo=WARSAW),
        ),
        (
            "2024-11-05 15:45:10+01:00",
            "14.10.2024 10:11",
            datetime(2024, 10, 14, 10, 11, 0, tzinfo=WARSAW),
        ),
        (
            "2024-11-05 15:45:10+01:00",
            "10:11",
            datetime(2024, 11, 5, 10, 11, 0, tzinfo=WARSAW),
        ),
        (None, None, None),
    ],
    ids=[
        "yesterday=>midnight",
        "two-days-ago=>keep-time",
        "date-dmy=>midnight",
        "date-long-en=>midnight",
        "date-time=>keep-time",
        "time-only=>today",
        "none=>none",
    ],
)
def test_parse_any_date_parametrized(frozen_iso, raw, expected):
    if frozen_iso:
        with freeze_time(frozen_iso):
            got = parse_any_date(raw)
    else:
        got = parse_any_date(raw)

    if expected is None:
        assert got is None
        return

    assert got == expected
    assert got.tzinfo is not None
    assert isinstance(got.tzinfo, ZoneInfo)
    assert got.tzinfo.key == "Europe/Warsaw"
