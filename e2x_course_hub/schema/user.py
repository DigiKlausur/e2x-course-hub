from pydantic import BaseModel


class UserCourseContext(BaseModel):
    """
    Represents the context of a user within a specific course and term.
    """

    username: str
    course_id: str
    term_id: str
