from fastapi import FastAPI, HTTPException
from routers import news, users, favorite, history
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from utils.exception_handlers import register_exception_handlers

app = FastAPI()

# 注册全局异常处理
register_exception_handlers(app)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# 挂载 注册路由
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)


# 添加cors中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 允许访问的源
    allow_credentials=True, # =允许携带cookie
    allow_methods=["*"], # 允许所有的请求方法
    allow_headers=["*"], # 允许所有的请求头
)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=10001, reload=True)