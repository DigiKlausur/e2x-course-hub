import os

from e2x_hub_rbac.backend.jupyterhub import HubAPI
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from jupyterhub.utils import url_path_join
from jupyterhub_fastapi_adapter.hub_oauth import (
    AuthenticationRequired,
    authentication_required_handler,
    oauth_callback,
)

from ..__about__ import __version__
from ..api.api import API
from ..errors import APIError
from ._data import DATA_FILES_PATH

# from jupyterhub_fastapi_adapter.dependencies import User, require_authenticated_user
from .common.dependency_types import CurrentUser
from .courses.router import router as courses_router
from .exception_handlers import api_error_handler
from .infrastructure.router import router as infrastructure_router
from .me.router import router as me_router
from .membership.router import router as membership_router
from .terms.router import router as terms_router

# ── Config from environment ──────────────────────────────────────────
service_prefix = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "/").rstrip("/")
api_token = os.environ.get("JUPYTERHUB_API_TOKEN", "")
api_url = os.environ.get("JUPYTERHUB_API_URL", "")
server_config_file = os.environ.get("E2X_COURSE_HUB_CONFIG", "config.yml")
add_users_to_hub = os.environ.get("E2X_ADD_USERS_TO_HUB", "false").lower() == "true"
static_path = os.path.join(DATA_FILES_PATH, "static")
template_path = os.path.join(DATA_FILES_PATH, "templates", "course_service")


JUPYTERHUB_SERVICE_PREFIX = os.environ["JUPYTERHUB_SERVICE_PREFIX"]


# ── Jinja2 environment for SPA template ──────────────────────────────
jinja_env = Environment(loader=FileSystemLoader(template_path))

# ── Build API layer (business logic, unchanged) ─────────────────────
hub_api = HubAPI(api_token=api_token, api_url=api_url)
api = API(
    server_config_file=server_config_file,
    hub_api=hub_api,
    add_users_to_hub=add_users_to_hub,
)

# ── FastAPI application ──────────────────────────────────────────────
app = FastAPI(
    title="E2X Course Hub API",
    version=__version__,
    openapi_url=f"{service_prefix}/openapi.json",
    docs_url=f"{service_prefix}/docs",
    redoc_url=f"{service_prefix}/redoc",
)

# Register exception handler (using decorator to satisfy type checker)
app.exception_handler(AuthenticationRequired)(authentication_required_handler)

# Register OAuth callback route
app.get(url_path_join(JUPYTERHUB_SERVICE_PREFIX, "oauth_callback"))(oauth_callback)

# Store the API instance on app state so dependencies can access it
app.state.api = api

# ── Exception handlers ───────────────────────────────────────────────
app.add_exception_handler(APIError, api_error_handler)

# ── Routers (all prefixed relative to the service prefix) ────────────
# The service_prefix is handled by JupyterHub proxy, so routers use
# their own /v1/... prefixes which will be served at
# {service_prefix}/v1/...
app.include_router(courses_router, prefix=service_prefix)
app.include_router(terms_router, prefix=service_prefix)
app.include_router(infrastructure_router, prefix=service_prefix)
app.include_router(membership_router, prefix=service_prefix)
app.include_router(me_router, prefix=service_prefix)

# ── Static files ─────────────────────────────────────────────────────
app.mount(
    f"{service_prefix}/static",
    StaticFiles(directory=static_path),
    name="static",
)


# ── SPA routes ───────────────────────────────────────────────────────
@app.get(f"{service_prefix}", include_in_schema=False)
async def root_redirect():
    """Redirect the service root to the SPA."""
    return RedirectResponse(url=f"{service_prefix}/app/")


@app.get(
    f"{service_prefix}/app/{{path:path}}", include_in_schema=False, response_class=HTMLResponse
)
async def spa(user: CurrentUser, path: str = ""):
    """Serve the React SPA with server-side config injected."""
    template = jinja_env.get_template("react_base.j2")
    html = template.render(
        service_prefix=service_prefix,
        api_url=f"{service_prefix}/v1",
        user=user,
    )
    return HTMLResponse(content=html)
