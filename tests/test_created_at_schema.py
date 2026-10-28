from datetime import datetime, timezone

from e2x_course_hub.course_service.courses.assembler import CourseAssembler
from e2x_course_hub.course_service.courses.schemas import CourseMetadataResponse
from e2x_course_hub.schema.course import CourseMetadata, TermConfig


def test_created_at_is_not_part_of_the_input_schemas():
    assert "created_at" not in CourseMetadata.model_json_schema()["properties"]
    assert "created_at" not in TermConfig.model_json_schema()["properties"]


def test_created_at_is_part_of_the_course_metadata_response():
    assert "created_at" in CourseMetadataResponse.model_json_schema()["properties"]


def test_course_metadata_response_keeps_created_at():
    created_at = datetime(2026, 10, 27, 12, 0, tzinfo=timezone.utc)
    metadata = CourseMetadata(course_id="c1", course_name="Course", created_at=created_at)

    # The assembler's metadata() does not use its permission checker or term assembler.
    response = CourseAssembler(None, None).metadata(metadata)

    assert response.created_at == created_at
