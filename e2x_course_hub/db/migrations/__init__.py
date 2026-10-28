"""Database schema migrations, managed with Alembic."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import Connection, Engine, inspect

# Separate from JupyterHub's "alembic_version" in case both share a database.
VERSION_TABLE = "e2x_course_hub_alembic_version"

# The revision matching the schema that create_all() built before migrations existed.
BASELINE_REVISION = "0001"


def alembic_config(connection: Connection) -> Config:
    """An Alembic config that runs the migrations on the given connection."""
    config = Config()
    config.set_main_option("script_location", str(Path(__file__).parent))
    config.attributes["connection"] = connection
    return config


def upgrade_db(engine: Engine) -> None:
    """Bring the database schema up to date.

    Databases created before migrations were introduced have the baseline tables
    but no version table. They are stamped as baseline first, so the baseline
    migration does not try to create the tables again.
    """
    with engine.begin() as connection:
        config = alembic_config(connection)
        inspector = inspect(connection)
        if inspector.has_table("courses") and not inspector.has_table(VERSION_TABLE):
            command.stamp(config, BASELINE_REVISION)
        command.upgrade(config, "head")
