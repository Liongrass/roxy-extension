from fastapi import APIRouter

from .crud import db
from .views import roxy_generic_router
from .views_api import roxy_api_router
from .views_proxy import roxy_proxy_router

roxy_ext: APIRouter = APIRouter(prefix="/roxy", tags=["roxy"])
roxy_ext.include_router(roxy_generic_router)
roxy_ext.include_router(roxy_api_router)
roxy_ext.include_router(roxy_proxy_router)

roxy_static_files = [
    {
        "path": "/roxy/static",
        "name": "roxy_static",
    }
]


def roxy_stop():
    pass


def roxy_start():
    pass


__all__ = [
    "db",
    "roxy_ext",
    "roxy_start",
    "roxy_static_files",
    "roxy_stop",
]
