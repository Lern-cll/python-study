"""路由聚合层：把 routes/ 子包下的各功能路由统一挂载到顶层 router 上。

外部（如 main.py）只需 `from testPy.routers import router` 即可。
"""
from fastapi import APIRouter

from .routes import (
    exception_router,
    path_router,
    query_router,
    request_router,
    response_router,
)

# 顶层 router,供 main.py 引用
router = APIRouter()

# 聚合 routes/ 子包下的各子路由
router.include_router(exception_router)
router.include_router(response_router)
router.include_router(request_router)
router.include_router(query_router)
router.include_router(path_router)


__all__ = ["router"]
