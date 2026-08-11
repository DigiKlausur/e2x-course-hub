import warnings

from fastapi import APIRouter

from ...schema.course import CourseConfig, CourseMetadata
from ..common.dependency_types import (
    CourseAPIDep,
    CurrentUser,
    DBSession,
    MembershipAPIDep,
)
from ..common.schemas import Environment, EnvironmentUpdate
from ..terms.schemas import TermSummaryResponse
from .dependencies import CourseAssemblerDep, CourseCollectionAssemblerDep, LoadedCourse
from .schemas import (
    CourseCollectionResponse,
    CourseDetailResponse,
    CourseMetadataUpdate,
)

router = APIRouter(
    prefix="/v1/courses",
    tags=["Courses"],
)


@router.get("", response_model=CourseCollectionResponse)
async def list_courses(
    user: CurrentUser,
    course_api: CourseAPIDep,
    session: DBSession,
    course_collection_assembler: CourseCollectionAssemblerDep,
) -> CourseCollectionResponse:
    courses = course_api.list_courses(user, session=session)
    return course_collection_assembler.collection(courses)


@router.get("/{course_id}", response_model=CourseDetailResponse)
async def get_course(
    course_assembler: CourseAssemblerDep,
    course: LoadedCourse,
) -> CourseDetailResponse:
    return course_assembler.detail(course)


@router.post("", response_model=CourseMetadata, status_code=201)
async def create_course(
    course: CourseConfig,
    user: CurrentUser,
    course_api: CourseAPIDep,
    membership_api: MembershipAPIDep,
    session: DBSession,
):
    course_api.add_course(user, course, session=session)
    await membership_api.bootstrap_course_owner(course.metadata.course_id, user.username)
    return course_api.get_course_metadata(user, course.metadata.course_id, session=session)


@router.delete("/{course_id}", status_code=204)
async def delete_course(
    course_id: str,
    user: CurrentUser,
    course_api: CourseAPIDep,
    session: DBSession,
):
    course_api.remove_course(user, course_id, session=session)


# ── Metadata ─────────────────────────────────────────────────────────
@router.get("/{course_id}/metadata", response_model=CourseMetadata)
async def get_course_metadata(
    course: LoadedCourse,
) -> CourseMetadata:
    return course.metadata


@router.patch("/{course_id}/metadata", response_model=CourseMetadata)
async def update_course_metadata(
    course_id: str,
    body: CourseMetadataUpdate,
    user: CurrentUser,
    course_api: CourseAPIDep,
    session: DBSession,
):
    # Let us log the body here
    warnings.warn(f"Updating course metadata for course {course_id} with data: {body}")
    course_api.set_course_metadata(
        user, course_id, body.course_name, body.description, session=session
    )
    return course_api.get_course_metadata(user, course_id, session=session)


# ── Environment ──────────────────────────────────────────────────────
@router.get("/{course_id}/environment", response_model=Environment)
async def get_course_environment(
    course_assembler: CourseAssemblerDep,
    course: LoadedCourse,
) -> Environment:
    return course_assembler.environment(course)


@router.patch("/{course_id}/environment", status_code=204)
async def patch_course_environment(
    course_id: str,
    update: EnvironmentUpdate,
    user: CurrentUser,
    course_api: CourseAPIDep,
    session: DBSession,
):
    if update.image is not None:
        course_api.set_course_image(user, course_id, update.image, session=session)
    if update.resources is not None:
        course_api.set_course_resources(user, course_id, update.resources, session=session)


@router.get("/{course_id}/terms", response_model=list[TermSummaryResponse])
async def get_terms(
    course_assembler: CourseAssemblerDep,
    course: LoadedCourse,
) -> list[TermSummaryResponse]:
    return course_assembler.detail(course).terms
