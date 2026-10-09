"""
Minimal FastAPI JupyterHub managed service.
Shows the authenticated user's information as JSON.

Uses jupyterhub.services.auth.HubOAuth to identify the logged-in user
from JupyterHub's OAuth cookie.
"""

import os

from fastapi import Depends, FastAPI
from jupyterhub.utils import url_path_join
from jupyterhub_fastapi_adapter import (
    AuthenticationRequired,
    User,
    authentication_required_handler,
    oauth_callback,
    require_authenticated_user,
)

JUPYTERHUB_SERVICE_PREFIX = os.environ["JUPYTERHUB_SERVICE_PREFIX"]

app = FastAPI()

# Register exception handler
app.exception_handler(AuthenticationRequired)(authentication_required_handler)

# Register OAuth callback route
app.get(url_path_join(JUPYTERHUB_SERVICE_PREFIX, "oauth_callback"))(oauth_callback)


@app.get(JUPYTERHUB_SERVICE_PREFIX)
async def index(user: User = Depends(require_authenticated_user)):
    """Return authenticated user information."""
    return user


@app.get(url_path_join(JUPYTERHUB_SERVICE_PREFIX, "hello"))
async def hello(user: User = Depends(require_authenticated_user)):
    return {"message": f"Hello, {user.username}!"}
