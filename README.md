# Roxy — Generic HTTP Proxy for LNbits

**Roxy** creates a stable public link — shown as a raw URL or as a bech32
**LNURL**, your choice — backed by a QR code. Requests made to that link are
forwarded live to a *target* URL (or LNURL) that you configure.

The link never changes. The target behind it can, at any time, through the
UI or the API. Print the QR code once, and keep repointing what it does
without reprinting it.

## How it works

1. Create a roxy: give it a title and a **target** — any `https://` URL, or
   an LNURL (`lnurl1...`).
2. Roxy gives you back a **proxy URL** (`https://<host>/roxy/api/v1/p/<hash>`),
   shown either raw or bech32-encoded as an LNURL, plus a QR code for it.
3. Anyone who visits that link gets forwarded to whatever the target
   currently is — query parameters included.
4. Change the target whenever you like. The link and QR code you already
   shared keep working, now pointing at the new target.

If the target is itself an LNURL, Roxy decodes it server-side and forwards
to the underlying service — useful for re-hosting an existing LNURL-pay or
LNURL-withdraw endpoint behind a link you control and can repoint later.

Roxy only forwards `GET` requests (the shape LNURL flows and most link
redirection use cases need); the body of the upstream response, its status
code, and its content type are passed straight back to the caller.

## Usage

1. Install the extension in LNbits.
2. Click **New Roxy**, pick a wallet, give it a title, and set the target
   URL or LNURL. Choose whether to share it as a raw URL or as an LNURL.
3. Click the **visibility** icon on any row to see its QR code and link.
4. Click the **edit** icon to change the target, title, share format, or to
   enable/disable it — the link stays the same.

## API

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/roxy/api/v1/roxies` | Invoice key | List all roxies |
| `GET` | `/roxy/api/v1/roxies/{id}` | Invoice key | Get a roxy |
| `POST` | `/roxy/api/v1/roxies` | Admin key | Create a roxy |
| `PUT` | `/roxy/api/v1/roxies/{id}` | Admin key | Update a roxy's title, target, share format, or enabled state |
| `DELETE` | `/roxy/api/v1/roxies/{id}` | Admin key | Delete a roxy |
| `GET` | `/roxy/api/v1/p/{unique_hash}` | None (public) | The proxy endpoint itself — forwards to the configured target |

Full schema is available in the Swagger docs at `/docs#/roxy`.

## Requirements

- LNbits 1.0.0 or later
- `httpx` (for outbound proxy requests)
