from sqlalchemy.ext.asyncio.session import AsyncSession
from models.news import Category, News
from sqlalchemy import select, func, update

# 获取新闻分类
async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    stmt = select(Category).order_by(Category.sort_order).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

# 获取新闻列表
async def get_news_list(db: AsyncSession, category_id: int, page: int, page_size: int):
    offset = (page - 1) * page_size
    limit = page_size
    stmt = select(News).where(News.category_id == category_id).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

# 获取新闻总数
async def get_news_total(db: AsyncSession, category_id: int = None):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one() # 返回一个值

# 获取新闻详情
async def get_news_detail(db: AsyncSession, id: int):
    stmt = select(News).where(News.id == id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none() # 如果没有数据，返回 None

# 更新新闻浏览量
async def increase_news_views(db: AsyncSession, id: int):
    stmt = update(News).where(News.id == id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit() # 这里是立即更新的意思
    return result.rowcount > 0 # 返回影响的行数

# 获取相关新闻
async def get_related_news(
    db: AsyncSession,
    news_id: int,
    category_id: int,
    limit: int = 5
):
    stmt = select(News).where(News.category_id == category_id, News.id != news_id).order_by(News.views.desc(), News.publish_time.desc()).limit(limit)
    result = await db.execute(stmt)
    # return result.scalars().all()
    related_news = result.scalars().all()
    return [
        {
            "id": news.id,
            "title": news.title,
            "content": news.content,
            "image": news.image,
            "author": news.author,
            "publishTime": news.publish_time,
            "categoryId": news.category_id,
            "views": news.views,
        } for news in related_news]
