# Course Service

The course service is the FastAPI application this package ships: a REST API under
`{service_prefix}/v1/...` for managing courses, terms, and course membership, plus the
bundled `course-service-ui` React app, served from the same process under
`{service_prefix}/app/`.

## JupyterHub Configuration

To run the service add the following to your `jupyterhub_config.py`:

```python
# jupyterhub_config.py
c.JupyterHub.services = [
    {
        "name": "course-service",
        "url": "http://127.0.0.1:10105",
        "command": ["uvicorn", "e2x_course_hub.course_service.fastapi_app:app"],
        "environment": {
            "UVICORN_HOST": "0.0.0.0",
            "UVICORN_PORT": "10105",
            "E2X_INFRASTRUCTURE_PROVIDER": "k8s_catalog",
            "E2X_ADD_USERS_TO_HUB": "true",
            "E2X_DELETE_EMPTY_GROUPS": "true",
            "E2X_COURSE_DB_URL": "sqlite:////srv/jupyterhub/courses.db",
        },
    }
]

c.JupyterHub.load_roles = [
    {
        "name": "course-service",
        "services": ["course-service"],
        "scopes": [
            "access:services!service=course-service",
            "admin:users",
            "list:users",
            "delete:users",
            "admin:groups",
        ],
    }
]
```

`JUPYTERHUB_API_URL`, `JUPYTERHUB_API_TOKEN`, and `JUPYTERHUB_SERVICE_PREFIX` are
injected automatically by JupyterHub for a managed service and don't need to be set
explicitly. All other settings are listed in {doc}`../reference/configuration`.

`E2X_INFRASTRUCTURE_PROVIDER` must name an installed infrastructure catalog provider,
such as the `k8s_catalog` provider from
[`e2x-course-hub-kubespawner`](https://github.com/DigiKlausur/e2x-course-hub-kubespawner).
The service fails to start if no provider with that name is installed.

Once JupyterHub is running, the UI is available at `/services/course-service/app/`.

## The first LMS admin

Roles are JupyterHub groups (see {doc}`../reference/roles`). A fresh deployment has no
LMS admin, so nobody can add one through the UI. Create the first one by putting a
user into the `lms.lms-admin` group from the JupyterHub configuration:

```python
c.JupyterHub.load_groups = {
    "lms.lms-admin": {"users": ["alice"]},
}
```

From then on, `alice` can add further LMS admins and course creators in the UI.

## Optional: `whoami` service

`e2x_course_hub.course_service.whoami:app` is a minimal standalone FastAPI service
that returns the authenticated caller's identity. It's handy for verifying JupyterHub
OAuth is wired up correctly before debugging the full course service:

```python
c.JupyterHub.services.append(
    {
        "name": "whoami",
        "url": "http://127.0.0.1:10101",
        "command": ["uvicorn", "e2x_course_hub.course_service.whoami:app"],
        "environment": {"UVICORN_HOST": "0.0.0.0", "UVICORN_PORT": "10101"},
    }
)
```
