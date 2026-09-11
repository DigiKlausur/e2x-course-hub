from pydantic import BaseModel, Field

from .selection import ImageSelection, SpawnRoleSelection, SpawnSelection
from .types import SpawnRole


class SpawnRoleConfigMixin(BaseModel):
    """Shared configuration for anything that maps spawn roles to selections."""

    image: ImageSelection = Field(
        ...,
        description="Image configuration.",
    )
    spawn_role_selections: dict[SpawnRole, SpawnRoleSelection] = Field(
        ...,
        description="Per-spawn role selection configuration.",
    )

    def get_spawn_selection(self, spawn_role: SpawnRole) -> SpawnSelection:
        selection = self.spawn_role_selections[spawn_role]
        return SpawnSelection(
            spawn_role=spawn_role,
            image=self.image,
            resource_tier_name=selection.resource_tier_name,
            profile_name=selection.profile_name,
        )

    def get_resource_selections(self) -> dict[SpawnRole, str]:
        return {role: sel.resource_tier_name for role, sel in self.spawn_role_selections.items()}

    def get_profile_selections(self) -> dict[SpawnRole, str]:
        return {role: sel.profile_name for role, sel in self.spawn_role_selections.items()}


class TermConfig(SpawnRoleConfigMixin):
    """Configuration for a specific term."""

    pass


class CourseMetadata(BaseModel):
    """
    Metadata information about a course.
    """

    course_id: str = Field(..., description="The id of the course.")
    course_name: str = Field(..., description="The full name of the course")
    description: str | None = Field(
        default=None, description="An optional text describing the course."
    )


class CourseConfig(SpawnRoleConfigMixin):
    metadata: CourseMetadata = Field(..., description="Metadata information about the course.")
    terms: dict[str, TermConfig] = Field(
        default_factory=dict,
        description="Per-term configuration overrides.",
    )
