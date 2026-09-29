from enum import StrEnum
from typing import Protocol


class UserLike(Protocol):
    """A protocol representing a user-like object with a username and groups."""

    username: str
    groups: list[str]


class SpawnRole(StrEnum):
    """Enumeration of spawn roles for the e2x course hub.

    Read-only access to the grader environment is not a separate role; it's the
    GRADER role spawned with ``SpawnSelection.course_readonly`` set.
    """

    STUDENT = "student"
    GRADER = "grader"
