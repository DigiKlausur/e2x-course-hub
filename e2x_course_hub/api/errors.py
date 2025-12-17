from typing import Any, Dict, Optional

# --- RFC 9457 HTTP Response Errors ---


class APIError(Exception):
    """
    Base class for all course service errors, RFC 9457-compliant.
    """

    status_code: int = 500
    type_uri: str = "about:blank"
    title: str = "Course Service Error"

    def __init__(self, detail: Optional[str] = None, **extra: Any):
        """
        :param detail: Human-readable explanation specific to this occurrence.
        :param extra: Optional extra fields to include in the problem details JSON.
        """
        self.detail: str = detail or self.title
        self.extra: Dict[str, Any] = extra
        super().__init__(self.detail)


class APIPermissionError(APIError):
    """
    Error raised when a user lacks the required permission for an action.
    """

    status_code: int = 403
    type_uri: str = "urn:e2x-course-hub:permission-denied"
    title: str = "Permission Denied"

    def __init__(
        self,
        user: str,
        action: str,
        resource: str,
        course_id: str,
        term_id: str,
        **constraints: Any,
    ):
        """
        :param user: Name of the acting user.
        :param action: The action that was attempted.
        :param resource: The resource the action was attempted on.
        :param course_id: Course identifier.
        :param term_id: Term identifier.
        :param constraints: Optional extra context.
        """
        constraint_msg = ", ".join(f"{k}={v}" for k, v in constraints.items())
        if constraint_msg:
            constraint_msg = f" with constraints ({constraint_msg})"

        detail = (
            f"User '{user}' does not have permission to {action} {resource} "
            f"in course '{course_id}', term '{term_id}'{constraint_msg}."
        )

        super().__init__(
            detail=detail,
            user=user,
            action=action,
            resource=resource,
            course_id=course_id,
            term_id=term_id,
            **constraints,
        )


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


# --- Hub API Communication Errors ---


class HubAPIError(Exception):
    """Base exception for all Hub API errors."""

    pass


class GroupNotFoundError(HubAPIError):
    """Raised when a requested group is not found in the Hub API."""

    def __init__(self, groupname: str):
        self.groupname = groupname
        super().__init__(f"Group '{groupname}' not found")


class UserNotFoundError(HubAPIError):
    """Raised when a requested user is not found in the Hub API."""

    def __init__(self, username: str):
        self.username = username
        super().__init__(f"User '{username}' not found")


class InvalidInputError(HubAPIError):
    """Raised when input validation fails."""

    pass
