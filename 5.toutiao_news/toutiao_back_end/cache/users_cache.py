# 用户相的缓存方法，用户的读取和写入
from typing import Any, Dict

from config.cache_conf import get_cache_list, set_cache

INFO_KEY = 'users:info'


# 获取用户缓存
async def get_cached_users():
    return await get_cache_list(INFO_KEY)


# 写入用户缓存
# 用户、配置： 7200；列表： 600；详情：1800； 验证码：120；
async def set_cached_users(data: list[Dict[str, Any]], expire: int = 3600, cache_key: str = INFO_KEY):
    return await set_cache(cache_key, data, expire)
