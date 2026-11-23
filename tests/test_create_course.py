from conftest import StubCatalogProvider, make_course
from fastapi import FastAPI
from fastapi.testclient import TestClient
from jupyterhub_fastapi_adapter.dependencies import User, require_authenticated_user

from e2x_course_hub.api.api import API
from e2x_course_hub.course_service.courses.router import router
from e2x_course_hub.course_service.exception_handlers import api_error_handler
from e2x_course_hub.errors import APIError


class FakeHub:
    """Keeps the groups in memory in place of JupyterHub."""

    def __init__(self):
        self.groups: dict[str, list[str]] = {}

    async def ensure_group_exists(self, group_name: str, create_if_missing: bool) -> None:
        self.groups.setdefault(group_name, [])

    async def ensure_users_exist(self, usernames: list[str], create_if_missing: bool) -> None:
        pass

    async def add_users_to_group(self, group_name: str, usernames: list[str]) -> None:
        self.groups[group_name].extend(usernames)


def test_course_creator_gets_the_metadata_of_the_created_course(repository):
    hub = FakeHub()
    app = FastAPI()
    app.state.api = API(hub, repository, StubCatalogProvider())
    app.add_exception_handler(APIError, api_error_handler)
    app.include_router(router)
    # As authenticated at the start of the request: not yet an owner of the new course.
    app.dependency_overrides[require_authenticated_user] = lambda: User(
        username="creator", groups=["lms.course-creator"]
    )

    response = TestClient(app).post("/v1/courses", json=make_course().model_dump(mode="json"))

    assert response.status_code == 201, response.text
    metadata = response.json()
    assert metadata["course_id"] == "c1"
    assert metadata["course_name"] == "Course"
    assert metadata["created_at"] is not None
    assert hub.groups == {"lms.course.c1.course-owner": ["creator"]}
