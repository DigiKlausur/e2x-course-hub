import glob
import os
from typing import Annotated, Dict, List, Literal, Mapping, Optional, Union

from pydantic import (
    BaseModel,
    Discriminator,
    TypeAdapter,
    ValidationError,
    model_validator,
)

from ..errors import ProfileNotFoundError
from ..utils import load_yaml, resolve_placeholders
from .enums import SpawnRole
from .infrastructure import Image, Resources, Runtime
from .mount import Mount, MountCatalog
from .user import UserCourseContext

# ── Resolved spawn profile ──────────────────────────────────────────


class SpawnProfile(BaseModel):
    """A fully resolved profile ready for spawning."""

    spawn_role: str
    display_name: str
    runtime: Runtime
    mounts: List[Mount] = []


# ── Profile definitions (loaded from YAML) ──────────────────────────


class _BaseProfile(BaseModel):
    """Common fields shared by student and grader profiles."""

    name: str
    display_name: str
    environment: Dict[str, Union[str, float, int, bool]] = {}
    mounts: List[str] = []


class StudentProfile(_BaseProfile):
    kind: Literal["student"] = "student"

    @model_validator(mode="after")
    def _check_required_mounts(self) -> "StudentProfile":
        missing = {"student_home"} - set(self.mounts)
        if missing:
            raise ValueError(f"Student profile '{self.name}' missing required mounts: {missing}")
        return self

    def resolve(
        self,
        image: Image,
        resources: Resources,
        mount_catalog: MountCatalog,
        ctx: UserCourseContext,
    ) -> SpawnProfile:
        return SpawnProfile(
            spawn_role=SpawnRole.STUDENT.value,
            display_name=self.display_name,
            runtime=Runtime(
                image=image,
                resources=resources,
                environment=resolve_placeholders(self.environment, ctx=ctx.model_dump()),
            ),
            mounts=mount_catalog.resolve_many(self.mounts, ctx),
        )


class GraderProfile(_BaseProfile):
    kind: Literal["grader"] = "grader"
    additional_role_mounts: Dict[str, List[str]] = {}

    @model_validator(mode="after")
    def _check_required_mounts(self) -> "GraderProfile":
        missing = {"grader_home", "course_term"} - set(self.mounts)
        if missing:
            raise ValueError(f"Grader profile '{self.name}' missing required mounts: {missing}")
        return self

    def get_all_mounts(self, roles: List[str] | None = None) -> List[str]:
        """Return profile mounts + any role-based additional mounts."""
        all_mounts = list(self.mounts)
        if roles:
            seen = set(all_mounts)
            for role in roles:
                for m in self.additional_role_mounts.get(role, []):
                    if m not in seen:
                        all_mounts.append(m)
                        seen.add(m)
        return all_mounts

    def resolve(
        self,
        image: Image,
        resources: Resources,
        mount_catalog: MountCatalog,
        ctx: UserCourseContext,
        roles: List[str] | None = None,
        archive_term_ids: List[str] | None = None,
    ) -> SpawnProfile:
        mounts = mount_catalog.resolve_many(self.get_all_mounts(roles), ctx)
        if archive_term_ids:
            mounts.extend(
                mount_catalog.resolve_archive_mounts(
                    username=ctx.username,
                    course_id=ctx.course_id,
                    term_ids=archive_term_ids,
                )
            )
        return SpawnProfile(
            spawn_role=SpawnRole.GRADER.value,
            display_name=self.display_name,
            runtime=Runtime(
                image=image,
                resources=resources,
                environment=resolve_placeholders(self.environment, ctx=ctx.model_dump()),
            ),
            mounts=mounts,
        )


_Profile = Annotated[Union[StudentProfile, GraderProfile], Discriminator("kind")]


# ── Selection & config ──────────────────────────────────────────────


class ProfileSelection(BaseModel):
    student: Optional[str] = None
    grader: Optional[str] = None

    def with_fallback(self, fallback: "ProfileSelection") -> "ProfileSelection":
        return ProfileSelection(
            student=self.student if self.student is not None else fallback.student,
            grader=self.grader if self.grader is not None else fallback.grader,
        )


class ProfilesConfig(BaseModel):
    """Loaded from the server config YAML."""

    profile_dir: str
    default_student: str
    default_grader: str


# ── Catalog ─────────────────────────────────────────────────────────


class StudentRoleProfiles(BaseModel):
    default: str
    profiles: Dict[str, StudentProfile] = {}


class GraderRoleProfiles(BaseModel):
    default: str
    profiles: Dict[str, GraderProfile] = {}


class AvailableRoleProfiles(BaseModel):
    default: str
    profiles: List[str] = []


class AvailableProfiles(BaseModel):
    student: AvailableRoleProfiles
    grader: AvailableRoleProfiles


class AvailableRoleProfileDetails(BaseModel):
    default: str
    profiles: Mapping[str, _Profile] = {}


class AvailableProfileDetails(BaseModel):
    student: AvailableRoleProfileDetails
    grader: AvailableRoleProfileDetails


class ProfileCatalog(BaseModel):
    student: StudentRoleProfiles
    grader: GraderRoleProfiles

    @classmethod
    def from_profiles_config(cls, config: ProfilesConfig) -> "ProfileCatalog":
        adapter = TypeAdapter(_Profile)
        students: Dict[str, StudentProfile] = {}
        graders: Dict[str, GraderProfile] = {}
        for path in glob.glob(os.path.join(config.profile_dir, "*.yaml")):
            data = load_yaml(path)
            try:
                profile = adapter.validate_python(data)
            except ValidationError as e:
                raise ValueError(f"Error validating profile in {path}: {e}") from e
            if isinstance(profile, StudentProfile):
                if profile.name in students:
                    raise ValueError(f"Duplicate student profile '{profile.name}' in {path}")
                students[profile.name] = profile
            else:
                if profile.name in graders:
                    raise ValueError(f"Duplicate grader profile '{profile.name}' in {path}")
                graders[profile.name] = profile
        return cls(
            student=StudentRoleProfiles(default=config.default_student, profiles=students),
            grader=GraderRoleProfiles(default=config.default_grader, profiles=graders),
        )

    @model_validator(mode="after")
    def _validate_defaults(self) -> "ProfileCatalog":
        if self.student.default not in self.student.profiles:
            raise ValueError(
                f"Default student profile '{self.student.default}' not found. "
                f"Available: {list(self.student.profiles.keys())}"
            )
        if self.grader.default not in self.grader.profiles:
            raise ValueError(
                f"Default grader profile '{self.grader.default}' not found. "
                f"Available: {list(self.grader.profiles.keys())}"
            )
        return self

    def get_student_profile(self, selection: ProfileSelection) -> StudentProfile:
        name = selection.student or self.student.default
        profile = self.student.profiles.get(name)
        if profile is None:
            raise ProfileNotFoundError(profile_name=name, spawn_role=SpawnRole.STUDENT)
        return profile

    def get_grader_profile(self, selection: ProfileSelection) -> GraderProfile:
        name = selection.grader or self.grader.default
        profile = self.grader.profiles.get(name)
        if profile is None:
            raise ProfileNotFoundError(profile_name=name, spawn_role=SpawnRole.GRADER)
        return profile

    def assert_profile_selection_exists(self, selection: ProfileSelection):
        if selection.student and selection.student not in self.student.profiles:
            raise ProfileNotFoundError(profile_name=selection.student, spawn_role=SpawnRole.STUDENT)
        if selection.grader and selection.grader not in self.grader.profiles:
            raise ProfileNotFoundError(profile_name=selection.grader, spawn_role=SpawnRole.GRADER)

    def get_default_profile_selection(self) -> ProfileSelection:
        return ProfileSelection(
            student=self.student.default,
            grader=self.grader.default,
        )

    def list_available_profiles(self) -> AvailableProfiles:
        return AvailableProfiles(
            student=AvailableRoleProfiles(
                default=self.student.default,
                profiles=list(self.student.profiles.keys()),
            ),
            grader=AvailableRoleProfiles(
                default=self.grader.default,
                profiles=list(self.grader.profiles.keys()),
            ),
        )

    def list_available_profile_details(self) -> AvailableProfileDetails:
        return AvailableProfileDetails(
            student=AvailableRoleProfileDetails(
                default=self.student.default,
                profiles=self.student.profiles,
            ),
            grader=AvailableRoleProfileDetails(
                default=self.grader.default,
                profiles=self.grader.profiles,
            ),
        )
