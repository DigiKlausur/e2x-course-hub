"""What a user can do, structured by product area.

Filled from permissions by the builders in ``builders.py``; never used for
enforcement, which stays with the permission checks in the APIs.
"""

from pydantic import BaseModel


class MemberListActions(BaseModel):
    list: bool
    add: bool
    remove: bool


class CatalogActions(BaseModel):
    view: bool
    manage: bool


# ── LMS ──────────────────────────────────────────────────────────────
class LmsCoursesActions(BaseModel):
    create: bool


class LmsMembersActions(BaseModel):
    lmsAdmins: MemberListActions
    courseCreators: MemberListActions


class LmsCatalogsActions(BaseModel):
    images: CatalogActions
    resources: CatalogActions
    profiles: CatalogActions


class LmsActions(BaseModel):
    courses: LmsCoursesActions
    members: LmsMembersActions
    catalogs: LmsCatalogsActions


# ── Course ───────────────────────────────────────────────────────────
class CourseMetadataActions(BaseModel):
    view: bool
    edit: bool


class CourseEnvironmentActions(BaseModel):
    select: bool


class CourseTermsActions(BaseModel):
    add: bool


class CourseMembersActions(BaseModel):
    courseOwners: MemberListActions


class CourseActions(BaseModel):
    view: bool
    remove: bool
    metadata: CourseMetadataActions
    environment: CourseEnvironmentActions
    terms: CourseTermsActions
    members: CourseMembersActions


# ── Term ─────────────────────────────────────────────────────────────
class TermEnvironmentActions(BaseModel):
    select: bool


class TermSpawnActions(BaseModel):
    student: bool
    grader: bool
    readonlyGrader: bool


class TermMembersActions(BaseModel):
    instructors: MemberListActions
    teachingAssistants: MemberListActions
    students: MemberListActions
    observers: MemberListActions


class TermActions(BaseModel):
    view: bool
    remove: bool
    environment: TermEnvironmentActions
    spawn: TermSpawnActions
    members: TermMembersActions
