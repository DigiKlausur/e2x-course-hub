# e2x Course Hub

A JupyterHub service for running multi-course, multi-term teaching deployments on
Kubernetes. It manages courses, terms, and course membership; enforces who may do what
via role-based access control; and tells a separate infrastructure spawner which
courses/terms a user may launch and with which environment — without ever deciding
hardware itself.

It ships as a FastAPI backend (REST API under `/v1/...`) plus a React single-page app
(`course-service-ui`) for course and membership management, both served from the same
process.

## What it does

- **Course & term management** — courses and their terms are stored in a database
  (SQLAlchemy) and managed through a REST API: create/remove courses and terms, edit
  metadata, and configure the environment (image, resource tier, profile) per course,
  overridable per term.
- **Role-based access control** — powered by [`e2x-hub-rbac`](https://github.com/Digiklausur/e2x-hub-rbac).
  Roles (LMS admin, course creator, course owner, instructor, teaching assistant,
  student, observer) are scoped to the LMS, a course, or a term, and membership is
  backed by JupyterHub groups.
- **A typed contract with the spawner** — `e2x_course_hub.contract` defines the
  boundary between this package and the JupyterHub Spawner that actually launches
  containers. The course hub owns authorization and course configuration; the spawner
  owns the runtime. They meet only through two `Protocol`s:
  - `SpawnOfferingProvider` (implemented here): tells the spawner, for a given user,
    which course/terms they may launch, in which role, with which selection.
  - `InfrastructureCatalogProvider` (implemented by the spawner): tells the course hub
    what images, resource tiers, and profiles actually exist, so course configuration
    can only ever offer valid choices.
- **A management UI** — `course-service-ui`, a React SPA served by the same FastAPI app,
  for browsing courses and managing membership in the browser.

See [`e2x_course_hub/contract/README.md`](e2x_course_hub/contract/README.md) for the
full contract reference, including the catalog/selection data model and how a spawn
plays out end to end.

## Architecture

```
e2x_course_hub/
├── contract/           # Protocol boundary shared with the infrastructure spawner
│   └── providers.py       # InfrastructureCatalogProvider, SpawnOfferingProvider
│       # (re-exports the catalog/selection models from schema/ below)
├── schema/              # Pydantic models backing the contract and the API
│   ├── catalog.py         # InfrastructureCatalogOptions and friends
│   ├── selection.py        # SpawnSelection, SpawnOffering, CourseReference
│   ├── course.py           # CourseConfig / TermConfig
│   └── types.py            # SpawnRole, UserLike
├── db/                  # SQLAlchemy models + CourseRepository
├── api/                 # Business logic, framework-agnostic
│   ├── api.py              # API — aggregates the sub-APIs below
│   ├── course_api.py        # Course/term CRUD and environment configuration
│   ├── membership_api.py    # Course membership (extends e2x-hub-rbac's MembershipAPI)
│   ├── infrastructure_api.py # Read-only access to the infrastructure catalog
│   ├── spawn_offering_api.py # Implements SpawnOfferingProvider for the spawner
│   └── *_permissions.py      # Role → permission mappings per sub-API
├── course_service/      # The FastAPI service
│   ├── fastapi_app.py       # App wiring: routers, auth, static files, SPA route
│   ├── settings.py          # ServiceSettings (extends settings.CoreSettings)
│   ├── whoami.py            # Minimal standalone service: returns the caller's identity
│   └── {courses,terms,infrastructure,membership,me}/  # One router + schemas per resource
├── loader.py            # Composition root: settings → concrete API objects
└── settings.py          # CoreSettings: hub API, DB, membership, infrastructure provider

course-service-ui/       # React 19 + TypeScript SPA, built with Vite
```

### The two sides

|            | Course hub (this repo)                                              | Infrastructure spawner                            |
|------------|-----------------------------------------------------------------------|----------------------------------------------------|
| Knows      | courses, terms, users, roles (via `e2x-hub-rbac`), permissions        | what can actually be run: image families/tags, resource tiers, profiles |
| Implements | `SpawnOfferingProvider`                                                | `InfrastructureCatalogProvider`                     |
| Consumes   | `InfrastructureCatalogProvider`                                        | `SpawnOfferingProvider`                             |
| Never does | translates a selection to hardware                                    | decides who is allowed to do what                   |

The spawner is a separate, pluggable package (a Kubernetes/KubeSpawner-based
implementation is used in production). The course hub discovers it at startup through
the `e2x_course_hub.infrastructure_catalog_providers` entry-point group, selected by
name via the `E2X_INFRASTRUCTURE_PROVIDER` setting — the hub never imports it directly.

## Installation

```bash
pip install git+https://github.com/Digiklausur/e2x-course-hub.git
```

For development:

```bash
git clone https://github.com/Digiklausur/e2x-course-hub
cd e2x-course-hub
pip install -e ".[dev]"
```

Building the package (`pip install .` or `python -m build`) also builds
`course-service-ui` via `hatch-jupyter-builder` and bundles the result into the wheel.
For frontend-only iteration:

```bash
cd course-service-ui
npm install
npm run dev
```

## Running it

The service is a standard [JupyterHub managed service](https://jupyterhub.readthedocs.io/en/stable/reference/services.html),
run with `uvicorn`:

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
explicitly.

### Configuration

All settings are read from the environment (via `pydantic-settings`):

| Variable                     | Default                    | Purpose                                                        |
|-------------------------------|-----------------------------|-----------------------------------------------------------------|
| `JUPYTERHUB_API_URL`          | —                            | JupyterHub Hub API URL, used to manage users and groups         |
| `JUPYTERHUB_API_TOKEN`        | —                            | API token for the above                                         |
| `JUPYTERHUB_SERVICE_PREFIX`   | `/`                          | URL prefix the service is mounted under                         |
| `E2X_COURSE_DB_URL`           | `sqlite:///courses.db`      | SQLAlchemy URL for the course/term database                     |
| `E2X_INFRASTRUCTURE_PROVIDER` | `default`                    | Entry-point name of the `InfrastructureCatalogProvider` to load |
| `E2X_ADD_USERS_TO_HUB`        | `false`                      | Create JupyterHub users automatically on membership changes     |
| `E2X_DELETE_EMPTY_GROUPS`     | `false`                      | Delete a course/term's JupyterHub group once it has no members  |

### Optional: `whoami` service

`e2x_course_hub.course_service.whoami:app` is a minimal standalone FastAPI service that
returns the authenticated caller's identity — handy for verifying JupyterHub OAuth is
wired up correctly before debugging the full course service.

## REST API

All routes are served under `{service_prefix}/v1`. Interactive docs (Swagger UI) are
available at `{service_prefix}/docs` once the service is running, and the schema can be
exported standalone with `python scripts/export_openapi.py`.

| Resource            | Routes                                                                                                   |
|----------------------|------------------------------------------------------------------------------------------------------------|
| Courses              | `GET/POST /courses`, `GET/DELETE /courses/{course_id}`, `GET/PATCH /courses/{course_id}/metadata`, `GET/PATCH /courses/{course_id}/environment`, `GET /courses/{course_id}/terms` |
| Terms                | `POST/GET/DELETE /courses/{course_id}/terms/{term_id}`, `GET/PATCH /courses/{course_id}/terms/{term_id}/environment` |
| Infrastructure       | `GET /catalogs/image-catalog`, `GET /catalogs/resource-tiers`, `GET /catalogs/profile-catalog`             |
| Membership           | `GET/PATCH /lms/admins`, `GET/PATCH /lms/course-creators`, `GET/PATCH /courses/{course_id}/owners`, `GET/PATCH /courses/{course_id}/terms/{term_id}/{instructors,teaching-assistants,students,observers}` |
| Current user         | `GET /me`                                                                                                  |

`course-service-ui` consumes this API with types generated from the OpenAPI schema
(`npm run generate:api-types` in `course-service-ui/`); CI fails if the committed types
drift from the schema.

## Roles & permissions

Roles are defined by `e2x-hub-rbac` and scoped to the LMS, a course, or a term. Default
permissions for course/term management (`e2x_course_hub/api/course_permissions.py`):

| Role                | Scope  | Default permissions                                                                 |
|---------------------|--------|----------------------------------------------------------------------------------------|
| LMS admin           | LMS    | Everything                                                                              |
| Course creator      | LMS    | Create courses, view courses                                                            |
| Course owner        | Course | Manage the course (metadata, environment, remove) and its terms (add/remove, environment) |
| Instructor          | Term   | View the course, manage the term (environment, remove)                                  |
| Teaching assistant  | Term   | View the course and term                                                                |
| Observer            | Term   | View the course and term                                                                |
| Student             | Term   | (none — spawns only, no management permissions)                                        |

Membership itself (who holds which role, per course/term) is managed separately through
the membership API, backed by JupyterHub groups.

## Development

```bash
ruff check .
ruff format --check .
```

```bash
cd course-service-ui
npm run lint
npm run format
```

CI (`.github/workflows/ci.yml`) runs Python linting, frontend linting/formatting, and
checks that the generated OpenAPI schema and TypeScript types are committed and in
sync with the routers.

## License

MIT License — see [LICENSE](LICENSE) for details.
