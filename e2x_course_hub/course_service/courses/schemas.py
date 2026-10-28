from datetime import datetime

from pydantic import BaseModel

from ...schema.course import CourseMetadata
from ..actions import CourseActions, LmsActions
from ..common.schemas import Environment
from ..terms.schemas import TermSummaryResponse


class CourseMetadataResponse(CourseMetadata):
    """Course metadata as returned by the API, including the read-only creation date."""

    created_at: datetime | None


class CourseSummaryResponse(BaseModel):
    metadata: CourseMetadataResponse
    actions: CourseActions


class CourseDetailResponse(BaseModel):
    metadata: CourseMetadataResponse
    environment: Environment
    terms: list[TermSummaryResponse]
    actions: CourseActions


class CourseCollectionResponse(BaseModel):
    courses: list[CourseSummaryResponse]
    actions: LmsActions


class CourseMetadataUpdate(BaseModel):
    """Request body for updating course metadata."""

    course_name: str | None = None
    description: str | None = None
