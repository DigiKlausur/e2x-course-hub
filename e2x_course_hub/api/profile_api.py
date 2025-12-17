from typing import Dict, List

from ..schema.profile import BaseProfile, ResolvedProfile
from ..schema.roles import Permission
from ..schema.user import User
from .base_api import BaseAPI


class ProfileAPI(BaseAPI):
    """API for managing and retrieving user profiles.

    Handles profile resolution with placeholder substitution and permission
    checking for profile spawning.
    """

    def _can_spawn_profile(self, user: User, course_id: str, term_id: str, profile_id: str) -> bool:
        """Check if the user has permission to spawn the given profile.

        Args:
            user: The user attempting to spawn the profile
            course_id: The course ID
            term_id: The term ID
            profile_id: The profile ID

        Returns:
            True if the user can spawn the profile, False otherwise
        """
        return self.has_permission_in_course(
            user=user,
            course_id=course_id,
            term_id=term_id,
            permission=Permission.spawn_profile(profile_id),
        )

    def get_profile(
        self, user: User, course_id: str, term_id: str, profile_id: str
    ) -> ResolvedProfile:
        """Retrieve and resolve a specific profile for the user.

        Args:
            user: The user requesting the profile
            course_id: The course ID
            term_id: The term ID
            profile_id: The profile ID

        Returns:
            The resolved profile with placeholders substituted

        Raises:
            PermissionError: If the user cannot spawn this profile
        """
        self.require_permission(
            user=user,
            course_id=course_id,
            term_id=term_id,
            permission=Permission.spawn_profile(profile_id),
        )
        profile = self.server.courses[course_id].terms[term_id][profile_id]
        return ResolvedProfile.from_profile(
            profile, user, {"course_id": course_id, "term_id": term_id}
        )

    def _get_accessible_profiles_for_term(
        self, user: User, course_id: str, term_id: str, term_profiles: Dict[str, BaseProfile]
    ) -> List[ResolvedProfile]:
        """Get all profiles the user can spawn in a specific term.

        Args:
            user: The user requesting profiles
            course_id: The course ID
            term_id: The term ID
            term_profiles: Dictionary of profile_id -> BaseProfile for the term

        Returns:
            List of resolved profiles the user can access
        """
        accessible = []
        for profile_id, profile in term_profiles.items():
            if self._can_spawn_profile(user, course_id, term_id, profile_id):
                resolved = ResolvedProfile.from_profile(
                    profile, user, {"course_id": course_id, "term_id": term_id}
                )
                # resolved = self._resolve_profile_placeholders(profile, user, course_id, term_id)
                accessible.append(resolved)
        return accessible

    def list_profiles(self, user: User) -> Dict[str, Dict[str, List[ResolvedProfile]]]:
        """Retrieve all profiles the user can spawn, organized by course and term.

        Profile placeholders are resolved for the user. Only courses and terms
        with at least one accessible profile are included.

        Args:
            user: The user requesting the profile list

        Returns:
            Nested dictionary: course_id -> term_id -> list of accessible profiles
        """
        result = {}

        for course_id, course in self.server.courses.items():
            course_profiles = {}

            for term_id, term_profiles in course.terms.items():
                accessible = self._get_accessible_profiles_for_term(
                    user, course_id, term_id, term_profiles
                )
                if accessible:
                    course_profiles[term_id] = accessible

            if course_profiles:
                result[course_id] = course_profiles

        return result
