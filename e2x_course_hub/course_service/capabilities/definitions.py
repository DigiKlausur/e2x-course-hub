"""Every capability, grouped by the level it applies to.

Ids match the fields of the capability response models (e.g. ``TermCapabilities``)
so the frontend can use one text per field. Capabilities without such a field
are only used to explain what a role can do.
"""

from e2x_hub_rbac.auth import Scope
from e2x_hub_rbac.permissions import MembershipPermission

from ...api.course_permissions import CoursePermission
from ...api.infrastructure_permissions import InfrastructurePermission
from ...api.spawn_permissions import SpawnPermission
from .model import Capability, MembershipCapabilityGroup


class LMS:
    CREATE_COURSE = Capability.of("createCourse", CoursePermission.ADD_COURSE)
    LMS_ADMINS = MembershipCapabilityGroup.of(
        "lmsAdmins",
        list=MembershipPermission.LIST_LMS_ADMINS,
        add=MembershipPermission.ADD_LMS_ADMIN,
        remove=MembershipPermission.REMOVE_LMS_ADMIN,
    )
    COURSE_CREATORS = MembershipCapabilityGroup.of(
        "courseCreators",
        list=MembershipPermission.LIST_COURSE_CREATORS,
        add=MembershipPermission.ADD_COURSE_CREATOR,
        remove=MembershipPermission.REMOVE_COURSE_CREATOR,
    )
    VIEW_IMAGE_CATALOG = Capability.of(
        "imageCatalog.view", InfrastructurePermission.LMS_VIEW_IMAGE_CATALOG
    )
    MANAGE_IMAGE_CATALOG = Capability.of(
        "imageCatalog.manage", InfrastructurePermission.LMS_MANAGE_IMAGE_CATALOG
    )
    VIEW_RESOURCE_CATALOG = Capability.of(
        "resourceCatalog.view", InfrastructurePermission.LMS_VIEW_RESOURCE_CATALOG
    )
    MANAGE_RESOURCE_CATALOG = Capability.of(
        "resourceCatalog.manage", InfrastructurePermission.LMS_MANAGE_RESOURCE_CATALOG
    )
    VIEW_PROFILE_CATALOG = Capability.of(
        "profileCatalog.view", InfrastructurePermission.LMS_VIEW_PROFILE_CATALOG
    )
    MANAGE_PROFILE_CATALOG = Capability.of(
        "profileCatalog.manage", InfrastructurePermission.LMS_MANAGE_PROFILE_CATALOG
    )


class COURSE:
    # No response field; explains that a role can open the course at all.
    VIEW_COURSE = Capability.of("viewCourse", CoursePermission.COURSE_VIEW)
    # No response field; separate from VIEW_COURSE because course creators may
    # open every course without seeing its metadata.
    VIEW_METADATA = Capability.of("viewMetadata", CoursePermission.COURSE_VIEW_METADATA)
    EDIT_METADATA = Capability.of("editMetadata", CoursePermission.COURSE_EDIT_METADATA)
    REMOVE_COURSE = Capability.of("removeCourse", CoursePermission.COURSE_REMOVE)
    SELECT_ENVIRONMENT = Capability.of(
        "selectEnvironment",
        CoursePermission.COURSE_SELECT_IMAGE,
        CoursePermission.COURSE_SELECT_RESOURCES,
        CoursePermission.COURSE_SELECT_PROFILES,
    )
    ADD_TERM = Capability.of("addTerm", CoursePermission.TERM_ADD)
    COURSE_OWNERS = MembershipCapabilityGroup.of(
        "courseOwners",
        list=MembershipPermission.LIST_COURSE_OWNERS,
        add=MembershipPermission.ADD_COURSE_OWNER,
        remove=MembershipPermission.REMOVE_COURSE_OWNER,
    )


class TERM:
    VIEW_TERM = Capability.of("viewTerm", CoursePermission.TERM_VIEW)
    REMOVE_TERM = Capability.of("removeTerm", CoursePermission.TERM_REMOVE)
    SELECT_ENVIRONMENT = Capability.of(
        "selectEnvironment",
        CoursePermission.TERM_SELECT_IMAGE,
        CoursePermission.TERM_SELECT_RESOURCES,
        CoursePermission.TERM_SELECT_PROFILES,
    )
    INSTRUCTORS = MembershipCapabilityGroup.of(
        "membership.instructors",
        list=MembershipPermission.LIST_INSTRUCTORS,
        add=MembershipPermission.ADD_INSTRUCTOR,
        remove=MembershipPermission.REMOVE_INSTRUCTOR,
    )
    TEACHING_ASSISTANTS = MembershipCapabilityGroup.of(
        "membership.teachingAssistants",
        list=MembershipPermission.LIST_TEACHING_ASSISTANTS,
        add=MembershipPermission.ADD_TEACHING_ASSISTANT,
        remove=MembershipPermission.REMOVE_TEACHING_ASSISTANT,
    )
    STUDENTS = MembershipCapabilityGroup.of(
        "membership.students",
        list=MembershipPermission.LIST_STUDENTS,
        add=MembershipPermission.ADD_STUDENT,
        remove=MembershipPermission.REMOVE_STUDENT,
    )
    OBSERVERS = MembershipCapabilityGroup.of(
        "membership.observers",
        list=MembershipPermission.LIST_OBSERVERS,
        add=MembershipPermission.ADD_OBSERVER,
        remove=MembershipPermission.REMOVE_OBSERVER,
    )
    # No response fields; the spawner enforces these (see PERMISSION_TO_SPAWN).
    SPAWN_STUDENT_ENVIRONMENT = Capability.of(
        "spawnStudentEnvironment", SpawnPermission.SPAWN_STUDENT_PROFILE
    )
    SPAWN_GRADER_ENVIRONMENT = Capability.of(
        "spawnGraderEnvironment", SpawnPermission.SPAWN_GRADER_PROFILE
    )
    SPAWN_READONLY_GRADER_ENVIRONMENT = Capability.of(
        "spawnReadonlyGraderEnvironment", SpawnPermission.SPAWN_GRADER_READONLY_PROFILE
    )


def _collect(namespace: type, scope: Scope) -> tuple[Capability, ...]:
    """All capabilities of a namespace, with the ones inside groups flattened.

    Raises if a capability does not belong to the namespace's level or an id is
    used twice, since either is a mistake in the definitions above.
    """
    capabilities: list[Capability] = []
    for value in vars(namespace).values():
        if isinstance(value, Capability):
            capabilities.append(value)
        elif isinstance(value, MembershipCapabilityGroup):
            capabilities.extend(value)

    for capability in capabilities:
        if capability.scope is not scope:
            raise ValueError(
                f"{namespace.__name__} capability {capability.id!r} has scope {capability.scope}"
            )
    ids = [capability.id for capability in capabilities]
    duplicates = {id for id in ids if ids.count(id) > 1}
    if duplicates:
        raise ValueError(f"{namespace.__name__} defines ids more than once: {sorted(duplicates)}")
    return tuple(capabilities)


CAPABILITIES_BY_SCOPE: dict[Scope, tuple[Capability, ...]] = {
    Scope.LMS: _collect(LMS, Scope.LMS),
    Scope.COURSE: _collect(COURSE, Scope.COURSE),
    Scope.TERM: _collect(TERM, Scope.TERM),
}

ALL_CAPABILITIES: tuple[Capability, ...] = tuple(
    capability for capabilities in CAPABILITIES_BY_SCOPE.values() for capability in capabilities
)
