from datetime import datetime, timezone

from conftest import make_course, make_term

START = datetime(2026, 11, 2, 9, 0, tzinfo=timezone.utc)
END = datetime(2027, 2, 15, 18, 0, tzinfo=timezone.utc)


def test_created_at_is_set_on_create(repository):
    before = datetime.now(timezone.utc)
    course = repository.create_course(make_course(terms={"t1": make_term()}))

    assert course.metadata.created_at >= before
    assert course.terms["t1"].created_at >= before


def test_created_at_survives_course_update(repository):
    created = repository.create_course(make_course(terms={"t1": make_term()}))

    # update_course rebuilds all term rows; the existing term must keep its date.
    config = repository.get_course("c1")
    config.terms["t2"] = make_term()
    updated = repository.update_course("c1", config)

    assert updated.metadata.created_at == created.metadata.created_at
    assert updated.terms["t1"].created_at == created.terms["t1"].created_at
    assert updated.terms["t2"].created_at is not None


def test_created_at_from_input_is_ignored(repository):
    course = make_course(terms={"t1": make_term(created_at=datetime(2000, 1, 1))})

    created = repository.create_course(course)

    assert created.terms["t1"].created_at.year != 2000


def test_access_period_round_trips_in_utc(repository):
    term = make_term(student_access_start=START, student_access_end=END)
    repository.create_course(make_course(terms={"t1": term}))

    stored = repository.get_term("c1", "t1")

    assert stored.student_access_start == START
    assert stored.student_access_end == END
    assert stored.student_access_start.tzinfo is not None
