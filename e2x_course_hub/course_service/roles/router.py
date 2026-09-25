from e2x_hub_rbac.auth import Scope
from e2x_hub_rbac.auth.rbac import ROLE_BY_NAME
from fastapi import APIRouter

from ..capabilities import role_capabilities
from ..common.dependency_types import CurrentUser
from .schemas import RoleCapabilitiesResponse, RoleName

router = APIRouter(
    prefix="/v1/roles",
    tags=["Roles"],
)


@router.get("/{role}/capabilities", response_model=RoleCapabilitiesResponse)
async def get_role_capabilities(role: RoleName, user: CurrentUser) -> RoleCapabilitiesResponse:
    """What a role may do, e.g. to explain it before adding someone to it.

    The same for every course and term, so any logged-in user may ask.
    """
    capabilities = role_capabilities(ROLE_BY_NAME[role])
    return RoleCapabilitiesResponse(
        role=role,
        lms=[capability.id for capability in capabilities[Scope.LMS]],
        course=[capability.id for capability in capabilities[Scope.COURSE]],
        term=[capability.id for capability in capabilities[Scope.TERM]],
    )
