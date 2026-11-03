"""Settings specific to running e2x_course_hub as the FastAPI service."""

from pydantic import Field

from ..settings import CoreSettings


class ServiceSettings(CoreSettings):
    """Adds web-only settings (service prefix, hub base URL) on top of CoreSettings."""

    service_prefix: str = Field("/", validation_alias="JUPYTERHUB_SERVICE_PREFIX")
    # Used to link to hub pages, such as the spawn page after joining a term.
    hub_base_url: str = Field("/", validation_alias="JUPYTERHUB_BASE_URL")
