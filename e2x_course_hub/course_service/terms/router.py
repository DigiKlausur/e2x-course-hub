from fastapi import APIRouter

from ..common.dependency_types import (
    CourseAPIDep,
    CurrentUser,
    DBSession,
)
from ..common.schemas import Environment, EnvironmentUpdate
from .dependencies import LoadedTerm, TermAssemblerDep
from .schemas import CreateTermRequest, TermDetailResponse

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
    term_config = body.term if body else None
    added_term = course_api.add_term(user, course_id, term_id, term_config, session=session)
    return term_assembler.detail(course_id, term_id, added_term)


@router.delete("", status_code=204)
async def delete_term(
    course_id: str,
    term_id: str,
    user: CurrentUser,
    course_api: CourseAPIDep,
    session: DBSession,
):
    course_api.remove_term(user, course_id, term_id, session=session)


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


@router.patch("/environment", status_code=204)
async def patch_term_environment(
    course_id: str,
    term_id: str,
    update: EnvironmentUpdate,
    user: CurrentUser,
    course_api: CourseAPIDep,
    session: DBSession,
):
    if update.image is not None:
        course_api.set_term_image(user, course_id, term_id, update.image, session=session)
    if update.resources is not None:
        course_api.set_term_resources(user, course_id, term_id, update.resources, session=session)
