"""FastAPI 应用入口。

业务路由（按功能拆分）都放在 testPy/routes/ 里，
由 testPy/routers.py 统一聚合后挂载到 app 上。
本文件只保留应用级别的配置：中间件、根路由等。
"""
from fastapi import FastAPI

from testPy.routers import router

app = FastAPI()

# 注册 testPy/routes/ 下所有的子路由
app.include_router(router)


# ---------- 中间件 ----------
@app.middleware("http")
async def add_middleware2(request, call_next):
    print("中间件2触发了")
    response = await call_next(request)
    print("中间件2执行完毕了")
    return response


@app.middleware("http")
async def add_middleware(request, call_next):
    print("中间件1触发了")
    response = await call_next(request)
    print("中间件1执行完毕了")
    return response


# ---------- 根路由 ----------
@app.get("/")
async def root():
    return {"message": "Hello World"}
