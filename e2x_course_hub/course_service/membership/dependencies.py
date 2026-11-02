from typing import Annotated

from fastapi import Depends

from ...errors import InvalidUsernamesError
from ..common.dependency_types import UsernameSettingsDep
from .schemas import MembershipPatch


def validate_membership_patch(
    body: MembershipPatch,
    username_settings: UsernameSettingsDep,
) -> MembershipPatch:
    """Reject usernames to add that match no username format, if enforced in the API.

    Removals are never checked, so members with outdated usernames can still be removed.
    """
    if username_settings.enforce_in_api:
        invalid = username_settings.invalid_usernames(body.add)
        if invalid:
            raise InvalidUsernamesError(invalid, [f.hint for f in username_settings.formats])
    return body


ValidatedMembershipPatch = Annotated[MembershipPatch, Depends(validate_membership_patch)]
