from e2x_hub_rbac.auth import PermissionChecker

from ...schema.course import CourseConfig, CourseMetadata
from ..actions import CourseActions, LmsActions, course_actions, lms_actions, user_can
from ..common.schemas import Environment
from ..terms.assembler import TermAssembler
from .schemas import (
    CourseCollectionResponse,
    CourseDetailResponse,
    CourseSummaryResponse,
)


class CourseAssembler:
    def __init__(
        self,
        permission_checker: PermissionChecker,
        term_assembler: TermAssembler,
    ):
        self.permission_checker = permission_checker
        self.term_assembler = term_assembler

    def _actions(self, course_id: str) -> CourseActions:
        return course_actions(user_can(self.permission_checker, course_id))

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
            resources=course_config.get_resource_selections(),
            profiles=course_config.get_profile_selections(),
        )

    def summary(self, course_metadata: CourseMetadata) -> CourseSummaryResponse:
        """
        Assemble a summary representation of the course metadata, including actions.

        Args:
            course_metadata (CourseMetadata): The course metadata to summarize.
        Returns:
            CourseSummaryResponse: The assembled summary response containing course metadata and
                actions.
        """
        return CourseSummaryResponse(
            metadata=course_metadata,
            actions=self._actions(course_metadata.course_id),
        )

    def detail(self, course_config: CourseConfig) -> CourseDetailResponse:
        """
        Assemble a detailed representation of the course configuration, including actions.

        Args:
            course_config (CourseConfig): The course configuration to detail.
        Returns:
            CourseDetailResponse: The assembled detailed response containing course configuration
                and actions.
        """
        return CourseDetailResponse(
            metadata=course_config.metadata,
            environment=self.environment(course_config),
            terms=[
                self.term_assembler.summary(course_config.metadata.course_id, term_id)
                for term_id in course_config.terms.keys()
            ],
            actions=self._actions(course_config.metadata.course_id),
        )


class CourseCollectionAssembler:
    def __init__(
        self,
        permission_checker: PermissionChecker,
        course_assembler: CourseAssembler,
    ):
        self.permission_checker = permission_checker
        self.course_assembler = course_assembler

    def _actions(self) -> LmsActions:
        return lms_actions(user_can(self.permission_checker))

    def collection(self, course_metadata_list: list[CourseMetadata]) -> CourseCollectionResponse:
        """
        Assemble a collection of course summaries, including the actions for the collection.

        Args:
            course_metadata_list (list[CourseMetadata]): A list of course metadata to summarize.
        Returns:
            CourseCollectionResponse: The assembled collection response containing course summaries
                and collection actions.
        """
        return CourseCollectionResponse(
            courses=[self.course_assembler.summary(metadata) for metadata in course_metadata_list],
            actions=self._actions(),
        )
