import json

import pytest
from pydantic import ValidationError

from e2x_course_hub.settings import UsernameSettings

FORMATS = [
    {"pattern": r"cid\d+[a-z]+", "hint": "Staff: campus ID, e.g. cid12354abc"},
    {"pattern": r"[a-z]{5}2s", "hint": "Students: 2s ID, e.g. abcde2s"},
]


@pytest.fixture
def settings(monkeypatch):
    monkeypatch.setenv("E2X_USERNAME_FORMATS", json.dumps(FORMATS))
    return UsernameSettings()


def test_formats_are_read_from_the_environment(settings):
    assert [f.hint for f in settings.formats] == [f["hint"] for f in FORMATS]
    assert settings.enforce_in_api is False


def test_usernames_matching_any_format_are_valid(settings):
    assert settings.invalid_usernames(["cid12354abc", "abcde2s"]) == []


def test_usernames_must_match_a_format_completely(settings):
    usernames = ["alice@h-brs.de", "abcde2s@h-brs.de", "xcid1a"]

    assert settings.invalid_usernames(usernames) == usernames


def test_without_formats_every_username_is_valid():
    assert UsernameSettings().invalid_usernames(["alice@h-brs.de"]) == []


def test_an_invalid_regex_is_rejected(monkeypatch):
    monkeypatch.setenv("E2X_USERNAME_FORMATS", json.dumps([{"pattern": "[a-z", "hint": "x"}]))

    with pytest.raises(ValidationError):
        UsernameSettings()


def test_formats_dump_patterns_as_strings(settings):
    assert settings.model_dump(mode="json")["formats"] == FORMATS
