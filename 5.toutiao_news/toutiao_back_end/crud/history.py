from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from models.users import User
from models.history import History


# 添加历史
async def add_history(db: AsyncSession, user: User, news_id: int):
    stms = select(History).where(History.user_id == user.id, History.news_id == news_id)
    result = await db.execute(stms)
    history = result.scalar_one_or_none()

    if history:
        # 已存在：更新 view_time 为当前时间
        history.view_time = datetime.now()
    else:
        # 不存在：新增
        history = History(user_id=user.id, news_id=news_id, view_time=datetime.now())
        db.add(history)

    await db.commit()
    await db.refresh(history)
    return history