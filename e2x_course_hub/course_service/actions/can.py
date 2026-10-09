from typing import Protocol

from e2x_hub_rbac.auth import PermissionChecker, PermissionProtocol, Role

from ...api.role_permissions import ROLE_PERMISSIONS


class Can(Protocol):
    """Whether all of the given permissions are granted."""

    def __call__(self, *permissions: PermissionProtocol) -> bool: ...


def user_can(
    checker: PermissionChecker, course_id: str | None = None, term_id: str | None = None
) -> Can:
    """For the current user, in the given course and term."""

    def can(*permissions: PermissionProtocol) -> bool:
        return all(
            checker.has_permission(permission, course_id=course_id, term_id=term_id)
            for permission in permissions
        )

    return can


def role_can(role: Role) -> Can:
    """For a role placed at its own scope, e.g. to preview it before granting it."""

    def can(*permissions: PermissionProtocol) -> bool:
        return set(permissions) <= ROLE_PERMISSIONS[role]

    return can
