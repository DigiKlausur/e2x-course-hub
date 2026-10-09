from contextlib import contextmanager
from typing import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base

_engine: Engine | None = None
_SessionFactory: sessionmaker | None = None


def init_db(db_url: str = "sqlite:///courses.db") -> Engine:
    global _engine, _SessionFactory
    _engine = create_engine(db_url)
    Base.metadata.create_all(_engine)
    _SessionFactory = sessionmaker(bind=_engine)
    return _engine


def get_engine() -> Engine:
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _engine


def get_session() -> Session:
    if _SessionFactory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _SessionFactory()


def get_session_factory() -> sessionmaker:
    if _SessionFactory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _SessionFactory


@contextmanager
def scoped_session() -> Generator[Session, None, None]:
    """Provide a transactional session scope.

    Commits on success, rolls back on exception, always closes.
    """
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
