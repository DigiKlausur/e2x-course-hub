from conftest import CATALOG, SELECTIONS

from e2x_course_hub.schema.catalog import UnavailableSelection
from e2x_course_hub.schema.selection import PartialImageSelection, SpawnRoleSelection
from e2x_course_hub.schema.types import SpawnRole


def test_find_unavailable_is_empty_when_everything_is_in_the_catalog():
    image = PartialImageSelection(family="python", tag="2025-09")

    assert CATALOG.find_unavailable(image, SELECTIONS) == []


def test_find_unavailable_reports_a_missing_family_but_not_its_tag():
    image = PartialImageSelection(family="retired", tag="2025-09")

    assert CATALOG.find_unavailable(image, SELECTIONS) == [
        UnavailableSelection(kind="image_family", name="retired")
    ]


def test_find_unavailable_reports_a_missing_tag():
    image = PartialImageSelection(family="python", tag="2024-09")

    assert CATALOG.find_unavailable(image, SELECTIONS) == [
        UnavailableSelection(kind="image_tag", name="2024-09")
    ]


def test_find_unavailable_reports_missing_tiers_and_profiles_with_their_role():
    selections = {
        **SELECTIONS,
        SpawnRole.STUDENT: SpawnRoleSelection(resource_tier_name="large", profile_name="gpu"),
    }

    assert CATALOG.find_unavailable(PartialImageSelection(family="python"), selections) == [
        UnavailableSelection(kind="resource_tier", name="large", spawn_role=SpawnRole.STUDENT),
        UnavailableSelection(kind="profile", name="gpu", spawn_role=SpawnRole.STUDENT),
    ]
