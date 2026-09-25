from e2x_hub_rbac.auth import PermissionChecker

from ...schema.course import TermConfig
from ..actions import TermActions, term_actions, user_can
from ..common.schemas import Environment
from .schemas import TermDetailResponse, TermSummaryResponse


class TermAssembler:
    def __init__(self, permission_checker: PermissionChecker):
        self.permission_checker = permission_checker

    def _actions(self, course_id: str, term_id: str) -> TermActions:
        return term_actions(user_can(self.permission_checker, course_id, term_id))

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
            resources=term_config.get_resource_selections(),
            profiles=term_config.get_profile_selections(),
        )

    def summary(self, course_id: str, term_id: str) -> TermSummaryResponse:
        """
        Assemble a summary representation of the term metadata, including actions.

        Args:
            course_id (str): The ID of the course to which the term belongs.
            term_id (str): The ID of the term to summarize.
        Returns:
            TermSummaryResponse: The assembled summary response containing term metadata and
                actions.
        """
        return TermSummaryResponse(
            course_id=course_id,
            term_id=term_id,
            actions=self._actions(course_id, term_id),
        )

    def detail(self, course_id: str, term_id: str, term_config: TermConfig) -> TermDetailResponse:
        """
        Assemble a detailed representation of the term metadata, including actions and
        environment selections.

        Args:
            course_id (str): The ID of the course to which the term belongs.
            term_id (str): The ID of the term to detail.
            term_config (TermConfig): The configuration of the term, including selected environment.
        Returns:
            TermDetailResponse: The assembled detailed response containing term metadata,
                actions, and environment selections.
        """
        return TermDetailResponse(
            course_id=course_id,
            term_id=term_id,
            environment=self.environment(term_config),
            actions=self._actions(course_id, term_id),
        )
