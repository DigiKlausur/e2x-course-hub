"""Add the student join link to terms.

Existing terms get an empty token, so their join link is off.

Revision ID: 0004
Revises: 0003
"""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"


def upgrade() -> None:
    op.add_column("terms", sa.Column("join_token", sa.String(), nullable=True))
    op.add_column("terms", sa.Column("join_token_expires_at", sa.DateTime(), nullable=True))
    op.create_index("ix_terms_join_token", "terms", ["join_token"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_terms_join_token", table_name="terms")
    # Batch mode, because SQLite cannot drop columns in place.
    with op.batch_alter_table("terms") as batch:
        batch.drop_column("join_token_expires_at")
        batch.drop_column("join_token")
