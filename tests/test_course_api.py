from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from conftest import make_course

from e2x_course_hub.api.course_api import CourseAPI
from e2x_course_hub.errors import (
    ImageFamilyNotFoundError,
    ProfileNotFoundError,
    ResourceTierNotFoundError,
)
from e2x_course_hub.schema.catalog import InfrastructureCatalogOptions
from e2x_course_hub.schema.course import StudentAccessPeriod
from e2x_course_hub.schema.selection import ImageSelection, SpawnRoleSelection
from e2x_course_hub.schema.types import SpawnRole

START = datetime(2026, 11, 2, 9, 0, tzinfo=timezone.utc)

OWNER = SimpleNamespace(username="owner", groups=["lms.course.c1.course-owner"])

# Matches the selections of `make_course`; "2026-09" is the default over an older tag.
CATALOG = InfrastructureCatalogOptions.model_validate(
    {
        "image_family_options": {
            "default_family": "python",
            "families": {
                "python": {
                    "display_name": "Python",
                    "description": "Python",
                    "default_tag": "2026-09",
                    "tags": {"2025-09": {"status": "old"}, "2026-09": {"status": "stable"}},
                }
            },
        },
        "spawn_role_options": {
            role: {
                "profile_options": {
                    "default_profile": "default",
                    "profiles": {"default": {"display_name": "Default"}},
                },
                "resource_tier_options": {
                    "default_tier": "small",
                    "tiers": {"small": {"display_name": "Small", "description": "Small"}},
                },
            }
            for role in SpawnRole
        },
    }
)


def _course_api(repository) -> CourseAPI:
    catalog_provider = SimpleNamespace(get_infrastructure_catalog=lambda: CATALOG)
    return CourseAPI(repository, catalog_provider)


def test_add_term_gets_the_default_tag_of_the_course_image_family(repository):
    repository.create_course(make_course())

    term = _course_api(repository).add_term(OWNER, "c1", "t1")

    assert term.image == ImageSelection(family="python", tag="2026-09")


def test_add_term_with_an_image_family_missing_from_the_catalog_fails(repository):
    repository.create_course(make_course().model_copy(update={"image_family": "retired"}))

    with pytest.raises(ImageFamilyNotFoundError):
        _course_api(repository).add_term(OWNER, "c1", "t1")


def _make_course_with_student_selection(selection: SpawnRoleSelection):
    course = make_course()
    course.spawn_role_selections[SpawnRole.STUDENT] = selection
    return course


def test_add_term_with_a_resource_tier_missing_from_the_catalog_fails(repository):
    repository.create_course(
        _make_course_with_student_selection(
            SpawnRoleSelection(resource_tier_name="retired", profile_name="default")
        )
    )

    with pytest.raises(ResourceTierNotFoundError) as error:
        _course_api(repository).add_term(OWNER, "c1", "t1")

    assert error.value.extra == {"tier_name": "retired", "spawn_role": SpawnRole.STUDENT}


def test_add_term_with_a_profile_missing_from_the_catalog_fails(repository):
    repository.create_course(
        _make_course_with_student_selection(
            SpawnRoleSelection(resource_tier_name="small", profile_name="retired")
        )
    )

    with pytest.raises(ProfileNotFoundError) as error:
        _course_api(repository).add_term(OWNER, "c1", "t1")

    assert error.value.extra == {"profile_name": "retired", "spawn_role": SpawnRole.STUDENT}


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
