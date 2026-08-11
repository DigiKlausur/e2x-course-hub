from typing import Annotated

from fastapi import Depends

from ...schema.course import CourseConfig
from ..common.dependency_types import (
    CourseAPIDep,
    CurrentUser,
    DBSession,
    MembershipAPIDep,
)
from ..terms.dependencies import TermAssemblerDep
from .assembler import CourseAssembler, CourseCollectionAssembler


def get_course_assembler(
    user: CurrentUser,
    course_api: CourseAPIDep,
    membership_api: MembershipAPIDep,
    term_assembler: TermAssemblerDep,
) -> CourseAssembler:
    return CourseAssembler(
        course_permission_checker=course_api.permission_checker(user),
        membership_permission_checker=membership_api.permission_checker(user),
        term_assembler=term_assembler,
    )


def get_course_collection_assembler(
    user: CurrentUser,
    course_api: CourseAPIDep,
    course_assembler: CourseAssembler = Depends(get_course_assembler),
) -> CourseCollectionAssembler:
    return CourseCollectionAssembler(
        course_permission_checker=course_api.permission_checker(user),
        course_assembler=course_assembler,
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
