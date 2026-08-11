from e2x_hub_rbac.api.membership_api import MembershipAPI as BaseMembershipAPI
from e2x_hub_rbac.auth import Role, RoleAssignment, UserLike


class MembershipAPI(BaseMembershipAPI):
    """Extended MembershipAPI with course-level owner management."""

    async def bootstrap_course_owner(self, course_id: str, username: str) -> None:
        """Bootstrap a course owner by adding the user to the course owners group."""
        role_assignment = RoleAssignment.course(
            role=Role.COURSE_OWNER,
            course_id=course_id,
        )
        await self.__add_role_assignment(role_assignment, [username])

    def get_role_assignments(self, user: UserLike) -> list[RoleAssignment]:
        """Get all role assignments for the user."""
        return self.permission_checker(user).assignments
