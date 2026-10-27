from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from conftest import make_course, make_term

from e2x_course_hub.api.spawn_offering_api import SpawnOfferingAPI
from e2x_course_hub.schema.types import SpawnRole

NOW = datetime.now(timezone.utc)
DAY = timedelta(days=1)


def _user(role: str):
    return SimpleNamespace(username=role, groups=[f"lms.course.c1.term.t1.{role}"])


def _offered_roles(repository, user) -> list[SpawnRole]:
    offerings = SpawnOfferingAPI(repository).get_spawn_offerings(user)
    return sorted(offering.selection.spawn_role for offering in offerings)


@pytest.mark.parametrize(
    ("start", "end", "offered"),
    [
        (None, None, True),
        (NOW - DAY, NOW + DAY, True),
        (NOW + DAY, None, False),
        (None, NOW - DAY, False),
    ],
)
def test_students_only_see_terms_within_the_access_period(repository, start, end, offered):
    term = make_term(student_access_start=start, student_access_end=end)
    repository.create_course(make_course(terms={"t1": term}))

    expected = [SpawnRole.STUDENT] if offered else []
    assert _offered_roles(repository, _user("student")) == expected


def test_staff_are_not_restricted_by_the_access_period(repository):
    term = make_term(student_access_end=NOW - DAY)
    repository.create_course(make_course(terms={"t1": term}))

    # An instructor can spawn both environments; only the student one is closed.
    assert _offered_roles(repository, _user("instructor")) == [SpawnRole.GRADER]
