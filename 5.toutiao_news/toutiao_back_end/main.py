import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.db_conf import AsyncSessionLocal
from routers import news, users, favorite, history, search_history, ai_chat
from utils.exception_handlers import register_exception_handlers
from utils.logging_conf import setup_logging
from utils.scheduler import daily_task_runner
from utils.token import clean_expired_tokens

# 初始化日志系统：控制台 + 业务 success_log / error_log（按天分文件，保留 30 天）
setup_logging(log_dir="logs", retention_days=30)
logger = logging.getLogger("app")

# 用于通知后台调度循环退出
scheduler_stop_event: asyncio.Event = None  # type: ignore
scheduler_task: asyncio.Task = None  # type: ignore


async def _run_clean_expired_tokens() -> None:
    """带 session 的任务包装，供调度器调用"""
    async with AsyncSessionLocal() as session:
        try:
            count = await clean_expired_tokens(session)
            logger.info("[token-cleanup] 清理过期 token 完成，共删除 %s 条", count)
        except Exception as e:
            logger.exception("[token-cleanup] 清理过期 token 失败: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时清理一次 + 注册后台每日调度"""
    global scheduler_stop_event, scheduler_task

    # 1. 启动时立即清理一次（兜底）
    await _run_clean_expired_tokens()

    # 2. 注册后台每日 00:00 调度
    scheduler_stop_event = asyncio.Event()
    scheduler_task = asyncio.create_task(
        daily_task_runner(
            task=_run_clean_expired_tokens,
            stop_event=scheduler_stop_event,
            hour=0,
            minute=0,
        )
    )

    yield  # 应用运行中

    # 3. 关闭时通知后台任务退出并等待
    scheduler_stop_event.set()
    try:
        await asyncio.wait_for(scheduler_task, timeout=5)
    except asyncio.TimeoutError:
        scheduler_task.cancel()


app = FastAPI(lifespan=lifespan)

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
app.include_router(search_history.router)
app.include_router(ai_chat.router)


# 添加cors中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许访问的源
    allow_credentials=True,  # =允许携带cookie
    allow_methods=["*"],  # 允许所有的请求方法
    allow_headers=["*"],  # 允许所有的请求头
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=10001, reload=True)