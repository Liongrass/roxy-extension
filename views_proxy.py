import httpx
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

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
        return JSONResponse(status_code=502, content={"detail": str(exc)})

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            upstream = await client.get(target, params=dict(request.query_params))
    except httpx.HTTPError as exc:
        return JSONResponse(
            status_code=502,
            content={
                "detail": f"Error reaching target {target!r} "
                f"(stored target_url: {roxy.target_url!r}): {exc!s}"
            },
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
