from typing import List, Optional

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from ..schema.types import SpawnRole


class Base(DeclarativeBase):
    pass


class CourseRow(Base):
    __tablename__ = "courses"

    course_id: Mapped[str] = mapped_column(primary_key=True)
    course_name: Mapped[str]
    description: Mapped[Optional[str]]

    # Default image selection
    image_family: Mapped[str]
    image_tag: Mapped[str]

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

    # Nullable: a spawn role may set only a resource tier or only a profile.
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

    # Nullable because this is an override.
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
