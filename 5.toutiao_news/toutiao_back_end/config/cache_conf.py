import json
from typing import Any
import redis.asyncio  as redis

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0


# 创建 Redis 的连接对象
redis_client = redis.Redis(
    host=REDIS_HOST, # Redis 主机地址
    port=REDIS_PORT, # Redis 端口号
    db=REDIS_DB,     # Redis 数据库编号 0-15 默认的是 0，如果做数据隔离，可以用其他的
    decode_responses=True, # 是否将 Redis 中的数据自动解码为 字符串
    protocol=2, # 兼容老版本 Redis（< 6.x 不支持 HELLO 命令，强制走 RESP2 协议）
)


# 设置 和 读取（字符串 和 列表或者字典） “[{}]”

# 读取：字符串
async def get_cache(key: str):
    # return await redis_client.get(key)
    try:
        return await redis_client.get(key)
    except Exception as e:
        # 处理异常，例如返回 None 或抛出异常
        print(f"读取缓存失败：{e}")
        return None


# 读取：列表或者字典
async def get_cache_list(key: str):
    try: 
        data =  await redis_client.get(key)
        if data :
            return json.loads(data)  # 将字符串转序列化
        return None
    except Exception as e:
        # 处理异常，例如返回 None 或抛出异常
        print(f"读取缓存失败：{e}")
        return None 

# 数据的存储
async def set_cache(key: str, value: any, expire: int = 3600):
    try:
        if isinstance(value, (list, dict)): # isinstance 判断是list 还是 dict
            value = json.dumps(value, ensure_ascii=False) # 序列化数据, 中文不转义，正常保存
        await redis_client.setex(key, expire, value)
        return True
    except Exception as e:
        # 处理异常，例如返回 None 或抛出异常
        print(f"设置缓存失败：{e}")
        return False


# 数据的删除
async def delete_cache(key: str):   
    try:
        await redis_client.delete(key)
        return True
    except Exception as e:
        # 处理异常，例如返回 None 或抛出异常
        print(f"删除缓存失败：{e}")
        return False

# 清空数据
async def flush_cache():
    try:
        await redis_client.flushdb()
        return True
    except Exception as e:
        # 处理异常，例如返回 None 或抛出异常
        print(f"清空缓存失败：{e}")
        return False
