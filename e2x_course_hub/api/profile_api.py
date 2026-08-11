from typing import Dict, List, Optional

from e2x_hub_rbac.auth import UserLike
from e2x_hub_rbac.auth.decorator import require_permission

from ..errors import CourseNotFoundError, RoleNotFoundError, TermNotFoundError
from ..schema.course import CourseConfig
from ..schema.enums import SpawnRole
from ..schema.infrastructure import Runtime
from ..schema.profile import SpawnProfile
from ..schema.user import UserCourseContext
from ..utils import resolve_placeholders
from .base import APIWithContext
from .profile_permissions import SPAWN_PROFILE_ROLE_PERMISSIONS, SpawnProfilePermission


class ProfileAPI(APIWithContext):
    def __init__(self, context, logger=None):
        super().__init__(
            context=context, role_permissions=SPAWN_PROFILE_ROLE_PERMISSIONS, logger=logger
        )

    def __get_course(self, course_id: str):
        course = self.context.get_course(course_id)
        if course is None:
            raise CourseNotFoundError(course_id)
        return course

    def __assert_term_exists(self, course: CourseConfig, term_id: str):
        if term_id not in course.terms:
            raise TermNotFoundError(course.metadata.course_id, term_id)

    def __get_grader_terms_in_course(self, user: UserLike, course_id: str) -> list[str]:
        course = self.__get_course(course_id)

        grader_terms = []
        for term_id in course.terms:
            if self.has_permission(
                user,
                SpawnProfilePermission.SPAWN_GRADER_PROFILE,
                course_id=course_id,
                term_id=term_id,
            ):
                grader_terms.append(term_id)
        return grader_terms

    @require_permission(SpawnProfilePermission.SPAWN_GRADER_PROFILE)
    def get_grader_term_profile(
        self,
        user: UserLike,
        course_id: str,
        term_id: str,
        archive_term_ids: Optional[List[str]] = None,
        roles: Optional[List[str]] = None,
    ) -> SpawnProfile:
        course = self.__get_course(course_id)
        self.__assert_term_exists(course, term_id)

        role = SpawnRole.GRADER

        profile = self.context.profile_catalog.get_grader_profile(
            course.get_term_profile_selection(term_id)
        )
        image = self.context.infrastructure_catalog.get_image_for_role(
            role, course.get_term_image_selection(term_id)
        )
        resources = self.context.infrastructure_catalog.get_resources_for_role(
            role, course.get_term_resource_selection(term_id)
        )

        if image is None:
            raise ValueError(
                f"No image selected for graders in term '{term_id}' of course '{course_id}'"
            )

        return profile.resolve(
            image=image,
            resources=resources,
            mount_catalog=self.context.mount_catalog,
            ctx=UserCourseContext(username=user.username, course_id=course_id, term_id=term_id),
            archive_term_ids=archive_term_ids,
            roles=roles,
        )

    @require_permission(SpawnProfilePermission.SPAWN_STUDENT_PROFILE)
    def get_student_term_profile(
        self, user: UserLike, course_id: str, term_id: str
    ) -> SpawnProfile:
        course = self.__get_course(course_id)
        self.__assert_term_exists(course, term_id)

        role = SpawnRole.STUDENT

        profile = self.context.profile_catalog.get_student_profile(
            course.get_term_profile_selection(term_id)
        )
        image = self.context.infrastructure_catalog.get_image_for_role(
            role, course.get_term_image_selection(term_id)
        )
        resources = self.context.infrastructure_catalog.get_resources_for_role(
            role, course.get_term_resource_selection(term_id)
        )

        if image is None:
            raise ValueError(
                f"No image selected for students in term '{term_id}' of course '{course_id}'"
            )

        return profile.resolve(
            image=image,
            resources=resources,
            mount_catalog=self.context.mount_catalog,
            ctx=UserCourseContext(username=user.username, course_id=course_id, term_id=term_id),
        )

    @require_permission(SpawnProfilePermission.SPAWN_OBSERVER_PROFILE)
    def get_observer_term_profile(
        self, user: UserLike, course_id: str, term_id: str
    ) -> SpawnProfile:
        course = self.__get_course(course_id)
        self.__assert_term_exists(course, term_id)

        # Observer: same grader profile/image/resources, all mounts readonly except grader_home
        profile = self.context.profile_catalog.get_grader_profile(
            course.get_term_profile_selection(term_id)
        )
        image = self.context.infrastructure_catalog.get_image_for_role(
            SpawnRole.GRADER, course.get_term_image_selection(term_id)
        )
        resources = self.context.infrastructure_catalog.get_resources_for_role(
            SpawnRole.GRADER, course.get_term_resource_selection(term_id)
        )

        if image is None:
            raise ValueError(
                f"No image selected for observers in term '{term_id}' of course '{course_id}'"
            )

        ctx = UserCourseContext(username=user.username, course_id=course_id, term_id=term_id)
        mounts = [
            mount if name == "grader_home" else mount.as_readonly()
            for name in profile.get_all_mounts()
            for mount in [self.context.mount_catalog.resolve(name, ctx)]
        ]
        observer_display_name = f"{profile.display_name} (Readonly)"
        return SpawnProfile(
            spawn_role=SpawnRole.OBSERVER.value,
            display_name=observer_display_name,
            runtime=Runtime(
                image=image,
                resources=resources,
                environment=resolve_placeholders(profile.environment, ctx=ctx.model_dump()),
            ),
            mounts=mounts,
        )

    def get_profile(
        self, user: UserLike, course_id: str, term_id: str, spawn_role: str
    ) -> SpawnProfile:
        if spawn_role == SpawnRole.STUDENT.value:
            return self.get_student_term_profile(user=user, course_id=course_id, term_id=term_id)
        elif spawn_role == SpawnRole.GRADER.value:
            grader_terms = self.__get_grader_terms_in_course(user, course_id)
            archive_term_ids = [t for t in grader_terms if t != term_id]
            roles = self.permission_checker(user).get_roles_in_term(course_id, term_id)

            return self.get_grader_term_profile(
                user=user,
                course_id=course_id,
                term_id=term_id,
                archive_term_ids=archive_term_ids,
                roles=roles,
            )
        elif spawn_role == SpawnRole.OBSERVER.value:
            return self.get_observer_term_profile(user=user, course_id=course_id, term_id=term_id)
        else:
            raise RoleNotFoundError(role_id=spawn_role)

    def list_course_profiles(self, user: UserLike, course_id: str) -> Dict[str, List[SpawnProfile]]:
        course = self.__get_course(course_id)
        spawn_profiles = {}
        grader_terms = self.__get_grader_terms_in_course(user, course_id)
        for term_id in course.terms:
            term_roles = self.permission_checker(user).get_roles_in_term(course_id, term_id)
            if self.has_permission(
                user,
                SpawnProfilePermission.SPAWN_STUDENT_PROFILE,
                course_id=course_id,
                term_id=term_id,
            ):
                spawn_profiles.setdefault(term_id, []).append(
                    self.get_student_term_profile(user=user, course_id=course_id, term_id=term_id)
                )
            if self.has_permission(
                user,
                SpawnProfilePermission.SPAWN_GRADER_PROFILE,
                course_id=course_id,
                term_id=term_id,
            ):
                archive_term_ids = [t for t in grader_terms if t != term_id]
                spawn_profiles.setdefault(term_id, []).append(
                    self.get_grader_term_profile(
                        user=user,
                        course_id=course_id,
                        term_id=term_id,
                        archive_term_ids=archive_term_ids,
                        roles=term_roles,
                    )
                )
            if self.has_permission(
                user,
                SpawnProfilePermission.SPAWN_OBSERVER_PROFILE,
                course_id=course_id,
                term_id=term_id,
            ):
                spawn_profiles.setdefault(term_id, []).append(
                    self.get_observer_term_profile(user=user, course_id=course_id, term_id=term_id)
                )
        return spawn_profiles

    def list_profiles(self, user: UserLike) -> Dict[str, Dict[str, List[SpawnProfile]]]:
        courses = self.context.list_course_ids()
        profiles = {}
        for course_id in courses:
            course_profiles = self.list_course_profiles(user, course_id)
            if course_profiles:
                profiles[course_id] = course_profiles
        return profiles
