# e2x-course-hub documentation

The E2x Course Hub is a JupyterHub service for running multi-course, multi-term
teaching deployments.

- Courses, terms, and their environment configuration (image, resource tier, profile
  per role) are stored in a database and managed through a REST API.
- Course membership is backed by JupyterHub Groups and controlled through role-based
  access control (LMS admin, course creator, course owner, instructor, teaching
  assistant, student, observer), provided by
  [`e2x-hub-rbac`](https://github.com/Digiklausur/e2x-hub-rbac).
- A typed contract (`e2x_course_hub.contract`) decouples this service from a separate
  infrastructure spawner: the course hub decides who may launch what, the spawner
  decides how that translates to a running container.
- A course service (FastAPI backend + React SPA) is used to manage courses and course
  membership.

In the user interface, terms are called **semesters**. The user guide uses the UI's
names; the reference pages use the names from the API.

```{image} ./images/course_service_courses.png
:align: center
:alt: The course list in the course service
:class: screenshot shadow
```

## Custom Spawner

The course hub itself has no spawn page — it only reports, per user, which
course/terms they may launch and with which configured environment. Presenting that
as a spawn page is the job of a separate infrastructure spawner that implements the
other half of the contract. See
[`e2x-course-hub-kubespawner`](https://github.com/DigiKlausur/e2x-course-hub-kubespawner)
for an example built on KubeSpawner, and {doc}`spawner/contract` for the contract
itself.

```{toctree}
:maxdepth: 2
:caption: Getting started

getting_started/installation
course_service/overview
```

```{toctree}
:maxdepth: 2
:caption: User guide

user_guide/courses
user_guide/semesters
user_guide/members
```

```{toctree}
:maxdepth: 2
:caption: Reference

reference/roles
reference/configuration
reference/rest_api
spawner/contract
```
