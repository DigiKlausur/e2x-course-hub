from types import SimpleNamespace

from conftest import CATALOG, make_course, make_term

from e2x_course_hub.course_service.courses.assembler import CourseAssembler
from e2x_course_hub.course_service.terms.assembler import TermAssembler
from e2x_course_hub.schema.catalog import UnavailableSelection
from e2x_course_hub.schema.selection import SpawnRoleSelection
from e2x_course_hub.schema.types import SpawnRole

# Only `unavailable` is under test, so the user may do nothing.
NO_PERMISSIONS = SimpleNamespace(has_permission=lambda *args, **kwargs: False)

TERM_ASSEMBLER = TermAssembler(NO_PERMISSIONS, CATALOG)
COURSE_ASSEMBLER = CourseAssembler(NO_PERMISSIONS, TERM_ASSEMBLER, CATALOG)

# `make_term` uses the tag "latest", which the catalog does not have.
MISSING_TAG = [UnavailableSelection(kind="image_tag", name="latest")]


def test_term_summary_lists_a_tag_missing_from_the_catalog():
    summary = TERM_ASSEMBLER.summary("c1", "t1", make_term())

    assert summary.unavailable == MISSING_TAG


def test_term_environment_lists_a_tag_missing_from_the_catalog():
    environment = TERM_ASSEMBLER.environment(make_term())

    assert environment.unavailable == MISSING_TAG


def test_course_environment_is_available_when_everything_is_in_the_catalog():
    assert COURSE_ASSEMBLER.environment(make_course()).unavailable == []


def test_course_environment_lists_a_resource_tier_missing_from_the_catalog():
    course = make_course()
    course.spawn_role_selections[SpawnRole.GRADER] = SpawnRoleSelection(
        resource_tier_name="large", profile_name="default"
    )

    assert COURSE_ASSEMBLER.environment(course).unavailable == [
        UnavailableSelection(kind="resource_tier", name="large", spawn_role=SpawnRole.GRADER)
    ]
