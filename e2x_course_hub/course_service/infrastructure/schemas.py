from pydantic import BaseModel

from ...schema.catalog import ImageFamilyOptions, ProfileOptions, ResourceTierOptions
from ...schema.types import SpawnRole


class InfrastructureCapabilities(BaseModel):
    manage: bool = False
    view: bool = False


class ImageCatalogResponse(BaseModel):
    capabilities: InfrastructureCapabilities
    catalog: ImageFamilyOptions


class ResourceTiersResponse(BaseModel):
    capabilities: InfrastructureCapabilities
    catalog: dict[SpawnRole, ResourceTierOptions]


class ProfileCatalogResponse(BaseModel):
    capabilities: InfrastructureCapabilities
    catalog: dict[SpawnRole, ProfileOptions]
