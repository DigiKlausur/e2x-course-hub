from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from ..utils import load_yaml, resolve_placeholders
from .user import UserCourseContext


class Mount(BaseModel):
    """Resolved volume mount ready for Kubernetes."""

    name: str = Field(..., description="Name of the volume")
    mountPath: str = Field(..., description="Path inside the container")
    subPath: str = Field(..., description="Sub-path within the volume")
    readOnly: bool = Field(default=True, description="Whether the mount is read-only")
    description: Optional[str] = Field(
        default=None, description="Human-readable description of the mount"
    )

    def as_readonly(self) -> "Mount":
        return self.model_copy(update={"readOnly": True})


class MountDefinition(BaseModel):
    """Template for a volume mount with placeholder support.

    Uses ${{inputs.username}}, ${{inputs.course_id}}, and ${{inputs.term_id}}
    placeholders that are resolved against a MountContext.

    Example YAML::

        student_home:
          name: disk2
          mountPath: "/home/${{inputs.username}}"
          subPath: "homes/students/${{inputs.course_id}}-${{inputs.term_id}}/${{inputs.username}}"
          readOnly: false
    """

    name: str = Field(..., description="Name of the volume")
    mountPath: str = Field(
        ..., description="Mount path inside the container (supports placeholders)"
    )
    subPath: str = Field(..., description="Sub-path within the volume (supports placeholders)")
    readOnly: bool = Field(default=True, description="Whether the mount is read-only")
    description: Optional[str] = Field(default=None, description="Human-readable description")

    def resolve(self, ctx: UserCourseContext) -> Mount:
        """Resolve placeholders using the standard context and return a Mount."""
        data = self.model_dump()
        resolved = resolve_placeholders(data, ctx.model_dump())
        return Mount(**resolved)

    def as_readonly(self) -> "MountDefinition":
        return self.model_copy(update={"readOnly": True})


class MountCatalog(BaseModel):
    """Catalog of all mount definitions.

    Includes three required standard mounts and optional extras.
    The ``archived_term`` mount is automatically derived from ``course_term``
    with ``readOnly=True``.
    """

    student_home: MountDefinition = Field(
        ..., description="Mount definition for student home directories"
    )
    grader_home: MountDefinition = Field(
        ..., description="Mount definition for grader home directories"
    )
    course_term: MountDefinition = Field(
        ...,
        description="Mount definition for the current term's course work directory",
    )
    extra: Dict[str, MountDefinition] = Field(
        default_factory=dict, description="Additional named mount definitions"
    )

    @classmethod
    def from_config_file(cls, file_path: str) -> "MountCatalog":
        """Load mount definitions from a YAML file and return a MountCatalog instance."""
        raw_mounts = load_yaml(file_path)
        return cls(**raw_mounts)

    @property
    def archived_term(self) -> MountDefinition:
        """The course_term mount as read-only, for archived terms."""
        return self.course_term.as_readonly()

    def get_all_definitions(self) -> Dict[str, MountDefinition]:
        """Return all named mount definitions including derived ones."""
        defs = {
            "student_home": self.student_home,
            "grader_home": self.grader_home,
            "course_term": self.course_term,
            "archived_term": self.archived_term,
        }
        defs.update(self.extra)
        return defs

    def resolve(self, name: str, ctx: UserCourseContext) -> Mount:
        """Resolve a single named mount definition."""
        defs = self.get_all_definitions()
        if name not in defs:
            raise KeyError(f"Unknown mount definition: '{name}'")
        return defs[name].resolve(ctx)

    def resolve_many(self, names: List[str], ctx: UserCourseContext) -> List[Mount]:
        """Resolve multiple mount definitions by name."""
        return [self.resolve(name, ctx) for name in names]

    def resolve_archive_mounts(
        self, username: str, course_id: str, term_ids: List[str]
    ) -> List[Mount]:
        """Resolve archived_term (course_term as read-only) for past terms.

        Called at spawn time for grader profiles. For each term_id where the
        user has a grader/admin role, this produces a read-only mount.

        Args:
            username: The user's username.
            course_id: The course identifier.
            term_ids: Term IDs to mount as archives.

        Returns:
            List of resolved read-only archive mounts.
        """
        archive_def = self.archived_term
        return [
            archive_def.resolve(
                UserCourseContext(username=username, course_id=course_id, term_id=tid)
            )
            for tid in term_ids
        ]
