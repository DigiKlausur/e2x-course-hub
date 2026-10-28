"""Baseline: the schema as create_all() built it before migrations existed.

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None

spawn_role = sa.Enum("STUDENT", "GRADER", name="spawnrole")


def upgrade() -> None:
    op.create_table(
        "courses",
        sa.Column("course_id", sa.String(), primary_key=True),
        sa.Column("course_name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("image_family", sa.String(), nullable=False),
        sa.Column("image_tag", sa.String(), nullable=False),
    )
    op.create_table(
        "course_spawn_configs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "course_id",
            sa.String(),
            sa.ForeignKey("courses.course_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("spawn_role", spawn_role, nullable=False),
        sa.Column("resource", sa.String(), nullable=False),
        sa.Column("profile", sa.String(), nullable=False),
        sa.UniqueConstraint("course_id", "spawn_role", name="uq_course_spawn_role"),
    )
    op.create_table(
        "terms",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "course_id",
            sa.String(),
            sa.ForeignKey("courses.course_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("term_id", sa.String(), nullable=False),
        sa.Column("image_family", sa.String(), nullable=False),
        sa.Column("image_tag", sa.String(), nullable=False),
        sa.UniqueConstraint("course_id", "term_id", name="uq_course_term"),
    )
    op.create_table(
        "term_spawn_configs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "term_row_id",
            sa.String(),
            sa.ForeignKey("terms.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("spawn_role", spawn_role, nullable=False),
        sa.Column("resource", sa.String(), nullable=False),
        sa.Column("profile", sa.String(), nullable=False),
        sa.UniqueConstraint("term_row_id", "spawn_role", name="uq_term_spawn_role"),
    )


def downgrade() -> None:
    op.drop_table("term_spawn_configs")
    op.drop_table("terms")
    op.drop_table("course_spawn_configs")
    op.drop_table("courses")
