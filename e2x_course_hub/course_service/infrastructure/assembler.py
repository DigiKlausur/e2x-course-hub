from e2x_hub_rbac.auth import PermissionChecker

from ...schema.catalog import ImageFamilyOptions, ProfileOptions, ResourceTierOptions
from ...schema.types import SpawnRole
from ..actions import LmsActions, lms_actions, user_can
from .schemas import (
    ImageCatalogResponse,
    ProfileCatalogResponse,
    ResourceTiersResponse,
)


class InfrastructureAssembler:
    def __init__(self, permission_checker: PermissionChecker):
        self.permission_checker = permission_checker

    def _lms_actions(self) -> LmsActions:
        return lms_actions(user_can(self.permission_checker))

    def image_catalog(self, image_catalog: ImageFamilyOptions) -> ImageCatalogResponse:
        return ImageCatalogResponse(
            actions=self._lms_actions().catalogs.images, catalog=image_catalog
        )

    def resource_tiers(
        self, resource_tiers: dict[SpawnRole, ResourceTierOptions]
    ) -> ResourceTiersResponse:
        return ResourceTiersResponse(
            actions=self._lms_actions().catalogs.resources, catalog=resource_tiers
        )

    def profile_catalog(
        self, available_profiles: dict[SpawnRole, ProfileOptions]
    ) -> ProfileCatalogResponse:
        return ProfileCatalogResponse(
            actions=self._lms_actions().catalogs.profiles, catalog=available_profiles
        )
