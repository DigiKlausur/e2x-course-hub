from e2x_hub_rbac.auth import PermissionChecker
from e2x_hub_rbac.permissions.membership import MembershipPermission

from .schemas import (
    MembershipCapabilities,
    MembershipCollectionResponse,
)


class MembershipAssembler:
    def __init__(self, membership_permission_checker: PermissionChecker):
        self.membership_permission_checker = membership_permission_checker

    def collection(
        self,
        usernames: list[str],
        view_permission: MembershipPermission,
        add_permission: MembershipPermission,
        remove_permission: MembershipPermission,
        course_id: str | None = None,
        term_id: str | None = None,
    ) -> MembershipCollectionResponse:
        """
        Assemble a response for membership collections, including the list of usernames and the
        capabilities (view, add and remove) based on the provided permissions.

        Args:
            usernames (list[str]): List of usernames in the collection.
            view_permission (MembershipPermission): Permission required to view the collection.
            add_permission (MembershipPermission): Permission required to add members.
            remove_permission (MembershipPermission): Permission required to remove members.
            course_id (str | None): The ID of the course.
            term_id (str | None): The ID of the term.
        Returns:
            MembershipCollectionResponse: The assembled response containing usernames and
                capabilities.
        """
        return MembershipCollectionResponse(
            usernames=usernames,
            capabilities=MembershipCapabilities(
                view=self.membership_permission_checker.has_permission(
                    view_permission, course_id=course_id, term_id=term_id
                ),
                add=self.membership_permission_checker.has_permission(
                    add_permission, course_id=course_id, term_id=term_id
                ),
                remove=self.membership_permission_checker.has_permission(
                    remove_permission, course_id=course_id, term_id=term_id
                ),
            ),
        )
