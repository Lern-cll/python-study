from fastapi import FastAPI
from testPy.routers import router

app = FastAPI()

app.include_router(router)

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


@app.get("/")
async def root():
    return {"message": "Hello World"}