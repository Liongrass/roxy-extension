from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field

Encoding = Literal["url", "lnurl"]


class CreateRoxyData(BaseModel):
    title: str
    wallet: Optional[str] = None
    target_url: str
    encoding: Encoding = "url"
    is_enabled: bool = True


class UpdateRoxyData(BaseModel):
    title: Optional[str] = None
    target_url: Optional[str] = None
    encoding: Optional[Encoding] = None
    is_enabled: Optional[bool] = None


class Roxy(BaseModel):
    id: str
    wallet: str
    title: str
    target_url: str
    encoding: Encoding = "url"
    is_enabled: bool = True
    unique_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    proxy_url: Optional[str] = Field(
        default=None,
        no_database=True,
        description="Raw proxy URL (use for QR code generation when encoding='url')",
    )
    lnurl: Optional[str] = Field(
        default=None,
        no_database=True,
        description="Bech32-encoded LNURL for the proxy URL (populated when encoding='lnurl')",
    )
