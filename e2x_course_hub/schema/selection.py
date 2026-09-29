from pydantic import BaseModel, ConfigDict, Field

from .types import SpawnRole


class ImageSelection(BaseModel):
    """A selection of an image family and an optional tag."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    family: str = Field(min_length=1)
    tag: str


class PartialImageSelection(BaseModel):
    """A partial selection of an image family and an optional tag."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    family: str = Field(..., min_length=1)
    tag: str | None = Field(default=None, min_length=1)


class SpawnSelection(BaseModel):
    """A selection of spawn options, including spawn role, image selection, resource tier,
    and profile name."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    spawn_role: SpawnRole
    # True when the course directory should be mounted read-only (e.g. an observer
    # spawning the grader environment). Never stored in course/term config.
    course_readonly: bool = False
    image: ImageSelection
    resource_tier_name: str
    profile_name: str

    def with_fallback(self, fallback: "SpawnSelection") -> "SpawnSelection":
        """
        Create a new SpawnSelection with fallback values for any missing fields.
        Args:
            fallback (SpawnSelection): The fallback SpawnSelection to use for missing values.
        Returns:
            SpawnSelection: A new SpawnSelection with fallback values applied.
        """
        return SpawnSelection(
            spawn_role=self.spawn_role,
            course_readonly=self.course_readonly,
            image=self.image or fallback.image,
            resource_tier_name=self.resource_tier_name or fallback.resource_tier_name,
            profile_name=self.profile_name or fallback.profile_name,
        )


class SpawnRoleSelection(BaseModel):
    """A selection of spawn options for a specific spawn role"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    resource_tier_name: str
    profile_name: str


class CourseReference(BaseModel):
    """
    Represents the context of a specific course and term.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    course_id: str = Field(min_length=1)
    term_id: str = Field(min_length=1)
    course_display_name: str = Field(min_length=1)
    course_description: str | None = None


class SpawnOffering(BaseModel):
    """
    Represents a spawn option for a user, including the course reference and the spawn selection.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)
    course: CourseReference
    selection: SpawnSelection
