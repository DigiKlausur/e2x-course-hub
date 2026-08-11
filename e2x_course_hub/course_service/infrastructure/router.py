from fastapi import APIRouter

from ..common.dependency_types import CurrentUser, InfrastructureAPIDep
from .dependencies import InfrastructureAssemblerDep
from .schemas import ImageCatalogResponse, ProfileCatalogResponse, ResourceTiersResponse

router = APIRouter(prefix="/v1/catalogs", tags=["Infrastructure"])


@router.get("/image-catalog", response_model=ImageCatalogResponse)
async def list_images(
    user: CurrentUser,
    infrastructure_api: InfrastructureAPIDep,
    infrastructure_assembler: InfrastructureAssemblerDep,
):
    return infrastructure_assembler.image_catalog(infrastructure_api.list_images(user))


@router.get("/resource-tiers", response_model=ResourceTiersResponse)
async def list_resources(
    user: CurrentUser,
    infrastructure_api: InfrastructureAPIDep,
    infrastructure_assembler: InfrastructureAssemblerDep,
):
    return infrastructure_assembler.resource_tiers(infrastructure_api.list_resources(user))


@router.get("/profile-catalog", response_model=ProfileCatalogResponse)
async def list_profiles(
    user: CurrentUser,
    infrastructure_api: InfrastructureAPIDep,
    infrastructure_assembler: InfrastructureAssemblerDep,
):
    profiles = infrastructure_api.list_profiles_details(user)
    return infrastructure_assembler.profile_catalog(profiles)
