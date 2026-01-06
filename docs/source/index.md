# e2x-course-hub documentation

The E2x Course Hub provides software to configure a JupyterHub in a course setup.

- Course membership is defined via JupyterHub Groups.
- Reusable Profiles are used within a course to define the complete user environment (resources, mounts, environment variables)
- Roles are used to to give a JupyterHub user permissions within a specific course and term.
- A custom spawn template lets users spawn profiles of courses they are a member of.
- A course service is used to manage course membership

## Custom Spawner

Below you see a the spawn interface of a JupyterHub using the E2x Course Hub.

```{image} ./images/spawn.png
:align: center
:alt: true
:class: screenshot shadow
```

## Course Management Service

In the course management service a user can see all courses they can view.

```{image} ./images/course_service_courses.png
:align: center
:alt: true
:class: screenshot shadow
```

Depending on the role within a course the user can add members to a course and remove them:

```{image} ./images/course_service_members.png
:align: center
:alt: true
:class: screenshot shadow
```

```{toctree}
:maxdepth: 2

getting_started/installation
course_service/overview
configuration/overview
```