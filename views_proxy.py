from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from loguru import logger

from .crud import get_roxy_by_hash
from .helpers import resolve_target_url

roxy_proxy_router = APIRouter(prefix="/api/v1/p")


def _with_extra_query(url: str, extra: list[tuple[str, str]]) -> str:
    """Append extra query params to url, preserving any it already has."""
    if not extra:
        return url
    parts = urlsplit(url)
    merged = parse_qsl(parts.query, keep_blank_values=True) + extra
    query = urlencode(merged)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


@roxy_proxy_router.get("/{unique_hash}", name="roxy.api_proxy")
async def api_proxy(request: Request, unique_hash: str) -> Response:
    roxy = await get_roxy_by_hash(unique_hash)
    if not roxy:
        return JSONResponse(status_code=404, content={"detail": "Roxy not found."})
    if not roxy.is_enabled:
        return JSONResponse(
            status_code=410, content={"detail": "This roxy is disabled."}
        )

    try:
        target = resolve_target_url(roxy.target_url)
    except ValueError as exc:
        # Logged server-side only -- this endpoint is public and
        # unauthenticated, so the response body must not leak the configured
        # target (internal hosts, ports, embedded credentials, etc.).
        logger.warning(f"Roxy {unique_hash!r}: could not resolve target: {exc!s}")
        return JSONResponse(
            status_code=502,
            content={"detail": "Could not resolve target."},
        )

    location = _with_extra_query(target, request.query_params.multi_items())
    return RedirectResponse(
        url=location,
        # 307, not 301/302/308: preserves GET semantics, and -- paired with
        # Cache-Control below -- must never be treated as permanent. A
        # roxy's entire point is that its target can be repointed later;
        # a cached redirect would silently defeat that.
        status_code=307,
        headers={"Cache-Control": "no-store"},
    )
