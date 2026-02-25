import re
from typing import Callable, Dict, List, Optional

from traitlets.config import Config

from .api.profile_api import ProfileAPI
from .schema.profile import ResolvedProfile
from .schema.server import Server
from .schema.user import User


def parse_term_for_sorting(term):
    """
    Parse term string into sortable format.

    Examples:
        SS25 -> 25-SS
        WS25 -> 25-WS
        Invalid -> Other

    Returns terms in format that sorts: WS25, SS25, WS24, SS24, ..., Other
    """
    if not term:
        return "Other"

    match = re.match(r"^(WS|SS)(\d+)$", term.strip())
    if not match:
        return "Other"

    semester, year = match.groups()
    # Return format: year-semester (e.g., "25-WS", "25-SS")
    # WS comes before SS alphabetically, so this naturally orders correctly
    return f"{year}-{semester}"


class KubespawnerProfileAPI(ProfileAPI):
    def __init__(self, server: Server, sorter: Optional[Callable[[str], str]] = None):
        super().__init__(server)
        self.sorter = sorter or parse_term_for_sorting

    def _build_kubespawner_profile_choices(
        self, course_id: str, term_id: str, profiles: List[ResolvedProfile]
    ) -> Dict[str, Dict]:
        """
        Converts a list of resolved BaseProfile objects into the 'choices' dictionary
        used in Kubespawner profile options.

        Args:
            course_id (str): The course ID.
            term_id (str): The term ID.
            profiles (List[BaseProfile]): The list of resolved profiles.
        Returns:
            Dict[str, Dict]: The choices dictionary for Kubespawner.
        """
        choices = {}
        for profile in profiles:
            choice_name = f"{course_id}.{term_id}.{profile.name}"
            choices[choice_name] = {
                "display_name": profile.display_name,
                "kubespawner_override": profile.runtime.to_kubespawner_override(),
            }
        return choices

    def _build_kubespawner_profile_entry(
        self, course_id: str, term_id: str, profiles: List[ResolvedProfile]
    ) -> Dict:
        """
        Build a single entry for the Kubespawner profile list. This includes metadata
        about the course and term, as well as the profile options.

        Args:
            course_id (str): The course ID.
            term_id (str): The term ID.
            profiles (List[BaseProfile]): The list of resolved profiles.
        Returns:
            Dict: The Kubespawner profile entry.
        """
        course_metadata = self.server.courses[course_id].metadata.model_dump(
            exclude_unset=True, exclude_none=True
        )
        choices = self._build_kubespawner_profile_choices(course_id, term_id, profiles)
        return {
            "display_name": f"{course_id} - {term_id}",
            "term": term_id,
            "sort_key": self.sorter(term_id),
            "metadata": course_metadata,
            "profile_options": {"profile-slug": {"display_name": "Profile", "choices": choices}},
        }

    def get_kubespawner_profile_list(self, user) -> List[Dict]:
        """
        Retrieves the list of Kubespawner profile entries the user can spawn.

        Args:
            user (User): The user requesting the profile list.
        Returns:
            List[Dict]: The list of Kubespawner profile entries.
        """
        profiles = self.list_profiles(user)
        profile_list = []
        for course_id, course_data in profiles.items():
            for term_id, term_profiles in course_data.items():
                kubespawner_profile = self._build_kubespawner_profile_entry(
                    course_id, term_id, term_profiles
                )
                profile_list.append(kubespawner_profile)
        return profile_list

    def get_profile_from_choice(self, user: User, choice_slug: str) -> ResolvedProfile:
        """
        Given a choice slug from Kubespawner profile options, return the resolved profile.
        The choice slug is expected to be in the format: course_id.term_id.profile_id

        Args:
            user (User): The user requesting the profile.
            choice_slug (str): The choice slug from Kubespawner.
        Returns:
            ResolvedProfile: The resolved profile.
        """
        try:
            course_id, term_id, profile_id = choice_slug.split(".")
        except ValueError:
            raise ValueError(f"Invalid choice slug format: {choice_slug}")

        return self.get_profile(user, course_id, term_id, profile_id)

    def get_profile_mounts_from_choice(self, user: User, choice_slug: str) -> List[Dict]:
        """
        Given a choice slug from Kubespawner profile options, return the list of volume mounts
        for that profile, including admin mounts if the user is an admin.

        Args:
            user (User): The user requesting the profile.
            choice_slug (str): The choice slug from Kubespawner.
        Returns:
            List[Dict]: The list of volume mounts for the profile.
        """
        profile = self.get_profile_from_choice(user, choice_slug)

        resolved_mounts = profile.resolve_mount_requests(self.server.mount_definitions)
        return [
            mount.model_dump(exclude_unset=True, exclude_none=True, exclude=set(["description"]))
            for mount in resolved_mounts
        ]


def get_profile_list_hook(
    server_config_file: str, sorter: Optional[Callable[[str], str]] = None
) -> Callable:
    """
    Returns a hook function to retrieve the Kubespawner profile list for a user.

    Args:
        server_config_file (str): Path to the server configuration file.
        sorter (Callable[[str], str], optional): A function that takes a term_id string
            and returns a sortable string. Defaults to parse_term_for_sorting.
            Example: lambda term: term  # Simple alphabetical sorting
    Returns:
        Callable: The hook function.
    """

    def hook(spawner):
        user = User(
            username=spawner.user.name,
            admin=getattr(spawner.user, "admin", False),
            groups=[g.name for g in spawner.user.groups],
        )
        server = Server.from_config_file(server_config_file)
        api = KubespawnerProfileAPI(server, sorter=sorter)
        return api.get_kubespawner_profile_list(user)

    return hook


def get_pre_spawn_hook(server_config_file: str) -> Callable:
    """
    Returns a pre-spawn hook function to set volume mounts based on the selected profile.

    Args:
        server_config_file (str): Path to the server configuration file.
    Returns:
        Callable: The pre-spawn hook function.
    """

    async def hook(spawner):
        await spawner.load_user_options()
        user = User(
            username=spawner.user.name,
            admin=getattr(spawner.user, "admin", False),
            groups=[g.name for g in spawner.user.groups],
        )
        # Sorter not needed for pre_spawn_hook since we're only looking up a specific profile
        server = Server.from_config_file(server_config_file)
        api = KubespawnerProfileAPI(server)
        spawner.log.debug(f"User options are: {spawner.user_options}")
        choice_slug = spawner.user_options.get("profile-slug")
        mounts = api.get_profile_mounts_from_choice(user, choice_slug)
        spawner.volume_mounts = []
        spawner.log.debug("Spawner mounts are:")
        for mount in mounts:
            spawner.log.debug(f"{mount}")
        spawner.volume_mounts = mounts
        # spawner.volume_mounts = []

    return hook


def configure_autospawn(
    config: Config, auto_spawn_single_course: bool = True, auto_spawn_countdown: int = 5
):
    """
    Configures the autospawn hooks in the given JupyterHub config.

    Args:
        config (Config): The JupyterHub configuration object to modify.
        auto_spawn_single_course (bool): Whether to auto-spawn a single course if only
            one profile is available.
        auto_spawn_countdown (int): The countdown time in seconds before auto-spawning.
    """
    if config.JupyterHub.template_vars is None:
        config.JupyterHub.template_vars = {}

    config.JupyterHub.template_vars.update(
        {
            "auto_spawn_single_course": auto_spawn_single_course,
            "auto_spawn_countdown": auto_spawn_countdown,
        }
    )
