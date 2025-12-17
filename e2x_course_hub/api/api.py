from logging import Logger, getLogger
from typing import Optional

from ..schema.server import Server
from .course_api import CourseAPI
from .hub_api import HubAPI
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
        """Initialize the API with the given server configuration file.

        Args:
            server_config_file: Path to the server configuration YAML file
            hub_api: Instance of the HubAPI class
            add_users_to_hub: Whether to add users to JupyterHub when they are created in the course
                service
            logger: Optional logger for logging purposes
        """
        if logger is None:
            logger = getLogger(__name__)
        self.server_config_file = server_config_file
        self.server = Server.from_config_file(server_config_file)
        self.course_api = CourseAPI(
            server=self.server,
            hub_api=hub_api,
            add_users_to_hub=add_users_to_hub,
            logger=logger,
        )
        self.profile_api = ProfileAPI(server=self.server, logger=logger)

    def reload_server_config(self) -> None:
        """Reload the server configuration from the configuration file."""
        self.server = Server.from_config_file(self.server_config_file)
