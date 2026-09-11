from e2x_hub_rbac.auth.rbac import PermissionEnum, Role, RolePermissions, Scope

from ..schema.types import SpawnRole


class SpawnPermission(PermissionEnum):
    """Permissions related to spawn profile management."""

    SPAWN_GRADER_PROFILE = ("spawn.grader_profile", Scope.TERM)
    SPAWN_STUDENT_PROFILE = ("spawn.student_profile", Scope.TERM)
    SPAWN_GRADER_READONLY_PROFILE = ("spawn.grader_readonly_profile", Scope.TERM)


class SpawnPermissionSets:
    """Predefined sets of permissions for spawn profile management."""

    SPAWN_ALL = frozenset(
        [
            SpawnPermission.SPAWN_GRADER_PROFILE,
            SpawnPermission.SPAWN_STUDENT_PROFILE,
            SpawnPermission.SPAWN_GRADER_READONLY_PROFILE,
        ]
    )


# What spawning with a given permission actually launches: the environment role to
# use for tier/profile lookup, and whether the course directory is read-only.
PERMISSION_TO_SPAWN: dict[SpawnPermission, tuple[SpawnRole, bool]] = {
    SpawnPermission.SPAWN_STUDENT_PROFILE: (SpawnRole.STUDENT, False),
    SpawnPermission.SPAWN_GRADER_PROFILE: (SpawnRole.GRADER, False),
    SpawnPermission.SPAWN_GRADER_READONLY_PROFILE: (SpawnRole.GRADER, True),
}

SPAWN_ROLE_PERMISSIONS: RolePermissions = {
    Role.LMS_ADMIN: frozenset(SpawnPermissionSets.SPAWN_ALL),
    Role.COURSE_CREATOR: frozenset([SpawnPermission.SPAWN_GRADER_READONLY_PROFILE]),
    Role.COURSE_OWNER: frozenset(
        frozenset(
            [
                SpawnPermission.SPAWN_GRADER_PROFILE,
                SpawnPermission.SPAWN_STUDENT_PROFILE,
            ]
        )
    ),
    Role.INSTRUCTOR: frozenset(
        frozenset(
            [
                SpawnPermission.SPAWN_GRADER_PROFILE,
                SpawnPermission.SPAWN_STUDENT_PROFILE,
            ]
        )
    ),
    Role.TEACHING_ASSISTANT: frozenset(
        [
            SpawnPermission.SPAWN_GRADER_PROFILE,
            SpawnPermission.SPAWN_STUDENT_PROFILE,
        ]
    ),
    Role.STUDENT: frozenset(
        [
            SpawnPermission.SPAWN_STUDENT_PROFILE,
        ]
    ),
    Role.OBSERVER: frozenset(
        [
            SpawnPermission.SPAWN_GRADER_READONLY_PROFILE,
            SpawnPermission.SPAWN_STUDENT_PROFILE,
        ]
    ),
}
