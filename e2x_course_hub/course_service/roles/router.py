from typing import TypeVar

from e2x_hub_rbac.auth import Role, Scope
from e2x_hub_rbac.auth.rbac import ROLE_BY_NAME
from fastapi import APIRouter

from ..capabilities import CAPABILITIES_BY_SCOPE, role_has
from ..common.dependency_types import CurrentUser
from .schemas import (
    RoleCapabilitiesResponse,
    RoleCourseCapability,
    RoleLmsCapability,
    RoleName,
    RoleTermCapability,
)

router = APIRouter(
    prefix="/v1/roles",
    tags=["Roles"],
)


RoleCapability = TypeVar(
    "RoleCapability", RoleLmsCapability, RoleCourseCapability, RoleTermCapability
)


def _grants(model: type[RoleCapability], role: Role, scope: Scope) -> list[RoleCapability]:
    return [
        model(id=capability.id, granted=role_has(role, capability))
        for capability in CAPABILITIES_BY_SCOPE[scope]
    ]


@router.get("/{role}/capabilities", response_model=RoleCapabilitiesResponse)
async def get_role_capabilities(role: RoleName, user: CurrentUser) -> RoleCapabilitiesResponse:
    """What a role can and cannot do, e.g. to explain it before adding someone to it.

    The same for every course and term, so any logged-in user may ask.
    """
    rbac_role = ROLE_BY_NAME[role]
    return RoleCapabilitiesResponse(
        role=role,
        lms=_grants(RoleLmsCapability, rbac_role, Scope.LMS),
        course=_grants(RoleCourseCapability, rbac_role, Scope.COURSE),
        term=_grants(RoleTermCapability, rbac_role, Scope.TERM),
    )
