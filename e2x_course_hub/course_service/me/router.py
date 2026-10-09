from fastapi import APIRouter

from ..common.dependency_types import CurrentUser
from .schemas import UserResponse

router = APIRouter(
    prefix="/v1/me",
    tags=["Me"],
)

hub_prefix = "/hub"
course_prefix = "/courses/{course_id}"
term_prefix = course_prefix + "/terms/{term_id}"


@router.get("")
async def get_current_user(
    user: CurrentUser,
) -> UserResponse:
    return UserResponse(
        username=user.username,
    )
