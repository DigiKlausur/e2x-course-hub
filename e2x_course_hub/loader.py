"""Composition root for e2x_course_hub.

Turns ``settings.py`` config into concrete ``api`` objects. This module has
no FastAPI dependency, so it can be used by the web service as well as by
standalone scripts that only need part of the API surface (e.g. just a
``SpawnOfferingProvider``).
"""

from importlib.metadata import entry_points
from typing import Optional

from e2x_hub_rbac.backend.jupyterhub import HubAPI

from .api.api import API
from .api.spawn_api import SpawnAPI
from .contract.providers import InfrastructureCatalogProvider
from .db.repository import CourseRepository, get_course_repository_from_db_url
from .settings import CoreSettings, CourseSettings


def load_infrastructure_catalog_provider(entry_point_name: str) -> InfrastructureCatalogProvider:
    """
    Dynamically load and instantiate an InfrastructureCatalogProvider implementation.

    The entry point must resolve to a zero-argument callable (typically a class with
    no required constructor arguments) that returns an instance implementing
    ``InfrastructureCatalogProvider``. Providers own their own configuration (e.g. by
    reading their settings from the environment via pydantic-settings, same as the
    ``CoreSettings`` classes in this package) so the hub never needs to know a
    provider-specific config shape.

    Args:
        entry_point_name (str): The entry point name registered under the
            'e2x_course_hub.infrastructure_catalog_providers' group.

    Returns:
        InfrastructureCatalogProvider: An instance of the loaded InfrastructureCatalogProvider.

    Raises:
        ImportError: If the entry point or the module/class it points to cannot be imported.
        TypeError: If the constructed object does not implement InfrastructureCatalogProvider.
    """
    try:
        for entry_point in entry_points(group="e2x_course_hub.infrastructure_catalog_providers"):
            if entry_point.name == entry_point_name:
                provider_factory = entry_point.load()
                provider = provider_factory()
                if not isinstance(provider, InfrastructureCatalogProvider):
                    raise TypeError(
                        f"'{entry_point.value}' does not implement InfrastructureCatalogProvider."
                    )
                return provider
        raise ValueError(
            f"No entry point found for '{entry_point_name}' in "
            "'e2x_course_hub.infrastructure_catalog_providers'."
        )
    except (ImportError, AttributeError, ValueError) as e:
        raise ImportError(
            f"Failed to load InfrastructureCatalogProvider from '{entry_point_name}': {e}"
        )


def get_course_repository(
    course_db_url: Optional[str] = None,
    settings: Optional[CourseSettings] = None,
) -> CourseRepository:
    """Build a CourseRepository, falling back to CourseSettings when not given explicitly."""
    settings = settings or CourseSettings()
    return get_course_repository_from_db_url(course_db_url or settings.db_url)


def load_spawn_api(
    course_repository: Optional[CourseRepository] = None,
    settings: Optional[CourseSettings] = None,
) -> SpawnAPI:
    """Build a standalone SpawnAPI, without needing the rest of the API layer."""
    course_repository = course_repository or get_course_repository(settings=settings)
    return SpawnAPI(course_repository=course_repository)


def load_api(settings: Optional[CoreSettings] = None) -> API:
    """
    Build the full API aggregate.

    Args:
        settings (Optional[CoreSettings]): Settings to configure the API. Accepts
            any CoreSettings subclass (e.g. course_service.settings.ServiceSettings).

    Returns:
        API: An instance of the API class.
    """
    settings = settings or CoreSettings()
    hub_api = HubAPI(api_token=settings.hub_api.token, api_url=settings.hub_api.url)
    infrastructure_catalog_provider = load_infrastructure_catalog_provider(
        settings.infrastructure.provider
    )
    course_repository = get_course_repository(settings=settings.courses)

    return API(
        hub_api=hub_api,
        course_repository=course_repository,
        infrastructure_provider=infrastructure_catalog_provider,
        add_users_to_hub=settings.membership.add_users_to_hub,
    )
