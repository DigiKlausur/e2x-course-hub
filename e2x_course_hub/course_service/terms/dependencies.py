from typing import Annotated

from fastapi import Depends

from e2x_course_hub.schema.course import TermConfig

from ..common.dependency_types import (
    CourseAPIDep,
    CurrentUser,
    DBSession,
    MembershipAPIDep,
)
from .assembler import TermAssembler


def get_term_assembler(
    user: CurrentUser,
    course_api: CourseAPIDep,
    membership_api: MembershipAPIDep,
) -> TermAssembler:
    return TermAssembler(
        course_permission_checker=course_api.permission_checker(user),
        membership_permission_checker=membership_api.permission_checker(user),
    )


def load_term(
    course_id: str,
    term_id: str,
    user: CurrentUser,
    course_api: CourseAPIDep,
    session: DBSession,
) -> TermConfig:
    course = course_api.get_course(course_id=course_id, user=user, session=session)
    term = course.terms.get(term_id) if course else None
    if term is None:
        raise ValueError(f"Term with ID {term_id} not found in course {course_id}.")
    return term


TermAssemblerDep = Annotated[TermAssembler, Depends(get_term_assembler)]
LoadedTerm = Annotated[TermConfig, Depends(load_term)]
