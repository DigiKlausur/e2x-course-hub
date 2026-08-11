from fastapi import Request
from fastapi.responses import JSONResponse

from ..errors import APIError


async def api_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler that converts APIError subclasses to RFC 9457 problem details."""
    assert isinstance(exc, APIError)
    problem = {
        "type": exc.type_uri,
        "title": exc.title,
        "status": exc.status_code,
        "detail": exc.detail,
    }
    problem.update(exc.extra)
    return JSONResponse(
        status_code=exc.status_code,
        content=problem,
        media_type="application/problem+json",
    )
