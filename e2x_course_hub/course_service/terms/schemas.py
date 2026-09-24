from pydantic import BaseModel

from ...schema.course import TermConfig
from ..common.schemas import Environment
from ..membership.schemas import MembershipCapabilities


class TermMembershipCapabilities(BaseModel):
    instructors: MembershipCapabilities
    teachingAssistants: MembershipCapabilities
    students: MembershipCapabilities
    observers: MembershipCapabilities


class TermSummaryCapabilities(BaseModel):
    viewTerm: bool
    removeTerm: bool


class TermCapabilities(TermSummaryCapabilities):
    selectEnvironment: bool
    membership: TermMembershipCapabilities


class TermSummaryResponse(BaseModel):
    course_id: str
    term_id: str
    capabilities: TermSummaryCapabilities


class TermDetailResponse(BaseModel):
    course_id: str
    term_id: str
    environment: Environment
    capabilities: TermCapabilities


class CreateTermRequest(BaseModel):
    """Request body for creating a term."""

    term: TermConfig | None = None
