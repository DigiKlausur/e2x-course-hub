from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from conftest import make_term
from sqlalchemy import create_engine, text

from e2x_course_hub.db.migrations import (
    BASELINE_REVISION,
    VERSION_TABLE,
    alembic_config,
    upgrade_db,
)
from e2x_course_hub.db.models import Base
from e2x_course_hub.db.repository import get_course_repository_from_db_url


def test_migrations_match_models(db_url):
    engine = create_engine(db_url)
    upgrade_db(engine)

    with engine.connect() as connection:
        context = MigrationContext.configure(connection, opts={"version_table": VERSION_TABLE})
        assert compare_metadata(context, Base.metadata) == []


def _create_pre_migration_db(db_url: str) -> None:
    """A database as create_all() built it before migrations existed, with one course."""
    engine = create_engine(db_url)
    with engine.begin() as connection:
        command.upgrade(alembic_config(connection), BASELINE_REVISION)
        connection.execute(text(f"DROP TABLE {VERSION_TABLE}"))
        connection.execute(
            text("INSERT INTO courses VALUES ('c1', 'Course', NULL, 'python', 'latest')")
        )
        connection.execute(
            text("INSERT INTO terms VALUES ('row-1', 'c1', 't1', 'python', 'latest')")
        )


def test_pre_migration_db_is_upgraded_and_keeps_its_data(db_url):
    _create_pre_migration_db(db_url)

    repository = get_course_repository_from_db_url(db_url)

    course = repository.get_course("c1")
    assert course.metadata.created_at is None
    assert course.terms["t1"].created_at is None
    assert course.terms["t1"].student_access_start is None
    assert course.terms["t1"].student_access_end is None


def test_unknown_created_at_stays_empty_after_course_update(db_url):
    _create_pre_migration_db(db_url)
    repository = get_course_repository_from_db_url(db_url)

    config = repository.get_course("c1")
    config.terms["t2"] = make_term()
    updated = repository.update_course("c1", config)

    assert updated.terms["t1"].created_at is None
    assert updated.terms["t2"].created_at is not None
