from fastapi import FastAPI
from routers import news

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

# 挂载 注册路由
app.include_router(news.router)





if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=10001, reload=True)