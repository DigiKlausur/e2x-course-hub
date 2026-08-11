from e2x_hub_rbac.auth import PermissionChecker
from e2x_hub_rbac.permissions.membership import MembershipPermission

from ...api.course_permissions import CoursePermission
from ...schema.course import TermConfig
from ..common.schemas import Environment
from .schemas import (
    TermCapabilities,
    TermDetailResponse,
    TermMembershipCapabilities,
    TermSummaryCapabilities,
    TermSummaryResponse,
)


class TermAssembler:
    def __init__(
        self,
        course_permission_checker: PermissionChecker,
        membership_permission_checker: PermissionChecker,
    ):
        self.course_permission_checker = course_permission_checker
        self.membership_permission_checker = membership_permission_checker

    def _membership_capabilities(self, course_id: str, term_id: str) -> TermMembershipCapabilities:
        return TermMembershipCapabilities(
            viewInstructors=self.membership_permission_checker.has_permission(
                permission=MembershipPermission.LIST_INSTRUCTORS,
                course_id=course_id,
                term_id=term_id,
            ),
            manageInstructors=all(
                self.membership_permission_checker.has_permission(
                    permission=permission,
                    course_id=course_id,
                    term_id=term_id,
                )
                for permission in [
                    MembershipPermission.ADD_INSTRUCTOR,
                    MembershipPermission.REMOVE_INSTRUCTOR,
                ]
            ),
            viewTeachingAssistants=self.membership_permission_checker.has_permission(
                permission=MembershipPermission.LIST_TEACHING_ASSISTANTS,
                course_id=course_id,
                term_id=term_id,
            ),
            manageTeachingAssistants=all(
                self.membership_permission_checker.has_permission(
                    permission=permission,
                    course_id=course_id,
                    term_id=term_id,
                )
                for permission in [
                    MembershipPermission.ADD_TEACHING_ASSISTANT,
                    MembershipPermission.REMOVE_TEACHING_ASSISTANT,
                ]
            ),
            viewStudents=self.membership_permission_checker.has_permission(
                permission=MembershipPermission.LIST_STUDENTS,
                course_id=course_id,
                term_id=term_id,
            ),
            manageStudents=all(
                self.membership_permission_checker.has_permission(
                    permission=permission,
                    course_id=course_id,
                    term_id=term_id,
                )
                for permission in [
                    MembershipPermission.ADD_STUDENT,
                    MembershipPermission.REMOVE_STUDENT,
                ]
            ),
            viewObservers=self.membership_permission_checker.has_permission(
                permission=MembershipPermission.LIST_OBSERVERS,
                course_id=course_id,
                term_id=term_id,
            ),
            manageObservers=all(
                self.membership_permission_checker.has_permission(
                    permission=permission,
                    course_id=course_id,
                    term_id=term_id,
                )
                for permission in [
                    MembershipPermission.ADD_OBSERVER,
                    MembershipPermission.REMOVE_OBSERVER,
                ]
            ),
        )

    def _summary_capabilities(self, course_id: str, term_id: str) -> TermSummaryCapabilities:
        return TermSummaryCapabilities(
            viewTerm=self.course_permission_checker.has_permission(
                permission=CoursePermission.TERM_VIEW,
                course_id=course_id,
                term_id=term_id,
            ),
            removeTerm=self.course_permission_checker.has_permission(
                permission=CoursePermission.TERM_REMOVE,
                course_id=course_id,
                term_id=term_id,
            ),
        )

    def _capabilities(self, course_id: str, term_id: str) -> TermCapabilities:
        return TermCapabilities(
            viewTerm=self.course_permission_checker.has_permission(
                permission=CoursePermission.TERM_VIEW,
                course_id=course_id,
                term_id=term_id,
            ),
            removeTerm=self.course_permission_checker.has_permission(
                permission=CoursePermission.TERM_REMOVE,
                course_id=course_id,
                term_id=term_id,
            ),
            membership=self._membership_capabilities(course_id, term_id),
        )

    def environment(self, term_config: TermConfig) -> Environment:
        """
        Assemble the environment configuration of a term.

        Args:
            term_config (TermConfig): The configuration of the term, including selected environment.
        Returns:
            EnvironmentSelection: The assembled environment selection containing image, resources,
                and profiles.
        """
        return Environment(
            image=term_config.image,
            resources=term_config.resources,
        )

    def summary(self, course_id: str, term_id: str) -> TermSummaryResponse:
        """
        Assemble a summary representation of the term metadata, including capabilities.

        Args:
            course_id (str): The ID of the course to which the term belongs.
            term_id (str): The ID of the term to summarize.
        Returns:
            TermSummaryResponse: The assembled summary response containing term metadata and
                capabilities.
        """
        return TermSummaryResponse(
            course_id=course_id,
            term_id=term_id,
            capabilities=self._summary_capabilities(course_id, term_id),
        )

    def detail(self, course_id: str, term_id: str, term_config: TermConfig) -> TermDetailResponse:
        """
        Assemble a detailed representation of the term metadata, including capabilities and
        environment selections.

        Args:
            course_id (str): The ID of the course to which the term belongs.
            term_id (str): The ID of the term to detail.
            term_config (TermConfig): The configuration of the term, including selected environment.
        Returns:
            TermDetailResponse: The assembled detailed response containing term metadata,
                capabilities, and environment selections.
        """
        return TermDetailResponse(
            course_id=course_id,
            term_id=term_id,
            environment=self.environment(term_config),
            capabilities=self._capabilities(course_id, term_id),
        )
