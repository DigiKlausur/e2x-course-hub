from pydantic import BaseModel

from ...schema.infrastructure import ImageCatalog, ResourceTiersByRole
from ...schema.profile import AvailableProfileDetails


class InfrastructureCapabilities(BaseModel):
    manage: bool = False
    view: bool = False


class ImageCatalogResponse(BaseModel):
    capabilities: InfrastructureCapabilities
    catalog: ImageCatalog


class ResourceTiersResponse(BaseModel):
    capabilities: InfrastructureCapabilities
    catalog: ResourceTiersByRole


class ProfileCatalogResponse(BaseModel):
    capabilities: InfrastructureCapabilities
    catalog: AvailableProfileDetails
