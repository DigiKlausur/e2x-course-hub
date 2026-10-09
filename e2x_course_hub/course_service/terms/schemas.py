from pydantic import BaseModel

from ...schema.course import TermConfig
from ..actions import TermActions
from ..common.schemas import Environment


class TermSummaryResponse(BaseModel):
    course_id: str
    term_id: str
    actions: TermActions


class TermDetailResponse(BaseModel):
    course_id: str
    term_id: str
    environment: Environment
    actions: TermActions


class CreateTermRequest(BaseModel):
    """Request body for creating a term."""

    term: TermConfig | None = None
