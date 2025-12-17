import glob
import os
from logging import Logger, getLogger
from typing import Dict, Optional

import yaml
from pydantic import BaseModel, Field, ValidationError

from .course import Course, CourseConfig
from .mount import MountDefinition
from .profile import BaseProfile, ProfileLoader, get_merged_profile
from .roles import Roles


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


def load_profiles(profile_path, logger: Optional[Logger] = None):
    """
    Load all profiles from the specified directory.

    Args:
        profile_path (str): Path to the directory containing profile YAML files.
        logger (Optional[Logger]): Logger for logging errors. If None, a default logger is created.
    Returns:
        Dict[str, BaseProfile]: A mapping of profile names to BaseProfile objects.
    """
    if logger is None:
        logger = getLogger(__name__)
    profiles = {}
    for profile_file in glob.glob(os.path.join(profile_path, "*.yaml")):
        try:
            with open(profile_file, "r") as f:
                raw_profile = yaml.safe_load(f)
            profile = ProfileLoader.model_validate(raw_profile).model
            profiles[profile.name] = profile
        except ValidationError as e:
            logger.error(f"Failed to validate profile from {profile_file}: {e}")
        except Exception as e:
            logger.error(f"Failed to load profile from {profile_file}: {e}")
    for name in profiles.keys():
        profiles[name] = get_merged_profile(name, profiles)
    return profiles


def load_course_configs(course_config_dir, logger: Optional[Logger] = None):
    """
    Load all course configurations from the specified directory.

    Args:
        course_config_dir (str): Path to the directory containing course config YAML files.
        logger (Optional[Logger]): Logger for logging errors. If None, a default logger is created.
    Returns:
        Dict[str, CourseConfig]: A mapping of course IDs to CourseConfig objects.

    Note:
        - If a course config fails validation, an error is logged and the file is skipped.
        - If two files have the same course_id, an error is logged and the later file is skipped.
    """
    if logger is None:
        logger = getLogger(__name__)
    courses = {}
    for course_config_file in glob.glob(os.path.join(course_config_dir, "*.yaml")):
        try:
            with open(course_config_file, "r") as f:
                course_config = CourseConfig(**yaml.safe_load(f))
                course_id = course_config.metadata.course_id

                if course_id in courses:
                    logger.error(
                        f"Duplicate course_id '{course_id}' found in {course_config_file}. "
                        f"Already loaded from another file. Skipping."
                    )
                    continue

                courses[course_id] = course_config
        except ValidationError as e:
            logger.error(f"Failed to validate course config from {course_config_file}: {e}")
        except Exception as e:
            logger.error(f"Failed to load course config from {course_config_file}: {e}")
    return courses


def load_mount_definitions(mount_definitions_file: str) -> Dict[str, MountDefinition]:
    """
    Load mount definitions from the specified YAML file.

    Args:
        mount_definitions_file (str): Path to the YAML file containing mount definitions.
    Returns:
        Dict[str, MountDefinition]: A mapping of mount names to MountDefinition objects.
    """
    with open(mount_definitions_file, "r") as f:
        raw_mounts = yaml.safe_load(f)
    mount_definitions = {}
    for mount_name, mount_data in raw_mounts.items():
        mount_definitions[mount_name] = MountDefinition(**mount_data)
    return mount_definitions


class ServerConfig(BaseModel):
    """
    Configuration for the server.
    """

    server_config_file: str = Field(..., description="The path to the server configuration file.")
    course_config_dir: str = Field(..., description="The base dir where course configs are stored.")
    profile_dir: str = Field(..., description="The dir where profile configs are stored.")
    mount_definitions_file: str = Field(
        ..., description="The YAML file defining mount definitions."
    )
    roles: Roles = Field(..., description="The global role and permission config.")
    modification_times: Dict[str, float] = Field(
        default_factory=dict,
        description="The last modification times of the server configuration files.",
    )

    @classmethod
    def from_config_file(cls, config_file: str):
        root = os.path.abspath(os.path.dirname(config_file))
        server_config = cls(server_config_file=config_file, **load_yaml(config_file))
        server_config.course_config_dir = os.path.join(root, server_config.course_config_dir)
        if not os.path.exists(server_config.course_config_dir):
            os.makedirs(server_config.course_config_dir)

        server_config.profile_dir = os.path.join(root, server_config.profile_dir)
        if not os.path.exists(server_config.profile_dir):
            os.makedirs(server_config.profile_dir)
        server_config.mount_definitions_file = os.path.join(
            root, server_config.mount_definitions_file
        )
        if not os.path.exists(server_config.mount_definitions_file):
            raise FileNotFoundError(
                f"Mount definitions file '{server_config.mount_definitions_file}' does not exist."
            )
        server_config.modification_times = server_config._get_modification_times()
        return server_config

    def _get_modification_times(self) -> Dict[str, float]:
        """
        Get the last modification times of the server configuration files.

        Returns:
            Dict[str, float]: A mapping of configuration file paths to their last
                modification times.
        """
        mod_times = {
            "server_config_file": os.path.getmtime(self.mount_definitions_file),
        }
        for course_file in glob.glob(os.path.join(self.course_config_dir, "*.yaml")):
            mod_times[course_file] = os.path.getmtime(course_file)
        for profile_file in glob.glob(os.path.join(self.profile_dir, "*.yaml")):
            mod_times[profile_file] = os.path.getmtime(profile_file)
        return mod_times

    def config_changed_on_disk(self) -> bool:
        """
        Check if the server configuration files have changed on disk.

        Returns:
            bool: True if any configuration file has changed, False otherwise.
        """
        current_mod_times = self._get_modification_times()
        # Check if profiles or courses have been added/removed/modified
        if set(current_mod_times.keys()) != set(self.modification_times.keys()):
            return True
        for file_path, mod_time in current_mod_times.items():
            if self.modification_times[file_path] != mod_time:
                return True
        return False


class Server(BaseModel):
    """
    Represents the server configuration, including courses and profiles.
    """

    config: ServerConfig = Field(..., description="The server config")
    profiles: Dict[str, BaseProfile] = Field(..., description="The base profiles for the server.")
    courses: Dict[str, Course] = Field(..., description="The courses for the server.")
    mount_definitions: Dict[str, MountDefinition] = Field(
        default_factory=dict, description="The mount definitions available on the server."
    )

    @property
    def roles(self) -> Roles:
        return self.config.roles

    @classmethod
    def from_server_config(cls, server_config: ServerConfig, logger: Optional[Logger] = None):
        if logger is None:
            logger = getLogger(__name__)
        profiles = load_profiles(server_config.profile_dir, logger=logger)
        courses = {}
        for course_id, course_config in load_course_configs(
            server_config.course_config_dir, logger=logger
        ).items():
            courses[course_id] = Course.from_course_config(course_config, profiles)
        mount_definitions = load_mount_definitions(server_config.mount_definitions_file)
        return cls(
            config=server_config,
            profiles=profiles,
            courses=courses,
            mount_definitions=mount_definitions,
        )

    @classmethod
    def from_config_file(cls, config_file: str):
        server_config = ServerConfig.from_config_file(config_file)
        return cls.from_server_config(server_config)

    def config_changed_on_disk(self) -> bool:
        """
        Check if the server configuration has changed on disk.

        Returns:
            bool: True if the configuration has changed, False otherwise.
        """
        return self.config.config_changed_on_disk()
