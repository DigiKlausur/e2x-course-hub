from e2x_hub_rbac.auth.rbac import ROLE_BY_NAME
from fastapi import APIRouter

from ..actions import course_actions, lms_actions, role_can, term_actions
from ..common.dependency_types import CurrentUser
from .schemas import RoleActionsResponse, RoleName

router = APIRouter(
    prefix="/v1/roles",
    tags=["Roles"],
)


@router.get("/{role}/actions", response_model=RoleActionsResponse)
async def get_role_actions(role: RoleName, user: CurrentUser) -> RoleActionsResponse:
    """What a role can and cannot do, e.g. to explain it before adding someone to it.

    The same for every course and term, so any logged-in user may ask.
    """
    can = role_can(ROLE_BY_NAME[role])
    return RoleActionsResponse(
        role=role,
        lms=lms_actions(can),
        course=course_actions(can),
        term=term_actions(can),
    )
