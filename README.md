# Roxy — Generic HTTP Redirector for LNbits

**Roxy** creates a stable public link — shown as a raw URL or as a bech32
**LNURL**, your choice — backed by a QR code. Visiting that link
**redirects** the caller to a *target* (a URL, an LNURL, or a Lightning
Address) that you configure.

The link never changes. The target behind it can, at any time, through the
UI or the API. Print the QR code once, and keep repointing what it does
without reprinting it.

## How it works

1. Create a roxy: give it a title and a **target** — any `https://` URL, an
   LNURL (`lnurl1...`), or a Lightning Address (`user@domain.tld`).
2. Roxy gives you back a **proxy URL** (`https://<host>/roxy/<hash>`), shown
   either raw or bech32-encoded as an LNURL, plus a QR code for it.
3. Anyone who visits that link gets an HTTP redirect to whatever the target
   currently is — query parameters carried over onto it.
4. Change the target whenever you like. The link and QR code you already
   shared keep working, now redirecting to the new target.

If the target is itself an LNURL, Roxy decodes it to the URL it points to
before redirecting. If it's a Lightning Address, Roxy resolves it (per
LUD-16) to `https://domain.tld/.well-known/lnurlp/user` first. Either way,
this is useful for re-hosting an existing LNURL-pay/withdraw endpoint, or
someone's Lightning Address, behind a link you control and can repoint
later.

The redirect is a `307` with `Cache-Control: no-store`, deliberately never a
permanent redirect: since a roxy's target can change at any time, nothing
(browser, wallet, CDN) should ever cache where it currently points.

## Usage

1. Install the extension in LNbits.
2. Click **New Roxy**, pick a wallet, give it a title, and set the target —
   a URL, an LNURL, or a Lightning Address. Choose whether to share it as a
   raw URL or as an LNURL.
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
| `GET` | `/roxy/{unique_hash}` | None (public) | The proxy endpoint itself — redirects to the configured target |

Full schema is available in the Swagger docs at `/docs#/roxy`.

## Requirements

- LNbits 1.0.0 or later
