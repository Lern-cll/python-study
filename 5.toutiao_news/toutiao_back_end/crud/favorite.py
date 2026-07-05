from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
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
