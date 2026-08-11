from typing import Annotated

from fastapi import Depends

from ..common.dependency_types import (
    CurrentUser,
    InfrastructureAPIDep,
)
from .assembler import InfrastructureAssembler


def get_infrastructure_assembler(
    user: CurrentUser,
    infrastructure_api: InfrastructureAPIDep,
) -> InfrastructureAssembler:
    return InfrastructureAssembler(
        infrastructure_permission_checker=infrastructure_api.permission_checker(user),
    )


InfrastructureAssemblerDep = Annotated[
    InfrastructureAssembler, Depends(get_infrastructure_assembler)
]
