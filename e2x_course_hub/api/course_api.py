from logging import Logger
from typing import List, Optional

from e2x_hub_rbac.api import BaseAPI
from e2x_hub_rbac.auth import UserLike
from e2x_hub_rbac.auth.decorator import require_permission
from sqlalchemy.orm import Session

from ..contract.providers import InfrastructureCatalogProvider
from ..db.repository import CourseRepository
from ..errors import CourseExistsError, CourseNotFoundError, TermExistsError, TermNotFoundError
from ..schema.catalog import InfrastructureCatalogOptions
from ..schema.course import CourseConfig, CourseMetadata, TermConfig
from ..schema.selection import ImageSelection, PartialImageSelection, SpawnSelection
from ..schema.types import SpawnRole
from .course_permissions import COURSE_ROLE_PERMISSIONS, CoursePermission


class CourseAPI(BaseAPI):
    """API for managing course memberships.

    Handles adding, removing, and listing course members with proper
    permission checking and JupyterHub group synchronization.

    Attributes:
        hub_api: JupyterHub API client for group management
    """

    def __init__(
        self,
        course_repository: CourseRepository,
        infrastructure_catalog_provider: InfrastructureCatalogProvider,
        logger: Optional[Logger] = None,
    ):
        super().__init__(logger=logger, role_permissions=COURSE_ROLE_PERMISSIONS)
        self.course_repository = course_repository
        self._infrastructure_catalog_provider = infrastructure_catalog_provider

    @property
    def infrastructure_options(self) -> InfrastructureCatalogOptions:
        return self._infrastructure_catalog_provider.get_infrastructure_catalog()

    def assert_infrastructure_options_exist(self, course: CourseConfig):
        """Assert that the infrastructure options specified in the course exist in the catalog.

        Args:
            course: The CourseConfig object containing the course configuration
        Raises:
            ValueError: If any of the specified infrastructure options do not exist in the catalog
        """
        self.infrastructure_options.assert_image_selection_exists(course.image)
        for spawn_role, spawn_selection in course.spawn_role_selections.items():
            self.infrastructure_options.assert_resource_tier_exists(
                spawn_role, spawn_selection.resource_tier_name
            )
            self.infrastructure_options.assert_profile_exists(
                spawn_role, spawn_selection.profile_name
            )

    def _get_course(self, course_id: str, session: Optional[Session] = None) -> CourseConfig:
        """Get a course by ID, raises CourseNotFoundError if not found."""
        course = self.course_repository.get_course(course_id, session=session)
        if not course:
            raise CourseNotFoundError(course_id)
        return course

    def _get_course_and_term(
        self, course_id: str, term_id: str, session: Optional[Session] = None
    ) -> tuple[CourseConfig, TermConfig]:
        course = self.course_repository.get_course(course_id, session=session)
        if course is None:
            raise CourseNotFoundError(course_id)
        term = course.terms.get(term_id)
        if term is None:
            raise TermNotFoundError(course_id, term_id)
        return course, term

    def get_permissions_in_course(
        self, user: UserLike, course_id: str, session: Optional[Session] = None
    ) -> List[str]:
        """Get a list of permissions the user has in the specified course.

        Args:
            user: The user for whom to check permissions
            course_id: The course ID
        Returns:
            List of Permission enums representing the permissions the user has in the course
        """
        checker = self.permission_checker(user)
        permissions = checker.get_permissions_in_course(course_id=course_id)
        return list([p.code for p in permissions])

    def get_permissions_in_term(
        self, user: UserLike, course_id: str, term_id: str, session: Optional[Session] = None
    ) -> List[str]:
        """Get a list of permissions the user has in the specified term.

        Args:
            user: The user for whom to check permissions
            course_id: The course ID
            term_id: The term ID
        Returns:
            List of Permission enums representing the permissions the user has in the term
        """
        checker = self.permission_checker(user)
        permissions = checker.get_permissions_in_term(course_id=course_id, term_id=term_id)
        return list([p.code for p in permissions])

    @require_permission(CoursePermission.COURSE_VIEW_METADATA)
    def get_course_metadata(
        self, user: UserLike, course_id: str, session: Optional[Session] = None
    ) -> CourseMetadata:
        """Retrieve metadata for the specified course.

        Args:
            user: The user requesting the course metadata
            course_id: The course ID
        Returns:
            CourseMetadata object containing the course metadata
        """
        course = self.course_repository.get_course(
            course_id, session=session
        )  # We know this exists from the previous check
        if course is None:
            raise CourseNotFoundError(course_id)
        return course.metadata

    @require_permission(CoursePermission.COURSE_EDIT_METADATA)
    def set_course_metadata(
        self,
        user: UserLike,
        course_id: str,
        course_name: Optional[str] = None,
        description: Optional[str] = None,
        session: Optional[Session] = None,
    ):
        """Set the metadata for the specified course.

        Args:
            user: The user setting the course metadata
            course_id: The course ID
            course_name: The new course name
            description: The new course description
        """
        course = self._get_course(course_id, session=session)
        course.metadata = CourseMetadata(
            course_id=course_id,
            course_name=course_name if course_name is not None else course.metadata.course_name,
            description=description if description is not None else course.metadata.description,
        )
        self.course_repository.update_course(course_id, course, session=session)

    @require_permission(CoursePermission.ADD_COURSE)
    def add_course(self, user: UserLike, course: CourseConfig, session: Optional[Session] = None):
        """Add a new course with the specified ID and name.

        Args:
            user: The user adding the course
            course: The CourseConfig object containing the course configuration
        Raises:
            CourseExistsError: If a course with the same ID already exists
        """
        if self.course_repository.get_course(course.metadata.course_id, session=session):
            raise CourseExistsError(course.metadata.course_id)
        self.assert_infrastructure_options_exist(course)
        self.course_repository.create_course(course, session=session)

    @require_permission(CoursePermission.COURSE_REMOVE)
    def remove_course(self, user: UserLike, course_id: str, session: Optional[Session] = None):
        """Remove the specified course.

        Args:
            user: The user removing the course
            course_id: The course ID
        Raises:
            CourseNotFoundError: If the course does not exist
        """
        _ = self._get_course(course_id, session=session)
        self.course_repository.delete_course(course_id, session=session)

    @require_permission(CoursePermission.COURSE_VIEW)
    def get_course(
        self, user: UserLike, course_id: str, session: Optional[Session] = None
    ) -> CourseConfig:
        """Retrieve the full course configuration for the specified course.

        Args:
            user: The user requesting the course configuration
            course_id: The course ID
        Returns:
            CourseConfig object containing the full course configuration
        """
        return self._get_course(course_id, session=session)

    def list_courses(
        self, user: UserLike, session: Optional[Session] = None
    ) -> List[CourseMetadata]:
        """List all courses the user has access to.

        Args:
            user: The user requesting the course list
        Returns:
            List of CourseMetadata objects for courses the user has access to
        """
        all_courses = self.course_repository.list_courses(session=session)
        accessible_courses = []
        for course_id, course in all_courses.items():
            if self.has_permission(user, CoursePermission.COURSE_VIEW, course_id=course_id):
                accessible_courses.append(course.metadata)
        return accessible_courses

    @require_permission(CoursePermission.TERM_ADD)
    def add_term(
        self,
        user: UserLike,
        course_id: str,
        term_id: str,
        term: Optional[TermConfig] = None,
        session: Optional[Session] = None,
    ) -> TermConfig:
        """Add a new term with the specified ID and name.

        Args:
            user: The user adding the term
            course_id: The course ID
            term_id: The term ID
            term: The TermConfig object containing the term configuration
        Raises:
            TermExistsError: If a term with the same ID already exists
        Returns:
            The TermConfig object for the newly added term
        """
        course = self._get_course(course_id, session=session)
        if term_id in course.terms:
            raise TermExistsError(course_id, term_id)
        if not term:
            term = TermConfig(
                image=course.image,
                spawn_role_selections=course.spawn_role_selections,
            )
        self.assert_infrastructure_options_exist(course)
        updated_course_config = self.course_repository.add_term(
            course_id, term_id, term, session=session
        )
        return updated_course_config.terms[term_id]

    @require_permission(CoursePermission.TERM_REMOVE)
    def remove_term(
        self, user: UserLike, course_id: str, term_id: str, session: Optional[Session] = None
    ):
        """Remove the specified term.

        Args:
            user: The user removing the term
            course_id: The course ID
            term_id: The term ID
        Raises:
            CourseNotFoundError: If the course does not exist
            TermNotFoundError: If the term does not exist within the course
        """
        _, _ = self._get_course_and_term(course_id, term_id, session=session)
        self.course_repository.remove_term(course_id, term_id, session=session)

    @require_permission(CoursePermission.TERM_VIEW)
    def get_term(
        self, user: UserLike, course_id: str, term_id: str, session: Optional[Session] = None
    ) -> TermConfig:
        """Retrieve the full term configuration for the specified term.

        Args:
            user: The user requesting the term configuration
            course_id: The course ID
            term_id: The term ID
        Returns:
            TermConfig object containing the full term configuration
        """
        _, term = self._get_course_and_term(course_id, term_id, session=session)
        return term

    @require_permission(CoursePermission.COURSE_SELECT_IMAGE)
    def get_course_image(
        self, user: UserLike, course_id: str, session: Optional[Session] = None
    ) -> ImageSelection:
        """Retrieve the image for the specified course.

        Args:
            user: The user requesting the course image
            course_id: The course ID
        Returns:
            ImageSelection object containing the course image information
        """
        course = self._get_course(course_id, session=session)
        image_families = self.infrastructure_options.image_family_options
        catalog_default_image = image_families.default_family
        if course.image:
            return course.image
        return ImageSelection(
            family=catalog_default_image,
            tag=image_families.families[catalog_default_image].default_tag,
        )

    @require_permission(CoursePermission.COURSE_VIEW)
    def get_course_spawn_selections(
        self, user: UserLike, course_id: str, session: Optional[Session] = None
    ) -> dict[SpawnRole, SpawnSelection]:
        """Retrieve the spawn selections for the specified course.

        Args:
            user: The user requesting the course spawn selections
            course_id: The course ID
        Returns:
            A dictionary mapping spawn roles to their respective SpawnSelection objects for the
              course
        """
        course = self._get_course(course_id, session=session)
        spawn_selections = {}
        for spawn_role in SpawnRole:
            course_selection = course.get_spawn_selection(spawn_role)
            default_selection = self.infrastructure_options.get_default_spawn_selection(spawn_role)
            spawn_selections[spawn_role] = course_selection.with_fallback(default_selection)
        return spawn_selections

    @require_permission(CoursePermission.COURSE_SELECT_IMAGE)
    def set_course_image(
        self,
        user: UserLike,
        course_id: str,
        image_selection: PartialImageSelection,
        session: Optional[Session] = None,
    ):
        """Set the default image for the specified course.

        Args:
            user: The user setting the course image
            course_id: The course ID
            image_selection: The image selection object containing the new image information
        """
        course = self._get_course(course_id, session=session)
        resolved_image_selection = ImageSelection(
            family=image_selection.family,
            tag=image_selection.tag
            or self.infrastructure_options.image_family_options.families[
                image_selection.family
            ].default_tag,
        )
        self.infrastructure_options.assert_image_selection_exists(resolved_image_selection)
        course.image = resolved_image_selection
        self.course_repository.update_course(course_id, course, session=session)

    @require_permission(CoursePermission.COURSE_SELECT_RESOURCES)
    def set_course_resources(
        self,
        user: UserLike,
        course_id: str,
        resources_selection: dict[SpawnRole, str],
        session: Optional[Session] = None,
    ):
        """Set the default resource tier for the specified course.

        Args:
            user: The user setting the course resources
            course_id: The course ID
            resources_selection: The resource selection object containing the new resource tier
                information
        """
        course = self._get_course(course_id, session=session)
        for spawn_role, tier_name in resources_selection.items():
            self.infrastructure_options.assert_resource_tier_exists(spawn_role, tier_name)
            course.spawn_role_selections[spawn_role].resource_tier_name = tier_name
        self.course_repository.update_course(course_id, course, session=session)

    @require_permission(CoursePermission.COURSE_SELECT_PROFILES)
    def set_course_profiles(
        self,
        user: UserLike,
        course_id: str,
        profiles_selection: dict[SpawnRole, str],
        session: Optional[Session] = None,
    ):
        """Set the default profile selection for the specified course.

        Args:
            user: The user setting the course profiles
            course_id: The course ID
            profiles_selection: The profile selection object containing the new profile selection
                information
        """
        course = self._get_course(course_id, session=session)
        for spawn_role, profile_name in profiles_selection.items():
            self.infrastructure_options.assert_profile_exists(spawn_role, profile_name)
            course.spawn_role_selections[spawn_role].profile_name = profile_name
        self.course_repository.update_course(course_id, course, session=session)

    @require_permission(CoursePermission.TERM_SELECT_PROFILES)
    def set_term_profiles(
        self,
        user: UserLike,
        course_id: str,
        term_id: str,
        profiles_selection: dict[SpawnRole, str],
        session: Optional[Session] = None,
    ):
        """Set the default profile selection for the specified term.

        Args:
            user: The user setting the term profiles
            course_id: The course ID
            term_id: The term ID
            profiles_selection: The profile selection object containing the new profile selection
                information
        """
        course, term = self._get_course_and_term(course_id, term_id, session=session)
        for spawn_role, profile_name in profiles_selection.items():
            self.infrastructure_options.assert_profile_exists(spawn_role, profile_name)
            term.spawn_role_selections[spawn_role].profile_name = profile_name
        self.course_repository.update_course(course_id, course, session=session)

    @require_permission(CoursePermission.TERM_VIEW)
    def get_term_image(
        self, user: UserLike, course_id: str, term_id: str, session: Optional[Session] = None
    ) -> ImageSelection:
        """Retrieve the image for the specified term.

        Args:
            user: The user requesting the term image
            course_id: The course ID
            term_id: The term ID
        Returns:
            ImageSelection object containing the term image information
        """
        course, term = self._get_course_and_term(course_id, term_id, session=session)
        return term.image or course.image

    @require_permission(CoursePermission.TERM_SELECT_IMAGE)
    def set_term_image(
        self,
        user: UserLike,
        course_id: str,
        term_id: str,
        image_selection: PartialImageSelection,
        session: Optional[Session] = None,
    ):
        """Set the image for the specified term.

        Args:
            user: The user setting the term image
            course_id: The course ID
            term_id: The term ID
            image_selection: The image selection object containing the new image information
        """
        course, term = self._get_course_and_term(course_id, term_id, session=session)
        resolved_image_selection = ImageSelection(
            family=image_selection.family,
            tag=image_selection.tag
            or self.infrastructure_options.image_family_options.families[
                image_selection.family
            ].default_tag,
        )
        self.infrastructure_options.assert_image_selection_exists(resolved_image_selection)
        term.image = resolved_image_selection
        self.course_repository.update_course(course_id, course, session=session)

    @require_permission(CoursePermission.TERM_VIEW)
    def get_term_spawn_selections(
        self, user: UserLike, course_id: str, term_id: str, session: Optional[Session] = None
    ) -> dict[SpawnRole, SpawnSelection]:
        """Retrieve the spawn selections for the specified term.

        Args:
            user: The user requesting the term spawn selections
            course_id: The course ID
            term_id: The term ID
        Returns:
            A dictionary mapping spawn roles to their respective SpawnSelection objects for the term
        """
        course, term = self._get_course_and_term(course_id, term_id, session=session)
        spawn_selections = {}
        for spawn_role in SpawnRole:
            term_selection = term.get_spawn_selection(spawn_role)
            course_selection = course.get_spawn_selection(spawn_role)
            default_selection = self.infrastructure_options.get_default_spawn_selection(spawn_role)
            spawn_selections[spawn_role] = term_selection.with_fallback(
                course_selection.with_fallback(default_selection)
            )
        return spawn_selections

    @require_permission(CoursePermission.TERM_SELECT_PROFILES)
    def set_term_resources(
        self,
        user: UserLike,
        course_id: str,
        term_id: str,
        resources_selection: dict[SpawnRole, str],
        session: Optional[Session] = None,
    ):
        """Set the resource tier for the specified term.

        Args:
            user: The user setting the term resources
            course_id: The course ID
            term_id: The term ID
            resources_selection: The resource selection object containing the new resource tier
                information
        """
        course, term = self._get_course_and_term(course_id, term_id, session=session)
        for spawn_role, tier_name in resources_selection.items():
            self.infrastructure_options.assert_resource_tier_exists(spawn_role, tier_name)
            term.spawn_role_selections[spawn_role].resource_tier_name = tier_name
        self.course_repository.update_course(course_id, course, session=session)
