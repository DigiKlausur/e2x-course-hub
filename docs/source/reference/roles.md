# Roles and permissions

Roles come from [`e2x-hub-rbac`](https://github.com/Digiklausur/e2x-hub-rbac). Each
role is held at one scope: for the whole LMS, for one course, or for one term
(semester in the UI). A role held for the LMS applies to every course and term, and
a role held for a course applies to all of its terms.

## Roles are JupyterHub groups

Holding a role means being a member of a JupyterHub group with a fixed name:

| Role               | Scope  | Group name                                         |
| ------------------ | ------ | -------------------------------------------------- |
| LMS admin          | LMS    | `lms.lms-admin`                                    |
| Course creator     | LMS    | `lms.course-creator`                               |
| Course owner       | Course | `lms.course.<course_id>.course-owner`              |
| Instructor         | Term   | `lms.course.<course_id>.term.<term_id>.instructor` |
| Teaching assistant | Term   | `lms.course.<course_id>.term.<term_id>.teaching-assistant` |
| Observer           | Term   | `lms.course.<course_id>.term.<term_id>.observer`   |
| Student            | Term   | `lms.course.<course_id>.term.<term_id>.student`    |

The course service creates these groups when the first member is added. With
`E2X_DELETE_EMPTY_GROUPS` it deletes a group again when its last member is removed.
Groups can also be managed outside the course service, for example with
`c.JupyterHub.load_groups`, which is how the first LMS admin is created (see
{doc}`../course_service/overview`).

## Default permissions

Every API checks its own permission table. The tables are defined in
`e2x_course_hub/api/*_permissions.py` and, for membership, in `e2x-hub-rbac`. The
`GET /v1/roles/{role}/actions` endpoint returns the same information per role.

### Courses and terms

| Role               | Permissions                                                                 |
| ------------------ | --------------------------------------------------------------------------- |
| LMS admin          | Everything                                                                  |
| Course creator     | Create courses, view courses                                                |
| Course owner       | Manage the course (metadata, environment, delete), create terms, manage its terms (environment, delete) |
| Instructor         | View the course and its metadata, manage the term (environment, delete)     |
| Teaching assistant | View the course, its metadata and the term                                  |
| Observer           | View the course, its metadata and the term                                  |
| Student            | None                                                                        |

### Membership

| Role               | Permissions                                                                 |
| ------------------ | --------------------------------------------------------------------------- |
| LMS admin          | Manage every role                                                           |
| Course creator     | None                                                                        |
| Course owner       | Manage course owners, instructors, teaching assistants, observers and students |
| Instructor         | View course owners; manage instructors, teaching assistants, observers and students |
| Teaching assistant | View course owners and all term members; add (but not remove) students      |
| Observer           | View course owners and all term members                                     |
| Student            | None                                                                        |

"Manage" means list, add and remove.

### Infrastructure catalog

| Role                                                 | Permissions                                   |
| ---------------------------------------------------- | --------------------------------------------- |
| LMS admin                                            | View and manage the image, resource and profile catalogs |
| Course creator, course owner, instructor, observer   | View the image, resource and profile catalogs |
| Teaching assistant                                   | View the image and resource catalogs          |
| Student                                              | None                                          |

The catalogs are provided by the infrastructure catalog provider and are read-only in
the course service. No endpoint uses the manage permissions yet.

### Starting environments

| Role               | Student environment | Grader environment | Read-only grader environment |
| ------------------ | :-----------------: | :----------------: | :--------------------------: |
| LMS admin          | ✓                   | ✓                  | ✓                            |
| Course creator     |                     |                    |                              |
| Course owner       | ✓                   | ✓                  |                              |
| Instructor         | ✓                   | ✓                  |                              |
| Teaching assistant | ✓                   | ✓                  |                              |
| Observer           | ✓                   |                    | ✓                            |
| Student            | ✓                   |                    |                              |

These permissions decide which spawn offerings a user gets per term (see
{doc}`../spawner/contract`). The read-only grader environment is the grader
environment with the course directory mounted read-only.
