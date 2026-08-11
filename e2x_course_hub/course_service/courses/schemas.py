from pydantic import BaseModel

from ...schema.course import CourseMetadata
from ..common.schemas import Environment
from ..terms.schemas import TermSummaryResponse


class CourseCapabilities(BaseModel):
    editMetadata: bool
    removeCourse: bool
    selectEnvironment: bool
    viewCourseOwners: bool
    manageCourseOwners: bool
    addTerm: bool


class CourseSummaryResponse(BaseModel):
    metadata: CourseMetadata
    capabilities: CourseCapabilities


class CourseDetailResponse(BaseModel):
    metadata: CourseMetadata
    environment: Environment
    terms: list[TermSummaryResponse]
    capabilities: CourseCapabilities


class CourseCollectionCapabilities(BaseModel):
    createCourse: bool


class CourseCollectionResponse(BaseModel):
    courses: list[CourseSummaryResponse]
    capabilities: CourseCollectionCapabilities


class CourseMetadataUpdate(BaseModel):
    """Request body for updating course metadata."""

    course_name: str | None = None
    description: str | None = None
