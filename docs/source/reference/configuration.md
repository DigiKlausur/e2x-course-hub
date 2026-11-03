# Configuration

All settings are read from environment variables via `pydantic-settings`. In a
JupyterHub deployment, set them in the `environment` of the service (see
{doc}`../course_service/overview`).

| Variable                      | Default                | Purpose                                                          |
| ----------------------------- | ---------------------- | ---------------------------------------------------------------- |
| `JUPYTERHUB_API_URL`          | —                      | JupyterHub API URL, used to manage users and groups. Set by JupyterHub. |
| `JUPYTERHUB_API_TOKEN`        | —                      | API token for the above. Set by JupyterHub.                      |
| `JUPYTERHUB_SERVICE_PREFIX`   | `/`                    | URL prefix the service is mounted under. Set by JupyterHub.      |
| `JUPYTERHUB_BASE_URL`         | `/`                    | Base URL of JupyterHub, used to send students to the spawn page after they join a semester. Set by JupyterHub for managed services; set it yourself for an external service. |
| `E2X_COURSE_DB_URL`           | `sqlite:///courses.db` | SQLAlchemy URL of the course and term database.                  |
| `E2X_INFRASTRUCTURE_PROVIDER` | `default`              | Entry-point name of the infrastructure catalog provider to load. |
| `E2X_ADD_USERS_TO_HUB`        | `false`                | Create JupyterHub users that don't exist yet when they are added to a role. Without it, adding an unknown username fails. |
| `E2X_DELETE_EMPTY_GROUPS`     | `false`                | Delete a role's JupyterHub group once its last member is removed. |
| `E2X_USERNAME_FORMATS`        | `[]`                   | Accepted username formats as a JSON list of `pattern` and `hint` pairs. Without formats, every username is accepted. |
| `E2X_USERNAME_ENFORCE_IN_API` | `false`                | Also reject usernames that match no format in the REST API, not only in the UI. |

## Username formats

Every university formats usernames differently. `E2X_USERNAME_FORMATS` lists the
accepted formats, each a regular expression with a hint for users:

```yaml
hub:
  services:
    course-service:
      environment:
        E2X_USERNAME_FORMATS: '[{"pattern": "[a-z]{2}\\d{4}", "hint": "Staff: staff ID, e.g. ab1234"}, {"pattern": "s\\d{7}", "hint": "Students: s and matriculation number, e.g. s1234567"}]'
        E2X_USERNAME_ENFORCE_IN_API: "true"
```

- A username is valid if it matches **any** format completely, so `s\d{7}` does not
  accept `s12345678`.
- The dialog for adding members lists the hints and refuses usernames that match no
  format. With `E2X_USERNAME_ENFORCE_IN_API`, the REST API rejects them too, with a
  `422` that names the usernames and hints.
- Removing members is never checked, so members with outdated usernames can still be
  removed after the format changes.
- The patterns are checked by Python on the server and by JavaScript in the browser.
  Stick to syntax both understand, such as character classes, quantifiers, `|` and
  `(?:…)`. Python-only syntax like `(?P<name>…)` breaks the dialog.
- The service does not start if a pattern is not a valid regular expression.

## Infrastructure catalog provider

`E2X_INFRASTRUCTURE_PROVIDER` selects an `InfrastructureCatalogProvider` by name from
the `e2x_course_hub.infrastructure_catalog_providers` entry-point group. The provider
is a separate package that defines which images, resource tiers and profiles exist. It
reads its own configuration, so its settings are documented with the provider. See
{doc}`../spawner/contract`.

## Settings classes

The service settings extend the framework-agnostic `CoreSettings`, which are also used
by `e2x_course_hub.loader` outside the web service.

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.course_service.settings.ServiceSettings
```

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.settings.CoreSettings
```

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.settings.HubApiSettings
```

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.settings.CourseSettings
```

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.settings.MembershipSettings
```

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.settings.UsernameSettings
```

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.settings.UsernameFormat
```

```{eval-rst}
.. autopydantic_model:: e2x_course_hub.settings.InfrastructureSettings
```
