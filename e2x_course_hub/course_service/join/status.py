from datetime import datetime

from e2x_hub_rbac.auth import RoleAssignment, UserLike

from ...schema.course import StudentJoinTarget
from .schemas import StudentJoinStatus


def student_join_status(
    target: StudentJoinTarget, user: UserLike, now: datetime
) -> StudentJoinStatus:
    """Whether, and how, the user can join the target term at the given time."""
    if _has_role_in(target, user):
        return StudentJoinStatus.ALREADY_MEMBER
    if target.student_access_end is not None and now >= target.student_access_end:
        return StudentJoinStatus.ENDED
    if target.is_student_access_open(now):
        return StudentJoinStatus.OPEN
    return StudentJoinStatus.NOT_YET_OPEN


def _has_role_in(target: StudentJoinTarget, user: UserLike) -> bool:
    """Whether the user has a role in the target term, or in its course."""
    for group_name in user.groups:
        assignment = RoleAssignment.from_group_name(group_name)
        if assignment is None or assignment.course_id != target.course_id:
            continue
        if assignment.term_id in (None, target.term_id):
            return True
    return False
