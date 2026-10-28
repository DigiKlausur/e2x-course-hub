"""Add the student access period to terms and created_at to courses and terms.

Existing rows keep empty values: no access limit, and an unknown creation date.

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"


def upgrade() -> None:
    op.add_column("courses", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("terms", sa.Column("student_access_start", sa.DateTime(), nullable=True))
    op.add_column("terms", sa.Column("student_access_end", sa.DateTime(), nullable=True))
    op.add_column("terms", sa.Column("created_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Batch mode, because SQLite cannot drop columns in place.
    with op.batch_alter_table("terms") as batch:
        batch.drop_column("created_at")
        batch.drop_column("student_access_end")
        batch.drop_column("student_access_start")
    with op.batch_alter_table("courses") as batch:
        batch.drop_column("created_at")
