from e2x_hub_rbac.permissions.membership import MembershipPermission
from fastapi import APIRouter

from ..common.dependency_types import CurrentUser, MembershipAPIDep
from .dependencies import MembershipAssemblerDep
from .schemas import MembershipCollectionResponse, MembershipPatch

router = APIRouter(
    prefix="/v1",
    tags=["Courses"],
)

lms_prefix = "/lms"
course_prefix = "/courses/{course_id}"
term_prefix = course_prefix + "/terms/{term_id}"


@router.get(lms_prefix + "/admins", response_model=MembershipCollectionResponse)
async def list_lms_admins(
    user: CurrentUser,
    membership_api: MembershipAPIDep,
    membership_assembler: MembershipAssemblerDep,
):
    return membership_assembler.collection(
        usernames=await membership_api.list_lms_admins(user),
        view_permission=MembershipPermission.LIST_LMS_ADMINS,
        manage_permission=(
            MembershipPermission.ADD_LMS_ADMIN,
            MembershipPermission.REMOVE_LMS_ADMIN,
        ),
    )


@router.patch(lms_prefix + "/admins", status_code=204)
async def patch_lms_admins(
    body: MembershipPatch,
    user: CurrentUser,
    membership_api: MembershipAPIDep,
):
    if body.add:
        await membership_api.add_lms_admins(user, body.add)
    if body.remove:
        await membership_api.remove_lms_admins(user, body.remove)


@router.get(lms_prefix + "/course-creators", response_model=MembershipCollectionResponse)
async def list_lms_course_creators(
    user: CurrentUser,
    membership_api: MembershipAPIDep,
    membership_assembler: MembershipAssemblerDep,
):
    return membership_assembler.collection(
        usernames=await membership_api.list_course_creators(user),
        view_permission=MembershipPermission.LIST_COURSE_CREATORS,
        manage_permission=(
            MembershipPermission.ADD_COURSE_CREATOR,
            MembershipPermission.REMOVE_COURSE_CREATOR,
        ),
    )


@router.patch(lms_prefix + "/course-creators", status_code=204)
async def patch_lms_course_creators(
    body: MembershipPatch,
    user: CurrentUser,
    membership_api: MembershipAPIDep,
):
    if body.add:
        await membership_api.add_course_creators(user, body.add)
    if body.remove:
        await membership_api.remove_course_creators(user, body.remove)


@router.get(course_prefix + "/owners", response_model=MembershipCollectionResponse)
async def list_course_owners(
    course_id: str,
    user: CurrentUser,
    membership_api: MembershipAPIDep,
    membership_assembler: MembershipAssemblerDep,
):
    return membership_assembler.collection(
        usernames=await membership_api.list_course_owners(user, course_id),
        view_permission=MembershipPermission.LIST_COURSE_OWNERS,
        manage_permission=(
            MembershipPermission.ADD_COURSE_OWNER,
            MembershipPermission.REMOVE_COURSE_OWNER,
        ),
        course_id=course_id,
    )


@router.patch(course_prefix + "/owners", status_code=204)
async def patch_course_owners(
    course_id: str,
    body: MembershipPatch,
    user: CurrentUser,
    membership_api: MembershipAPIDep,
):
    if body.add:
        await membership_api.add_course_owners(user, course_id, body.add)
    if body.remove:
        await membership_api.remove_course_owners(user, course_id, body.remove)


@router.get(term_prefix + "/instructors", response_model=MembershipCollectionResponse)
async def list_term_instructors(
    course_id: str,
    term_id: str,
    user: CurrentUser,
    membership_api: MembershipAPIDep,
    membership_assembler: MembershipAssemblerDep,
):
    return membership_assembler.collection(
        usernames=await membership_api.list_instructors(user, course_id, term_id),
        view_permission=MembershipPermission.LIST_INSTRUCTORS,
        manage_permission=(
            MembershipPermission.ADD_INSTRUCTOR,
            MembershipPermission.REMOVE_INSTRUCTOR,
        ),
        course_id=course_id,
        term_id=term_id,
    )


@router.patch(term_prefix + "/instructors", status_code=204)
async def patch_term_instructors(
    course_id: str,
    term_id: str,
    body: MembershipPatch,
    user: CurrentUser,
    membership_api: MembershipAPIDep,
):
    if body.add:
        await membership_api.add_instructors(user, course_id, term_id, body.add)
    if body.remove:
        await membership_api.remove_instructors(user, course_id, term_id, body.remove)


@router.get(
    term_prefix + "/teaching-assistants",
    response_model=MembershipCollectionResponse,
)
async def list_term_teaching_assistants(
    course_id: str,
    term_id: str,
    user: CurrentUser,
    membership_api: MembershipAPIDep,
    membership_assembler: MembershipAssemblerDep,
):
    return membership_assembler.collection(
        usernames=await membership_api.list_teaching_assistants(user, course_id, term_id),
        view_permission=MembershipPermission.LIST_TEACHING_ASSISTANTS,
        manage_permission=(
            MembershipPermission.ADD_TEACHING_ASSISTANT,
            MembershipPermission.REMOVE_TEACHING_ASSISTANT,
        ),
        course_id=course_id,
        term_id=term_id,
    )


@router.patch(term_prefix + "/teaching-assistants", status_code=204)
async def patch_term_teaching_assistants(
    course_id: str,
    term_id: str,
    body: MembershipPatch,
    user: CurrentUser,
    membership_api: MembershipAPIDep,
):
    if body.add:
        await membership_api.add_teaching_assistants(user, course_id, term_id, body.add)
    if body.remove:
        await membership_api.remove_teaching_assistants(user, course_id, term_id, body.remove)


@router.get(term_prefix + "/students", response_model=MembershipCollectionResponse)
async def list_term_students(
    course_id: str,
    term_id: str,
    user: CurrentUser,
    membership_api: MembershipAPIDep,
    membership_assembler: MembershipAssemblerDep,
):
    return membership_assembler.collection(
        usernames=await membership_api.list_students(user, course_id, term_id),
        view_permission=MembershipPermission.LIST_STUDENTS,
        manage_permission=(
            MembershipPermission.ADD_STUDENT,
            MembershipPermission.REMOVE_STUDENT,
        ),
        course_id=course_id,
        term_id=term_id,
    )


@router.patch(term_prefix + "/students", status_code=204)
async def patch_term_students(
    course_id: str,
    term_id: str,
    body: MembershipPatch,
    user: CurrentUser,
    membership_api: MembershipAPIDep,
):
    if body.add:
        await membership_api.add_students(user, course_id, term_id, body.add)
    if body.remove:
        await membership_api.remove_students(user, course_id, term_id, body.remove)


@router.get(term_prefix + "/observers", response_model=MembershipCollectionResponse)
async def list_term_observers(
    course_id: str,
    term_id: str,
    user: CurrentUser,
    membership_api: MembershipAPIDep,
    membership_assembler: MembershipAssemblerDep,
):
    return membership_assembler.collection(
        usernames=await membership_api.list_observers(user, course_id, term_id),
        view_permission=MembershipPermission.LIST_OBSERVERS,
        manage_permission=(
            MembershipPermission.ADD_OBSERVER,
            MembershipPermission.REMOVE_OBSERVER,
        ),
        course_id=course_id,
        term_id=term_id,
    )


@router.patch(term_prefix + "/observers", status_code=204)
async def patch_term_observers(
    course_id: str,
    term_id: str,
    body: MembershipPatch,
    user: CurrentUser,
    membership_api: MembershipAPIDep,
):
    if body.add:
        await membership_api.add_observers(user, course_id, term_id, body.add)
    if body.remove:
        await membership_api.remove_observers(user, course_id, term_id, body.remove)
