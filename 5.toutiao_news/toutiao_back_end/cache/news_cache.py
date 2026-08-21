# 新闻相关的缓存方法，新闻的读取和写入
from typing import Any, Dict, Optional

from config.cache_conf import get_cache_list, set_cache

CATEGORIES_KEY = 'news:categories'


# 获取新闻分类缓存
async def get_cached_categories():
    return await get_cache_list(CATEGORIES_KEY)


# 写入新闻分类缓存
# 分类、配置： 7200；列表： 600；详情：1800； 验证码：120；
async def set_cached_categories(categories: list[Dict[str, Any]], expire: int = 3600, cache_key: str = CATEGORIES_KEY):
    return await set_cache(cache_key, categories, expire)



# 写入缓存-新闻列表
# key=news_list:分类id:页码:每页数量 + 列表数据 + 过期时间
async def set_cached_news_list(
    category_id: Optional[int],
    page: int,
    page_size: int,
    news_list: list[Dict[str, Any]],
    expire: int = 600):
    category_port = category_id if category_id is not None else 'all'
    cache_key = f'news_list:{category_port}:{page}:{page_size}'
    return await set_cache(cache_key, news_list, expire)

# 获取缓存-新闻列表
async def get_cached_news_list(
    category_id: Optional[int],
    page: int,
    page_size: int):
    category_port = category_id if category_id is not None else 'all'
    cache_key = f'news_list:{category_port}:{page}:{page_size}'
    return await get_cache_list(cache_key)

# 写入缓存-新闻详情
async def set_cached_news_detail(news_id: int, news_detail: Dict[str, Any], expire: int = 600):
    cache_key = f'news_detail:{news_id}'
    return await set_cache(cache_key, news_detail, expire)

# 获取缓存-新闻详情
async def get_cached_news_detail(news_id: int):
    news_port = news_id if news_id is not None else 'all'
    cache_key = f'news_detail:{news_port}'
    return await get_cache_list(cache_key)

# 写入缓存-相关新闻, key: related_news:category_id:news_id
async def set_cached_related_news(category_id: int, news_id: int, related_news: list[Dict[str, Any]], expire: int = 3600):
    cache_key = f'related_news:{category_id}:{news_id}'
    return await set_cache(cache_key, related_news, expire)

# 获取缓存-相关新闻
async def get_cached_related_news(category_id: int, news_id: int):
    cache_key = f'related_news:{category_id}:{news_id}'
    return await get_cache_list(cache_key)


