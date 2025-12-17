from typing import Dict, Optional, Union

from pydantic import Field

from .base import Parameter, ResolveableModel


class Mount(ResolveableModel):
    """
    Represents a volume mount inside a container.
    """

    name: str = Field(..., description="Name of the volume")
    mountPath: str = Field(..., description="Path inside the container")
    subPath: str = Field(..., description="Sub-path within the volume")
    readOnly: bool = Field(
        default=True, description="Whether the mount is read-only. Default is True."
    )
    description: Optional[str] = Field(
        default=None, description="Human-readable description of the mount"
    )


class MountRequest(ResolveableModel):
    """
    Represents a request to mount a volume.
    """

    id: str = Field(..., description="Identifier of the requested mount.")
    args: Dict[str, str | int | bool | float] = Field(
        default_factory=dict, description="Arguments for the mount request."
    )


class MountDefinition(Mount):
    """
    Represents a definition for a volume mount.
    Extends Mount with input definitions for placeholder resolution.
    """

    inputs: Dict[str, Parameter] = Field(
        default_factory=dict, description="Input definitions for the profile."
    )
    readOnly: Union[bool, str] = Field(
        default="true", description="Whether the mount is read-only."
    )

    def get_mount_from_request(self, request: MountRequest) -> Mount:
        """
        Resolves the mount definition using the provided mount request.

        Args:
            request (MountRequest): The mount request with parameter values.

        Returns:
            Mount: The resolved mount.
        """
        return Mount(**self.resolve_placeholders(request.args).model_dump())
