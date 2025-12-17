import re
from typing import Dict, List

from pydantic import BaseModel, Field, model_validator


class User(BaseModel):
    """
    Represents a user in the system.
    """

    username: str
    admin: bool = Field(default=False)
    groups: List[str] = Field(default_factory=list)

    # Computed attribute
    course_roles: Dict[str, Dict[str, List[str]]] = Field(default_factory=dict)

    _group_pattern = re.compile(r"^(?P<course_id>[^.]+)\.(?P<term_id>[^.]+)\.(?P<role_id>[^.]+)$")

    @model_validator(mode="after")
    def compute_course_roles(self):
        """Compute course_roles once at model initialization."""
        roles: Dict[str, Dict[str, List[str]]] = {}
        for group in self.groups:
            match = self._group_pattern.match(group)
            if not match:
                continue  # ignore non-matching groups

            course_id = match.group("course_id")
            term_id = match.group("term_id")
            role_id = match.group("role_id")

            roles.setdefault(course_id, {}).setdefault(term_id, []).append(role_id)

        self.course_roles = roles
        return self

    def get_roles_in_course(self, course_id: str, term_id: str) -> List[str]:
        """
        Return roles for a given course and term.
        Returns an empty list if course or term is not found.
        """
        return self.course_roles.get(course_id, {}).get(term_id, [])
