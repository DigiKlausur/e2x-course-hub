from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

from conftest import make_course

from e2x_course_hub.api.course_api import CourseAPI
from e2x_course_hub.schema.catalog import InfrastructureCatalogOptions
from e2x_course_hub.schema.course import StudentAccessPeriod

START = datetime(2026, 11, 2, 9, 0, tzinfo=timezone.utc)

OWNER = SimpleNamespace(username="owner", groups=["lms.course.c1.course-owner"])


def _course_api(repository) -> CourseAPI:
    # The catalog is only used for existence checks, which a mock always passes.
    catalog = MagicMock(spec=InfrastructureCatalogOptions)
    catalog_provider = SimpleNamespace(get_infrastructure_catalog=lambda: catalog)
    return CourseAPI(repository, catalog_provider)


def test_add_term_without_access_period_is_unrestricted(repository):
    repository.create_course(make_course())

    term = _course_api(repository).add_term(OWNER, "c1", "t1")

    assert term.student_access_start is None
    assert term.student_access_end is None


def test_add_term_with_access_period(repository):
    repository.create_course(make_course())

    _course_api(repository).add_term(
        OWNER, "c1", "t1", access_period=StudentAccessPeriod(student_access_start=START)
    )

    stored = repository.get_term("c1", "t1")
    assert stored.student_access_start == START
    assert stored.student_access_end is None
