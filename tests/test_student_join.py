from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from conftest import StubCatalogProvider, make_course, make_term

from e2x_course_hub.api.course_api import CourseAPI
from e2x_course_hub.course_service.join.schemas import StudentJoinStatus
from e2x_course_hub.course_service.join.status import student_join_status
from e2x_course_hub.errors import StudentJoinLinkInvalidError
from e2x_course_hub.schema.course import StudentJoinTarget

NOW = datetime(2026, 11, 2, 9, 0, tzinfo=timezone.utc)
HOUR = timedelta(hours=1)

INSTRUCTOR = SimpleNamespace(username="instructor", groups=["lms.course.c1.term.t1.instructor"])


@pytest.fixture
def course_api(repository) -> CourseAPI:
    repository.create_course(make_course(terms={"t1": make_term()}))
    return CourseAPI(repository, StubCatalogProvider())


# ── Resolving a join link ────────────────────────────────────────────


def test_valid_token_leads_to_its_term(course_api):
    link = course_api.set_term_student_join_link(INSTRUCTOR, "c1", "t1", NOW + HOUR)

    target = course_api.resolve_student_join_link(link.token, NOW)

    assert target == StudentJoinTarget(course_id="c1", course_name="Course", term_id="t1")


def test_unknown_token_is_invalid(course_api):
    with pytest.raises(StudentJoinLinkInvalidError):
        course_api.resolve_student_join_link("never-created", NOW)


@pytest.mark.parametrize("expires_at", [NOW, NOW - HOUR])
def test_expired_token_is_invalid(course_api, expires_at):
    link = course_api.set_term_student_join_link(INSTRUCTOR, "c1", "t1", expires_at)

    with pytest.raises(StudentJoinLinkInvalidError):
        course_api.resolve_student_join_link(link.token, NOW)


def test_replaced_token_is_invalid(course_api):
    old = course_api.set_term_student_join_link(INSTRUCTOR, "c1", "t1", None)
    course_api.regenerate_term_student_join_link(INSTRUCTOR, "c1", "t1")

    with pytest.raises(StudentJoinLinkInvalidError):
        course_api.resolve_student_join_link(old.token, NOW)


# ── Join status ──────────────────────────────────────────────────────


def _target(start: datetime | None = None, end: datetime | None = None) -> StudentJoinTarget:
    return StudentJoinTarget(
        course_id="c1",
        course_name="Course",
        term_id="t1",
        student_access_start=start,
        student_access_end=end,
    )


def _user(*groups: str) -> SimpleNamespace:
    return SimpleNamespace(username="someone", groups=list(groups))


@pytest.mark.parametrize(
    ("start", "end", "status"),
    [
        (None, None, StudentJoinStatus.OPEN),
        (NOW - HOUR, NOW + HOUR, StudentJoinStatus.OPEN),
        (NOW + HOUR, None, StudentJoinStatus.NOT_YET_OPEN),
        (None, NOW, StudentJoinStatus.ENDED),
        (None, NOW - HOUR, StudentJoinStatus.ENDED),
    ],
)
def test_status_follows_the_access_period(start, end, status):
    assert student_join_status(_target(start, end), _user(), NOW) is status


@pytest.mark.parametrize(
    "group",
    [
        "lms.course.c1.term.t1.student",
        "lms.course.c1.term.t1.teaching-assistant",
        "lms.course.c1.course-owner",
    ],
)
def test_a_role_in_the_term_or_course_means_already_member(group):
    # Takes precedence over the access period, so staff never see "ended".
    target = _target(end=NOW - HOUR)

    assert student_join_status(target, _user(group), NOW) is StudentJoinStatus.ALREADY_MEMBER


@pytest.mark.parametrize(
    "group",
    [
        "lms.course.c1.term.t2.student",
        "lms.course.c2.term.t1.student",
        "lms.course.c2.course-owner",
        "some-unrelated-group",
    ],
)
def test_roles_elsewhere_do_not_count(group):
    assert student_join_status(_target(), _user(group), NOW) is StudentJoinStatus.OPEN
