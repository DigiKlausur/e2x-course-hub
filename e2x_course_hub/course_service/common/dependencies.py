from typing import Generator

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from ...api.api import API
from ...api.course_api import CourseAPI
from ...api.infrastructure_api import InfrastructureAPI
from ...api.membership_api import MembershipAPI
from ...api.profile_api import ProfileAPI


# ── API layer dependencies ──────────────────────────────────────────
def get_api(request: Request) -> API:
    """Retrieve the shared API instance from the app state."""
    return request.app.state.api


def get_db_session(api: API = Depends(get_api)) -> Generator[Session, None, None]:
    """Provide a single DB session per request.

    Commits on success, rolls back on exception, always closes.
    """
    session = api.context.course_repo._session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_course_api(api: API = Depends(get_api)) -> CourseAPI:
    return api.courses


def get_membership_api(api: API = Depends(get_api)) -> MembershipAPI:
    return api.memberships


def get_infrastructure_api(api: API = Depends(get_api)) -> InfrastructureAPI:
    return api.infrastructure


def get_profile_api(api: API = Depends(get_api)) -> ProfileAPI:
    return api.profiles
