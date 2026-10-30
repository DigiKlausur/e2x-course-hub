from pydantic import BaseModel

from ...schema.catalog import UnavailableSelection
from ...schema.selection import PartialImageSelection
from ...schema.types import SpawnRole


class Environment(BaseModel):
    """Response body containing the environment configuration of a course or term.

    A course has no image tag; each new term gets the family's default tag.
    """

    image: PartialImageSelection
    resources: dict[SpawnRole, str] = {}
    profiles: dict[SpawnRole, str] = {}
    unavailable: list[UnavailableSelection] = []


class EnvironmentUpdate(BaseModel):
    """Request body for updating the environment configuration of a course or term.

    A course ignores the image tag; a term without one gets the family's default tag.
    """

    image: PartialImageSelection | None = None
    resources: dict[SpawnRole, str] | None = None
    profiles: dict[SpawnRole, str] | None = None
