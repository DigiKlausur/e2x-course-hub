import uuid
from contextlib import contextmanager
from typing import Dict, Generator, List, Optional

from sqlalchemy.orm import Session, sessionmaker

from ..errors import (
    CourseExistsError,
    CourseNotFoundError,
    TermExistsError,
    TermNotFoundError,
)
from ..schema.course import CourseConfig, CourseMetadata, TermConfig
from ..schema.selection import ImageSelection, SpawnRoleSelection
from ..schema.types import SpawnRole
from .database import init_db
from .models import (
    CourseRow,
    CourseSpawnConfigRow,
    TermRow,
    TermSpawnConfigRow,
)


class CourseRepository:
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory

    @contextmanager
    def _session(self, external: Optional[Session] = None) -> Generator[Session, None, None]:
        """Provide a session scope.

        If an external session is provided, yield it as-is
        (caller owns the transaction).

        Otherwise create one, commit on success, rollback on failure,
        and always close.
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

        image = ImageSelection(
            family=row.image_family,
            tag=row.image_tag,
        )

        spawn_role_selections: dict[SpawnRole, SpawnRoleSelection] = {
            spawn_role_row.spawn_role: SpawnRoleSelection(
                resource_tier_name=spawn_role_row.resource,
                profile_name=spawn_role_row.profile,
            )
            for spawn_role_row in row.spawn_configs
        }

        return TermConfig(
            image=image,
            spawn_role_selections=spawn_role_selections,
        )

    @staticmethod
    def _course_row_to_config(row: CourseRow) -> CourseConfig:
        terms: Dict[str, TermConfig] = {
            term_row.term_id: CourseRepository._term_row_to_config(term_row)
            for term_row in row.terms
        }

        spawn_role_selections: dict[SpawnRole, SpawnRoleSelection] = {
            spawn_role_row.spawn_role: SpawnRoleSelection(
                resource_tier_name=spawn_role_row.resource,
                profile_name=spawn_role_row.profile,
            )
            for spawn_role_row in row.spawn_configs
        }

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
            spawn_role_selections=spawn_role_selections,
            terms=terms,
        )

    @staticmethod
    def _build_course_spawn_configs(
        config: CourseConfig,
    ) -> List[CourseSpawnConfigRow]:
        """Build DB spawn-config rows from course configuration."""
        roles = set(config.spawn_role_selections)

        return [
            CourseSpawnConfigRow(
                spawn_role=spawn_role,
                resource=config.spawn_role_selections[spawn_role].resource_tier_name,
                profile=config.spawn_role_selections[spawn_role].profile_name,
            )
            for spawn_role in roles
        ]

    @staticmethod
    def _build_term_spawn_configs(
        config: TermConfig,
    ) -> List[TermSpawnConfigRow]:
        """Build DB spawn-config rows from term configuration."""
        roles = set(config.spawn_role_selections)
        return [
            TermSpawnConfigRow(
                spawn_role=spawn_role,
                resource=config.spawn_role_selections[spawn_role].resource_tier_name,
                profile=config.spawn_role_selections[spawn_role].profile_name,
            )
            for spawn_role in roles
        ]

    @staticmethod
    def _config_to_course_row(config: CourseConfig) -> CourseRow:
        row = CourseRow(
            course_id=config.metadata.course_id,
            course_name=config.metadata.course_name,
            description=config.metadata.description,
            image_family=config.image.family,
            image_tag=config.image.tag,
            spawn_configs=CourseRepository._build_course_spawn_configs(config),
        )

        for term_id, term_config in config.terms.items():
            row.terms.append(
                CourseRepository._config_to_term_row(
                    config.metadata.course_id,
                    term_id,
                    term_config,
                )
            )

        return row

    @staticmethod
    def _config_to_term_row(
        course_id: str,
        term_id: str,
        config: TermConfig,
    ) -> TermRow:
        return TermRow(
            id=str(uuid.uuid4()),
            course_id=course_id,
            term_id=term_id,
            image_family=config.image.family if config.image else None,
            image_tag=config.image.tag if config.image else None,
            spawn_configs=CourseRepository._build_term_spawn_configs(config),
        )

    # ── CRUD ────────────────────────────────────────────────────────

    def get_course(
        self,
        course_id: str,
        session: Optional[Session] = None,
    ) -> Optional[CourseConfig]:
        with self._session(session) as s:
            row = s.get(CourseRow, course_id)
            if row is None:
                return None

            return self._course_row_to_config(row)

    def list_courses(
        self,
        session: Optional[Session] = None,
    ) -> Dict[str, CourseConfig]:
        with self._session(session) as s:
            rows = s.query(CourseRow).all()

            return {row.course_id: self._course_row_to_config(row) for row in rows}

    def create_course(
        self,
        config: CourseConfig,
        session: Optional[Session] = None,
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
    
    def _build_single_spawn_config(
        self,
        course_id: str,
        spawn_role: SpawnRole,
        sel: SpawnRoleSelection,
    ) -> "CourseSpawnConfigRow":
        return CourseSpawnConfigRow(
            course_id=course_id,
            spawn_role=spawn_role,
            resource=sel.resource_tier_name,
            profile=sel.profile_name,
        )

    def _sync_spawn_configs(
        self,
        row: CourseRow,
        course_id: str,
        config: CourseConfig,
    ) -> None:
        """Update spawn-config rows in place; add new roles, remove stale ones."""
        existing: dict[SpawnRole, "CourseSpawnConfigRow"] = {
            sc.spawn_role: sc for sc in row.spawn_configs
        }
        desired = set(config.spawn_role_selections)

        # Remove roles that are no longer in the config.
        for spawn_role in set(existing) - desired:
            row.spawn_configs.remove(existing[spawn_role])
            del existing[spawn_role]

        # Update existing rows or insert new ones.
        for spawn_role, sel in config.spawn_role_selections.items():
            if spawn_role in existing:
                existing[spawn_role].resource = sel.resource_tier_name
                existing[spawn_role].profile = sel.profile_name
            else:
                row.spawn_configs.append(
                    self._build_single_spawn_config(course_id, spawn_role, sel)
                )


    def update_course(
        self,
        course_id: str,
        config: CourseConfig,
        session: Optional[Session] = None,
    ) -> CourseConfig:
        with self._session(session) as s:
            row = s.get(CourseRow, course_id)
            if row is None:
                raise CourseNotFoundError(course_id)

            # Update scalar fields.
            row.course_name = config.metadata.course_name
            row.description = config.metadata.description
            row.image_family = config.image.family
            row.image_tag = config.image.tag

            # Sync course-level spawn-role configuration in place.
            self._sync_spawn_configs(row, course_id, config)

            # Rebuild terms (flush deletes before inserts to avoid
            # UNIQUE constraint violations from INSERT-before-DELETE ordering).
            row.terms.clear()
            s.flush()
            for term_id, term_config in config.terms.items():
                row.terms.append(
                    self._config_to_term_row(
                        course_id,
                        term_id,
                        term_config,
                    )
                )

            s.flush()
            s.refresh(row)

            return self._course_row_to_config(row)


    def delete_course(
        self,
        course_id: str,
        session: Optional[Session] = None,
    ) -> None:
        with self._session(session) as s:
            row = s.get(CourseRow, course_id)
            if row is None:
                raise CourseNotFoundError(course_id)

            s.delete(row)

    # ── Term-level operations ───────────────────────────────────────

    def get_term(
        self,
        course_id: str,
        term_id: str,
        session: Optional[Session] = None,
    ) -> Optional[TermConfig]:
        with self._session(session) as s:
            course_row = s.get(CourseRow, course_id)
            if course_row is None:
                raise CourseNotFoundError(course_id)

            for term_row in course_row.terms:
                if term_row.term_id == term_id:
                    return self._term_row_to_config(term_row)

            return None

    def add_term(
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

            for term in row.terms:
                if term.term_id == term_id:
                    raise TermExistsError(course_id, term_id)

            row.terms.append(
                self._config_to_term_row(
                    course_id,
                    term_id,
                    config,
                )
            )

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
            course = s.get(CourseRow, course_id)

            if course is None:
                raise CourseNotFoundError(course_id)

            for term in course.terms:
                if term.term_id != term_id:
                    continue

                # Replace image override.
                if config.image is None:
                    term.image_family = None
                    term.image_tag = None
                else:
                    term.image_family = config.image.family
                    term.image_tag = config.image.tag

                # Replace spawn-role overrides.
                term.spawn_configs.clear()
                term.spawn_configs.extend(self._build_term_spawn_configs(config))

                s.flush()
                s.refresh(course)

                return self._course_row_to_config(course)

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

            for term in row.terms:
                if term.term_id == term_id:
                    s.delete(term)
                    s.flush()
                    s.refresh(row)

                    return self._course_row_to_config(row)

            raise TermNotFoundError(course_id, term_id)

    def list_course_ids(
        self,
        session: Optional[Session] = None,
    ) -> List[str]:
        with self._session(session) as s:
            rows = s.query(CourseRow.course_id).all()
            return [r[0] for r in rows]


def get_course_repository_from_db_url(course_db_url: str) -> CourseRepository:
    """Get a CourseRepository instance connected to the specified database URL."""
    engine = init_db(course_db_url)
    session_factory = sessionmaker(bind=engine)
    return CourseRepository(session_factory)
