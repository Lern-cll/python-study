from sqlalchemy.ext.asyncio.session import AsyncSession
from models.news import category
from sqlalchemy import select

async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    stmt = select(category).order_by(category.sort_order).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()