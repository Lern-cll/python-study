from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News
from models.users import User

# 是否收藏
async def is_new_favorite(db: AsyncSession, user: User, new_id: int):
    query = select(Favorite).where(
        Favorite.user_id == user.id,
        Favorite.news_id == new_id
    )
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None

# 添加收藏
async def add_new_favorite(db: AsyncSession, user: User, news_id: int):
    favorite = Favorite(user_id=user.id, news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite


# 取消收藏
async def remove_new_favorite(db: AsyncSession, user: User, news_id: int):
    stmt = delete(Favorite).where(
        Favorite.user_id == user.id,
        Favorite.news_id == news_id
    )
    result = await db.execute(stmt)
    await db.commit()
    return  result.rowcount > 0

# 获取收藏列表： 获取某个用户的新闻列表 + 分页功能
async def get_favorite_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10
):
    # 总量 + 收藏的新闻列表
    count_query = select(func.count()).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    # 获取收藏列表- 联表查询 join() + 收藏时间 +分页 limit()
    # select(查询主体模型).join(联合收藏模型， 联合查询的条件).where().order_by().offset().limit()
    offset = (page - 1) * page_size
    # [
    # (新闻对象，收藏时间，收藏id)
    # ]
    query = (select(News, Favorite.created_at.label("favorite_time"), Favorite.id.label("favorite_id")).
             join(Favorite, Favorite.news_id == News.id)
             .where(Favorite.user_id == user_id).
             order_by(Favorite.created_at.desc()).
             offset(offset).
             limit(page_size))
    result = await db.execute(query)
    rows = result.all()
    return  rows, total

# 取消用户下所有的的收藏列表
async def remove_all_favorite(db: AsyncSession, user_id: int):
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0
