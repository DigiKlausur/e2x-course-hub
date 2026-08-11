from logging import Logger, getLogger
from typing import Optional

from e2x_hub_rbac.backend.jupyterhub import HubAPI

from ..context import AppContext
from .course_api import CourseAPI
from .infrastructure_api import InfrastructureAPI
from .membership_api import MembershipAPI
from .profile_api import ProfileAPI


class API:
    """Central API class aggregating various service APIs."""

    def __init__(
        self,
        server_config_file: str,
        hub_api: HubAPI,
        add_users_to_hub: bool = False,
        logger: Optional[Logger] = None,
    ):
        if logger is None:
            logger = getLogger(__name__)
        self.server_config_file = server_config_file
        self.context = AppContext.from_config_file(server_config_file)

        self.courses = CourseAPI(
            context=self.context,
            logger=logger,
        )
        self.profiles = ProfileAPI(
            context=self.context,
            logger=logger,
        )
        self.memberships = MembershipAPI(
            group_backend=hub_api,
            add_users_to_hub=add_users_to_hub,
            logger=logger,
        )
        self.infrastructure = InfrastructureAPI(
            context=self.context,
            logger=logger,
        )

    def reload_server_config(self) -> None:
        """Reload the server configuration from the configuration file.
        Note: courses are in the database and do not need reloading.
        """
        self.context = AppContext.from_config_file(self.server_config_file)
