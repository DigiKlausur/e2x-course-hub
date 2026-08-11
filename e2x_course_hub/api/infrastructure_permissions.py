from e2x_hub_rbac.auth.rbac import PermissionEnum, Role, RolePermissions, Scope


class InfrastructurePermission(PermissionEnum):
    """Permissions related to infrastructure management."""

    HUB_VIEW_IMAGE_CATALOG = ("hub.view_image_catalog", Scope.HUB)
    HUB_MANAGE_IMAGE_CATALOG = ("hub.manage_image_catalog", Scope.HUB)
    HUB_VIEW_RESOURCE_CATALOG = ("hub.view_resource_catalog", Scope.HUB)
    HUB_MANAGE_RESOURCE_CATALOG = ("hub.manage_resource_catalog", Scope.HUB)
    HUB_VIEW_PROFILE_CATALOG = ("hub.view_profile_catalog", Scope.HUB)
    HUB_MANAGE_PROFILE_CATALOG = ("hub.manage_profile_catalog", Scope.HUB)


class InfrastructurePermissionSets:
    """Predefined sets of permissions for infrastructure management."""

    VIEWER_PERMISSIONS = frozenset(
        [
            InfrastructurePermission.HUB_VIEW_IMAGE_CATALOG,
            InfrastructurePermission.HUB_VIEW_RESOURCE_CATALOG,
            InfrastructurePermission.HUB_VIEW_PROFILE_CATALOG,
        ]
    )

    MANAGER_PERMISSIONS = frozenset(
        [
            InfrastructurePermission.HUB_MANAGE_IMAGE_CATALOG,
            InfrastructurePermission.HUB_MANAGE_RESOURCE_CATALOG,
            InfrastructurePermission.HUB_MANAGE_PROFILE_CATALOG,
        ]
    )


INFRASTRUCTURE_ROLE_PERMISSIONS: RolePermissions = {
    Role.HUB_ADMIN: frozenset(
        InfrastructurePermissionSets.VIEWER_PERMISSIONS
        | InfrastructurePermissionSets.MANAGER_PERMISSIONS
    ),
    Role.COURSE_CREATOR: frozenset(InfrastructurePermissionSets.VIEWER_PERMISSIONS),
    Role.COURSE_OWNER: frozenset(InfrastructurePermissionSets.VIEWER_PERMISSIONS),
    Role.INSTRUCTOR: frozenset(InfrastructurePermissionSets.VIEWER_PERMISSIONS),
    Role.TEACHING_ASSISTANT: frozenset(
        [
            InfrastructurePermission.HUB_VIEW_IMAGE_CATALOG,
            InfrastructurePermission.HUB_VIEW_RESOURCE_CATALOG,
        ]
    ),
    Role.STUDENT: frozenset(),
    Role.OBSERVER: frozenset(InfrastructurePermissionSets.VIEWER_PERMISSIONS),
}
