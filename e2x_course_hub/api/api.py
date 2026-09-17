from logging import Logger, getLogger
from typing import Optional

from e2x_hub_rbac.backend.jupyterhub import HubAPI

from ..contract.providers import InfrastructureCatalogProvider
from ..db.repository import CourseRepository
from .course_api import CourseAPI
from .infrastructure_api import InfrastructureAPI
from .membership_api import MembershipAPI


class API:
    """Central API class aggregating various service APIs."""

    def __init__(
        self,
        hub_api: HubAPI,
        course_repository: CourseRepository,
        infrastructure_provider: InfrastructureCatalogProvider,
        add_users_to_hub: bool = False,
        delete_empty_groups: bool = False,
        logger: Optional[Logger] = None,
    ):
        if logger is None:
            logger = getLogger(__name__)

        self.courses = CourseAPI(
            course_repository=course_repository,
            infrastructure_catalog_provider=infrastructure_provider,
            logger=logger,
        )
        self.memberships = MembershipAPI(
            group_backend=hub_api,
            add_users_to_hub=add_users_to_hub,
            delete_empty_groups=delete_empty_groups,
            logger=logger,
        )
        self.infrastructure = InfrastructureAPI(
            infrastructure_provider=infrastructure_provider,
            logger=logger,
        )
