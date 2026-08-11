import os
from logging import Logger, getLogger
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from .db.database import init_db
from .db.repository import CourseRepository
from .schema.infrastructure import InfrastructureCatalog
from .schema.mount import MountCatalog
from .schema.profile import ProfileCatalog, ProfilesConfig


def load_yaml(yaml_file):
    """
    Loads a YAML file and returns its contents as a dictionary.

    Args:
        yaml_file (str): Path to the YAML file.
    Returns:
        dict: The contents of the YAML file.
    """
    with open(yaml_file, "r") as f:
        return yaml.safe_load(f)


class ServerConfig(BaseModel):
    """
    Configuration for the server.
    """

    server_config_file: str = Field(..., description="The path to the server configuration file.")
    db_url: str = Field(
        default="sqlite:///courses.db",
        description="Database URL for course storage.",
    )
    profiles: ProfilesConfig = Field(..., description="Profiles configuration.")
    mount_catalog_file: str = Field(..., description="The YAML file containing mount definitions.")
    infrastructure_catalog_file: str = Field(
        ..., description="The YAML file containing the infrastructure catalog."
    )

    @classmethod
    def from_config_file(cls, config_file: str):
        root = os.path.abspath(os.path.dirname(config_file))
        raw = load_yaml(config_file)
        server_config = cls(server_config_file=config_file, **raw)

        server_config.profiles.profile_dir = os.path.join(root, server_config.profiles.profile_dir)
        if not os.path.exists(server_config.profiles.profile_dir):
            os.makedirs(server_config.profiles.profile_dir)
        server_config.mount_catalog_file = os.path.join(root, server_config.mount_catalog_file)
        if not os.path.exists(server_config.mount_catalog_file):
            raise FileNotFoundError(
                f"Mount definitions file '{server_config.mount_catalog_file}' does not exist."
            )
        server_config.infrastructure_catalog_file = os.path.join(
            root, server_config.infrastructure_catalog_file
        )
        if not os.path.exists(server_config.infrastructure_catalog_file):
            raise FileNotFoundError(
                f"Infrastructure definitions file '{server_config.infrastructure_catalog_file}' "
                "does not exist."
            )

        # Resolve relative sqlite paths against config dir
        if server_config.db_url.startswith("sqlite:///") and not server_config.db_url.startswith(
            "sqlite:////"
        ):
            db_path = server_config.db_url.replace("sqlite:///", "")
            server_config.db_url = f"sqlite:///{os.path.join(root, db_path)}"

        return server_config


class AppContext(BaseModel):
    """
    Application context holding catalogs, repositories, and infrastructure
    needed by the API layer. Not a schema — this is the runtime service container.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    config: ServerConfig = Field(..., description="The server config")
    profile_catalog: ProfileCatalog = Field(..., description="The profile catalog for the server.")
    mount_catalog: MountCatalog = Field(..., description="The mount catalog for the server.")
    infrastructure_catalog: InfrastructureCatalog = Field(
        ..., description="The infrastructure catalog for the server."
    )
    course_repo: CourseRepository = Field(
        ..., description="Repository for course data persistence."
    )

    # ── Course convenience methods ──────────────────────────────────

    def get_course(self, course_id: str, session: Optional[Session] = None):
        """Get a course by ID, returns None if not found."""
        return self.course_repo.get_course(course_id, session=session)

    def list_courses(self, session: Optional[Session] = None) -> Dict:
        """Return all courses as {course_id: CourseConfig}."""
        return self.course_repo.list_courses(session=session)

    def list_course_ids(self, session: Optional[Session] = None) -> List[str]:
        """Return all course IDs."""
        return self.course_repo.list_course_ids(session=session)

    @classmethod
    def from_server_config(cls, server_config: ServerConfig, logger: Optional[Logger] = None):
        if logger is None:
            logger = getLogger(__name__)

        from sqlalchemy.orm import sessionmaker

        engine = init_db(server_config.db_url)
        course_repo = CourseRepository(sessionmaker(bind=engine))

        profile_catalog = ProfileCatalog.from_profiles_config(server_config.profiles)
        return cls(
            config=server_config,
            profile_catalog=profile_catalog,
            mount_catalog=MountCatalog.from_config_file(server_config.mount_catalog_file),
            infrastructure_catalog=InfrastructureCatalog.from_config_file(
                server_config.infrastructure_catalog_file
            ),
            course_repo=course_repo,
        )

    @classmethod
    def from_config_file(cls, config_file: str):
        server_config = ServerConfig.from_config_file(config_file)
        return cls.from_server_config(server_config)
