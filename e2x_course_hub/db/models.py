from typing import List, Optional

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class CourseRow(Base):
    __tablename__ = "courses"

    course_id: Mapped[str] = mapped_column(primary_key=True)
    course_name: Mapped[str]
    description: Mapped[Optional[str]]

    # Default image selection
    image_family: Mapped[str]
    image_tag: Mapped[Optional[str]]

    # Default resource selection (tier names)
    resource_student: Mapped[Optional[str]]
    resource_grader: Mapped[Optional[str]]

    # Default profile selection (profile names)
    profile_student: Mapped[Optional[str]]
    profile_grader: Mapped[Optional[str]]

    terms: Mapped[List["TermRow"]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )


class TermRow(Base):
    __tablename__ = "terms"

    id: Mapped[str] = mapped_column(primary_key=True)
    course_id: Mapped[str] = mapped_column(ForeignKey("courses.course_id", ondelete="CASCADE"))
    term_id: Mapped[str]

    # Optional overrides
    image_family: Mapped[str]
    image_tag: Mapped[str]
    resource_student: Mapped[str]
    resource_grader: Mapped[str]
    profile_student: Mapped[str]
    profile_grader: Mapped[str]

    course: Mapped["CourseRow"] = relationship(back_populates="terms")

    __table_args__ = (UniqueConstraint("course_id", "term_id", name="uq_course_term"),)
