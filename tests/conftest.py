import pytest

from e2x_course_hub.db.repository import CourseRepository, get_course_repository_from_db_url
from e2x_course_hub.schema.catalog import InfrastructureCatalogOptions
from e2x_course_hub.schema.course import CourseConfig, CourseMetadata, TermConfig
from e2x_course_hub.schema.selection import ImageSelection, SpawnRoleSelection
from e2x_course_hub.schema.types import SpawnRole

IMAGE = ImageSelection(family="python", tag="latest")
SELECTIONS = {
    role: SpawnRoleSelection(resource_tier_name="small", profile_name="default")
    for role in SpawnRole
}

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


def make_term(**fields) -> TermConfig:
    return TermConfig(image=IMAGE, spawn_role_selections=SELECTIONS, **fields)


def make_course(course_id: str = "c1", terms: dict[str, TermConfig] | None = None) -> CourseConfig:
    return CourseConfig(
        metadata=CourseMetadata(course_id=course_id, course_name="Course"),
        image_family=IMAGE.family,
        spawn_role_selections=SELECTIONS,
        terms=terms or {},
    )


@pytest.fixture
def db_url(tmp_path) -> str:
    return f"sqlite:///{tmp_path / 'courses.db'}"


@pytest.fixture
def repository(db_url) -> CourseRepository:
    return get_course_repository_from_db_url(db_url)
