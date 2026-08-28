from typing import Optional
from urllib.parse import urlsplit

from fastapi import Request
from lnurl import decode as lnurl_decode
from lnurl import encode as lnurl_encode

from .models import Roxy


def is_onion_host(host: str) -> bool:
    return host.lower().endswith(".onion")


def resolve_target_url(target_url: str) -> str:
    """Return the real HTTP(S) URL a roxy should forward requests to.

    A target_url may be a plain http(s) URL (scheme optional -- defaults to
    "https://", or "http://" for a bare .onion host, since Tor hidden
    services are conventionally served over plain http), or a bech32-encoded
    LNURL string, optionally prefixed with a "lightning:" URI scheme (as
    wallets/QR codes commonly display it) -- in which case it is decoded to
    the URL it points to.
    """
    stripped = target_url.strip()
    if stripped.lower().startswith("lightning:"):
        stripped = stripped[len("lightning:") :].strip()
    if stripped.lower().startswith("lnurl1"):
        try:
            stripped = str(lnurl_decode(stripped))
        except Exception as exc:
            raise ValueError(f"Could not decode LNURL target: {stripped!r}.") from exc
    # Applies whether stripped came in as-is or just came out of lnurl_decode
    # above -- a decoded LNURL can be schemeless too if it was encoded from a
    # bare host/path in the first place.
    if not urlsplit(stripped).scheme:
        host = stripped.split("/", 1)[0].split(":", 1)[0]
        scheme = "http" if is_onion_host(host) else "https"
        stripped = f"{scheme}://{stripped}"
    return stripped


def build_roxy_urls(roxy: Roxy, req: Request) -> tuple[str, Optional[str]]:
    """Build the public-facing (proxy_url, lnurl) pair for a roxy.

    proxy_url is always the raw callback URL. lnurl is its bech32 encoding,
    populated only when the roxy is configured to be shared as an LNURL.
    """
    try:
        proxy_url = str(req.url_for("roxy.api_proxy", unique_hash=roxy.unique_hash))
    except Exception as exc:
        # e.g. starlette.routing.NoMatchFound if the route can't be resolved
        # for some reason -- callers only need to know proxy_url/lnurl could
        # not be built, not have the whole request blow up over it.
        raise ValueError(
            f"Could not build the proxy URL for roxy {roxy.unique_hash!r}: {exc!s}"
        ) from exc
    if proxy_url.strip().lower().startswith("lnurl1"):
        # Should be structurally impossible: url_for() always returns a plain
        # http(s) URL. Guard anyway so a bech32-in-bech32 LNURL can never be
        # served to a wallet -- fail loudly instead of handing out a link
        # that decodes to another LNURL instead of a fetchable URL.
        raise ValueError(
            f"Refusing to LNURL-encode a value that is already an LNURL: "
            f"`{proxy_url!s}`."
        )
    if roxy.encoding != "lnurl":
        return proxy_url, None
    try:
        return proxy_url, str(lnurl_encode(proxy_url).bech32)
    except Exception as exc:
        raise ValueError(
            f"Error creating LNURL with url: `{proxy_url!s}`. "
            "Check your webserver proxy configuration."
        ) from exc
