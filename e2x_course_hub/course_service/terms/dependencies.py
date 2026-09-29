from typing import Annotated

from fastapi import Depends

from ...errors import CourseNotFoundError, TermNotFoundError
from ...schema.course import TermConfig
from ..common.dependency_types import (
    CourseAPIDep,
    CurrentUser,
    DBSession,
    PermissionCheckerDep,
)
from .assembler import TermAssembler


def get_term_assembler(permission_checker: PermissionCheckerDep) -> TermAssembler:
    return TermAssembler(permission_checker=permission_checker)


def load_term(
    course_id: str,
    term_id: str,
    user: CurrentUser,
    course_api: CourseAPIDep,
    session: DBSession,
) -> TermConfig:
    try:
        course = course_api.get_course(course_id=course_id, user=user, session=session)
    except CourseNotFoundError:
        raise CourseNotFoundError(course_id=course_id)
    term = course.terms.get(term_id) if course else None
    if term is None:
        raise TermNotFoundError(course_id=course_id, term_id=term_id)
    return term


TermAssemblerDep = Annotated[TermAssembler, Depends(get_term_assembler)]
LoadedTerm = Annotated[TermConfig, Depends(load_term)]
