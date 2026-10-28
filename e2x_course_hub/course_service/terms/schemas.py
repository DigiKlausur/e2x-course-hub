from datetime import datetime

from pydantic import BaseModel

from ...schema.course import StudentAccessPeriod, TermConfig
from ..actions import TermActions
from ..common.schemas import Environment


class TermSummaryResponse(BaseModel):
    course_id: str
    term_id: str
    created_at: datetime | None
    actions: TermActions


class TermDetailResponse(BaseModel):
    course_id: str
    term_id: str
    created_at: datetime | None
    environment: Environment
    access_period: StudentAccessPeriod
    actions: TermActions


class CreateTermRequest(BaseModel):
    """Request body for creating a term."""

    term: TermConfig | None = None
    access_period: StudentAccessPeriod | None = None
