# REST API

All routes are served under `{service_prefix}/v1`. Requests are authenticated through
JupyterHub OAuth, and every request is checked against the caller's roles (see
{doc}`roles`).

Once the service is running, the interactive documentation is available at
`{service_prefix}/docs` (Swagger UI) and `{service_prefix}/redoc`. The OpenAPI schema
is at `{service_prefix}/openapi.json`. It can also be exported without a running
deployment:

```bash
python scripts/export_openapi.py
```

| Resource       | Routes                                                                     |
| -------------- | -------------------------------------------------------------------------- |
| Courses        | `GET/POST /courses`, `GET/DELETE /courses/{course_id}`, `GET/PATCH /courses/{course_id}/metadata`, `GET/PATCH /courses/{course_id}/environment`, `GET /courses/{course_id}/terms` |
| Terms          | `POST/GET/DELETE /courses/{course_id}/terms/{term_id}`, `GET/PATCH /courses/{course_id}/terms/{term_id}/environment` |
| Infrastructure | `GET /catalogs/image-catalog`, `GET /catalogs/resource-tiers`, `GET /catalogs/profile-catalog` |
| Membership     | `GET/PATCH /lms/admins`, `GET/PATCH /lms/course-creators`, `GET/PATCH /courses/{course_id}/owners`, `GET/PATCH /courses/{course_id}/terms/{term_id}/{instructors,teaching-assistants,students,observers}` |
| Roles          | `GET /roles/{role}/actions`                                                |
| Current user   | `GET /me`                                                                  |

## Actions

Course and term responses include an `actions` object: a tree of booleans that says
what the caller may do with that resource, for example:

```json
"actions": {
  "view": true,
  "remove": false,
  "metadata": { "view": true, "edit": false }
}
```

Clients should use this tree to decide what to show instead of computing permissions
from roles. The server enforces the permissions either way.

## Errors

Errors are returned as [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457) problem
details (`application/problem+json`) with `type`, `title`, `status` and a `detail`
sentence that can be shown to a user.
