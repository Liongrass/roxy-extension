from datetime import datetime, timezone
from typing import Optional

from lnbits.db import Database
from lnbits.helpers import urlsafe_short_hash

from .models import CreateRoxyData, Roxy, UpdateRoxyData

db = Database("ext_roxy")


async def create_roxy(data: CreateRoxyData, wallet_id: str) -> Roxy:
    roxy = Roxy(
        id=urlsafe_short_hash()[:22],
        wallet=wallet_id,
        title=data.title,
        target_url=data.target_url,
        encoding=data.encoding,
        is_enabled=data.is_enabled,
        unique_hash=urlsafe_short_hash(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    await db.insert("roxy.roxies", roxy)
    return roxy


async def get_roxy(roxy_id: str) -> Optional[Roxy]:
    return await db.fetchone(
        "SELECT * FROM roxy.roxies WHERE id = :id",
        {"id": roxy_id},
        Roxy,
    )


async def get_roxy_by_hash(unique_hash: str) -> Optional[Roxy]:
    return await db.fetchone(
        "SELECT * FROM roxy.roxies WHERE unique_hash = :hash",
        {"hash": unique_hash},
        Roxy,
    )


async def get_roxies(wallet_ids: list[str]) -> list[Roxy]:
    if not wallet_ids:
        return []
    placeholders = ",".join(f":w{i}" for i in range(len(wallet_ids)))
    values = {f"w{i}": w for i, w in enumerate(wallet_ids)}
    return await db.fetchall(
        f"SELECT * FROM roxy.roxies WHERE wallet IN ({placeholders}) ORDER BY created_at DESC",
        values,
        model=Roxy,
    )


async def update_roxy(roxy_id: str, data: UpdateRoxyData) -> Optional[Roxy]:
    roxy = await get_roxy(roxy_id)
    if not roxy:
        return None
    updates = data.dict(exclude_unset=True)
    for key, value in updates.items():
        setattr(roxy, key, value)
    roxy.updated_at = datetime.now(timezone.utc)
    await db.update("roxy.roxies", roxy)
    return roxy


async def delete_roxy(roxy_id: str) -> None:
    await db.execute(
        "DELETE FROM roxy.roxies WHERE id = :id",
        {"id": roxy_id},
    )
