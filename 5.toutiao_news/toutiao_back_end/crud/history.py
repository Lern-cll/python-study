from datetime import datetime
from itertools import count

from sqlalchemy.engine import Result
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio.session import AsyncSession

from models import news
from models.users import User
from models.history import History
from models.news import News



# 添加历史
async def add_history(db: AsyncSession, user: User, news_id: int):
    stms = select(History).where(History.user_id == user.id, History.news_id == news_id)
    result:Result = await db.execute(stms)
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

# 获取历史列表
async def get_history_list(db: AsyncSession, user: User, page: int = 1, page_size: int = 10):
    count_query = select(func.count()).where(History.user_id == user.id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    offset = (page - 1) * page_size
    stms = (select(
                News,
                History.id.label("history_id"),
                History.view_time,
            ).
            join(History, News.id == History.news_id)
            .where(History.user_id == user.id)
            .order_by(History.view_time.desc())
            .limit(page_size)
            .offset(offset))
    result = await db.execute(stms)
    rows = result.all()
    return rows, total

# 删除某条历史记录
async def delete_history(db: AsyncSession, user: User, news_id: int):
    stms = delete(History).where(History.user_id == user.id, History.news_id == news_id)
    result:Result = await db.execute(stms)
    await db.commit()
    return result.rowcount > 0

# 删除所有历史记录
async def delete_all_history(db: AsyncSession, user: User):
    stms = delete(History).where(History.user_id == user.id)
    result:Result = await db.execute(stms)
    return result.rowcount or 0
