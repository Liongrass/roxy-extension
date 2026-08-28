from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from lnbits.core.crud import get_user
from lnbits.core.models import SimpleStatus, WalletTypeInfo
from lnbits.decorators import require_admin_key, require_invoice_key

from .crud import create_roxy, delete_roxy, get_roxies, get_roxy, update_roxy
from .helpers import build_roxy_urls
from .models import CreateRoxyData, Roxy, UpdateRoxyData

roxy_api_router = APIRouter(prefix="/api/v1")


def _with_urls(roxy: Roxy, request: Request) -> Roxy:
    try:
        roxy.proxy_url, roxy.lnurl = build_roxy_urls(roxy, request)
    except ValueError:
        pass
    return roxy


@roxy_api_router.get("/roxies", status_code=HTTPStatus.OK)
async def api_list_roxies(
    request: Request,
    key_info: WalletTypeInfo = Depends(require_invoice_key),
    all_wallets: bool = Query(False),
) -> list[Roxy]:
    wallet_ids = [key_info.wallet.id]
    if all_wallets:
        user = await get_user(key_info.wallet.user)
        wallet_ids = user.wallet_ids if user else []

    roxies = await get_roxies(wallet_ids)
    return [_with_urls(roxy, request) for roxy in roxies]


@roxy_api_router.get("/roxies/{roxy_id}", status_code=HTTPStatus.OK)
async def api_get_roxy(
    request: Request,
    roxy_id: str,
    key_info: WalletTypeInfo = Depends(require_invoice_key),
) -> Roxy:
    roxy = await get_roxy(roxy_id)
    if not roxy:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Roxy not found.")
    if roxy.wallet != key_info.wallet.id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Not your roxy.")
    return _with_urls(roxy, request)


@roxy_api_router.post("/roxies", status_code=HTTPStatus.CREATED)
async def api_create_roxy(
    request: Request,
    data: CreateRoxyData,
    key_info: WalletTypeInfo = Depends(require_admin_key),
) -> Roxy:
    if not data.wallet:
        data.wallet = key_info.wallet.id

    roxy = await create_roxy(data, data.wallet)
    return _with_urls(roxy, request)


@roxy_api_router.put("/roxies/{roxy_id}", status_code=HTTPStatus.OK)
async def api_update_roxy(
    request: Request,
    roxy_id: str,
    data: UpdateRoxyData,
    key_info: WalletTypeInfo = Depends(require_admin_key),
) -> Roxy:
    roxy = await get_roxy(roxy_id)
    if not roxy:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Roxy not found.")
    if roxy.wallet != key_info.wallet.id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Not your roxy.")

    updated = await update_roxy(roxy_id, data)
    assert updated
    return _with_urls(updated, request)


@roxy_api_router.delete("/roxies/{roxy_id}", status_code=HTTPStatus.OK)
async def api_delete_roxy(
    roxy_id: str,
    key_info: WalletTypeInfo = Depends(require_admin_key),
) -> SimpleStatus:
    roxy = await get_roxy(roxy_id)
    if not roxy:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Roxy not found.")
    if roxy.wallet != key_info.wallet.id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Not your roxy.")
    await delete_roxy(roxy_id)
    return SimpleStatus(success=True, message="Roxy deleted.")
