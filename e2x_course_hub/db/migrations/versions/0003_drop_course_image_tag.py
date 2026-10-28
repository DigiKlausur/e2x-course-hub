"""Drop the image tag from courses.

A course only selects the image family; a new term gets that family's default tag.

Revision ID: 0003
Revises: 0002
"""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"


def upgrade() -> None:
    # Batch mode, because SQLite cannot drop columns in place.
    with op.batch_alter_table("courses") as batch:
        batch.drop_column("image_tag")


def downgrade() -> None:
    # The dropped tags cannot be restored, so courses get an empty tag to be chosen again.
    op.add_column(
        "courses",
        sa.Column("image_tag", sa.String(), nullable=False, server_default=""),
    )
