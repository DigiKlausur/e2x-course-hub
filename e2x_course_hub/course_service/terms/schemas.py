from datetime import datetime

from pydantic import AwareDatetime, BaseModel, Field

from ...schema.catalog import UnavailableSelection
from ...schema.course import StudentAccessPeriod
from ..actions import TermActions
from ..common.schemas import Environment


class TermSummaryResponse(BaseModel):
    course_id: str
    term_id: str
    created_at: datetime | None
    actions: TermActions
    unavailable: list[UnavailableSelection] = []


class TermDetailResponse(BaseModel):
    course_id: str
    term_id: str
    created_at: datetime | None
    environment: Environment
    access_period: StudentAccessPeriod
    actions: TermActions


class CreateTermRequest(BaseModel):
    """Request body for creating a term. The term's environment comes from the course."""

    access_period: StudentAccessPeriod | None = None


class StudentJoinLinkUpdate(BaseModel):
    """Request body for turning the student join link on or changing its expiry.

    The token is never sent by the client; the server creates it.
    """

    expires_at: AwareDatetime | None = Field(
        default=None,
        description="When the link stops working. Empty means it works until turned off.",
    )
