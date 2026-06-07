"""中间件示例：请求日志、计时、添加自定义头。

FastAPI 的中间件通常注册在 app 层面（`app.add_middleware(...)` 或 `@app.middleware("http")`），
本文件以可导入的 `BaseHTTPMiddleware` 子类形式提供，方便 main.py 统一挂载。
"""
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class RequestLogMiddleware(BaseHTTPMiddleware):
    """打印每个请求的方法、路径与耗时（毫秒）。"""

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        cost_ms = (time.perf_counter() - start) * 1000
        print(
            f"[{request.method}] {request.url.path} -> {response.status_code} ({cost_ms:.2f}ms)"
        )
        return response


class CustomHeaderMiddleware(BaseHTTPMiddleware):
    """为所有响应统一追加自定义响应头。"""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Powered-By"] = "FastAPI-Demo"
        return response


__all__ = ["RequestLogMiddleware", "CustomHeaderMiddleware"]
