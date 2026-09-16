"""Export the course service OpenAPI schema.

This deliberately does not import ``e2x_course_hub.course_service.fastapi_app``:
that module builds the whole API layer at import time (course database,
infrastructure catalog provider, JupyterHub client), none of which schema
generation needs. Instead a throwaway app is assembled from the same routers,
so the schema can be produced from a checkout without a configured deployment.

Usage:
    python scripts/export_openapi.py [output.json]

The output feeds ``course-service-ui``'s ``npm run generate:api-types``, which
turns it into TypeScript. Regenerate both whenever a router or response model
changes.
"""

import json
import os
import sys
from pathlib import Path

# The JupyterHub auth dependencies read these when their module is imported.
# The values are irrelevant here because no request is ever served.
os.environ.setdefault("JUPYTERHUB_API_URL", "http://localhost:8081/hub/api")
os.environ.setdefault("JUPYTERHUB_API_TOKEN", "")
os.environ.setdefault("JUPYTERHUB_SERVICE_PREFIX", "/")

from fastapi import FastAPI  # noqa: E402

from e2x_course_hub.__about__ import __version__  # noqa: E402
from e2x_course_hub.course_service.courses.router import router as courses_router  # noqa: E402
from e2x_course_hub.course_service.infrastructure.router import (  # noqa: E402
    router as infrastructure_router,
)
from e2x_course_hub.course_service.me.router import router as me_router  # noqa: E402
from e2x_course_hub.course_service.membership.router import (  # noqa: E402
    router as membership_router,
)
from e2x_course_hub.course_service.terms.router import router as terms_router  # noqa: E402

# Mirrors the router registration in ``course_service.fastapi_app``. The service
# prefix is applied there by the JupyterHub proxy and is left off here so the
# generated paths stay deployment independent.
ROUTERS = (
    courses_router,
    terms_router,
    infrastructure_router,
    membership_router,
    me_router,
)


def build_app() -> FastAPI:
    app = FastAPI(title="E2X Course Hub API", version=__version__)
    for router in ROUTERS:
        app.include_router(router)
    return app


def main() -> None:
    destination = Path(sys.argv[1] if len(sys.argv) > 1 else "openapi.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(build_app().openapi(), indent=2) + "\n")
    print(f"Wrote {destination}")


if __name__ == "__main__":
    main()
