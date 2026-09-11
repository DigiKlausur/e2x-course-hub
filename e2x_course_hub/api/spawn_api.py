from e2x_hub_rbac.api import BaseAPI
from e2x_hub_rbac.auth import UserLike

from ..contract.providers import SpawnOfferingProvider
from ..db.repository import CourseRepository
from ..schema.selection import CourseReference, SpawnOffering, SpawnSelection
from .spawn_permissions import (
    PERMISSION_TO_SPAWN,
    SPAWN_ROLE_PERMISSIONS,
)


class SpawnAPI(BaseAPI, SpawnOfferingProvider):
    def __init__(self, course_repository: CourseRepository, logger=None):
        super().__init__(logger=logger, role_permissions=SPAWN_ROLE_PERMISSIONS)
        self._course_repository = course_repository

    def get_spawn_offerings_in_course(self, user: UserLike, course_id: str) -> list[SpawnOffering]:
        course = self._course_repository.get_course(course_id)
        if course is None:
            raise ValueError(f"Course with ID '{course_id}' not found.")

        spawn_offerings = []
        for term_id in course.terms:
            for permission, (spawn_role, course_readonly) in PERMISSION_TO_SPAWN.items():
                if self.has_permission(user, permission, course_id=course_id, term_id=term_id):
                    term = self._course_repository.get_term(
                        course_id, term_id
                    )  # Ensure term exists
                    if term is None:
                        continue  # Skip if term does not exist
                    image = term.image

                    spawn_selection = SpawnSelection(
                        spawn_role=spawn_role,
                        course_readonly=course_readonly,
                        image=image,
                        resource_tier_name=term.spawn_role_selections[
                            spawn_role
                        ].resource_tier_name,
                        profile_name=term.spawn_role_selections[spawn_role].profile_name,
                    )
                    spawn_offerings.append(
                        SpawnOffering(
                            course=CourseReference(
                                course_id=course.metadata.course_id,
                                term_id=term_id,
                                course_display_name=course.metadata.course_name,
                                course_description=course.metadata.description,
                            ),
                            selection=spawn_selection,
                        )
                    )
        return spawn_offerings

    def get_spawn_offerings(self, user: UserLike) -> list[SpawnOffering]:
        spawn_offerings = []
        for course_id in self._course_repository.list_course_ids():
            spawn_offerings.extend(self.get_spawn_offerings_in_course(user, course_id))
        return spawn_offerings
