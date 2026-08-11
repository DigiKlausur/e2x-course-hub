from e2x_hub_rbac.auth import PermissionChecker

from ...api.infrastructure_permissions import InfrastructurePermission
from ...schema.infrastructure import ImageCatalog, ResourceTiersByRole
from ...schema.profile import AvailableProfileDetails
from .schemas import (
    ImageCatalogResponse,
    InfrastructureCapabilities,
    ProfileCatalogResponse,
    ResourceTiersResponse,
)


class InfrastructureAssembler:
    def __init__(
        self,
        infrastructure_permission_checker: PermissionChecker,
    ):
        self.infrastructure_permission_checker = infrastructure_permission_checker

    def _image_catalog_capabilities(self) -> InfrastructureCapabilities:
        return InfrastructureCapabilities(
            manage=self.infrastructure_permission_checker.has_permission(
                InfrastructurePermission.LMS_MANAGE_IMAGE_CATALOG
            ),
            view=self.infrastructure_permission_checker.has_permission(
                InfrastructurePermission.LMS_VIEW_IMAGE_CATALOG
            ),
        )

    def _resource_catalog_capabilities(self) -> InfrastructureCapabilities:
        return InfrastructureCapabilities(
            manage=self.infrastructure_permission_checker.has_permission(
                InfrastructurePermission.LMS_MANAGE_RESOURCE_CATALOG
            ),
            view=self.infrastructure_permission_checker.has_permission(
                InfrastructurePermission.LMS_VIEW_RESOURCE_CATALOG
            ),
        )

    def _profile_catalog_capabilities(self) -> InfrastructureCapabilities:
        return InfrastructureCapabilities(
            manage=self.infrastructure_permission_checker.has_permission(
                InfrastructurePermission.LMS_MANAGE_PROFILE_CATALOG
            ),
            view=self.infrastructure_permission_checker.has_permission(
                InfrastructurePermission.LMS_VIEW_PROFILE_CATALOG
            ),
        )

    def image_catalog(self, image_catalog: ImageCatalog) -> ImageCatalogResponse:
        return ImageCatalogResponse(
            capabilities=self._image_catalog_capabilities(), catalog=image_catalog
        )

    def resource_tiers(self, resource_tiers: ResourceTiersByRole) -> ResourceTiersResponse:
        return ResourceTiersResponse(
            capabilities=self._resource_catalog_capabilities(), catalog=resource_tiers
        )

    def profile_catalog(
        self, available_profiles: AvailableProfileDetails
    ) -> ProfileCatalogResponse:
        return ProfileCatalogResponse(
            capabilities=self._profile_catalog_capabilities(), catalog=available_profiles
        )
