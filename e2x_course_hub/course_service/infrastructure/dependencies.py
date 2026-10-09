from typing import Annotated

from fastapi import Depends

from ..common.dependency_types import PermissionCheckerDep
from .assembler import InfrastructureAssembler


def get_infrastructure_assembler(
    permission_checker: PermissionCheckerDep,
) -> InfrastructureAssembler:
    return InfrastructureAssembler(permission_checker=permission_checker)


InfrastructureAssemblerDep = Annotated[
    InfrastructureAssembler, Depends(get_infrastructure_assembler)
]
