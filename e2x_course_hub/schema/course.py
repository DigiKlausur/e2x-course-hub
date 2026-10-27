from datetime import datetime

from pydantic import AwareDatetime, BaseModel, Field, model_validator
from pydantic.json_schema import SkipJsonSchema

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


class StudentAccessPeriod(BaseModel):
    """The period in which students may spawn a term. Staff are not restricted."""

    student_access_start: AwareDatetime | None = Field(
        default=None,
        description="From when students may spawn the term. Empty means immediately.",
    )
    student_access_end: AwareDatetime | None = Field(
        default=None,
        description="Until when students may spawn the term. Empty means indefinitely.",
    )

    @model_validator(mode="after")
    def _check_end_after_start(self) -> "StudentAccessPeriod":
        if (
            self.student_access_start is not None
            and self.student_access_end is not None
            and self.student_access_end <= self.student_access_start
        ):
            raise ValueError("student_access_end must be after student_access_start.")
        return self

    def is_student_access_open(self, now: datetime) -> bool:
        """Whether students may spawn the term at the given (timezone-aware) time."""
        if self.student_access_start is not None and now < self.student_access_start:
            return False
        if self.student_access_end is not None and now >= self.student_access_end:
            return False
        return True


class TermConfig(SpawnRoleConfigMixin, StudentAccessPeriod):
    """Configuration for a specific term."""

    # Hidden from the API schema: TermConfig is only used as request input, and
    # the term responses expose created_at themselves.
    created_at: SkipJsonSchema[datetime | None] = Field(
        default=None,
        description="When the term was created. Set by the database, ignored on write. "
        "Empty for terms created before this was recorded.",
    )


class CourseMetadata(BaseModel):
    """
    Metadata information about a course.
    """

    course_id: str = Field(..., description="The id of the course.")
    course_name: str = Field(..., description="The full name of the course")
    description: str | None = Field(
        default=None, description="An optional text describing the course."
    )
    # Hidden from the API schema, so clients cannot send it when creating a course;
    # CourseMetadataResponse exposes it in responses.
    created_at: SkipJsonSchema[datetime | None] = Field(
        default=None,
        description="When the course was created. Set by the database, ignored on write. "
        "Empty for courses created before this was recorded.",
    )


class CourseConfig(SpawnRoleConfigMixin):
    metadata: CourseMetadata = Field(..., description="Metadata information about the course.")
    terms: dict[str, TermConfig] = Field(
        default_factory=dict,
        description="Per-term configuration overrides.",
    )
