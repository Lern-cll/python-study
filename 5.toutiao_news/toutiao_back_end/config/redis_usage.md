# Redis 封装缓存操作

缓存操作就是围绕 Redis 做"存、取、删、判断、过期"等操作，让数据访问更快、数据库压力更小。

Redis 存储数据：**key - value**

## 方法说明

| 方法 | 参数 | 描述 |
| --- | --- | --- |
| `setex` | `key: str`<br>`expire: int`（秒）<br>`value: str` | 设置缓存并指定过期时间（秒） |
| `get` | `key: str` | 获取缓存值。若缓存不存在，返回 `None` |
| `delete` | `key: str` | 删除指定的缓存值 |
| `exists` | `key: str` | 检查键存储是否存在，返回布尔值 |

## 常见边界处理

### 1. 缓存穿透（Cache Penetration）

**场景**：查询一个**数据库中根本不存在**的数据（如 `id = -1`），缓存和数据库都"查不到"，导致每次请求都直接打到数据库。

**解决思路**：
- 缓存空值：即使数据库查不到，也把 `None` / 空标记写入缓存，并设置**较短**的过期时间。
- 布隆过滤器（Bloom Filter）：在缓存前置一层布隆过滤器，快速判断 key 是否可能存在，不存在则直接拦截。

```python
async def get_user_safe(redis, user_id: int):
    key = f"user:{user_id}"
    cached = await redis.get(key)
    if cached is None:
        # 数据库查询
        user = await db.get_user(user_id)
        if user is None:
            # 缓存空值，设置较短过期时间，防止反复穿透
            await redis.setex(key, 60, "null")
            return None
        await redis.setex(key, 3600, json.dumps(user))
        return user
    if cached == "null":
        return None
    return json.loads(cached)
```

---

### 2. 缓存击穿（Cache Breakdown）

**场景**：某个 **热点 key 过期瞬间**，大量并发请求同时打到数据库。

**解决思路**：
- 互斥锁（分布式锁）：只让一个线程去回源数据库，其余等待。
- 逻辑过期：不设置真实 TTL，在 value 中存过期时间字段，发现过期时加锁回源。

```python
import asyncio

async def get_hot_news(redis, news_id: int, lock_redis):
    key = f"news:hot:{news_id}"
    cached = await redis.get(key)
    if cached:
        return json.loads(cached)

    # 加锁，只让一个请求回源
    lock_key = f"lock:{key}"
    got = await lock_redis.set(lock_key, "1", nx=True, ex=10)
    if got:
        try:
            news = await db.get_news(news_id)
            await redis.setex(key, 3600, json.dumps(news))
            return news
        finally:
            await lock_redis.delete(lock_key)
    else:
        await asyncio.sleep(0.05)
        return await get_hot_news(redis, news_id, lock_redis)
```

---

### 3. 缓存雪崩（Cache Avalanche）

**场景**：大量 key **在同一时间集中过期**，或 Redis 宕机，导致请求全部涌向数据库。

**解决思路**：
- 过期时间加随机偏移：避免同一时刻大批 key 失效。
- 多级缓存：本地缓存（Caffeine / 进程内存）+ Redis。
- 高可用：Redis Cluster / Sentinel，避免单点故障。
- 熔断降级：数据库压力大时直接返回兜底数据。

```python
import random

async def set_cache_with_jitter(redis, key, value, base_ttl=3600):
    # 基础 TTL 上叠加随机偏移，分散过期时间
    jitter = random.randint(0, 300)
    await redis.setex(key, base_ttl + jitter, value)
```

---

## 对比总结

| 问题 | 触发条件 | 核心方案 |
| --- | --- | --- |
| 穿透 | 查询不存在的数据 | 缓存空值、布隆过滤器 |
| 击穿 | 热点 key 过期瞬间高并发 | 分布式锁、逻辑过期 |
| 雪崩 | 大量 key 同时过期 / Redis 宕机 | 过期时间加随机偏移、多级缓存、高可用 |
