from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator

from ..schema.types import SpawnRole


class UTCDateTime(TypeDecorator):
    """A timezone-aware datetime, stored as naive UTC.

    SQLite drops timezone information, so values are converted to UTC on the
    way in and marked as UTC on the way out.
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return value.replace(tzinfo=timezone.utc)


class Base(DeclarativeBase):
    pass


class CourseRow(Base):
    __tablename__ = "courses"

    course_id: Mapped[str] = mapped_column(primary_key=True)
    course_name: Mapped[str]
    description: Mapped[Optional[str]]

    # Image family for new terms; each term gets the family's default tag when created.
    image_family: Mapped[str]

    # Set by the repository; empty for courses created before this column existed.
    created_at: Mapped[Optional[datetime]] = mapped_column(UTCDateTime)

    spawn_configs: Mapped[List["CourseSpawnConfigRow"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
    )

    terms: Mapped[List["TermRow"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
    )


class CourseSpawnConfigRow(Base):
    __tablename__ = "course_spawn_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    course_id: Mapped[str] = mapped_column(ForeignKey("courses.course_id", ondelete="CASCADE"))

    spawn_role: Mapped[SpawnRole]

    resource: Mapped[str]
    profile: Mapped[str]

    course: Mapped["CourseRow"] = relationship(back_populates="spawn_configs")

    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "spawn_role",
            name="uq_course_spawn_role",
        ),
    )


class TermRow(Base):
    __tablename__ = "terms"

    id: Mapped[str] = mapped_column(primary_key=True)

    course_id: Mapped[str] = mapped_column(ForeignKey("courses.course_id", ondelete="CASCADE"))

    term_id: Mapped[str]

    image_family: Mapped[str]
    image_tag: Mapped[str]

    # When students may spawn this term; empty means no limit on that side.
    student_access_start: Mapped[Optional[datetime]] = mapped_column(UTCDateTime)
    student_access_end: Mapped[Optional[datetime]] = mapped_column(UTCDateTime)

    # Set by the repository; empty for terms created before this column existed.
    created_at: Mapped[Optional[datetime]] = mapped_column(UTCDateTime)

    spawn_configs: Mapped[List["TermSpawnConfigRow"]] = relationship(
        back_populates="term",
        cascade="all, delete-orphan",
    )

    course: Mapped["CourseRow"] = relationship(back_populates="terms")

    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "term_id",
            name="uq_course_term",
        ),
    )


class TermSpawnConfigRow(Base):
    __tablename__ = "term_spawn_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    term_row_id: Mapped[str] = mapped_column(ForeignKey("terms.id", ondelete="CASCADE"))

    spawn_role: Mapped[SpawnRole]

    resource: Mapped[str]
    profile: Mapped[str]

    term: Mapped["TermRow"] = relationship(back_populates="spawn_configs")

    __table_args__ = (
        UniqueConstraint(
            "term_row_id",
            "spawn_role",
            name="uq_term_spawn_role",
        ),
    )
