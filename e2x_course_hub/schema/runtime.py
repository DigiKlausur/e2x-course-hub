from typing import Any, Dict, Optional, Union

from pydantic import Field

from .base import MergeableModel


class ImagePartial(MergeableModel["ImagePartial"]):
    """
    Partial definition of a container image.
    """

    name: Optional[str] = Field(
        default=None,
        description="Name of the image",
    )
    tag: Optional[str] = Field(
        default=None,
        description="Tag of the image",
    )
    pullPolicy: Optional[str] = Field(
        default=None,
        description="Pull policy for the image.",
        pattern="^(Always|IfNotPresent|Never)$",
    )


class Image(MergeableModel[ImagePartial]):
    """
    Definition of a container image.
    """

    name: str = Field(
        ...,
        description="Name of the image",
    )
    tag: str = Field(
        ...,
        description="Tag of the image",
    )
    pullPolicy: str = Field(
        "IfNotPresent",
        description="Pull policy for the image. Default is 'IfNotPresent'",
        pattern="^(Always|IfNotPresent|Never)$",
    )

    @property
    def full_image_name(self):
        return f"{self.name}:{self.tag}"


class ResourcesPartial(MergeableModel["ResourcesPartial"]):
    """
    Partial definition of resource requirements.
    """

    cpu_guarantee: Optional[float] = Field(default=None, description="Guaranteed CPU resources")
    cpu_limit: Optional[float] = Field(default=None, description="CPU resource limit")
    mem_guarantee: Optional[str] = Field(default=None, description="Guaranteed memory resources")
    mem_limit: Optional[str] = Field(default=None, description="Memory resource limit")


class Resources(MergeableModel[ResourcesPartial]):
    """
    Definition of resource requirements.
    """

    cpu_guarantee: float = Field(default=0.001, description="Guaranteed CPU resources")
    cpu_limit: float = Field(default=2.0, description="CPU resource limit")
    mem_guarantee: str = Field(default="1.0G", description="Guaranteed memory resources")
    mem_limit: str = Field(default="2.0G", description="Memory resource limit")


class RuntimePartial(MergeableModel["RuntimePartial"]):
    """
    Partial definition of a runtime environment.
    """

    image: ImagePartial = Field(
        default_factory=ImagePartial, description="The default image to use."
    )
    resources: ResourcesPartial = Field(
        default_factory=ResourcesPartial, description="The default resources to use."
    )
    environment: Dict[str, Union[str, float, int, bool]] = Field(
        default_factory=dict, description="Environment variables for the runtime."
    )

    def merge(self, partial: Union["RuntimePartial", None]) -> "RuntimePartial":
        copy = RuntimePartial(**self.model_dump())
        if not partial:
            return copy
        copy.image = copy.image.merge(partial.image)
        copy.resources = copy.resources.merge(partial.resources)
        copy.environment.update(partial.environment)
        return copy


class Runtime(MergeableModel[RuntimePartial]):
    """
    Definition of a runtime environment.
    """

    image: Image = Field(..., description="The image to use.")
    resources: Resources = Field(..., description="The resources to use.")
    environment: Dict[str, str | float | int | bool] = Field(
        default_factory=dict, description="Environment variables for the runtime."
    )

    def merge(self, partial: RuntimePartial | None) -> "Runtime":
        copy = Runtime(**self.model_dump())
        if not partial:
            return copy
        copy.image = copy.image.merge(partial.image)
        copy.resources = copy.resources.merge(partial.resources)
        copy.environment.update(partial.environment)
        return copy

    def to_kubespawner_override(self) -> Dict[str, Any]:
        """
        Convert the runtime definition to a dictionary of overrides suitable for Kubespawner.

        Returns:
            Dict[str, Any]: The Kubespawner override dictionary.
        """
        overrides = {}
        overrides["image"] = self.image.full_image_name
        overrides["image_pull_policy"] = self.image.pullPolicy
        resources = self.resources.model_dump()
        overrides.update(resources)
        overrides["environment"] = {}
        for key, value in self.environment.items():
            overrides["environment"][key] = str(value)
        return overrides
