from __future__ import annotations

from typing import Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field, RootModel, model_validator

# --- Permission Model ---


class Permission(BaseModel):
    """Represents a permission in the RBAC system.

    A permission defines an action that can be performed on a resource,
    optionally with constraints (filters). Permissions follow the pattern:
    `action:resource!constraint_key=constraint_value`

    Examples:
        - "add:course-members!role=student" - Add students to course
        - "list:course-members" - List all course members
        - "spawn:profile!profile=grader_profile" - Spawn a specific profile

    Attributes:
        action: The action to perform (e.g., "add", "list", "remove", "spawn")
        resource: The resource being acted upon (e.g., "course-members", "profile")
        constraints: Optional filters to restrict the permission scope
    """

    action: str
    resource: str
    constraints: Optional[Dict[str, str]] = None

    @model_validator(mode="before")
    def parse_permission(cls, values):
        """Parse permission from string format.

        Supports string input like "add:course-members!role=student" and converts
        it to the Permission model with action, resource, and constraints.

        Args:
            values: Either a dict with permission fields or a string to parse

        Returns:
            Dict with parsed action, resource, and constraints
        """
        if isinstance(values, str):
            permission_str = values
            if "!" in permission_str:
                main, constraint_str = permission_str.split("!", 1)
                key, value = constraint_str.split("=", 1)
                constraints = {key: value}
            else:
                main = permission_str
                constraints = None

            action, resource = main.split(":", 1)
            return {"action": action, "resource": resource, "constraints": constraints}
        return values

    # --- Factory methods for common permissions ---
    # These provide type-safety and prevent typos

    @classmethod
    def add_course_members(cls, role: str) -> "Permission":
        """Permission to add members to a course with a specific role."""
        return cls(action="add", resource="course-members", constraints={"role": role})

    @classmethod
    def remove_course_members(cls, role: str) -> "Permission":
        """Permission to remove members from a course with a specific role."""
        return cls(action="remove", resource="course-members", constraints={"role": role})

    @classmethod
    def list_course_members(cls, role: Optional[str] = None) -> "Permission":
        """Permission to list course members, optionally filtered by role."""
        constraints = {"role": role} if role else None
        return cls(action="list", resource="course-members", constraints=constraints)

    @classmethod
    def spawn_profile(cls, profile: str) -> "Permission":
        """Permission to spawn a specific profile."""
        return cls(action="spawn", resource="profile", constraints={"profile": profile})

    @classmethod
    def view_course_metadata(cls) -> "Permission":
        """Permission to view course metadata."""
        return cls(action="view", resource="course-metadata")

    @classmethod
    def leave_course(cls) -> "Permission":
        """Permission to leave a course."""
        return cls(action="leave", resource="course")


# --- Default Permission Definitions ---

# Define built-in permission implications (subscopes)
# Following JupyterHub's terminology: a permission can have subscopes that are implied
# e.g., add:course-members implies list:course-members (you need to see members to add them)
DEFAULT_PERMISSION_DEFINITIONS = {
    "view:course-metadata": [],
    "add:course-members": ["list:course-members", "view:course-metadata"],
    "remove:course-members": ["list:course-members", "view:course-metadata"],
    "spawn:profile": [],
    "leave:course": [],
}


class PermissionDefinition(BaseModel):
    """Defines subscopes (implied permissions) for a permission.

    Aligned with JupyterHub's scope system where permissions can have subscopes.
    This allows defining permission hierarchies where granting one permission
    automatically grants related permissions.

    Example:
        custom:myservice:write has subscopes: [custom:myservice:read]
        This means granting write access automatically grants read access.

    Attributes:
        subscopes: List of permission strings that are implied by this permission
    """

    subscopes: List[str] = []


# --- Role Model ---


class Role(BaseModel):
    """Represents a role with permissions and priority-based hierarchy.

    Roles define sets of permissions with a priority level that determines
    their strength. Higher priority roles automatically include permissions
    from all lower priority roles, creating a natural hierarchy.

    For example, a 'course_admin' (priority 300) automatically gets all
    permissions from 'grader' (priority 200) and 'student' (priority 100).

    Attributes:
        priority: Numeric priority level (higher = stronger role)
        scopes: List of permissions directly granted to this role
    """

    priority: int = Field(..., description="Priority level, higher values indicate stronger roles")
    scopes: List[Permission] = []


# --- Roles Container (Root) ---


class RolesConfig(BaseModel):
    """Configuration for roles and permission definitions.

    This wrapper allows combining the roles dictionary with optional
    permission_definitions, since RootModel doesn't support extra fields.
    Used when loading from YAML with both roles and custom permission definitions.

    Attributes:
        roles: Dictionary mapping role names to Role objects
        permission_definitions: Optional custom permission definitions to override defaults
    """

    roles: Dict[str, Role] = Field(default_factory=dict)
    permission_definitions: Dict[str, PermissionDefinition] = Field(default_factory=dict)


class Roles(RootModel[Dict[str, Role]]):
    """Container for roles with permission checking and expansion.

    This is the main class for managing roles and checking permissions.
    It handles:
    - Role inheritance (roles can inherit from other roles)
    - Permission expansion (permissions can imply other permissions via subscopes)
    - Permission checking with constraint matching

    The class extends RootModel to act as a dictionary of role_name -> Role,
    while providing additional methods for permission management.

    Example:
        ```python
        roles = Roles(**yaml_config)

        # Check if user has permission
        if roles.has_permission(['grader'], Permission.add_course_members('student')):
            # User can add students
            pass

        # List all permissions for a role
        perms = roles.list_permissions('grader')
        ```
    """

    @model_validator(mode="before")
    @classmethod
    def validate_roles(cls, data):
        """Handle different input formats for roles configuration.

        This validator allows flexible input formats when loading from YAML:
        1. Direct dict of roles: {role_name: Role, ...}
        2. Nested with 'roles' key: {roles: {...}, permission_definitions: {...}}

        Args:
            data: Input data to validate

        Returns:
            Validated data in appropriate format for __init__
        """
        if isinstance(data, dict):
            # Check if this looks like a roles dict (has Role objects or role configs)
            # vs a config dict (has 'roles' and/or 'permission_definitions' keys)
            if "roles" in data or "permission_definitions" in data:
                # This is a config dict, keep as-is for __init__ to handle
                return data
            else:
                # This is a direct roles dict, wrap it for RootModel
                return data
        return data

    def __init__(self, root=None, **data):
        """Initialize Roles with optional permission_definitions.

        Handles multiple input patterns:
        - Direct roles dict from YAML: roles: {student: {...}, grader: {...}}
        - Config dict with permission_definitions: {roles: {...}, permission_definitions: {...}}

        Built-in permission definitions are always available and can be overridden
        by custom definitions in the config.

        Args:
            root: Dict of role_name -> Role, or None if using **data
            **data: Keyword arguments (roles dict or permission_definitions)
        """
        # Extract permission_definitions if present in data
        permission_definitions = data.pop("permission_definitions", None)

        # Handle different input patterns
        if root is None and data:
            # Data passed as kwargs (from YAML like roles: {student: {...}})
            root = data
            data = {}

        # Handle config dict pattern: {'roles': {...}, 'permission_definitions': {...}}
        if (
            isinstance(root, dict)
            and "roles" in root
            and not any(isinstance(v, Role) for v in root.values())
        ):
            config_dict = root
            root = config_dict.get("roles", {})
            if permission_definitions is None:
                permission_definitions = config_dict.get("permission_definitions", {})

        # Ensure root is not None
        if root is None:
            root = {}

        super().__init__(root=root)

        # Store permission definitions for building merged definitions
        self._permission_definitions = permission_definitions or {}
        self._merged_definitions = self._build_merged_definitions()

    def _build_merged_definitions(self) -> Dict[str, List[str]]:
        """Merge default definitions with user config (user config overrides defaults)."""
        merged = DEFAULT_PERMISSION_DEFINITIONS.copy()

        # Override/extend with user-defined permissions
        for key, defn in self._permission_definitions.items():
            if isinstance(defn, PermissionDefinition):
                merged[key] = defn.subscopes
            elif isinstance(defn, dict) and "subscopes" in defn:
                merged[key] = defn["subscopes"]

        return merged

    # --- Internal helpers ---

    def _normalize_roles(self, actor_roles: Union[str, List[str]]) -> List[str]:
        """Normalize role input to a list.

        Args:
            actor_roles: Single role name or list of role names

        Returns:
            List of role names
        """
        if isinstance(actor_roles, str):
            return [actor_roles]
        return actor_roles

    def _permissions_for_role(self, role: str) -> List[Permission]:
        """Get permissions directly assigned to a role.

        Does not include inherited permissions or subscopes.

        Args:
            role: Role name

        Returns:
            List of permissions assigned to this role
        """
        if role not in self.root:
            return []
        return self.root[role].scopes

    def _matches(
        self, perm: Permission, action: str, resource: str, constraints: Dict[str, str]
    ) -> bool:
        """Check if a permission matches the requested action, resource, and constraints.

        A permission matches if:
        - Action and resource match exactly
        - Permission has no constraints (grants access to all), OR
        - All requested constraints match the permission's constraints

        Args:
            perm: Permission to check
            action: Requested action
            resource: Requested resource
            constraints: Requested constraints

        Returns:
            True if the permission matches the request
        """
        if perm.action != action or perm.resource != resource:
            return False
        if not perm.constraints:
            return True
        for key, value in constraints.items():
            if perm.constraints.get(key) != value:
                return False
        return True

    def _all_roles_for(self, role: str) -> Set[str]:
        """Return role plus all roles with lower priority.

        With priority-based hierarchy, a role automatically includes
        permissions from all roles with lower priority values.

        Args:
            role: Role name

        Returns:
            Set containing the role and all lower-priority roles
        """
        if role not in self.root:
            return set()
        role_obj = self.root[role]
        role_priority = role_obj.priority

        # Include this role and all roles with lower priority
        included_roles = {role}
        for other_role_name, other_role_obj in self.root.items():
            if other_role_obj.priority < role_priority:
                included_roles.add(other_role_name)

        return included_roles

    def _expand_permission(self, perm: Permission) -> List[Permission]:
        """Expand a permission to include all implied subscope permissions.

        Following JupyterHub's subscopes pattern:
        - If add:course-members!role=student is granted
        - And add:course-members has subscope list:course-members
        - Then list:course-members (without constraint) is also granted

        This allows broader listing when you have specific add/delete permissions.
        """
        result = [perm]
        key = f"{perm.action}:{perm.resource}"

        if key in self._merged_definitions:
            for subscope_str in self._merged_definitions[key]:
                # Parse subscope permission (typically without constraints)
                # Use model_validator by passing string to Permission constructor
                subscope = Permission.model_validate(subscope_str)
                result.append(subscope)

        return result

    # --- Public API ---

    def list_permissions(self, actor_roles: Union[str, List[str]]) -> List[Permission]:
        """Return all effective permissions for a user with one or more roles.

        This method computes the complete set of permissions by:
        1. Collecting all roles (including inherited roles)
        2. Gathering permissions from each role
        3. Expanding permissions with their subscopes (implied permissions)
        4. Deduplicating the result

        Args:
            actor_roles: Single role name or list of role names

        Returns:
            List of all effective permissions (deduplicated)

        Example:
            ```python
            # Grader inherits from student and has add:course-members!role=student
            # add:course-members implies list:course-members
            perms = roles.list_permissions('grader')
            # Returns: student permissions + grader permissions + implied list permission
            ```
        """
        roles = self._normalize_roles(actor_roles)
        all_perms: List[Permission] = []
        seen = set()
        for role in roles:
            for r in self._all_roles_for(role):
                for p in self._permissions_for_role(r):
                    # Expand to include subscopes (implied permissions)
                    for expanded_p in self._expand_permission(p):
                        # dedup by (action, resource, constraints)
                        key = (
                            expanded_p.action,
                            expanded_p.resource,
                            frozenset((expanded_p.constraints or {}).items()),
                        )
                        if key not in seen:
                            seen.add(key)
                            all_perms.append(expanded_p)
        return all_perms

    def has_permission(self, actor_roles: Union[str, List[str]], permission: Permission) -> bool:
        """Check if actor has the requested permission.

        Checks if any of the actor's roles (including inherited roles and implied
        permissions via subscopes) grant the requested permission.

        Args:
            actor_roles: Single role name or list of role names
            permission: Permission to check

        Returns:
            True if the actor has the permission, False otherwise

        Example:
            ```python
            # Check if grader can add students
            can_add = roles.has_permission(
                'grader',
                Permission.add_course_members('student')
            )
            ```
        """
        for p in self.list_permissions(actor_roles):
            if self._matches(
                p, permission.action, permission.resource, permission.constraints or {}
            ):
                return True
        return False

    def get_strongest_role(self, roles: List[str]) -> Optional[str]:
        """Return the strongest role from a list of roles.

        The strongest role is the one with the highest priority value.

        Args:
            roles: List of role names

        Returns:
            The strongest role name, or None if the list is empty or contains only invalid roles

        Example:
            ```python
            # User has both student and grader roles
            strongest = roles.get_strongest_role(['student', 'grader'])
            # Returns: 'grader' (assuming grader has higher priority)
            ```
        """
        if not roles:
            return None

        valid_roles = [(r, self.root[r].priority) for r in roles if r in self.root]
        if not valid_roles:
            return None

        return max(valid_roles, key=lambda x: x[1])[0]
