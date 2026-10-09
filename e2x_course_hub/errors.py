from typing import Optional

from e2x_hub_rbac.errors import APIError


class UnauthorizedError(APIError):
    """
    Error raised when a user is not authenticated.
    """

    status_code: int = 401
    type_uri: str = "urn:e2x-course-hub:unauthorized"
    title: str = "Unauthorized"

    def __init__(self, detail: Optional[str] = None):
        """
        :param detail: Human-readable explanation specific to this occurrence.
        """
        detail = detail or "Authentication is required to perform this action."
        super().__init__(detail=detail)


class CourseNotFoundError(APIError):
    """
    Error raised when a specified course is not found.
    """

    status_code: int = 404
    type_uri: str = "urn:e2x-course-hub:course-not-found"
    title: str = "Course Not Found"

    def __init__(self, course_id: str):
        """
        :param course_id: The ID of the course that was not found.
        """
        detail = f"Course with ID '{course_id}' was not found."
        super().__init__(detail=detail, course_id=course_id)


class CourseExistsError(APIError):
    """
    Error raised when a course with the same ID already exists.
    """

    status_code: int = 409
    type_uri: str = "urn:e2x-course-hub:course-exists"
    title: str = "Course Already Exists"

    def __init__(self, course_id: str):
        """
        :param course_id: The ID of the course that already exists.
        """
        detail = f"Course with ID '{course_id}' already exists."
        super().__init__(detail=detail, course_id=course_id)


class TermExistsError(APIError):
    """
    Error raised when a term with the same ID already exists within a course.
    """

    status_code: int = 409
    type_uri: str = "urn:e2x-course-hub:term-exists"
    title: str = "Term Already Exists"

    def __init__(self, course_id: str, term_id: str):
        """
        :param course_id: The ID of the course.
        :param term_id: The ID of the term that already exists.
        """
        detail = f"Term with ID '{term_id}' already exists in course '{course_id}'."
        super().__init__(detail=detail, course_id=course_id, term_id=term_id)


class TermNotFoundError(APIError):
    """
    Error raised when a specified term is not found within a course.
    """

    status_code: int = 404
    type_uri: str = "urn:e2x-course-hub:term-not-found"
    title: str = "Term Not Found"

    def __init__(self, course_id: str, term_id: str):
        """
        :param course_id: The ID of the course.
        :param term_id: The ID of the term that was not found.
        """
        detail = f"Term with ID '{term_id}' was not found in course '{course_id}'."
        super().__init__(detail=detail, course_id=course_id, term_id=term_id)


class RoleNotFoundError(APIError):
    """
    Error raised when a specified role is not found.
    """

    status_code: int = 404
    type_uri: str = "urn:e2x-course-hub:role-not-found"
    title: str = "Role Not Found"

    def __init__(self, role_id: str):
        """
        :param role_id: The ID of the role that was not found.
        """
        detail = f"Role with ID '{role_id}' was not found."
        super().__init__(detail=detail, role_id=role_id)


class ImageFamilyNotFoundError(APIError):
    """
    Error raised when a specified image family is not found in the infrastructure catalog.
    """

    status_code: int = 404
    type_uri: str = "urn:e2x-course-hub:image-family-not-found"
    title: str = "Image Family Not Found"

    def __init__(self, family_name: str):
        """
        :param family_name: The name of the image family that was not found.
        """
        detail = f"Image family '{family_name}' was not found in the infrastructure catalog."
        super().__init__(detail=detail, family_name=family_name)


class ImageTagNotFoundError(APIError):
    """
    Error raised when a specified image tag is not found in the infrastructure catalog.
    """

    status_code: int = 404
    type_uri: str = "urn:e2x-course-hub:image-tag-not-found"
    title: str = "Image Tag Not Found"

    def __init__(self, family_name: str, tag_name: str):
        """
        :param family_name: The name of the image family.
        :param tag_name: The name of the image tag that was not found.
        """
        detail = (
            f"Image tag '{tag_name}' in family '{family_name}' was not found "
            "in the infrastructure catalog."
        )
        super().__init__(detail=detail, family_name=family_name, tag_name=tag_name)


class ResourceTierNotFoundError(APIError):
    """
    Error raised when a specified resource tier is not found in the infrastructure catalog.
    """

    status_code: int = 404
    type_uri: str = "urn:e2x-course-hub:resource-tier-not-found"
    title: str = "Resource Tier Not Found"

    def __init__(self, tier_name: str, spawn_role: str):
        """
        :param tier_name: The name of the resource tier that was not found.
        :param spawn_role: The role for which the resource tier was not found.
        """
        detail = (
            f"Resource tier '{tier_name}' for role '{spawn_role}' was not found "
            "in the infrastructure catalog."
        )
        super().__init__(detail=detail, tier_name=tier_name, spawn_role=spawn_role)


class ProfileNotFoundError(APIError):
    """
    Error raised when a specified profile is not found in the profile catalog.
    """

    status_code: int = 404
    type_uri: str = "urn:e2x-course-hub:profile-not-found"
    title: str = "Profile Not Found"

    def __init__(self, profile_name: str, spawn_role: str):
        """
        :param profile_name: The name of the profile that was not found.
        :param spawn_role: The role for which the profile was not found.
        """
        detail = (
            f"Profile '{profile_name}' for role '{spawn_role}' was not found "
            "in the profile catalog."
        )
        super().__init__(detail=detail, profile_name=profile_name, spawn_role=spawn_role)
