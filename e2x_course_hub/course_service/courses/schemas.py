from pydantic import BaseModel

from ...schema.course import CourseMetadata
from ..actions import CourseActions, LmsActions
from ..common.schemas import Environment
from ..terms.schemas import TermSummaryResponse


class CourseSummaryResponse(BaseModel):
    metadata: CourseMetadata
    actions: CourseActions


class CourseDetailResponse(BaseModel):
    metadata: CourseMetadata
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
