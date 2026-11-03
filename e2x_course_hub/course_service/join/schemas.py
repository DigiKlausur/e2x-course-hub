from enum import StrEnum

from ...schema.course import StudentJoinTarget


class StudentJoinStatus(StrEnum):
    """Whether, and how, the current user can join a term with a student join link."""

    OPEN = "open"
    """Can join, and students can start the term right away."""
    NOT_YET_OPEN = "not_yet_open"
    """Can join, but students can only start the term once the access period begins."""
    ENDED = "ended"
    """Cannot join, because the access period has ended."""
    ALREADY_MEMBER = "already_member"
    """Nothing to join: the user already has a role in the term or its course."""


class StudentJoinInfo(StudentJoinTarget):
    """What the join page shows before the user joins."""

    status: StudentJoinStatus
