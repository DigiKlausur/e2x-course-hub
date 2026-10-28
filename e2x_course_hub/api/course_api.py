from logging import Logger
from typing import List, Optional

from e2x_hub_rbac.api import BaseAPI
from e2x_hub_rbac.auth import UserLike
from e2x_hub_rbac.auth.decorator import require_permission
from sqlalchemy.orm import Session

from ..contract.providers import InfrastructureCatalogProvider
from ..db.repository import CourseRepository
from ..errors import (
    CourseExistsError,
    CourseNotFoundError,
    ImageFamilyNotFoundError,
    TermExistsError,
    TermNotFoundError,
)
from ..schema.catalog import InfrastructureCatalogOptions
from ..schema.course import CourseConfig, CourseMetadata, StudentAccessPeriod, TermConfig
from ..schema.selection import (
    ImageSelection,
    PartialImageSelection,
    SpawnRoleSelection,
    SpawnSelection,
)
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
        self.infrastructure_options.image_family_options.assert_family_and_tag_exists(
            course.image_family, tag=None
        )
        self._assert_spawn_role_selections_exist(course.spawn_role_selections)

    def _assert_spawn_role_selections_exist(
        self, spawn_role_selections: dict[SpawnRole, SpawnRoleSelection]
    ):
        """Assert that the resource tiers and profiles exist in the catalog.

        Raises:
            ValueError: If a resource tier or profile does not exist in the catalog
        """
        for spawn_role, spawn_selection in spawn_role_selections.items():
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
        access_period: Optional[StudentAccessPeriod] = None,
        session: Optional[Session] = None,
    ) -> TermConfig:
        """Add a new term with the course's image family, resources and profiles.

        The term gets the image family's current default tag, so new terms never
        start with an outdated tag.

        Args:
            user: The user adding the term
            course_id: The course ID
            term_id: The term ID
            access_period: When students may spawn the term; empty means no limit
        Raises:
            TermExistsError: If a term with the same ID already exists
            ImageFamilyNotFoundError: If the course's image family is not in the catalog
        Returns:
            The TermConfig object for the newly added term
        """
        course = self._get_course(course_id, session=session)
        if term_id in course.terms:
            raise TermExistsError(course_id, term_id)
        families = self.infrastructure_options.image_family_options.families
        if course.image_family not in families:
            raise ImageFamilyNotFoundError(course.image_family)
        term = TermConfig(
            image=ImageSelection(
                family=course.image_family,
                tag=families[course.image_family].default_tag,
            ),
            spawn_role_selections=course.spawn_role_selections,
        )
        if access_period is not None:
            term.student_access_start = access_period.student_access_start
            term.student_access_end = access_period.student_access_end
        self._assert_spawn_role_selections_exist(term.spawn_role_selections)
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
    def set_course_image(
        self,
        user: UserLike,
        course_id: str,
        image_family: str,
        session: Optional[Session] = None,
    ):
        """Set the image family that new terms of the specified course get.

        Args:
            user: The user setting the course image
            course_id: The course ID
            image_family: The image family; new terms get its default tag
        """
        course = self._get_course(course_id, session=session)
        self.infrastructure_options.image_family_options.assert_family_and_tag_exists(
            image_family, tag=None
        )
        course.image_family = image_family
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
            current_selection = course.spawn_role_selections[spawn_role]
            if current_selection.resource_tier_name == tier_name:
                continue  # No change needed
            self.infrastructure_options.assert_resource_tier_exists(spawn_role, tier_name)

            course.spawn_role_selections[spawn_role] = SpawnRoleSelection(
                resource_tier_name=tier_name, profile_name=current_selection.profile_name
            )
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
            current_selection = course.spawn_role_selections[spawn_role]
            if current_selection.profile_name == profile_name:
                continue  # No change needed
            self.infrastructure_options.assert_profile_exists(spawn_role, profile_name)
            course.spawn_role_selections[spawn_role] = SpawnRoleSelection(
                resource_tier_name=current_selection.resource_tier_name, profile_name=profile_name
            )
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
            current_selection = term.spawn_role_selections[spawn_role]
            if current_selection.profile_name == profile_name:
                continue  # No change needed
            self.infrastructure_options.assert_profile_exists(spawn_role, profile_name)
            term.spawn_role_selections[spawn_role] = SpawnRoleSelection(
                resource_tier_name=current_selection.resource_tier_name, profile_name=profile_name
            )
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
        _, term = self._get_course_and_term(course_id, term_id, session=session)
        return term.image

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
        _, term = self._get_course_and_term(course_id, term_id, session=session)
        spawn_selections = {}
        for spawn_role in SpawnRole:
            term_selection = term.get_spawn_selection(spawn_role)
            default_selection = self.infrastructure_options.get_default_spawn_selection(spawn_role)
            spawn_selections[spawn_role] = term_selection.with_fallback(default_selection)
        return spawn_selections

    @require_permission(CoursePermission.TERM_SELECT_RESOURCES)
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
            current_selection = term.spawn_role_selections[spawn_role]
            if current_selection.resource_tier_name == tier_name:
                continue  # No change needed
            self.infrastructure_options.assert_resource_tier_exists(spawn_role, tier_name)

            term.spawn_role_selections[spawn_role] = SpawnRoleSelection(
                resource_tier_name=tier_name, profile_name=current_selection.profile_name
            )
        self.course_repository.update_course(course_id, course, session=session)

    @require_permission(CoursePermission.TERM_EDIT_ACCESS_PERIOD)
    def set_term_student_access_period(
        self,
        user: UserLike,
        course_id: str,
        term_id: str,
        access_period: StudentAccessPeriod,
        session: Optional[Session] = None,
    ):
        """Set the period in which students may spawn the specified term.

        Args:
            user: The user setting the access period
            course_id: The course ID
            term_id: The term ID
            access_period: The new access period; empty bounds mean no limit on that side
        """
        course, term = self._get_course_and_term(course_id, term_id, session=session)
        term.student_access_start = access_period.student_access_start
        term.student_access_end = access_period.student_access_end
        self.course_repository.update_course(course_id, course, session=session)
