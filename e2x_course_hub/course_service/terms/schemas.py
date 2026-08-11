from pydantic import BaseModel

from ...schema.course import TermConfig
from ..common.schemas import Environment


class TermMembershipCapabilities(BaseModel):
    viewInstructors: bool
    manageInstructors: bool
    viewTeachingAssistants: bool
    manageTeachingAssistants: bool
    viewStudents: bool
    manageStudents: bool
    viewObservers: bool
    manageObservers: bool


class TermSummaryCapabilities(BaseModel):
    viewTerm: bool
    removeTerm: bool


class TermCapabilities(TermSummaryCapabilities):
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
