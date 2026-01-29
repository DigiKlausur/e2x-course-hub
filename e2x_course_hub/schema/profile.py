from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, model_validator

from .base import MergeableModel, Parameter, ResolveableModel
from .mount import Mount, MountDefinition, MountRequest
from .runtime import Runtime, RuntimePartial
from .user import User


class InheritedProfile(MergeableModel["InheritedProfile"]):
    """
    Partial profile model for merging into a full Profile.
    """

    name: str = Field(..., description="Human-readable name for the profile.")
    display_name: str = Field(..., description="Optional display name for the profile.")
    inherits: str = Field(..., description="The profile this one inherits from.")
    description: Optional[str] = Field(
        default=None, description="Detailed description of the profile."
    )
    inputs: Dict[str, Parameter] = Field(
        default_factory=dict, description="Input parameter definitions for the profile."
    )
    runtime: Optional[RuntimePartial] = Field(
        default=None, description="Runtime configuration for the profile."
    )
    mount_requests: Dict[str, MountRequest] = Field(
        default_factory=dict, description="Mount configurations for the profile."
    )
    admin_mount_requests: Dict[str, MountRequest] = Field(
        default_factory=dict, description="Admin-only mount configurations for the profile."
    )


class BaseProfile(MergeableModel[InheritedProfile], ResolveableModel):
    """
    Full profile model.
    """

    name: str = Field(..., description="Human-readable name for the profile.")
    display_name: str = Field(..., description="Optional display name for the profile.")
    inherits: None = Field(default=None, description="Base profile, cannot inherit further.")
    description: Optional[str] = Field(
        default=None, description="Detailed description of the profile."
    )
    inputs: Dict[str, Parameter] = Field(
        default_factory=dict, description="Input parameter definitions for the profile."
    )
    runtime: Runtime = Field(..., description="Runtime configuration for the profile.")
    mount_requests: Dict[str, MountRequest] = Field(
        default_factory=dict, description="Mount requests for the profile."
    )
    admin_mount_requests: Dict[str, MountRequest] = Field(
        default_factory=dict, description="Admin-only mount requests for the profile."
    )

    def merge(self, partial: InheritedProfile | None) -> "BaseProfile":
        profile = BaseProfile(**self.model_dump())
        if partial is None:
            return profile
        profile.name = partial.name
        profile.display_name = partial.display_name
        profile.description = partial.description
        profile.inputs.update(partial.inputs)
        profile.runtime = profile.runtime.merge(partial.runtime)
        profile.mount_requests.update(partial.mount_requests)
        profile.admin_mount_requests.update(partial.admin_mount_requests)
        return profile


class ResolvedProfile(BaseModel):
    """
    A profile with all placeholders and mount requests resolved.
    """

    name: str = Field(..., description="Human-readable name for the profile.")
    display_name: str = Field(..., description="Optional display name for the profile.")
    description: Optional[str] = Field(
        default=None, description="Detailed description of the profile."
    )
    runtime: Runtime = Field(..., description="Runtime configuration for the profile.")
    mount_requests: List[MountRequest] = Field(
        default_factory=list, description="The mount requests for the profile."
    )

    @classmethod
    def from_profile(
        cls,
        profile: BaseProfile,
        user: User,
        context: Dict[str, Any],
    ) -> "ResolvedProfile":
        context["username"] = user.username
        # Remove everything from the context that is not a parameter
        context = {k: v for k, v in context.items() if k in profile.inputs}
        resolved_profile = profile.resolve_placeholders(context)
        mount_requests = resolved_profile.mount_requests.copy()
        if user.admin:
            mount_requests.update(resolved_profile.admin_mount_requests)

        return ResolvedProfile(
            name=resolved_profile.name,
            display_name=resolved_profile.display_name,
            description=resolved_profile.description,
            runtime=resolved_profile.runtime,
            mount_requests=list(mount_requests.values()),
        )

    def resolve_mount_requests(self, mount_definitions: Dict[str, MountDefinition]) -> List[Mount]:
        """
        Resolve the mount requests of this profile using the provided mount definitions.

        Args:
            mount_definitions (Dict[str, MountDefinition]): The mount definitions to use
                for resolution.

        Returns:
            List[Mount]: The resolved mounts.
        """
        return [
            mount_definitions[request.id].get_mount_from_request(request)
            for request in self.mount_requests
        ]


Profile = Union[BaseProfile, InheritedProfile]


class ProfileLoader(BaseModel):
    """
    A dispatcher that loads either BaseProfile or InheritedProfile depending
    on whether the `inherits` key is present and non-null.

    Profile.model will always contain the concrete profile instance.
    """

    model: Profile

    @model_validator(mode="before")
    @classmethod
    def dispatch(cls, data: Any):
        """
        Decide which profile class to use based solely on the presence and
        value of the `inherits` field.
        """
        if not isinstance(data, dict):
            raise TypeError("Profile must be built from a mapping/dict")

        inherits_value = data.get("inherits", None)

        # Case A: inherited profile
        if isinstance(inherits_value, str) and inherits_value.strip() != "":
            return {"model": InheritedProfile(**data)}

        # Case B: base profile
        return {"model": BaseProfile(**data)}

    @classmethod
    def parse_profile(cls, data: Any) -> Union[BaseProfile, InheritedProfile]:
        loader = cls.model_validate(data)
        return loader.model


def get_merged_profile(profile_name: str, profiles: Dict[str, Profile]) -> BaseProfile:
    """
    Recursively resolve and merge profiles to produce a BaseProfile.

    Args:
        profile_name (str): The name of the profile to resolve.
        profiles (Dict[str, Profile]): A mapping of profile names to Profile objects.

    Returns:
        BaseProfile: The fully resolved and merged BaseProfile.
    """
    if profile_name not in profiles:
        raise ValueError(f"Profile '{profile_name}' not found.")
    base_profile = profiles[profile_name]
    if isinstance(base_profile, BaseProfile):
        return base_profile
    parent_profile = get_merged_profile(base_profile.inherits, profiles)
    merged_profile = parent_profile.merge(base_profile)
    return merged_profile
