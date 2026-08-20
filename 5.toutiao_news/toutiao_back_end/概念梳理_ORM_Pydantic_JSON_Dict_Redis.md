# 概念梳理：ORM 对象 / Pydantic 模型 / dict / JSON / Redis / 命名风格

> 目标：用项目里的真实代码，把下面这些词一次性讲清楚。

---

## 0. 速查表

| 概念 | 一句话 | 能直接塞 Redis 吗 |
|---|---|---|
| 类 (Class) | 图纸，定义字段和类型 | ❌ |
| ORM 对象 (Instance) | 按 ORM 图纸造出来的实物，绑着数据库 | ❌ |
| dict | 纯数据结构 `{key: value}` | ✅ |
| JSON 字符串 | dict 序列化后的文本（Redis 实际存的） | ✅ |
| Pydantic 模型 | 带校验 + 字段映射规则的图纸 | ❌（它本身是类） |
| snake_case | `category_id`（DB / 后端内部） | — |
| camelCase | `categoryId`（HTTP 出参给前端） | — |

---

## 1. 类（Class）—— 图纸

类不是数据，是模板。项目有两个图纸：

### 1.1 ORM 类（给数据库看）—— `models/news.py`

```python
class News(Base):
    __tablename__ = "news"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    category_id: Mapped[int] = mapped_column(Integer)   # snake_case，对应 DB 列名
    publish_time: Mapped[datetime] = mapped_column(DateTime)
```

### 1.2 Pydantic 类（给代码 / 接口看）—— `schemas/base.py`

```python
class NewsItemBase(BaseModel):
    id: int
    title: str
    category_id: int = Field(alias="categoryId")         # 本名 ↔ 别名
    publish_time: Optional[datetime] = Field(None, alias="publishedTime")

    model_config = ConfigDict(
        from_attributes=True,      # 允许从 ORM 属性读取
        populate_by_name=True,     # 允许用本名或别名赋值
    )
```

Pydantic 比 ORM 类多了三个能力：
1. **类型校验**：传错类型立刻报错
2. **字段映射**：`category_id` ↔ `categoryId`
3. **字段过滤**：只挑图纸上声明的字段

---

## 2. ORM 对象（Instance）—— 实物

类不能存，但**造出来的实例**可以存——只是不能直接存 Redis。

```python
stmt = select(News).where(News.category_id == category_id)
result = await db.execute(stmt)
news_list = result.scalars().all()   # ORM 对象列表
```

```python
news = news_list[0]
type(news)           # <class 'models.news.News'>
news.category_id     # 1（按属性访问）
news.publish_time    # datetime(2026, 8, 20, 10, 0, 0) 不是字符串
```

直接 `json.dumps(news)` 会报错：

```python
json.dumps(news)
# TypeError: Object of type datetime is not JSON serializable
# TypeError: Object of type News is not JSON serializable
```

**ORM 对象必须先翻译成纯 dict 才能存 Redis**。

---

## 3. dict —— 纯数据

```python
d = {
    "id": 1,
    "title": "今天天气真好",
    "category_id": 1,                              # snake_case
    "publish_time": "2026-08-20T10:00:00",         # datetime 已被转字符串
}
json.dumps(d)   # ✅ 能
```

判断能不能进 Redis，就看能不能 `json.dumps`。

---

## 4. JSON 字符串 —— Redis 真正存的东西

Redis 只能存字符串、列表、哈希等基本类型，**不能存 Python 对象**。

```python
data_dict = {...}
redis.set("key", json.dumps(data_dict))    # 写
raw = redis.get("key")
data_dict = json.loads(raw)               # 读
```

---

## 5. Pydantic —— 翻译官

ORM → dict 有三种办法：

### A. 手搓（最累）

```python
d = {
    "id": news.id,
    "title": news.title,
    "publish_time": news.publish_time.isoformat(),  # datetime 手动转字符串
    ...
}
```

### B. `jsonable_encoder`（FastAPI 自带，看 `crud/news_cache.py` 第 23 行）

```python
from fastapi.encoders import jsonable_encoder
jsonable_encoder(news)   # ORM → dict，datetime 转字符串
```

**缺点：不管字段名映射。** `category_id` 出来还是 `category_id`。

### C. Pydantic（新闻列表用的，看 `crud/news_cache.py` 第 50 行）

```python
news_data = [
    NewsItemBase.model_validate(item)                    # ① ORM → Pydantic
                 .model_dump(mode="json", by_alias=False) # ② Pydantic → dict
    for item in news_list
]
```

#### ① `model_validate(item)` —— ORM 过 Pydantic 图纸

```python
p = NewsItemBase.model_validate(item)
type(p)   # NewsItemBase 实例
```

这一步做了：
- 只挑图纸上声明的字段（`content` 长文本不会进缓存，省 Redis 空间）
- 类型校验
- 别名信息准备好

#### ② `model_dump(mode="json", by_alias=False)` —— Pydantic → dict

- `mode="json"`：datetime 转 ISO 字符串
- `by_alias=False`：用本名 `category_id`（不用别名 `categoryId`）

---

## 6. snake_case vs camelCase（重点）

| 场景 | 命名 |
|---|---|
| 数据库表 / 列 | snake_case：`category_id`, `publish_time` |
| 后端内部（Redis、CRUD 返回值） | snake_case：`category_id`, `publish_time` |
| HTTP API 出参（给前端） | camelCase：`categoryId`, `publishedTime` |

`schemas/base.py` 用 `alias` 把两套名字串起来：

```python
category_id: int = Field(alias="categoryId")
publish_time: Optional[datetime] = Field(None, alias="publishedTime")
```

### `by_alias=False` / `True` 怎么选？

```python
model_dump(mode="json", by_alias=False)   # → {"category_id":1, ...}
model_dump(mode="json", by_alias=True)    # → {"categoryId":1, ...}
```

新闻列表缓存选 `False`，**因为 Redis 是后端用的，下游还要 `News(**item)` 回填 ORM**，而 ORM 列名就是 snake_case，正好对上。

如果是要把数据返回给前端 HTTP 接口，那就 `by_alias=True`。

---

## 7. 完整链路（`get_news_list`）

```
MySQL
  │ select(News)
  ▼
ORM 对象 [News(id=1, category_id=1, publish_time=datetime(...))]
  │ NewsItemBase.model_validate(item)                ← Pydantic 校验 + 字段过滤
  ▼
Pydantic 实例 [NewsItemBase(id=1, category_id=1, ...)]
  │ .model_dump(mode="json", by_alias=False)         ← datetime 转字符串、丢掉别名
  ▼
纯 dict [{"id":1, "category_id":1, "publish_time":"2026-08-20T10:00:00"}]
  │ json.dumps
  ▼
JSON 字符串 '[{"id":1,...}]'
  ▼
Redis (key = news_list:1:1:10)
       ─────── 下次再访问 ───────
JSON 字符串 → json.loads → dict（snake_case）
  │ News(**item)                                     ← 本名对上 ORM 列名
  ▼
ORM 对象 [News(id=1, ...)]
```

读缓存那行：

```python
return [News(**item) for item in cached_news_list]
```

**这就是为什么 Redis 里要存 snake_case**——`News(**dict)` 把 key 当字段名赋值，key 是 `category_id` 才对得上 `News.category_id`。

---

## 8. 一句话总结

- **类**：图纸，不能存
- **ORM 对象**：实物，绑数据库，不能直接存
- **Pydantic 模型**：按 Pydantic 图纸校验/清洗后的中间形态
- **dict**：纯数据结构，能 `json.dumps`
- **JSON 字符串**：Redis 实际存的
- **snake_case**：DB / 后端约定
- **camelCase**：HTTP 出参约定
- **`by_alias`**：由数据的"下一个消费者"决定（后端用 → False，前端用 → True）

---

## 9. 动手练习

```python
news = News(
    id=1, title="标题", description="简介",
    content="很长的内容...",   # 这个不进缓存
    image="http://...", author="张三",
    category_id=2, views=100,
    publish_time=datetime(2026, 8, 20, 10, 0, 0),
)
```

**参考答案**：

```python
from models.news import News
from schemas.base import NewsItemBase
from datetime import datetime
import json, redis

# 1. ORM → Pydantic → dict（过滤 + 命名转换）
data = NewsItemBase.model_validate(news).model_dump(mode="json", by_alias=False)
# {"id":1,"category_id":2,"publish_time":"2026-08-20T10:00:00",...}
# 注意：content 没出现，datetime 变字符串，字段是 category_id 不是 categoryId

# 2. dict → JSON → Redis
r = redis.Redis()
r.set("k", json.dumps(data))
raw = json.loads(r.get("k"))    # 读回 dict，snake_case

# 3. dict → ORM
news_back = News(**raw)
# raw 里 key 是 category_id，正好对上 News.category_id
```

跑通这三步，整条链路就彻底懂了。
