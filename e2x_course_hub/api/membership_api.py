from e2x_hub_rbac.api.membership_api import GroupNotFoundError
from e2x_hub_rbac.api.membership_api import MembershipAPI as BaseMembershipAPI
from e2x_hub_rbac.auth import Role, RoleAssignment, Scope


class MembershipAPI(BaseMembershipAPI):
    """Extended MembershipAPI with course-level owner management."""

    async def __remove_all_role_assignment_members(self, role_assignment: RoleAssignment):
        """Remove all members from a role assignment."""
        try:
            current_members = await self.__list_role_assignment_members(role_assignment)
            await self.__remove_role_assignment(role_assignment, current_members)
        except GroupNotFoundError:
            # Group doesn't exist, so nothing to remove
            return

    async def bootstrap_course_owner(self, course_id: str, username: str) -> None:
        """Bootstrap a course owner by adding the user to the course owners group."""
        role_assignment = RoleAssignment.course(
            role=Role.COURSE_OWNER,
            course_id=course_id,
        )
        await self.__add_role_assignment(role_assignment, [username])

    async def remove_term_members(self, course_id: str, term_id: str) -> None:
        """Remove all members from a term-level role assignment."""
        term_roles = [role for role in Role if role.scope is Scope.TERM]
        for role in term_roles:
            role_assignment = RoleAssignment.term(
                role=role,
                course_id=course_id,
                term_id=term_id,
            )
            await self.__remove_all_role_assignment_members(role_assignment)

    async def remove_course_members(self, course_id: str, term_ids: list[str]) -> None:
        """Remove all members from a course-level role assignment."""
        for term_id in term_ids:
            await self.remove_term_members(course_id, term_id)
        course_roles = [role for role in Role if role.scope is Scope.COURSE]
        for role in course_roles:
            role_assignment = RoleAssignment.course(
                role=role,
                course_id=course_id,
            )
            await self.__remove_all_role_assignment_members(role_assignment)
