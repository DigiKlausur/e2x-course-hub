from enum import StrEnum
from typing import TYPE_CHECKING

from e2x_hub_rbac.auth import Role, Scope
from pydantic import BaseModel

from ..capabilities import CAPABILITIES_BY_SCOPE

# Built from the definitions so the OpenAPI schema, and with it the generated
# frontend types, always list exactly the roles and capability ids that exist.
# Type checkers cannot follow enums created at runtime, so they see plain
# strings; pydantic and the OpenAPI schema see the enums.
if TYPE_CHECKING:
    RoleName = str
    LmsCapabilityId = str
    CourseCapabilityId = str
    TermCapabilityId = str
else:

    def _capability_ids(name: str, scope: Scope) -> type[StrEnum]:
        ids = [capability.id for capability in CAPABILITIES_BY_SCOPE[scope]]
        return StrEnum(name, {id: id for id in ids})

    RoleName = StrEnum("RoleName", {role.name: role.role_name for role in Role})
    LmsCapabilityId = _capability_ids("LmsCapabilityId", Scope.LMS)
    CourseCapabilityId = _capability_ids("CourseCapabilityId", Scope.COURSE)
    TermCapabilityId = _capability_ids("TermCapabilityId", Scope.TERM)


# One model per level so each id is typed with its level's enum. Objects rather
# than a dict of id to bool, because a dict loses the key type in the generated
# frontend types.
class RoleLmsCapability(BaseModel):
    id: LmsCapabilityId
    granted: bool


class RoleCourseCapability(BaseModel):
    id: CourseCapabilityId
    granted: bool


class RoleTermCapability(BaseModel):
    id: TermCapabilityId
    granted: bool


class RoleCapabilitiesResponse(BaseModel):
    """Every capability and whether a role has it, grouped by the level each applies to.

    Denied capabilities are included so a role can be explained by what it can
    and cannot do. The order follows the definitions.
    """

    role: RoleName
    lms: list[RoleLmsCapability]
    course: list[RoleCourseCapability]
    term: list[RoleTermCapability]
