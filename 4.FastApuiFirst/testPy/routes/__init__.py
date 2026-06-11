"""testPy 子路由包：按功能拆分的各路由文件都在这里。

把子路由和模型在此统一重新导出，
外部可以直接 `from testPy.routes import exception_router, BookItem` 使用。
"""
from .exception import router as exception_router
from .path import router as path_router
from .query import router as query_router
from .request import router as request_router
from .response import router as response_router

from .middleware import CustomHeaderMiddleware, RequestLogMiddleware

from .dependencies import Pagination, get_current_user, require_token

from .models import BookItem, News, User

__all__ = [
    # 子路由
    "exception_router",
    "response_router",
    "request_router",
    "query_router",
    "path_router",
    # 中间件
    "RequestLogMiddleware",
    "CustomHeaderMiddleware",
    # 依赖注入
    "Pagination",
    "require_token",
    "get_current_user",
    # 数据模型
    "BookItem",
    "BookAdd",
    "BookUpdate",
    "News",
    "User",
]
