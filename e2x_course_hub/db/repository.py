import uuid
from contextlib import contextmanager
from typing import Dict, Generator, List, Optional

from sqlalchemy.orm import Session, sessionmaker

from ..errors import CourseExistsError, CourseNotFoundError, TermExistsError, TermNotFoundError
from ..schema.course import CourseConfig, CourseMetadata, TermConfig
from ..schema.infrastructure import ImageSelection, ResourceSelection
from ..schema.profile import ProfileSelection
from .models import CourseRow, TermRow


class CourseRepository:
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory

    @contextmanager
    def _session(self, external: Optional[Session] = None) -> Generator[Session, None, None]:
        """Provide a session scope.

        If an external session is provided, yield it as-is (caller owns the transaction).
        Otherwise create one, commit on success, rollback on failure, always close.
        """
        if external is not None:
            yield external
        else:
            session = self._session_factory()
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()

    # ── helpers: DB row ↔ Pydantic ──────────────────────────────────

    @staticmethod
    def _term_row_to_config(row: TermRow) -> TermConfig:
        image = ImageSelection(family=row.image_family, tag=row.image_tag)

        resources = ResourceSelection(
            student=row.resource_student,
            grader=row.resource_grader,
        )

        profiles = ProfileSelection(
            student=row.profile_student,
            grader=row.profile_grader,
        )

        return TermConfig(image=image, resources=resources, profiles=profiles)

    @staticmethod
    def _course_row_to_config(row: CourseRow) -> CourseConfig:
        terms: Dict[str, TermConfig] = {}
        for term_row in row.terms:
            terms[term_row.term_id] = CourseRepository._term_row_to_config(term_row)

        return CourseConfig(
            metadata=CourseMetadata(
                course_id=row.course_id,
                course_name=row.course_name,
                description=row.description,
            ),
            image=ImageSelection(
                family=row.image_family,
                tag=row.image_tag,
            ),
            resources=ResourceSelection(
                student=row.resource_student,
                grader=row.resource_grader,
            ),
            profiles=ProfileSelection(
                student=row.profile_student,
                grader=row.profile_grader,
            ),
            terms=terms,
        )

    @staticmethod
    def _config_to_course_row(config: CourseConfig) -> CourseRow:
        row = CourseRow(
            course_id=config.metadata.course_id,
            course_name=config.metadata.course_name,
            description=config.metadata.description,
            image_family=config.image.family,
            image_tag=config.image.tag,
            resource_student=config.resources.student,
            resource_grader=config.resources.grader,
            profile_student=config.profiles.student,
            profile_grader=config.profiles.grader,
        )
        for term_id, term_config in config.terms.items():
            row.terms.append(
                CourseRepository._config_to_term_row(
                    config.metadata.course_id, term_id, term_config
                )
            )
        return row

    @staticmethod
    def _config_to_term_row(course_id: str, term_id: str, config: TermConfig) -> TermRow:
        return TermRow(
            id=str(uuid.uuid4()),
            course_id=course_id,
            term_id=term_id,
            image_family=config.image.family if config.image else None,
            image_tag=config.image.tag if config.image else None,
            resource_student=config.resources.student if config.resources else None,
            resource_grader=config.resources.grader if config.resources else None,
            profile_student=config.profiles.student if config.profiles else None,
            profile_grader=config.profiles.grader if config.profiles else None,
        )

    # ── CRUD ────────────────────────────────────────────────────────

    def get_course(
        self, course_id: str, session: Optional[Session] = None
    ) -> Optional[CourseConfig]:
        with self._session(session) as s:
            row = s.get(CourseRow, course_id)
            if row is None:
                return None
            return self._course_row_to_config(row)

    def list_courses(self, session: Optional[Session] = None) -> Dict[str, CourseConfig]:
        with self._session(session) as s:
            rows = s.query(CourseRow).all()
            return {row.course_id: self._course_row_to_config(row) for row in rows}

    def create_course(
        self, config: CourseConfig, session: Optional[Session] = None
    ) -> CourseConfig:
        with self._session(session) as s:
            existing = s.get(CourseRow, config.metadata.course_id)
            if existing is not None:
                raise CourseExistsError(config.metadata.course_id)
            row = self._config_to_course_row(config)
            s.add(row)
            s.flush()
            s.refresh(row)
            return self._course_row_to_config(row)

    def update_course(
        self, course_id: str, config: CourseConfig, session: Optional[Session] = None
    ) -> CourseConfig:
        with self._session(session) as s:
            row = s.get(CourseRow, course_id)
            if row is None:
                raise CourseNotFoundError(course_id)

            row.course_name = config.metadata.course_name
            row.description = config.metadata.description
            row.image_family = config.image.family
            row.image_tag = config.image.tag
            row.resource_student = config.resources.student
            row.resource_grader = config.resources.grader
            row.profile_student = config.profiles.student
            row.profile_grader = config.profiles.grader

            # Rebuild terms: delete existing, add new
            row.terms.clear()
            s.flush()
            for term_id, term_config in config.terms.items():
                row.terms.append(self._config_to_term_row(course_id, term_id, term_config))

            s.flush()
            s.refresh(row)
            return self._course_row_to_config(row)

    def delete_course(self, course_id: str, session: Optional[Session] = None) -> None:
        with self._session(session) as s:
            row = s.get(CourseRow, course_id)
            if row is None:
                raise CourseNotFoundError(course_id)
            s.delete(row)

    # ── Term-level operations ───────────────────────────────────────

    def add_term(
        self,
        course_id: str,
        term_id: str,
        config: Optional[TermConfig] = None,
        session: Optional[Session] = None,
    ) -> CourseConfig:
        # If config is None, create a default TermConfig with course-level defaults.

        if config is None:
            # First get the course to retrieve its defaults
            course = self.get_course(course_id, session=session)
            if course is None:
                raise CourseNotFoundError(course_id)
            config = TermConfig(
                image=course.image,
                resources=course.resources,
                profiles=course.profiles,
            )
        with self._session(session) as s:
            row = s.get(CourseRow, course_id)
            if row is None:
                raise CourseNotFoundError(course_id)
            # Check for duplicate term
            for t in row.terms:
                if t.term_id == term_id:
                    raise TermExistsError(course_id, term_id)
            row.terms.append(self._config_to_term_row(course_id, term_id, config))
            s.flush()
            s.refresh(row)
            return self._course_row_to_config(row)

    def update_term(
        self,
        course_id: str,
        term_id: str,
        config: TermConfig,
        session: Optional[Session] = None,
    ) -> CourseConfig:
        with self._session(session) as s:
            row = s.get(CourseRow, course_id)
            if row is None:
                raise CourseNotFoundError(course_id)
            for t in row.terms:
                if t.term_id == term_id:
                    if config.image is not None:
                        t.image_family = config.image.family
                        if config.image.tag is not None:
                            t.image_tag = config.image.tag
                    if config.resources is not None:
                        if config.resources.student is not None:
                            t.resource_student = config.resources.student
                        if config.resources.grader is not None:
                            t.resource_grader = config.resources.grader
                    if config.profiles is not None:
                        if config.profiles.student is not None:
                            t.profile_student = config.profiles.student
                        if config.profiles.grader is not None:
                            t.profile_grader = config.profiles.grader
                    s.flush()
                    s.refresh(row)
                    return self._course_row_to_config(row)
            raise TermNotFoundError(course_id, term_id)

    def remove_term(
        self,
        course_id: str,
        term_id: str,
        session: Optional[Session] = None,
    ) -> CourseConfig:
        with self._session(session) as s:
            row = s.get(CourseRow, course_id)
            if row is None:
                raise CourseNotFoundError(course_id)
            for t in row.terms:
                if t.term_id == term_id:
                    s.delete(t)
                    s.flush()
                    s.refresh(row)
                    return self._course_row_to_config(row)
            raise TermNotFoundError(course_id, term_id)

    def list_course_ids(self, session: Optional[Session] = None) -> List[str]:
        with self._session(session) as s:
            rows = s.query(CourseRow.course_id).all()
            return [r[0] for r in rows]
