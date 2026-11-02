import json

import pytest

from e2x_course_hub.course_service.membership.dependencies import validate_membership_patch
from e2x_course_hub.course_service.membership.schemas import MembershipPatch
from e2x_course_hub.errors import InvalidUsernamesError
from e2x_course_hub.settings import UsernameSettings

HINT = "Students: 2s ID, e.g. abcde2s"
FORMATS = [{"pattern": r"[a-z]{5}2s", "hint": HINT}]


def make_settings(monkeypatch, enforce_in_api: bool) -> UsernameSettings:
    monkeypatch.setenv("E2X_USERNAME_FORMATS", json.dumps(FORMATS))
    monkeypatch.setenv("E2X_USERNAME_ENFORCE_IN_API", json.dumps(enforce_in_api))
    return UsernameSettings()


def test_invalid_usernames_to_add_are_rejected(monkeypatch):
    settings = make_settings(monkeypatch, enforce_in_api=True)
    body = MembershipPatch(add=["abcde2s", "alice@h-brs.de"])

    with pytest.raises(InvalidUsernamesError) as exc_info:
        validate_membership_patch(body, settings)

    assert exc_info.value.status_code == 422
    assert exc_info.value.extra == {"usernames": ["alice@h-brs.de"], "hints": [HINT]}


def test_invalid_usernames_can_still_be_removed(monkeypatch):
    settings = make_settings(monkeypatch, enforce_in_api=True)
    body = MembershipPatch(remove=["alice@h-brs.de"])

    assert validate_membership_patch(body, settings) is body


def test_invalid_usernames_are_accepted_when_not_enforced(monkeypatch):
    settings = make_settings(monkeypatch, enforce_in_api=False)
    body = MembershipPatch(add=["alice@h-brs.de"])

    assert validate_membership_patch(body, settings) is body
