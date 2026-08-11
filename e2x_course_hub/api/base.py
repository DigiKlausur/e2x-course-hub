from e2x_hub_rbac.api.base_api import BaseAPI
from e2x_hub_rbac.auth import RolePermissions

from ..context import AppContext


class APIWithContext(BaseAPI):
    """API class that includes the application context."""

    def __init__(self, context: AppContext, role_permissions: RolePermissions, logger=None):
        super().__init__(logger=logger, role_permissions=role_permissions)
        self.context = context
