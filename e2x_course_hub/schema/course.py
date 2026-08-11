from typing import Dict, Optional

from pydantic import BaseModel, Field

from .infrastructure import ImageSelection, ResourceSelection
from .profile import ProfileSelection


class TermConfig(BaseModel):
    image: ImageSelection = Field(
        ...,
        description="Image configuration for this term.",
    )
    resources: ResourceSelection = Field(
        ...,
        description="Resource tier configuration for this term.",
    )
    profiles: ProfileSelection = Field(
        ...,
        description="Profile configuration for this term.",
    )


class CourseMetadata(BaseModel):
    """
    Metadata information about a course.
    """

    course_id: str = Field(..., description="The id of the course.")
    course_name: str = Field(..., description="The full name of the course")
    description: Optional[str] = Field(
        default=None, description="An optional text describing the course."
    )


class CourseConfig(BaseModel):
    metadata: CourseMetadata = Field(..., description="Metadata information about the course.")
    image: ImageSelection = Field(..., description="Default image configuration for the course.")
    resources: ResourceSelection = Field(
        default_factory=ResourceSelection,
        description="Default resource tier configuration for the course.",
    )
    profiles: ProfileSelection = Field(
        default_factory=ProfileSelection,
        description="Default profile configuration for the course.",
    )
    terms: Dict[str, TermConfig] = Field(
        default_factory=dict,
        description="Per-term configuration overrides.",
    )

    def get_term_image_selection(self, term_id: str) -> ImageSelection:
        """
        Get the image configuration for a specific term, applying any overrides.
        Args:
            term_id (str): The id of the term to get the image configuration for.
        Returns:
            ImageSelection: The image configuration for the term.
        """
        assert term_id in self.terms, f"Term '{term_id}' not found in course configuration."
        term_config = self.terms[term_id]
        return term_config.image

    def get_term_resource_selection(self, term_id: str) -> ResourceSelection:
        """
        Get the resource tier configuration for a specific term, applying any overrides.
        Args:
            term_id (str): The id of the term to get the resource tier configuration for.
        Returns:
            ResourceSelection: The resource tier configuration for the term.
        """
        assert term_id in self.terms, f"Term '{term_id}' not found in course configuration."
        term_config = self.terms[term_id]
        return term_config.resources

    def get_term_profile_selection(self, term_id: str) -> ProfileSelection:
        """
        Get the profile configuration for a specific term, applying any overrides.
        Args:
            term_id (str): The id of the term to get the profile configuration for.
        Returns:
            ProfileSelection: The profile configuration for the term.
        """
        assert term_id in self.terms, f"Term '{term_id}' not found in course configuration."
        term_config = self.terms[term_id]
        return term_config.profiles
