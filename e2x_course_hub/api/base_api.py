from logging import Logger, getLogger
from typing import List, Optional

from ..schema.roles import Permission
from ..schema.server import Server
from ..schema.user import User
from .errors import APIPermissionError


class BaseAPI:
    """Base class for all API classes providing common functionality.

    Provides access to the server configuration and common permission
    checking utilities for course-based operations.

    Attributes:
        server_config_file: The path to the server configuration file
        server: The Server configuration containing courses, profiles, and roles
    """

    def __init__(self, server: Server, logger: Optional[Logger] = None):
        """Initialize the API with server configuration.

        Args:
            server: The Server configuration object
            logger: Optional logger for logging purposes
        """
        if logger is None:
            logger = getLogger(__name__)
        self.server = server

    def has_permission_in_course(
        self, user: User, course_id: str, term_id: str, permission: Permission
    ) -> bool:
        """Check if the user has the specified permission in the course context.

        Args:
            user: The user requesting the permission check
            course_id: The course ID context
            term_id: The term ID context
            permission: The permission to check

        Returns:
            True if the user has the permission, False otherwise
        """
        return self.server.roles.has_permission(
            actor_roles=user.get_roles_in_course(course_id, term_id), permission=permission
        )

    def require_permission(
        self, user: User, course_id: str, term_id: str, permission: Permission
    ) -> None:
        """Require that the user has the specified permission, raise error if not.

        This is a convenience method that checks permission and raises
        PermissionError with a descriptive message if the check fails.

        Args:
            user: The user requesting the permission check
            course_id: The course ID context
            term_id: The term ID context
            permission: The permission to check

        Raises:
            APIPermissionError: If the user does not have the required permission
        """
        if not self.has_permission_in_course(user, course_id, term_id, permission):
            raise APIPermissionError(
                user=user.username,
                action=permission.action,
                resource=permission.resource,
                course_id=course_id,
                term_id=term_id,
            )

    def list_permissions(self, user: User, course_id: str, term_id: str) -> List[Permission]:
        """List all permissions the user has in the specified course context.

        Args:
            user: The user requesting the permission list
            course_id: The course ID context
            term_id: The term ID context
        Returns:
            List of permissions the user has in the course context
        """
        actor_roles = user.get_roles_in_course(course_id, term_id)
        permissions = self.server.roles.list_permissions(actor_roles=actor_roles)
        # Only take the most powerful permission for each action/resource pair
        # That means if there is a permission without constraints, take that one
        # over a permission with constraints
        # We want to end up with a dictionary of (action, resource) -> list of permissions
        unique_permissions = {}
        for perm in permissions:
            key = (perm.action, perm.resource)
            if key not in unique_permissions:
                unique_permissions[key] = [perm]
            else:
                unique_permissions[key].append(perm)
        final_permissions = []
        for perms in unique_permissions.values():
            # Check if any permission has no constraints
            no_constraint_perms = [p for p in perms if not p.constraints]
            if no_constraint_perms:
                final_permissions.append(no_constraint_perms[0])
            else:
                final_permissions.extend(perms)
        return final_permissions
