from e2x_hub_rbac.auth import PermissionChecker, Role, UserLike

from ...api.role_permissions import ROLE_PERMISSIONS
from ..membership.schemas import MembershipCapabilities
from .model import Capability, MembershipCapabilityGroup


class CapabilityChecker:
    """Evaluates capabilities for one user.

    Built on the combined permission tables, so a single checker can answer for
    capabilities from every API. This is only for telling the user what they can
    do; each API still enforces its own permissions.
    """

    def __init__(self, checker: PermissionChecker):
        self._checker = checker

    @classmethod
    def for_user(cls, user: UserLike) -> "CapabilityChecker":
        return cls(PermissionChecker(user, ROLE_PERMISSIONS))

    def has(
        self, capability: Capability, course_id: str | None = None, term_id: str | None = None
    ) -> bool:
        return all(
            self._checker.has_permission(permission, course_id=course_id, term_id=term_id)
            for permission in capability.permissions
        )

    def membership(
        self,
        group: MembershipCapabilityGroup,
        course_id: str | None = None,
        term_id: str | None = None,
    ) -> MembershipCapabilities:
        return MembershipCapabilities(
            view=self.has(group.view, course_id, term_id),
            add=self.has(group.add, course_id, term_id),
            remove=self.has(group.remove, course_id, term_id),
        )


def role_has(role: Role, capability: Capability) -> bool:
    """Whether a role, placed at its own scope, has the capability.

    A lookup rather than a permission check: under the scope rules of
    e2x_hub_rbac, a role is granted each of its permissions at that permission's
    own level, so no course or term is needed.
    """
    return capability.permissions <= ROLE_PERMISSIONS[role]
