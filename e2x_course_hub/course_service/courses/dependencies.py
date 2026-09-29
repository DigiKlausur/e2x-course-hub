from typing import Annotated

from fastapi import Depends

from ...schema.course import CourseConfig
from ..common.dependency_types import (
    CourseAPIDep,
    CurrentUser,
    DBSession,
    PermissionCheckerDep,
)
from ..terms.dependencies import TermAssemblerDep
from .assembler import CourseAssembler, CourseCollectionAssembler


def get_course_assembler(
    permission_checker: PermissionCheckerDep,
    term_assembler: TermAssemblerDep,
) -> CourseAssembler:
    return CourseAssembler(permission_checker=permission_checker, term_assembler=term_assembler)


def get_course_collection_assembler(
    permission_checker: PermissionCheckerDep,
    course_assembler: CourseAssembler = Depends(get_course_assembler),
) -> CourseCollectionAssembler:
    return CourseCollectionAssembler(
        permission_checker=permission_checker, course_assembler=course_assembler
    )


def load_course(
    course_id: str,
    user: CurrentUser,
    course_api: CourseAPIDep,
    session: DBSession,
) -> CourseConfig:
    return course_api.get_course(course_id=course_id, user=user, session=session)


CourseAssemblerDep = Annotated[CourseAssembler, Depends(get_course_assembler)]
CourseCollectionAssemblerDep = Annotated[
    CourseCollectionAssembler, Depends(get_course_collection_assembler)
]
LoadedCourse = Annotated[CourseConfig, Depends(load_course)]
