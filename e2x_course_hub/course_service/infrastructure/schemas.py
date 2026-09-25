from pydantic import BaseModel

from ...schema.catalog import ImageFamilyOptions, ProfileOptions, ResourceTierOptions
from ...schema.types import SpawnRole
from ..actions import CatalogActions


class ImageCatalogResponse(BaseModel):
    actions: CatalogActions
    catalog: ImageFamilyOptions


class ResourceTiersResponse(BaseModel):
    actions: CatalogActions
    catalog: dict[SpawnRole, ResourceTierOptions]


class ProfileCatalogResponse(BaseModel):
    actions: CatalogActions
    catalog: dict[SpawnRole, ProfileOptions]
