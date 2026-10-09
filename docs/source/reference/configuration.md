# Configuration

All settings are read from environment variables via `pydantic-settings`. In a
JupyterHub deployment, set them in the `environment` of the service (see
{doc}`../course_service/overview`).

| Variable                      | Default                | Purpose                                                          |
| ----------------------------- | ---------------------- | ---------------------------------------------------------------- |
| `JUPYTERHUB_API_URL`          | —                      | JupyterHub API URL, used to manage users and groups. Set by JupyterHub. |
| `JUPYTERHUB_API_TOKEN`        | —                      | API token for the above. Set by JupyterHub.                      |
| `JUPYTERHUB_SERVICE_PREFIX`   | `/`                    | URL prefix the service is mounted under. Set by JupyterHub.      |
| `E2X_COURSE_DB_URL`           | `sqlite:///courses.db` | SQLAlchemy URL of the course and term database.                  |
| `E2X_INFRASTRUCTURE_PROVIDER` | `default`              | Entry-point name of the infrastructure catalog provider to load. |
| `E2X_ADD_USERS_TO_HUB`        | `false`                | Create JupyterHub users that don't exist yet when they are added to a role. Without it, adding an unknown username fails. |
| `E2X_DELETE_EMPTY_GROUPS`     | `false`                | Delete a role's JupyterHub group once its last member is removed. |

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
.. autopydantic_model:: e2x_course_hub.settings.InfrastructureSettings
```
