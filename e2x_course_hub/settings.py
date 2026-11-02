"""Central, framework-agnostic settings for e2x_course_hub.

These settings are consumed by ``loader.py`` to build the ``api`` package's
objects and are independent of the FastAPI service. Web-only settings (e.g.
``service_prefix``) live in ``course_service.settings.ServiceSettings``,
which extends ``CoreSettings``.
"""

import re

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class HubApiSettings(BaseSettings):
    token: str = Field(default="", validation_alias="JUPYTERHUB_API_TOKEN")
    url: str = Field(default="", validation_alias="JUPYTERHUB_API_URL")


class CourseSettings(BaseSettings):
    db_url: str = Field(default="sqlite:///courses.db", validation_alias="E2X_COURSE_DB_URL")


class MembershipSettings(BaseSettings):
    add_users_to_hub: bool = Field(default=False, validation_alias="E2X_ADD_USERS_TO_HUB")
    delete_empty_groups: bool = Field(default=False, validation_alias="E2X_DELETE_EMPTY_GROUPS")


class UsernameFormat(BaseModel):
    """An accepted username format, with a hint telling users how to enter it."""

    pattern: re.Pattern[str]
    hint: str

    def matches(self, username: str) -> bool:
        return self.pattern.fullmatch(username) is not None


class UsernameSettings(BaseSettings):
    """Username formats of the university. Without formats, every username is accepted."""

    formats: list[UsernameFormat] = Field(
        default_factory=list, validation_alias="E2X_USERNAME_FORMATS"
    )
    enforce_in_api: bool = Field(default=False, validation_alias="E2X_USERNAME_ENFORCE_IN_API")

    def invalid_usernames(self, usernames: list[str]) -> list[str]:
        """Return the usernames that match none of the formats."""
        if not self.formats:
            return []
        return [u for u in usernames if not any(f.matches(u) for f in self.formats)]


class InfrastructureSettings(BaseSettings):
    provider: str = Field(default="default", validation_alias="E2X_INFRASTRUCTURE_PROVIDER")


class CoreSettings(BaseSettings):
    """Settings needed to build the full API layer, independent of any web framework."""

    hub_api: HubApiSettings = Field(default_factory=HubApiSettings)
    courses: CourseSettings = Field(default_factory=CourseSettings)
    membership: MembershipSettings = Field(default_factory=MembershipSettings)
    usernames: UsernameSettings = Field(default_factory=UsernameSettings)
    infrastructure: InfrastructureSettings = Field(default_factory=InfrastructureSettings)
