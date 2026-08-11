from e2x_hub_rbac.auth import UserLike
from e2x_hub_rbac.auth.decorator import require_permission

from ..context import AppContext
from ..schema.infrastructure import ImageCatalog, ResourceTiersByRole
from ..schema.profile import AvailableProfileDetails, AvailableProfiles
from .base import APIWithContext
from .infrastructure_permissions import INFRASTRUCTURE_ROLE_PERMISSIONS, InfrastructurePermission


class InfrastructureAPI(APIWithContext):
    def __init__(self, context: AppContext, logger=None):
        super().__init__(
            context=context, role_permissions=INFRASTRUCTURE_ROLE_PERMISSIONS, logger=logger
        )

    @require_permission(InfrastructurePermission.HUB_VIEW_IMAGE_CATALOG)
    def list_images(self, user: UserLike) -> ImageCatalog:
        return self.context.infrastructure_catalog.image_catalog

    @require_permission(InfrastructurePermission.HUB_VIEW_RESOURCE_CATALOG)
    def list_resources(self, user: UserLike) -> ResourceTiersByRole:
        return self.context.infrastructure_catalog.resource_tiers

    @require_permission(InfrastructurePermission.HUB_VIEW_PROFILE_CATALOG)
    def list_profiles(self, user: UserLike) -> AvailableProfiles:
        return self.context.profile_catalog.list_available_profiles()

    @require_permission(InfrastructurePermission.HUB_VIEW_PROFILE_CATALOG)
    def list_profiles_details(self, user: UserLike) -> AvailableProfileDetails:
        return self.context.profile_catalog.list_available_profile_details()
