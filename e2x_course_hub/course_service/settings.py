"""Settings specific to running e2x_course_hub as the FastAPI service."""

from pydantic import Field

from ..settings import CoreSettings


class ServiceSettings(CoreSettings):
    """Adds web-only settings (service prefix) on top of CoreSettings."""

    service_prefix: str = Field("/", validation_alias="JUPYTERHUB_SERVICE_PREFIX")
