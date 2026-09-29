from e2x_hub_rbac.api import BaseAPI
from e2x_hub_rbac.auth import UserLike
from e2x_hub_rbac.auth.decorator import require_permission

from ..contract.providers import InfrastructureCatalogProvider
from ..schema.catalog import (
    ImageFamilyOptions,
    InfrastructureCatalogOptions,
    ProfileOptions,
    ResourceTierOptions,
)
from ..schema.types import SpawnRole
from .infrastructure_permissions import INFRASTRUCTURE_ROLE_PERMISSIONS, InfrastructurePermission


class InfrastructureAPI(BaseAPI):
    def __init__(self, infrastructure_provider: InfrastructureCatalogProvider, logger=None):
        super().__init__(role_permissions=INFRASTRUCTURE_ROLE_PERMISSIONS, logger=logger)
        self._infrastructure_provider = infrastructure_provider

    @property
    def infrastructure_options(self) -> InfrastructureCatalogOptions:
        return self._infrastructure_provider.get_infrastructure_catalog()

    @require_permission(InfrastructurePermission.LMS_VIEW_IMAGE_CATALOG)
    def list_images(self, user: UserLike) -> ImageFamilyOptions:
        return self.infrastructure_options.image_family_options

    @require_permission(InfrastructurePermission.LMS_VIEW_RESOURCE_CATALOG)
    def list_resources(self, user: UserLike) -> dict[SpawnRole, ResourceTierOptions]:
        return {
            spawn_role: self.infrastructure_options.spawn_role_options[
                spawn_role
            ].resource_tier_options
            for spawn_role in SpawnRole
        }

    @require_permission(InfrastructurePermission.LMS_VIEW_PROFILE_CATALOG)
    def list_profiles(self, user: UserLike) -> dict[SpawnRole, ProfileOptions]:
        return {
            spawn_role: self.infrastructure_options.spawn_role_options[spawn_role].profile_options
            for spawn_role in SpawnRole
        }
