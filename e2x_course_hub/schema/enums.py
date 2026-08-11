from enum import Enum


class SpawnRole(str, Enum):
    """The three roles that can spawn a server: student, grader, or observer."""

    STUDENT = "student"
    GRADER = "grader"
    OBSERVER = "observer"
