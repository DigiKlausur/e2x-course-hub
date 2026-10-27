from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from e2x_course_hub.schema.course import StudentAccessPeriod

NOW = datetime(2026, 11, 2, 9, 0, tzinfo=timezone.utc)
HOUR = timedelta(hours=1)


def test_no_bounds_is_always_open():
    assert StudentAccessPeriod().is_student_access_open(NOW)


@pytest.mark.parametrize(
    ("start", "end", "is_open"),
    [
        (NOW - HOUR, None, True),
        (NOW + HOUR, None, False),
        (None, NOW + HOUR, True),
        (None, NOW - HOUR, False),
        (NOW - HOUR, NOW + HOUR, True),
        # The start is inclusive, the end exclusive.
        (NOW, None, True),
        (None, NOW, False),
    ],
)
def test_is_student_access_open(start, end, is_open):
    period = StudentAccessPeriod(student_access_start=start, student_access_end=end)
    assert period.is_student_access_open(NOW) is is_open


@pytest.mark.parametrize("end", [NOW, NOW - HOUR])
def test_end_must_be_after_start(end):
    with pytest.raises(ValidationError, match="must be after"):
        StudentAccessPeriod(student_access_start=NOW, student_access_end=end)


def test_naive_datetimes_are_rejected():
    with pytest.raises(ValidationError):
        StudentAccessPeriod(student_access_start=datetime(2026, 11, 2, 9, 0))
