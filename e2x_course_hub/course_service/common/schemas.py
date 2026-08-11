from pydantic import BaseModel

from ...schema.infrastructure import ImageSelection, ResourceSelection


class Environment(BaseModel):
    """Response body containing the environment configuration of a course or term."""

    image: ImageSelection
    resources: ResourceSelection


class EnvironmentUpdate(BaseModel):
    """Request body for updating the environment configuration of a course or term."""

    image: ImageSelection | None = None
    resources: ResourceSelection | None = None
