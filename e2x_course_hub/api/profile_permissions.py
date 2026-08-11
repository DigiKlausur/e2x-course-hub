from e2x_hub_rbac.auth.rbac import PermissionEnum, Role, RolePermissions, Scope


class SpawnProfilePermission(PermissionEnum):
    """Permissions related to spawn profile management."""

    SPAWN_GRADER_PROFILE = ("spawn.grader_profile", Scope.TERM)
    SPAWN_STUDENT_PROFILE = ("spawn.student_profile", Scope.TERM)
    SPAWN_OBSERVER_PROFILE = ("spawn.observer_profile", Scope.TERM)


class SpawnProfilePermissionSets:
    """Predefined sets of permissions for spawn profile management."""

    SPAWN_ALL_PROFILES = frozenset(
        [
            SpawnProfilePermission.SPAWN_GRADER_PROFILE,
            SpawnProfilePermission.SPAWN_STUDENT_PROFILE,
            SpawnProfilePermission.SPAWN_OBSERVER_PROFILE,
        ]
    )


SPAWN_PROFILE_ROLE_PERMISSIONS: RolePermissions = {
    Role.LMS_ADMIN: frozenset(SpawnProfilePermissionSets.SPAWN_ALL_PROFILES),
    Role.COURSE_CREATOR: frozenset([SpawnProfilePermission.SPAWN_OBSERVER_PROFILE]),
    Role.COURSE_OWNER: frozenset(
        frozenset(
            [
                SpawnProfilePermission.SPAWN_GRADER_PROFILE,
                SpawnProfilePermission.SPAWN_STUDENT_PROFILE,
            ]
        )
    ),
    Role.INSTRUCTOR: frozenset(
        frozenset(
            [
                SpawnProfilePermission.SPAWN_GRADER_PROFILE,
                SpawnProfilePermission.SPAWN_STUDENT_PROFILE,
            ]
        )
    ),
    Role.TEACHING_ASSISTANT: frozenset(
        [
            SpawnProfilePermission.SPAWN_GRADER_PROFILE,
            SpawnProfilePermission.SPAWN_STUDENT_PROFILE,
        ]
    ),
    Role.STUDENT: frozenset(
        [
            SpawnProfilePermission.SPAWN_STUDENT_PROFILE,
        ]
    ),
    Role.OBSERVER: frozenset(
        [
            SpawnProfilePermission.SPAWN_OBSERVER_PROFILE,
            SpawnProfilePermission.SPAWN_STUDENT_PROFILE,
        ]
    ),
}
