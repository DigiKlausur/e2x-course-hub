"""Alembic environment: runs the migrations on the connection passed in by ``upgrade_db``."""

from alembic import context

from e2x_course_hub.db.migrations import VERSION_TABLE
from e2x_course_hub.db.models import Base

context.configure(
    connection=context.config.attributes["connection"],
    target_metadata=Base.metadata,
    version_table=VERSION_TABLE,
)

with context.begin_transaction():
    context.run_migrations()
