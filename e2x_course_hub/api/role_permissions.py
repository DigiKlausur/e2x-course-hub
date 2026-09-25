"""All permission tables combined, to answer what a role may do across every API.

Each API enforces its own table. This module only reads the same tables, so it
cannot disagree with what the APIs check.
"""

from e2x_hub_rbac.auth import PermissionProtocol, Role, RolePermissions
from e2x_hub_rbac.permissions import MEMBERSHIP_ROLE_PERMISSIONS

from .course_permissions import COURSE_ROLE_PERMISSIONS
from .infrastructure_permissions import INFRASTRUCTURE_ROLE_PERMISSIONS
from .spawn_permissions import SPAWN_ROLE_PERMISSIONS

ROLE_PERMISSION_TABLES: tuple[RolePermissions, ...] = (
    COURSE_ROLE_PERMISSIONS,
    MEMBERSHIP_ROLE_PERMISSIONS,
    INFRASTRUCTURE_ROLE_PERMISSIONS,
    SPAWN_ROLE_PERMISSIONS,
)

# Each role mapped to the union of its permissions from all tables.
ROLE_PERMISSIONS: RolePermissions = {
    role: frozenset().union(*(table.get(role, frozenset()) for table in ROLE_PERMISSION_TABLES))
    for role in Role
}

ALL_PERMISSIONS: frozenset[PermissionProtocol] = frozenset().union(*ROLE_PERMISSIONS.values())
