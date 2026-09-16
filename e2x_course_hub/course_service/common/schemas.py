from pydantic import BaseModel

from ...schema.selection import ImageSelection
from ...schema.types import SpawnRole


class Environment(BaseModel):
    """Response body containing the environment configuration of a course or term."""

    image: ImageSelection
    resources: dict[SpawnRole, str] = {}
    profiles: dict[SpawnRole, str] = {}


class EnvironmentUpdate(BaseModel):
    """Request body for updating the environment configuration of a course or term."""

    image: ImageSelection | None = None
    resources: dict[SpawnRole, str] | None = None
    profiles: dict[SpawnRole, str] | None = None
