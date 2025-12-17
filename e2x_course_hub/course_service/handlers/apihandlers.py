import json

from tornado import web

from .base import BaseAPIHandler


class PermissionHandler(BaseAPIHandler):
    @web.authenticated
    async def get(self, course_id: str, term_id: str):
        user = await self.get_user()
        permissions = self.course_api.list_permissions(user, course_id, term_id)
        permissions_data = [permission.model_dump() for permission in permissions]
        self.write(json.dumps({"permissions": permissions_data}))


class CourseHandler(BaseAPIHandler):
    @web.authenticated
    async def get(self, course_id: str, term_id: str):
        user = await self.get_user()
        metadata = self.course_api.get_course_metadata(user, course_id, term_id)
        self.write(json.dumps(metadata))


class LeaveCourseHandler(BaseAPIHandler):
    @web.authenticated
    async def post(self, course_id: str, term_id: str):
        user = await self.get_user()
        await self.course_api.leave_course(user, course_id, term_id)
        self.set_status(204)


class ListCoursesUserCanSeeHandler(BaseAPIHandler):
    @web.authenticated
    async def get(self):
        user = await self.get_user()
        manageable_courses = self.course_api.list_courses_user_can_see(user)
        self.write(json.dumps({"courses": manageable_courses}))


class ListRolesUserCanAssignHandler(BaseAPIHandler):
    @web.authenticated
    async def get(self, course_id: str, term_id: str):
        user = await self.get_user()
        roles = self.course_api.list_roles_user_can_assign(user, course_id, term_id)
        self.write(json.dumps({"roles": roles}))


class CourseMemberHandler(BaseAPIHandler):
    @web.authenticated
    async def post(self, course_id: str, term_id: str):
        user = await self.get_user()
        data = json.loads(self.request.body)
        role_id = data.get("role")
        usernames = data.get("usernames", [])
        await self.course_api.add_course_members(user, course_id, term_id, role_id, usernames)
        self.set_status(204)

    @web.authenticated
    async def delete(self, course_id: str, term_id: str):
        user = await self.get_user()
        data = json.loads(self.request.body)
        self.log.warning(f"Removing course members: {data}")
        # role_id = data.get("role")
        usernames = data.get("usernames", [])
        await self.course_api.remove_course_members(user, course_id, term_id, usernames)
        self.set_status(204)

    @web.authenticated
    async def get(self, course_id: str, term_id: str):
        user = await self.get_user()
        metadata = await self.course_api.list_course_members(user, course_id, term_id)
        self.write(json.dumps(metadata))


class ProfileHandler(BaseAPIHandler):
    @web.authenticated
    async def get(self, course_id: str, term_id: str, profile_id: str):
        user = await self.get_user()
        profile = self.profile_api.get_profile(user, course_id, term_id, profile_id)
        self.write(json.dumps(profile.model_dump()))


default_handlers = [
    (r"/api/courses", ListCoursesUserCanSeeHandler),
    (r"/api/courses/(?P<course_id>[^/]+)/(?P<term_id>[^/]+)/leave", LeaveCourseHandler),
    (r"/api/courses/(?P<course_id>[^/]+)/(?P<term_id>[^/]+)", CourseHandler),
    (r"/api/course-members/(?P<course_id>[^/]+)/(?P<term_id>[^/]+)", CourseMemberHandler),
    (r"/api/permissions/(?P<course_id>[^/]+)/(?P<term_id>[^/]+)", PermissionHandler),
    (
        r"/api/roles/assignable/(?P<course_id>[^/]+)/(?P<term_id>[^/]+)",
        ListRolesUserCanAssignHandler,
    ),
    (
        r"/api/profiles/(?P<course_id>[^/]+)/(?P<term_id>[^/]+)/(?P<profile_id>[^/]+)",
        ProfileHandler,
    ),
]
