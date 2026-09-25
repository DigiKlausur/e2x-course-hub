from enum import StrEnum
from typing import TYPE_CHECKING

from e2x_hub_rbac.auth import Role
from pydantic import BaseModel

from ..actions import CourseActions, LmsActions, TermActions

# Built from the roles so the OpenAPI schema lists exactly the roles that exist.
# Type checkers cannot follow enums created at runtime, so they see a plain
# string; pydantic and the OpenAPI schema see the enum.
if TYPE_CHECKING:
    RoleName = str
else:
    RoleName = StrEnum("RoleName", {role.name: role.role_name for role in Role})


class RoleActionsResponse(BaseModel):
    """What a role can and cannot do at each level."""

    role: RoleName
    lms: LmsActions
    course: CourseActions
    term: TermActions
