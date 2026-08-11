from e2x_hub_rbac.auth.rbac import PermissionEnum, Role, RolePermissions, Scope


class InfrastructurePermission(PermissionEnum):
    """Permissions related to infrastructure management."""

    LMS_VIEW_IMAGE_CATALOG = ("lms.view_image_catalog", Scope.LMS)
    LMS_MANAGE_IMAGE_CATALOG = ("lms.manage_image_catalog", Scope.LMS)
    LMS_VIEW_RESOURCE_CATALOG = ("lms.view_resource_catalog", Scope.LMS)
    LMS_MANAGE_RESOURCE_CATALOG = ("lms.manage_resource_catalog", Scope.LMS)
    LMS_VIEW_PROFILE_CATALOG = ("lms.view_profile_catalog", Scope.LMS)
    LMS_MANAGE_PROFILE_CATALOG = ("lms.manage_profile_catalog", Scope.LMS)


class InfrastructurePermissionSets:
    """Predefined sets of permissions for infrastructure management."""

    VIEWER_PERMISSIONS = frozenset(
        [
            InfrastructurePermission.LMS_VIEW_IMAGE_CATALOG,
            InfrastructurePermission.LMS_VIEW_RESOURCE_CATALOG,
            InfrastructurePermission.LMS_VIEW_PROFILE_CATALOG,
        ]
    )

    MANAGER_PERMISSIONS = frozenset(
        [
            InfrastructurePermission.LMS_MANAGE_IMAGE_CATALOG,
            InfrastructurePermission.LMS_MANAGE_RESOURCE_CATALOG,
            InfrastructurePermission.LMS_MANAGE_PROFILE_CATALOG,
        ]
    )


INFRASTRUCTURE_ROLE_PERMISSIONS: RolePermissions = {
    Role.LMS_ADMIN: frozenset(
        InfrastructurePermissionSets.VIEWER_PERMISSIONS
        | InfrastructurePermissionSets.MANAGER_PERMISSIONS
    ),
    Role.COURSE_CREATOR: frozenset(InfrastructurePermissionSets.VIEWER_PERMISSIONS),
    Role.COURSE_OWNER: frozenset(InfrastructurePermissionSets.VIEWER_PERMISSIONS),
    Role.INSTRUCTOR: frozenset(InfrastructurePermissionSets.VIEWER_PERMISSIONS),
    Role.TEACHING_ASSISTANT: frozenset(
        [
            InfrastructurePermission.LMS_VIEW_IMAGE_CATALOG,
            InfrastructurePermission.LMS_VIEW_RESOURCE_CATALOG,
        ]
    ),
    Role.STUDENT: frozenset(),
    Role.OBSERVER: frozenset(InfrastructurePermissionSets.VIEWER_PERMISSIONS),
}
