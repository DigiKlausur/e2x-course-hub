"""Which permissions each action needs.

The same builders serve the current user (the assemblers) and the role preview
(the roles route); only the ``can`` passed in differs.
"""

from e2x_hub_rbac.auth import PermissionProtocol
from e2x_hub_rbac.permissions import MembershipPermission

from ...api.course_permissions import CoursePermission
from ...api.infrastructure_permissions import InfrastructurePermission
from ...api.spawn_permissions import SpawnPermission
from .can import Can
from .models import (
    CatalogActions,
    CourseActions,
    CourseEnvironmentActions,
    CourseMembersActions,
    CourseMetadataActions,
    CourseTermsActions,
    LmsActions,
    LmsCatalogsActions,
    LmsCoursesActions,
    LmsMembersActions,
    MemberListActions,
    TermActions,
    TermEnvironmentActions,
    TermMembersActions,
    TermSpawnActions,
)


def member_list(
    can: Can, list: PermissionProtocol, add: PermissionProtocol, remove: PermissionProtocol
) -> MemberListActions:
    return MemberListActions(list=can(list), add=can(add), remove=can(remove))


def catalog(can: Can, view: PermissionProtocol, manage: PermissionProtocol) -> CatalogActions:
    return CatalogActions(view=can(view), manage=can(manage))


def lms_actions(can: Can) -> LmsActions:
    return LmsActions(
        courses=LmsCoursesActions(create=can(CoursePermission.ADD_COURSE)),
        members=LmsMembersActions(
            lmsAdmins=member_list(
                can,
                list=MembershipPermission.LIST_LMS_ADMINS,
                add=MembershipPermission.ADD_LMS_ADMIN,
                remove=MembershipPermission.REMOVE_LMS_ADMIN,
            ),
            courseCreators=member_list(
                can,
                list=MembershipPermission.LIST_COURSE_CREATORS,
                add=MembershipPermission.ADD_COURSE_CREATOR,
                remove=MembershipPermission.REMOVE_COURSE_CREATOR,
            ),
        ),
        catalogs=LmsCatalogsActions(
            images=catalog(
                can,
                view=InfrastructurePermission.LMS_VIEW_IMAGE_CATALOG,
                manage=InfrastructurePermission.LMS_MANAGE_IMAGE_CATALOG,
            ),
            resources=catalog(
                can,
                view=InfrastructurePermission.LMS_VIEW_RESOURCE_CATALOG,
                manage=InfrastructurePermission.LMS_MANAGE_RESOURCE_CATALOG,
            ),
            profiles=catalog(
                can,
                view=InfrastructurePermission.LMS_VIEW_PROFILE_CATALOG,
                manage=InfrastructurePermission.LMS_MANAGE_PROFILE_CATALOG,
            ),
        ),
    )


def course_actions(can: Can) -> CourseActions:
    return CourseActions(
        view=can(CoursePermission.COURSE_VIEW),
        remove=can(CoursePermission.COURSE_REMOVE),
        metadata=CourseMetadataActions(
            view=can(CoursePermission.COURSE_VIEW_METADATA),
            edit=can(CoursePermission.COURSE_EDIT_METADATA),
        ),
        environment=CourseEnvironmentActions(
            select=can(
                CoursePermission.COURSE_SELECT_IMAGE,
                CoursePermission.COURSE_SELECT_RESOURCES,
                CoursePermission.COURSE_SELECT_PROFILES,
            ),
        ),
        terms=CourseTermsActions(add=can(CoursePermission.TERM_ADD)),
        members=CourseMembersActions(
            courseOwners=member_list(
                can,
                list=MembershipPermission.LIST_COURSE_OWNERS,
                add=MembershipPermission.ADD_COURSE_OWNER,
                remove=MembershipPermission.REMOVE_COURSE_OWNER,
            ),
        ),
    )


def term_actions(can: Can) -> TermActions:
    return TermActions(
        view=can(CoursePermission.TERM_VIEW),
        remove=can(CoursePermission.TERM_REMOVE),
        environment=TermEnvironmentActions(
            select=can(
                CoursePermission.TERM_SELECT_IMAGE,
                CoursePermission.TERM_SELECT_RESOURCES,
                CoursePermission.TERM_SELECT_PROFILES,
            ),
        ),
        spawn=TermSpawnActions(
            student=can(SpawnPermission.SPAWN_STUDENT_PROFILE),
            grader=can(SpawnPermission.SPAWN_GRADER_PROFILE),
            readonlyGrader=can(SpawnPermission.SPAWN_GRADER_READONLY_PROFILE),
        ),
        members=TermMembersActions(
            instructors=member_list(
                can,
                list=MembershipPermission.LIST_INSTRUCTORS,
                add=MembershipPermission.ADD_INSTRUCTOR,
                remove=MembershipPermission.REMOVE_INSTRUCTOR,
            ),
            teachingAssistants=member_list(
                can,
                list=MembershipPermission.LIST_TEACHING_ASSISTANTS,
                add=MembershipPermission.ADD_TEACHING_ASSISTANT,
                remove=MembershipPermission.REMOVE_TEACHING_ASSISTANT,
            ),
            students=member_list(
                can,
                list=MembershipPermission.LIST_STUDENTS,
                add=MembershipPermission.ADD_STUDENT,
                remove=MembershipPermission.REMOVE_STUDENT,
            ),
            observers=member_list(
                can,
                list=MembershipPermission.LIST_OBSERVERS,
                add=MembershipPermission.ADD_OBSERVER,
                remove=MembershipPermission.REMOVE_OBSERVER,
            ),
        ),
    )
