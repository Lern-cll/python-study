from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio.session import AsyncSession
from models.news import Category, News
from sqlalchemy import select, func, update, or_
from cache.news_cache import get_cached_categories, set_cached_categories, get_cached_news_list, set_cached_news_list
from schemas.base import NewsItemBase



# 获取新闻分类
async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    # 从缓存中获取新闻分类
    cached_categories = await get_cached_categories()
    if cached_categories:
        return cached_categories

    stmt = select(Category).order_by(Category.sort_order).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()  # ORM

    # 写入缓存
    if categories:
        categories = jsonable_encoder(categories)
        await set_cached_categories(categories)

    # 返回数据
    return categories

# 获取新闻列表
async def get_news_list(db: AsyncSession, category_id: int, page: int, page_size: int):
    # 从缓存中获取新闻列表
    cached_news_list = await get_cached_news_list(category_id, page, page_size) # 缓存中的数据是 JSON 字符串
    if cached_news_list:
        # return cached_news_list  # 要的是ORM 对象，需要转换为 JSON 可序列化
        return [News(**item) for item in cached_news_list]

    offset = (page - 1) * page_size
    limit = page_size
    stmt = select(News).where(News.category_id == category_id).offset(offset).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()
    
    # 写入缓存
    if news_list:
        # 先把ORM 对象转换为 JSON 可序列化, 才能写入缓存
        # news_list = jsonable_encoder(news_list)

        # ORM 对象转为Pydantic 模型实例, 再转为字典
        # by_alias  = False 不适用别名， 保存Python 风格， 因为Redis数据是给后端用的
        news_data = [NewsItemBase.model_validate(item).model_dump(mode="json", by_alias=False) for item in news_list]
        await set_cached_news_list(category_id, page, page_size, news_data)

    return news_list

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

# ============ 新闻搜索 ============
# 转义 LIKE 通配符：用户输入的 % 和 _ 在 LIKE 中有特殊含义，需要转义
def _escape_like(keyword: str) -> str:
    return keyword.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


# 新闻搜索：跨 title/description/content/author 四个字段做子串匹配，
# 排序优先级：title 命中 > description 命中 > author 命中 > content 命中；同级别内 views 倒序
async def search_news(db: AsyncSession, keyword: str, page: int, page_size: int):
    # 去除空格、strip、转义 LIKE 通配符
    clean_kw = keyword.replace(' ', '').strip()
    if not clean_kw:
        return []
    pattern = f"%{_escape_like(clean_kw)}%"
    offset = (page - 1) * page_size

    # OR 条件：任一字段命中即视为匹配
    match_filter = or_(
        News.title.like(pattern, escape='\\'),
        News.description.like(pattern, escape='\\'),
        News.content.like(pattern, escape='\\'),
        News.author.like(pattern, escape='\\'),
    )
    # 字段命中权重：title > description > author > content，最后 views DESC
    stmt = (
        select(News)
        .where(match_filter)
        .order_by(
            News.title.like(pattern, escape='\\').desc(),
            News.description.like(pattern, escape='\\').desc(),
            News.author.like(pattern, escape='\\').desc(),
            News.content.like(pattern, escape='\\').desc(),
            News.views.desc(),
        )
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


# 新闻搜索总数（同一过滤条件下的命中数量）
async def search_news_total(db: AsyncSession, keyword: str):
    clean_kw = keyword.replace(' ', '').strip()
    if not clean_kw:
        return 0
    pattern = f"%{_escape_like(clean_kw)}%"
    match_filter = or_(
        News.title.like(pattern, escape='\\'),
        News.description.like(pattern, escape='\\'),
        News.content.like(pattern, escape='\\'),
        News.author.like(pattern, escape='\\'),
    )
    stmt = select(func.count(News.id)).where(match_filter)
    result = await db.execute(stmt)
    return result.scalar_one()


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
