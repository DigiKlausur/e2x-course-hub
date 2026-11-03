from fastapi import APIRouter

from ...schema.course import StudentAccessPeriod, StudentJoinLink
from ..common.dependency_types import (
    CourseAPIDep,
    CurrentUser,
    DBSession,
    MembershipAPIDep,
)
from ..common.schemas import Environment, EnvironmentUpdate
from .dependencies import LoadedTerm, TermAssemblerDep
from .schemas import CreateTermRequest, StudentJoinLinkUpdate, TermDetailResponse

router = APIRouter(
    prefix="/v1/courses/{course_id}/terms/{term_id}",
    tags=["Courses"],
)


@router.post("", status_code=201, response_model=TermDetailResponse)
async def create_term(
    course_id: str,
    term_id: str,
    user: CurrentUser,
    course_api: CourseAPIDep,
    session: DBSession,
    term_assembler: TermAssemblerDep,
    body: CreateTermRequest | None = None,
):
    access_period = body.access_period if body else None
    added_term = course_api.add_term(user, course_id, term_id, access_period, session=session)
    return term_assembler.detail(course_id, term_id, added_term)


@router.delete("", status_code=204)
async def delete_term(
    course_id: str,
    term_id: str,
    user: CurrentUser,
    course_api: CourseAPIDep,
    membership_api: MembershipAPIDep,
    session: DBSession,
):
    course_api.remove_term(user, course_id, term_id, session=session)
    await membership_api.remove_term_members(course_id, term_id)


@router.get("", response_model=TermDetailResponse)
async def get_term(
    course_id: str,
    term_id: str,
    term_assembler: TermAssemblerDep,
    term: LoadedTerm,
) -> TermDetailResponse:
    return term_assembler.detail(course_id, term_id, term)


@router.get("/environment", response_model=Environment)
async def get_term_environment(
    term_assembler: TermAssemblerDep,
    term: LoadedTerm,
) -> Environment:
    return term_assembler.environment(term)


@router.patch("/environment", response_model=Environment)
async def patch_term_environment(
    course_id: str,
    term_id: str,
    update: EnvironmentUpdate,
    user: CurrentUser,
    course_api: CourseAPIDep,
    session: DBSession,
    term_assembler: TermAssemblerDep,
) -> Environment:
    if update.image is not None:
        course_api.set_term_image(user, course_id, term_id, update.image, session=session)
    if update.resources is not None:
        course_api.set_term_resources(user, course_id, term_id, update.resources, session=session)
    if update.profiles is not None:
        course_api.set_term_profiles(user, course_id, term_id, update.profiles, session=session)
    return term_assembler.environment(
        course_api.get_term(user=user, course_id=course_id, term_id=term_id, session=session)
    )


# PUT, not PATCH: an empty bound means "no limit", so both bounds are always replaced.
@router.put("/access-period", response_model=StudentAccessPeriod)
async def put_term_access_period(
    course_id: str,
    term_id: str,
    access_period: StudentAccessPeriod,
    user: CurrentUser,
    course_api: CourseAPIDep,
    session: DBSession,
    term_assembler: TermAssemblerDep,
) -> StudentAccessPeriod:
    course_api.set_term_student_access_period(
        user, course_id, term_id, access_period, session=session
    )
    return term_assembler.access_period(
        course_api.get_term(user=user, course_id=course_id, term_id=term_id, session=session)
    )


@router.get("/student-join-link", response_model=StudentJoinLink)
async def get_term_student_join_link(
    course_id: str,
    term_id: str,
    user: CurrentUser,
    course_api: CourseAPIDep,
    session: DBSession,
) -> StudentJoinLink:
    return course_api.get_term_student_join_link(user, course_id, term_id, session=session)


# PUT, not PATCH: an empty expiry means "no expiry", so it is always replaced.
@router.put("/student-join-link", response_model=StudentJoinLink)
async def put_term_student_join_link(
    course_id: str,
    term_id: str,
    update: StudentJoinLinkUpdate,
    user: CurrentUser,
    course_api: CourseAPIDep,
    session: DBSession,
) -> StudentJoinLink:
    return course_api.set_term_student_join_link(
        user, course_id, term_id, update.expires_at, session=session
    )


@router.post("/student-join-link/regenerate", response_model=StudentJoinLink)
async def regenerate_term_student_join_link(
    course_id: str,
    term_id: str,
    user: CurrentUser,
    course_api: CourseAPIDep,
    session: DBSession,
) -> StudentJoinLink:
    return course_api.regenerate_term_student_join_link(user, course_id, term_id, session=session)


@router.delete("/student-join-link", status_code=204)
async def delete_term_student_join_link(
    course_id: str,
    term_id: str,
    user: CurrentUser,
    course_api: CourseAPIDep,
    session: DBSession,
):
    course_api.disable_term_student_join_link(user, course_id, term_id, session=session)
