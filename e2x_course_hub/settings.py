"""Central, framework-agnostic settings for e2x_course_hub.

These settings are consumed by ``loader.py`` to build the ``api`` package's
objects and are independent of the FastAPI service. Web-only settings (e.g.
``service_prefix``) live in ``course_service.settings.ServiceSettings``,
which extends ``CoreSettings``.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class HubApiSettings(BaseSettings):
    token: str = Field(default="", validation_alias="JUPYTERHUB_API_TOKEN")
    url: str = Field(default="", validation_alias="JUPYTERHUB_API_URL")


class CourseSettings(BaseSettings):
    db_url: str = Field(default="sqlite:///courses.db", validation_alias="E2X_COURSE_DB_URL")


class MembershipSettings(BaseSettings):
    add_users_to_hub: bool = Field(default=False, validation_alias="E2X_ADD_USERS_TO_HUB")


class InfrastructureSettings(BaseSettings):
    provider: str = Field(default="default", validation_alias="E2X_INFRASTRUCTURE_PROVIDER")


class CoreSettings(BaseSettings):
    """Settings needed to build the full API layer, independent of any web framework."""

    hub_api: HubApiSettings = Field(default_factory=HubApiSettings)
    courses: CourseSettings = Field(default_factory=CourseSettings)
    membership: MembershipSettings = Field(default_factory=MembershipSettings)
    infrastructure: InfrastructureSettings = Field(default_factory=InfrastructureSettings)
