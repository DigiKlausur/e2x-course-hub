from e2x_hub_rbac.auth.rbac import PermissionEnum, Role, RolePermissions, Scope


class CoursePermission(PermissionEnum):
    """Permissions related to course management."""

    ADD_COURSE = ("course.add", Scope.HUB)

    COURSE_VIEW = ("course.view", Scope.COURSE)
    COURSE_REMOVE = ("course.remove", Scope.COURSE)
    COURSE_EDIT_METADATA = ("course.edit_metadata", Scope.COURSE)
    COURSE_VIEW_METADATA = ("course.view_metadata", Scope.COURSE)
    COURSE_SELECT_IMAGE = ("course.select_image", Scope.COURSE)
    COURSE_SELECT_RESOURCES = ("course.select_resources", Scope.COURSE)
    COURSE_SELECT_PROFILES = ("course.select_profiles", Scope.COURSE)

    TERM_ADD = ("term.add", Scope.COURSE)
    TERM_REMOVE = ("term.remove", Scope.TERM)
    TERM_VIEW = ("term.view", Scope.TERM)
    TERM_SELECT_IMAGE = ("term.select_image", Scope.TERM)
    TERM_SELECT_RESOURCES = ("term.select_resources", Scope.TERM)
    TERM_SELECT_PROFILES = ("term.select_profiles", Scope.TERM)


class CoursePermissionSets:
    """Predefined sets of permissions for course management."""

    ALL_PERMISSIONS = frozenset(
        [
            CoursePermission.ADD_COURSE,
            CoursePermission.COURSE_VIEW,
            CoursePermission.COURSE_REMOVE,
            CoursePermission.COURSE_EDIT_METADATA,
            CoursePermission.COURSE_VIEW_METADATA,
            CoursePermission.COURSE_SELECT_IMAGE,
            CoursePermission.COURSE_SELECT_RESOURCES,
            CoursePermission.COURSE_SELECT_PROFILES,
            CoursePermission.TERM_ADD,
            CoursePermission.TERM_REMOVE,
            CoursePermission.TERM_VIEW,
            CoursePermission.TERM_SELECT_IMAGE,
            CoursePermission.TERM_SELECT_RESOURCES,
            CoursePermission.TERM_SELECT_PROFILES,
        ]
    )

    COURSE_VIEW_PERMISSIONS = frozenset(
        [
            CoursePermission.COURSE_VIEW,
            CoursePermission.COURSE_VIEW_METADATA,
        ]
    )

    COURSE_MANAGE_PERMISSIONS = frozenset(
        [
            CoursePermission.COURSE_VIEW,
            CoursePermission.COURSE_REMOVE,
            CoursePermission.COURSE_EDIT_METADATA,
            CoursePermission.COURSE_VIEW_METADATA,
            CoursePermission.COURSE_SELECT_IMAGE,
            CoursePermission.COURSE_SELECT_RESOURCES,
            CoursePermission.COURSE_SELECT_PROFILES,
        ]
    )

    TERM_PERMISSIONS = frozenset(
        [
            # CoursePermission.TERM_ADD,
            CoursePermission.TERM_REMOVE,
            CoursePermission.TERM_VIEW,
            CoursePermission.TERM_SELECT_IMAGE,
            CoursePermission.TERM_SELECT_RESOURCES,
            CoursePermission.TERM_SELECT_PROFILES,
        ]
    )


COURSE_ROLE_PERMISSIONS: RolePermissions = {
    Role.HUB_ADMIN: CoursePermissionSets.ALL_PERMISSIONS,
    Role.COURSE_CREATOR: frozenset(
        [
            CoursePermission.ADD_COURSE,
            CoursePermission.COURSE_VIEW,
        ]
    ),
    Role.COURSE_OWNER: frozenset(
        CoursePermissionSets.COURSE_MANAGE_PERMISSIONS
        | CoursePermissionSets.TERM_PERMISSIONS
        | {CoursePermission.TERM_ADD}
    ),
    Role.INSTRUCTOR: frozenset(
        CoursePermissionSets.TERM_PERMISSIONS | CoursePermissionSets.COURSE_VIEW_PERMISSIONS
    ),
    Role.TEACHING_ASSISTANT: frozenset(
        {CoursePermission.TERM_VIEW} | CoursePermissionSets.COURSE_VIEW_PERMISSIONS
    ),
    Role.STUDENT: frozenset(),
    Role.OBSERVER: frozenset(
        {CoursePermission.TERM_VIEW} | CoursePermissionSets.COURSE_VIEW_PERMISSIONS
    ),
}
