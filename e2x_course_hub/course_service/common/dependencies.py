from typing import Generator

from e2x_hub_rbac.auth import PermissionChecker
from fastapi import Depends, Request
from jupyterhub_fastapi_adapter.dependencies import User, require_authenticated_user
from sqlalchemy.orm import Session

from ...api.api import API
from ...api.course_api import CourseAPI
from ...api.infrastructure_api import InfrastructureAPI
from ...api.membership_api import MembershipAPI
from ...api.role_permissions import ROLE_PERMISSIONS


# ── API layer dependencies ──────────────────────────────────────────
def get_api(request: Request) -> API:
    """Retrieve the shared API instance from the app state."""
    return request.app.state.api


def get_db_session(api: API = Depends(get_api)) -> Generator[Session, None, None]:
    """Provide a single DB session per request.

    Commits on success, rolls back on exception, always closes.
    """
    session = api.courses.course_repository._session_factory()
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


# ── Actions ─────────────────────────────────────────────────────────
def get_permission_checker(user: User = Depends(require_authenticated_user)) -> PermissionChecker:
    """The current user's permissions from all tables, for building their actions.

    Only for telling the user what they can do; each API still enforces its own
    permissions.
    """
    return PermissionChecker(user, ROLE_PERMISSIONS)
