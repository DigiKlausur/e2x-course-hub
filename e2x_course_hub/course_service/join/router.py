from datetime import datetime, timezone

from fastapi import APIRouter

from ...errors import StudentAccessEndedError
from ..common.dependency_types import CourseAPIDep, CurrentUser, DBSession, MembershipAPIDep
from .schemas import StudentJoinInfo, StudentJoinStatus
from .status import student_join_status

# The token alone identifies the term, so course and term IDs stay out of the link.
router = APIRouter(
    prefix="/v1/student-join/{token}",
    tags=["Student join"],
)


@router.get("", response_model=StudentJoinInfo)
async def get_student_join_info(
    token: str,
    user: CurrentUser,
    course_api: CourseAPIDep,
    session: DBSession,
) -> StudentJoinInfo:
    now = datetime.now(timezone.utc)
    target = course_api.resolve_student_join_link(token, now, session=session)
    return StudentJoinInfo(**target.model_dump(), status=student_join_status(target, user, now))


@router.post("", status_code=204)
async def join_as_student(
    token: str,
    user: CurrentUser,
    course_api: CourseAPIDep,
    membership_api: MembershipAPIDep,
    session: DBSession,
):
    now = datetime.now(timezone.utc)
    target = course_api.resolve_student_join_link(token, now, session=session)
    match student_join_status(target, user, now):
        case StudentJoinStatus.ENDED:
            raise StudentAccessEndedError(target.course_id, target.term_id)
        case StudentJoinStatus.ALREADY_MEMBER:
            return  # Nothing to do; joining twice is harmless.
        case _:
            await membership_api.join_term_as_student(
                target.course_id, target.term_id, user.username
            )
