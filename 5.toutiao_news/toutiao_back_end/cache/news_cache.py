# 新闻相关的缓存方法，新闻的读取和写入
from typing import Any, Dict

from config.cache_conf import get_cache_list, set_cache

CATEGORIES_KEY = 'news:categories'


# 获取新闻分类缓存
async def get_cached_categories():
    return await get_cache_list(CATEGORIES_KEY)


# 写入新闻分类缓存
# 分类、配置： 7200；列表： 600；详情：1800； 验证码：120；
async def set_cached_categories(categories: list[Dict[str, Any]], expire: int = 3600, cache_key: str = CATEGORIES_KEY):
    return await set_cache(cache_key, categories, expire)
