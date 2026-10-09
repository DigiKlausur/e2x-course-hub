# Spawner contract

The course hub does not start notebook servers. A separate infrastructure spawner
does, and the two packages meet only through the contract in
`e2x_course_hub.contract`. This page is for people who write such a spawner.
[`e2x-course-hub-kubespawner`](https://github.com/DigiKlausur/e2x-course-hub-kubespawner)
is a complete example built on KubeSpawner.

## Registering a catalog provider

The course hub loads the spawner's `InfrastructureCatalogProvider` through an entry
point. Register a zero-argument callable, usually the provider class, in the
spawner's `pyproject.toml`:

```toml
[project.entry-points."e2x_course_hub.infrastructure_catalog_providers"]
my_catalog = "my_spawner.catalog:MyCatalogProvider"
```

and select it with `E2X_INFRASTRUCTURE_PROVIDER=my_catalog`. The provider reads its
own configuration; the course hub never passes it any.

## Getting spawn offerings

The spawner gets a `SpawnOfferingProvider` from the course hub without the web
service:

```python
from e2x_course_hub.loader import load_spawn_offering_api

offerings = load_spawn_offering_api().get_spawn_offerings(user)
```

It reads the course database from `E2X_COURSE_DB_URL`, so the spawner needs the same
value as the course service.

```{include} ../../../e2x_course_hub/contract/README.md
:start-line: 2
```
