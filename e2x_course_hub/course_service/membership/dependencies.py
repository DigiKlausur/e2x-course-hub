from typing import Annotated

from fastapi import Depends

from ..common.dependency_types import CurrentUser, MembershipAPIDep
from .assembler import MembershipAssembler


def get_membership_assembler(
    user: CurrentUser,
    membership_api: MembershipAPIDep,
) -> MembershipAssembler:
    return MembershipAssembler(
        membership_permission_checker=membership_api.permission_checker(user),
    )


MembershipAssemblerDep = Annotated[MembershipAssembler, Depends(get_membership_assembler)]
