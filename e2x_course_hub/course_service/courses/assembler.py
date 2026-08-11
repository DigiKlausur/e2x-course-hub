from e2x_hub_rbac.auth import PermissionChecker
from e2x_hub_rbac.permissions.membership import MembershipPermission

from ...api.course_permissions import CoursePermission
from ...schema.course import CourseConfig, CourseMetadata
from ..common.schemas import Environment
from ..terms.assembler import TermAssembler
from .schemas import (
    CourseCapabilities,
    CourseCollectionCapabilities,
    CourseCollectionResponse,
    CourseDetailResponse,
    CourseSummaryResponse,
)


class CourseAssembler:
    def __init__(
        self,
        course_permission_checker: PermissionChecker,
        membership_permission_checker: PermissionChecker,
        term_assembler: TermAssembler,
    ):
        self.course_permission_checker = course_permission_checker
        self.membership_permission_checker = membership_permission_checker
        self.term_assembler = term_assembler

    def _capabilities(self, course_id: str) -> CourseCapabilities:
        return CourseCapabilities(
            editMetadata=self.course_permission_checker.has_permission(
                permission=CoursePermission.COURSE_EDIT_METADATA,
                course_id=course_id,
            ),
            removeCourse=self.course_permission_checker.has_permission(
                permission=CoursePermission.COURSE_REMOVE,
                course_id=course_id,
            ),
            selectEnvironment=all(
                self.course_permission_checker.has_permission(
                    permission=permission,
                    course_id=course_id,
                )
                for permission in [
                    CoursePermission.COURSE_SELECT_IMAGE,
                    CoursePermission.COURSE_SELECT_RESOURCES,
                    CoursePermission.COURSE_SELECT_PROFILES,
                ]
            ),
            viewCourseOwners=self.membership_permission_checker.has_permission(
                permission=MembershipPermission.LIST_COURSE_OWNERS,
                course_id=course_id,
            ),
            manageCourseOwners=all(
                self.membership_permission_checker.has_permission(
                    permission=permission,
                    course_id=course_id,
                )
                for permission in [
                    MembershipPermission.ADD_COURSE_OWNER,
                    MembershipPermission.REMOVE_COURSE_OWNER,
                ]
            ),
            addTerm=self.course_permission_checker.has_permission(
                permission=CoursePermission.TERM_ADD,
                course_id=course_id,
            ),
        )

    def environment(self, course_config: CourseConfig) -> Environment:
        """
        Assemble the environment configuration of a course.

        Args:
            course_config (CourseConfig): The course configuration containing environment details.
        Returns:
            Environment: The assembled environment response containing image and resources.
        """
        return Environment(
            image=course_config.image,
            resources=course_config.resources,
        )

    def summary(self, course_metadata: CourseMetadata) -> CourseSummaryResponse:
        """
        Assemble a summary representation of the course metadata, including capabilities.

        Args:
            course_metadata (CourseMetadata): The course metadata to summarize.
        Returns:
            CourseSummaryResponse: The assembled summary response containing course metadata and
                capabilities.
        """
        return CourseSummaryResponse(
            metadata=course_metadata,
            capabilities=self._capabilities(course_metadata.course_id),
        )

    def detail(self, course_config: CourseConfig) -> CourseDetailResponse:
        """
        Assemble a detailed representation of the course configuration, including capabilities.

        Args:
            course_config (CourseConfig): The course configuration to detail.
        Returns:
            CourseDetailResponse: The assembled detailed response containing course configuration
                and capabilities.
        """
        return CourseDetailResponse(
            metadata=course_config.metadata,
            environment=self.environment(course_config),
            terms=[
                self.term_assembler.summary(course_config.metadata.course_id, term_id)
                for term_id in course_config.terms.keys()
            ],
            capabilities=self._capabilities(course_config.metadata.course_id),
        )


class CourseCollectionAssembler:
    def __init__(
        self, course_permission_checker: PermissionChecker, course_assembler: CourseAssembler
    ):
        self.course_permission_checker = course_permission_checker
        self.course_assembler = course_assembler

    def _capabilities(self) -> CourseCollectionCapabilities:
        """
        Assemble the capabilities for the course collection.

        Returns:
            CourseCollectionCapabilities: The assembled capabilities for the course collection.
        """
        return CourseCollectionCapabilities(
            createCourse=self.course_permission_checker.has_permission(
                permission=CoursePermission.ADD_COURSE
            )
        )

    def collection(self, course_metadata_list: list[CourseMetadata]) -> CourseCollectionResponse:
        """
        Assemble a collection of course summaries, including capabilities for the collection.

        Args:
            course_metadata_list (list[CourseMetadata]): A list of course metadata to summarize.
        Returns:
            CourseCollectionResponse: The assembled collection response containing course summaries
                and collection capabilities.
        """
        return CourseCollectionResponse(
            courses=[self.course_assembler.summary(metadata) for metadata in course_metadata_list],
            capabilities=self._capabilities(),
        )
