from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from conftest import StubCatalogProvider, make_course, make_term
from e2x_hub_rbac.errors import APIPermissionError

from e2x_course_hub.api.course_api import CourseAPI
from e2x_course_hub.schema.course import StudentJoinLink

EXPIRY = datetime(2027, 2, 15, 18, 0, tzinfo=timezone.utc)
LATER = datetime(2027, 3, 1, 18, 0, tzinfo=timezone.utc)


def _term_member(role: str) -> SimpleNamespace:
    return SimpleNamespace(username=role, groups=[f"lms.course.c1.term.t1.{role}"])


INSTRUCTOR = _term_member("instructor")
TEACHING_ASSISTANT = _term_member("teaching-assistant")


@pytest.fixture
def course_api(repository) -> CourseAPI:
    repository.create_course(make_course(terms={"t1": make_term()}))
    return CourseAPI(repository, StubCatalogProvider())


def test_link_is_off_for_a_new_term(course_api):
    assert course_api.get_term_student_join_link(INSTRUCTOR, "c1", "t1") == StudentJoinLink()


def test_turning_the_link_on_creates_a_token(course_api):
    link = course_api.set_term_student_join_link(INSTRUCTOR, "c1", "t1", EXPIRY)

    assert link.token
    assert link.expires_at == EXPIRY
    assert course_api.get_term_student_join_link(INSTRUCTOR, "c1", "t1") == link


def test_changing_the_expiry_keeps_the_token(course_api):
    first = course_api.set_term_student_join_link(INSTRUCTOR, "c1", "t1", EXPIRY)

    second = course_api.set_term_student_join_link(INSTRUCTOR, "c1", "t1", LATER)

    assert second == StudentJoinLink(token=first.token, expires_at=LATER)


def test_regenerating_replaces_the_token_and_keeps_the_expiry(course_api):
    first = course_api.set_term_student_join_link(INSTRUCTOR, "c1", "t1", EXPIRY)

    regenerated = course_api.regenerate_term_student_join_link(INSTRUCTOR, "c1", "t1")

    assert regenerated.token != first.token
    assert regenerated.expires_at == EXPIRY


def test_turning_the_link_off_clears_token_and_expiry(course_api):
    course_api.set_term_student_join_link(INSTRUCTOR, "c1", "t1", EXPIRY)

    course_api.disable_term_student_join_link(INSTRUCTOR, "c1", "t1")

    assert course_api.get_term_student_join_link(INSTRUCTOR, "c1", "t1") == StudentJoinLink()


def test_link_survives_course_update(course_api, repository):
    link = course_api.set_term_student_join_link(INSTRUCTOR, "c1", "t1", EXPIRY)

    # update_course rebuilds all term rows; the existing term must keep its link.
    config = repository.get_course("c1")
    config.terms["t2"] = make_term()
    repository.update_course("c1", config)

    assert repository.get_student_join_link("c1", "t1") == link
    assert repository.get_student_join_link("c1", "t2") == StudentJoinLink()


def test_teaching_assistants_cannot_manage_the_link(course_api):
    with pytest.raises(APIPermissionError):
        course_api.get_term_student_join_link(TEACHING_ASSISTANT, "c1", "t1")
    with pytest.raises(APIPermissionError):
        course_api.set_term_student_join_link(TEACHING_ASSISTANT, "c1", "t1", EXPIRY)
