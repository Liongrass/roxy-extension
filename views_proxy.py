import httpx
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from loguru import logger

from .crud import get_roxy_by_hash
from .helpers import resolve_target_url

roxy_proxy_router = APIRouter(prefix="/api/v1/p")

# Hop-by-hop / framing headers that must not be copied verbatim from the
# upstream response -- httpx/starlette recompute these for the new response.
_EXCLUDED_RESPONSE_HEADERS = {
    "content-encoding",
    "content-length",
    "transfer-encoding",
    "connection",
    # A roxy's target is arbitrary and can be repointed by its owner at any
    # time; forwarding this would let it set cookies scoped to this LNbits
    # instance's own origin on behalf of anyone who visits the roxy link.
    "set-cookie",
}


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
        # Same reasoning as below: don't leak the stored target_url (which
        # resolve_target_url's own error messages embed) to an unauthenticated
        # public caller.
        logger.warning(f"Roxy {unique_hash!r}: could not resolve target: {exc!s}")
        return JSONResponse(
            status_code=502,
            content={"detail": "Could not resolve target."},
        )

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            upstream = await client.get(target, params=dict(request.query_params))
    except httpx.HTTPError as exc:
        # Details (target/target_url) are logged server-side only -- this
        # endpoint is public and unauthenticated, so the response body must
        # not leak the configured target (internal hosts, ports, embedded
        # credentials, etc.) to whoever triggered the error.
        logger.warning(
            f"Roxy {unique_hash!r}: error reaching target {target!r} "
            f"(stored target_url: {roxy.target_url!r}): {exc!s}"
        )
        return JSONResponse(
            status_code=502,
            content={"detail": "Error reaching target."},
        )

    headers = {
        key: value
        for key, value in upstream.headers.items()
        if key.lower() not in _EXCLUDED_RESPONSE_HEADERS
    }
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=headers,
        media_type=upstream.headers.get("content-type"),
    )
