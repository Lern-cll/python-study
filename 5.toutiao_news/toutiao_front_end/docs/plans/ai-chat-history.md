# AI 问答历史会话 - 实施计划

## 功能目标

实现 AI 问答的历史会话持久化与会话切换能力：

1. pinia 持久化当前会话（切 tab 不丢）
2. 后端 `ai_chat_session` 表 + 5 个 REST 接口
3. 侧边栏抽屉展示历史列表（搜索 / 详情 / 删除）
4. 输入区圆形 `+` 按钮新建会话

## 架构说明

- **后端**：FastAPI + SQLAlchemy 2.x + Pydantic v2 + MySQL。新增 model/schema/crud/router，与现有 `history` / `search_history` 模块同模式。
- **前端**：Vue 3 + Pinia + Element Plus + Axios。新增 `aiChatStore` 管理会话状态，`AiChat.vue` 接入 store 并新增抽屉 UI。
- **API 边界**：千问调用仍走前端 `/qwen` 代理（API key 在前端），后端只负责会话 CRUD。
- **生命周期**：首条 AI 回成功 → POST 入库；后续每轮 AI 回成功 → PUT 覆盖 messages。

## 技术栈

- 后端：FastAPI、SQLAlchemy Async、Pydantic v2、aiomysql
- 前端：Vue 3 `<script setup>`、Pinia、Element Plus、Axios、SCSS
- 无新依赖

## 存放路径

- Spec：`docs/specs/ai-chat-history.md`
- 本计划：`docs/plans/ai-chat-history.md`
- 后端文件：
  - 修改：`D:\project_project_project\python-study\5.toutiao_news\toutiao_back_end\物料文件\database.sql`
  - 修改：`D:\project_project_project\python-study\5.toutiao_news\toutiao_back_end\main.py`
  - 修改：`D:\project_project_project\python-study\5.toutiao_news\toutiao_back_end\物料文件\API接口规范文档.md`
  - 新建：`D:\project_project_project\python-study\5.toutiao_news\toutiao_back_end\models\ai_chat_session.py`
  - 新建：`D:\project_project_project\python-study\5.toutiao_news\toutiao_back_end\schemas\ai_chat.py`
  - 新建：`D:\project_project_project\python-study\5.toutiao_news\toutiao_back_end\crud\ai_chat.py`
  - 新建：`D:\project_project_project\python-study\5.toutiao_news\toutiao_back_end\routers\ai_chat.py`
- 前端文件：
  - 修改：`src\router\index.ts`
  - 新建：`src\api\aiChat.ts`
  - 新建：`src\pinia\aiChatStore.ts`
  - 重构：`src\pages\ai\AiChat.vue`

---

## 任务清单

### 任务 1：DDL 增量（database.sql）

**涉及文件**：`toutiao_back_end\物料文件\database.sql`

**实施步骤**：

在 `ai_chat` 表 DDL 之后追加新表 DDL（来自 Spec）：

```sql
-- AI 会话表
CREATE TABLE IF NOT EXISTS `ai_chat_session` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '会话ID',
  `user_id` INT UNSIGNED NOT NULL COMMENT '用户ID',
  `title` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '会话标题',
  `model` VARCHAR(64) NOT NULL DEFAULT '' COMMENT 'AI模型标识',
  `messages` JSON NOT NULL COMMENT '完整消息数组',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  INDEX `fk_ai_chat_session_user_idx` (`user_id` ASC),
  INDEX `idx_user_updated` (`user_id` ASC, `updated_at` DESC),
  CONSTRAINT `fk_ai_chat_session_user`
    FOREIGN KEY (`user_id`)
    REFERENCES `user` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI 会话表';
```

**验证方式**：
- 文件存在新增 DDL 段；SQL 语法符合现有段风格（COMMENT、CHARSET、ENGINE）。
- 不动现有 `ai_chat` 表。

**完成标准**：DDL 完整插入。

---

### 任务 2：新建 SQLAlchemy 模型 `models/ai_chat_session.py`

**涉及文件**：`toutiao_back_end\models\ai_chat_session.py`（新建）

**实施步骤**：

```python
from sqlalchemy import Integer, String, ForeignKey, Index, text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from models.base import Base


class AiChatSession(Base):
    """AI 会话表"""
    __tablename__ = "ai_chat_session"

    __table_args__ = (
        Index("fk_ai_chat_session_user_idx", "user_id"),
        Index("idx_user_updated", text("user_id desc"), text("updated_at desc")),
        {"comment": "AI 会话表"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="会话ID")
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        comment="用户ID",
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="", comment="会话标题")
    model: Mapped[str] = mapped_column(String(64), nullable=False, default="", comment="模型")
    messages: Mapped[list] = mapped_column(JSON, nullable=False, comment="消息数组")
    created_at: Mapped[datetime] = mapped_column(
        # 与 DDL 一致：使用 server_default
        ...,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        ...,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        nullable=False,
        comment="更新时间",
    )

    def __repr__(self):
        return f"<AiChatSession(id={self.id}, user_id={self.user_id}, title={self.title[:20]})>"
```

> 注意：如果项目没有 `JSON` 列类型（部分 MySQL 旧版），可改为 `Text` 字段手工 `json.dumps/loads`，但 MySQL 5.7+ 均支持 JSON。检查项目实际用法（参考 `models/users.py` 是否使用过 JSON）。

**验证方式**：IDE 无 Python 语法报错；`from models.ai_chat_session import AiChatSession` 可成功导入（用 IDE 跳转确认）。

**完成标准**：模型定义完整，可被 ORM 注册。

---

### 任务 3：新建 Pydantic Schema `schemas/ai_chat.py`

**涉及文件**：`toutiao_back_end\schemas\ai_chat.py`（新建）

**实施步骤**：

```python
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ChatMessage(BaseModel):
    """单条消息（与千问 ChatMessage 兼容）"""
    role: str = Field(..., description="system | user | assistant")
    content: str = Field(..., description="消息内容")


class SessionCreateRequest(BaseModel):
    """创建会话请求体"""
    model: str = Field(..., min_length=1, max_length=64)
    messages: list[ChatMessage] = Field(..., min_length=1)
    title: str | None = Field(default=None, max_length=255)


class SessionUpdateRequest(BaseModel):
    """更新会话请求体（覆盖式）"""
    model: str = Field(..., min_length=1, max_length=64)
    messages: list[ChatMessage] = Field(..., min_length=1)
    title: str | None = Field(default=None, max_length=255)


class SessionDetailResponse(BaseModel):
    """会话详情"""
    id: int
    title: str
    model: str
    messages: list[ChatMessage]
    createdAt: datetime = Field(..., alias="created_at")
    updatedAt: datetime = Field(..., alias="updated_at")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class SessionListItemResponse(BaseModel):
    """列表项（不含 messages，减少 payload）"""
    id: int
    title: str
    model: str
    updatedAt: datetime = Field(..., alias="updated_at")
    messageCount: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class SessionListResponse(BaseModel):
    list: list[SessionListItemResponse]
    total: int
    hasMore: bool = Field(..., alias="has_more")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class SessionSearchItemResponse(BaseModel):
    """搜索结果项（极简）"""
    id: int
    title: str
    updatedAt: datetime = Field(..., alias="updated_at")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class SessionSearchResponse(BaseModel):
    list: list[SessionSearchItemResponse]
    total: int
```

**验证方式**：IDE 无报错；导入语句 `from schemas.ai_chat import SessionCreateRequest` 正常。

**完成标准**：所有 schema 类型定义完整、字段命名与前端契约对齐。

---

### 任务 4：新建 CRUD `crud/ai_chat.py`

**涉及文件**：`toutiao_back_end\crud\ai_chat.py`（新建）

**实施步骤**：

```python
from datetime import datetime
from sqlalchemy import select, func, delete, or_
from sqlalchemy.ext.asyncio.session import AsyncSession

from models.users import User
from models.ai_chat_session import AiChatSession


SEARCH_LIMIT = 5  # 搜索结果硬上限


def _gen_title(messages: list[dict]) -> str:
    """从 messages 列表提取首条 user 消息的前 30 字符作为标题"""
    for m in messages:
        if m.get("role") == "user":
            content = (m.get("content") or "").strip().replace("\n", " ")
            return content[:30]
    return ""


async def create_session(db: AsyncSession, user: User, payload) -> AiChatSession:
    """创建会话；title 缺省时自动从 messages 生成"""
    messages = [m.model_dump() for m in payload.messages]
    title = (payload.title or "").strip() or _gen_title(messages)
    row = AiChatSession(
        user_id=user.id,
        title=title,
        model=payload.model,
        messages=messages,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def update_session(db: AsyncSession, user: User, session_id: int, payload) -> AiChatSession | None:
    """全量覆盖更新会话；不存在或非当前用户返回 None"""
    stmt = select(AiChatSession).where(
        AiChatSession.id == session_id,
        AiChatSession.user_id == user.id,
    )
    row = (await db.execute(stmt)).scalar_one_or_none()
    if not row:
        return None
    messages = [m.model_dump() for m in payload.messages]
    row.messages = messages
    row.model = payload.model
    if payload.title is not None and payload.title.strip():
        row.title = payload.title.strip()
    await db.commit()
    await db.refresh(row)
    return row


async def get_session(db: AsyncSession, user: User, session_id: int) -> AiChatSession | None:
    stmt = select(AiChatSession).where(
        AiChatSession.id == session_id,
        AiChatSession.user_id == user.id,
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def get_session_list(db: AsyncSession, user: User, page: int, page_size: int):
    """分页获取当前用户的会话列表（按 updated_at desc）"""
    offset = (page - 1) * page_size

    total_stmt = select(func.count()).where(AiChatSession.user_id == user.id)
    total = (await db.execute(total_stmt)).scalar_one()

    list_stmt = (
        select(AiChatSession)
        .where(AiChatSession.user_id == user.id)
        .order_by(AiChatSession.updated_at.desc())
        .limit(page_size)
        .offset(offset)
    )
    rows = (await db.execute(list_stmt)).scalars().all()
    return rows, total


async def search_sessions(db: AsyncSession, user: User, keyword: str, limit: int = SEARCH_LIMIT):
    """
    搜索 title 或 messages 内容；返回最多 limit 条（默认 5）。
    - keyword 为空时返回空列表（搜索接口语义）
    - title LIKE 和 JSON 文本 LIKE 任一命中即可
    """
    keyword = keyword.strip()
    if not keyword:
        return [], 0
    like = f"%{keyword}%"

    # JSON 字段转字符串后 LIKE
    total_stmt = select(func.count()).where(
        AiChatSession.user_id == user.id,
        or_(
            AiChatSession.title.like(like),
            func.cast(AiChatSession.messages, __import__("sqlalchemy").Text).like(like),
        ),
    )
    total = (await db.execute(total_stmt)).scalar_one()

    list_stmt = (
        select(AiChatSession)
        .where(
            AiChatSession.user_id == user.id,
            or_(
                AiChatSession.title.like(like),
                func.cast(AiChatSession.messages, __import__("sqlalchemy").Text).like(like),
            ),
        )
        .order_by(AiChatSession.updated_at.desc())
        .limit(min(limit, SEARCH_LIMIT))
    )
    rows = (await db.execute(list_stmt)).scalars().all()
    return rows, total


async def delete_session(db: AsyncSession, user: User, session_id: int) -> int:
    stmt = delete(AiChatSession).where(
        AiChatSession.id == session_id,
        AiChatSession.user_id == user.id,
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0
```

> 备注：`func.cast(messages, Text)` 需要 `from sqlalchemy import Text`；上面使用了 `__import__` 避免顶部多 import（避免误导）。实际写法建议改为顶部 `from sqlalchemy import Text` 然后 `func.cast(AiChatSession.messages, Text).like(like)`。

**验证方式**：IDE 无报错；`from crud import ai_chat` 可导入。

**完成标准**：CRUD 函数全部覆盖 6 个接口所需的数据操作。

---

### 任务 5：新建路由 `routers/ai_chat.py`

**涉及文件**：`toutiao_back_end\routers\ai_chat.py`（新建）

**实施步骤**：

```python
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession

from config.db_conf import get_db
from crud import ai_chat
from models.users import User
from schemas.ai_chat import (
    SessionCreateRequest,
    SessionUpdateRequest,
    SessionDetailResponse,
    SessionListItemResponse,
    SessionListResponse,
    SessionSearchItemResponse,
    SessionSearchResponse,
)
from utils.auth import get_current_user
from utils.response import success_response


router = APIRouter(
    prefix="/api/ai-chat",
    tags=["ai-chat"],
)


@router.post("/sessions")
async def create_session(
    data: SessionCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = await ai_chat.create_session(db, user, data)
    return success_response(
        message="创建会话成功",
        data=SessionDetailResponse.model_validate(row),
    )


@router.put("/sessions/{session_id}")
async def update_session(
    session_id: int,
    data: SessionUpdateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = await ai_chat.update_session(db, user, session_id, data)
    if not row:
        raise HTTPException(status_code=404, detail="会话不存在")
    return success_response(
        message="更新会话成功",
        data=SessionDetailResponse.model_validate(row),
    )


@router.get("/sessions")
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
):
    rows, total = await ai_chat.get_session_list(db, user, page, pageSize)
    items = [
        SessionListItemResponse.model_validate({
            "id": r.id,
            "title": r.title,
            "model": r.model,
            "updated_at": r.updated_at,
            "messageCount": len(r.messages or []),
        })
        for r in rows
    ]
    has_more = total > pageSize * page
    return success_response(
        message="获取会话列表成功",
        data=SessionListResponse(list=items, total=total, has_more=has_more),
    )


@router.get("/sessions/search")
async def search_sessions(
    keyword: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows, total = await ai_chat.search_sessions(db, user, keyword, limit=5)
    items = [SessionSearchItemResponse.model_validate({
        "id": r.id,
        "title": r.title,
        "updated_at": r.updated_at,
    }) for r in rows]
    return success_response(
        message="搜索会话成功",
        data=SessionSearchResponse(list=items, total=total),
    )


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = await ai_chat.get_session(db, user, session_id)
    if not row:
        raise HTTPException(status_code=404, detail="会话不存在")
    return success_response(
        message="获取会话详情成功",
        data=SessionDetailResponse.model_validate(row),
    )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    count = await ai_chat.delete_session(db, user, session_id)
    if count == 0:
        raise HTTPException(status_code=404, detail="会话不存在")
    return success_response(message=f"删除会话成功，共 {count} 条")
```

**验证方式**：IDE 无报错；`from routers.ai_chat import router` 可导入。

**完成标准**：6 个接口（POST/PUT/GET-list/GET-search/GET-detail/DELETE）全部就绪。

---

### 任务 6：注册路由 `main.py`

**涉及文件**：`toutiao_back_end\main.py`

**实施步骤**：

1. 在 `from routers import ...` 行加入 `ai_chat`：
   ```python
   from routers import news, users, favorite, history, search_history, ai_chat
   ```
2. 在 `app.include_router(...)` 区块加入：
   ```python
   app.include_router(ai_chat.router)
   ```

**验证方式**：保存后 IDE 无报错；启动后端 `uvicorn main:app --reload`，浏览器访问 `http://127.0.0.1:10001/docs` 应能看到 `ai-chat` tag 下 6 个接口。

**完成标准**：路由注册成功，FastAPI 自动生成的 `/docs` 页面展示新接口。

---

### 任务 7：更新 API 接口规范文档

**涉及文件**：`toutiao_back_end\物料文件\API接口规范文档.md`

**实施步骤**：

在文档末尾追加"### AI 问答会话模块"章节，按现有章节格式（接口地址 / 请求头 / 请求参数表 / 请求示例 / 响应示例 / 业务规则）逐个写：

1. 创建会话（`POST /api/ai-chat/sessions`）
2. 更新会话（`PUT /api/ai-chat/sessions/{session_id}`）
3. 获取会话列表（`GET /api/ai-chat/sessions`）
4. 搜索会话（`GET /api/ai-chat/sessions/search`）
5. 获取会话详情（`GET /api/ai-chat/sessions/{session_id}`）
6. 删除会话（`DELETE /api/ai-chat/sessions/{session_id}`）

参考文档中已有"收藏模块"和"浏览历史模块"章节的格式。响应示例参考 Spec 中的出参定义。

**验证方式**：文档格式与前面章节一致；6 个接口都覆盖；每个接口都有响应示例和必要参数表。

**完成标准**：6 个新接口的文档完整、可被前端开发直接对照实现。

---

### 任务 8：新建 REST 封装 `src/api/aiChat.ts`

**涉及文件**：`toutiao_front_end\src\api\aiChat.ts`（新建）

**实施步骤**：

```ts
import request from '@/utils/request'

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
}

export interface SessionDetail {
  id: number
  title: string
  model: string
  messages: ChatMessage[]
  createdAt: string
  updatedAt: string
}

export interface SessionListItem {
  id: number
  title: string
  model: string
  updatedAt: string
  messageCount: number
}

export interface SessionListPayload {
  list: SessionListItem[]
  total: number
  hasMore: boolean
}

export interface SessionSearchItem {
  id: number
  title: string
  updatedAt: string
}

export interface SessionSearchPayload {
  list: SessionSearchItem[]
  total: number
}

/**
 * 创建会话（首条 AI 回复成功后调用）
 */
export const createSession = (payload: {
  model: string
  messages: ChatMessage[]
  title?: string
}) => request.post<unknown, { data: SessionDetail }>('/api/ai-chat/sessions', payload)

/**
 * 更新会话（后续每轮 AI 回复成功后调用）
 */
export const updateSession = (
  sessionId: number,
  payload: { model: string; messages: ChatMessage[]; title?: string }
) => request.put<unknown, { data: SessionDetail }>(`/api/ai-chat/sessions/${sessionId}`, payload)

/**
 * 获取会话列表（分页，按 updated_at desc）
 */
export const getSessionList = (params: { page?: number; pageSize?: number }) =>
  request.get<unknown, { data: SessionListPayload }>('/api/ai-chat/sessions', { params })

/**
 * 搜索会话（title + messages，最多 5 条）
 */
export const searchSessions = (keyword: string) =>
  request.get<unknown, { data: SessionSearchPayload }>('/api/ai-chat/sessions/search', {
    params: { keyword }
  })

/**
 * 获取会话详情（含完整 messages）
 */
export const getSessionDetail = (sessionId: number) =>
  request.get<unknown, { data: SessionDetail }>(`/api/ai-chat/sessions/${sessionId}`)

/**
 * 删除会话
 */
export const deleteSession = (sessionId: number) =>
  request.delete<unknown, { data: { deletedCount: number } }>(`/api/ai-chat/sessions/${sessionId}`)
```

> 备注：`request` 默认拦截器会解包 `data` 字段，所以方法返回类型可以是 `{ data: T }`，但前端调用时可以直接拿到 `data`。具体使用方式参考 `src/api/favorite.ts` 的写法。

**验证方式**：IDE 无 TypeScript 报错；导入路径 `@/utils/request` 正确。

**完成标准**：6 个 REST 方法封装完成。

---

### 任务 9：新建 Pinia Store `src/pinia/aiChatStore.ts`

**涉及文件**：`toutiao_front_end\src\pinia\aiChatStore.ts`（新建）

**实施步骤**：

```ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { chat, type ChatMessage as QwenMessage } from '@/api/ai'
import {
  createSession,
  updateSession,
  getSessionList,
  searchSessions,
  getSessionDetail,
  deleteSession as deleteSessionApi,
  type SessionListItem,
  type SessionSearchItem,
  type ChatMessage,
} from '@/api/aiChat'

/** 千问 system prompt（与现有 AiChat.vue 保持一致） */
const SYSTEM_PROMPT = '你是头条新闻 App 的智能助手，回答简洁友好，必要时可结合新闻领域知识给出建议。'

/** 前端展示用的消息类型 */
interface UiMessage {
  type: 'user' | 'ai'
  content: string
}

export const useAiChatStore = defineStore('aiChat', () => {
  // ============ 状态 ============
  const messages = ref<UiMessage[]>([])
  const currentSessionId = ref<number | null>(null)
  const isTyping = ref(false)
  const drawerOpen = ref(false)
  const searchKeyword = ref('')
  const sessionList = ref<SessionListItem[]>([])
  const searchResults = ref<SessionSearchItem[]>([])
  const sessionListLoading = ref(false)
  const sessionListPage = ref(1)
  const sessionListHasMore = ref(false)

  // ============ 工具方法 ============
  /**
   * 从 messages 数组生成 title（首条 user 消息前 30 字）
   */
  const genTitle = (msgs: UiMessage[]): string => {
    for (const m of msgs) {
      if (m.type === 'user') {
        return m.content.replace(/\n/g, ' ').trim().slice(0, 30)
      }
    }
    return ''
  }

  /**
   * UI 消息 → 千问 ChatMessage
   */
  const toQwenMessages = (msgs: UiMessage[]): QwenMessage[] => {
    const history = msgs.map((m) => ({
      role: m.type === 'user' ? 'user' : 'assistant',
      content: m.content,
    }))
    return [{ role: 'system', content: SYSTEM_PROMPT }, ...history]
  }

  /**
   * 千问 ChatMessage → UI 消息（仅 user/assistant）
   */
  const toUiMessages = (msgs: ChatMessage[]): UiMessage[] =>
    msgs
      .filter((m) => m.role === 'user' || m.role === 'assistant')
      .map((m) => ({ type: m.role === 'user' ? 'user' : 'ai', content: m.content }))

  // ============ Action ============
  /**
   * 发送消息：调用千问 → 成功后将完整 messages 落库（POST/PUT）
   */
  const send = async (text: string) => {
    if (isTyping.value) return
    const trimmed = text.trim()
    if (!trimmed) return
    messages.value.push({ type: 'user', content: trimmed })
    isTyping.value = true
    try {
      const reply = await chat(toQwenMessages(messages.value))
      messages.value.push({ type: 'ai', content: reply })

      // 落库
      const payload = {
        model: 'qwen3-max',
        messages: toQwenMessages(messages.value).slice(1), // 去掉 system
      }
      try {
        if (currentSessionId.value === null) {
          const res = await createSession({ ...payload, title: genTitle(messages.value) })
          currentSessionId.value = res.data.id
        } else {
          await updateSession(currentSessionId.value, {
            ...payload,
            title: genTitle(messages.value),
          })
        }
      } catch (e) {
        console.warn('AI 会话落库失败', e)
        // 不弹错，避免影响聊天；下次发送仍会重试
      }
    } catch (err: any) {
      ElMessage.error(err?.message || '千问调用失败，请稍后重试')
    } finally {
      isTyping.value = false
    }
  }

  /**
   * 新会话：清空 messages 与 currentSessionId
   */
  const newChat = () => {
    messages.value = []
    currentSessionId.value = null
    searchKeyword.value = ''
  }

  /**
   * 加载历史会话详情
   */
  const loadSession = async (sessionId: number) => {
    try {
      const res = await getSessionDetail(sessionId)
      messages.value = toUiMessages(res.data.messages)
      currentSessionId.value = res.data.id
      drawerOpen.value = false
    } catch (e) {
      ElMessage.error('加载会话失败')
    }
  }

  /**
   * 删除会话
   */
  const removeSession = async (sessionId: number) => {
    try {
      await deleteSessionApi(sessionId)
      sessionList.value = sessionList.value.filter((s) => s.id !== sessionId)
      searchResults.value = searchResults.value.filter((s) => s.id !== sessionId)
      if (currentSessionId.value === sessionId) {
        newChat()
      }
    } catch (e) {
      ElMessage.error('删除失败')
    }
  }

  /**
   * 抽屉开关
   */
  const toggleDrawer = () => {
    drawerOpen.value = !drawerOpen.value
  }
  const closeDrawer = () => {
    drawerOpen.value = false
  }

  /**
   * 拉取会话列表（分页）
   */
  const fetchSessionList = async (reset = false) => {
    if (reset) {
      sessionListPage.value = 1
      sessionList.value = []
    }
    sessionListLoading.value = true
    try {
      const res = await getSessionList({ page: sessionListPage.value, pageSize: 10 })
      const payload = res.data
      sessionList.value = reset ? payload.list : [...sessionList.value, ...payload.list]
      sessionListHasMore.value = payload.hasMore
      sessionListPage.value++
    } catch (e) {
      ElMessage.error('获取会话列表失败')
    } finally {
      sessionListLoading.value = false
    }
  }

  /**
   * 搜索会话（最多 5 条）
   */
  const searchSession = async (keyword: string) => {
    searchKeyword.value = keyword
    if (!keyword.trim()) {
      searchResults.value = []
      return
    }
    try {
      const res = await searchSessions(keyword.trim())
      searchResults.value = res.data.list
    } catch (e) {
      ElMessage.error('搜索失败')
    }
  }

  return {
    messages,
    currentSessionId,
    isTyping,
    drawerOpen,
    searchKeyword,
    sessionList,
    searchResults,
    sessionListLoading,
    sessionListHasMore,
    send,
    newChat,
    loadSession,
    removeSession,
    toggleDrawer,
    closeDrawer,
    fetchSessionList,
    searchSession,
  }
})
```

**验证方式**：IDE 无 TypeScript 报错；`useAiChatStore` 可在 Vue 组件内 `import` 使用。

**完成标准**：所有状态和 action 都暴露；导入 `@/api/ai` 的 `chat` 与 `@/api/aiChat` 的 6 个方法都能正确解析。

---

### 任务 10：重构 `AiChat.vue`

**涉及文件**：`toutiao_front_end\src\pages\ai\AiChat.vue`（重写）

**实施步骤**：

完整重写为如下结构（保留 markdown 渲染逻辑、消息气泡样式、SCSS 主题色）：

```vue
<template>
  <div class="ai-chat-page">
    <!-- 顶部 -->
    <div class="header">
      <el-icon class="header-icon" @click="store.toggleDrawer">
        <component :is="store.drawerOpen ? Close : Memo" />
      </el-icon>
      <h1 class="title">AI 问答助手</h1>
    </div>

    <!-- 对话列表 -->
    <div class="chat-container" ref="chatContainer">
      <div v-if="store.messages.length === 0" class="empty-chat">
        <el-icon :size="48"><ChatDotSquare /></el-icon>
        <p>有什么问题可以问我哦~</p>
      </div>
      <div
        v-for="(msg, index) in store.messages"
        :key="index"
        :class="['message', msg.type]"
      >
        <div class="message-avatar">
          <el-icon :size="24">
            <component :is="msg.type === 'user' ? 'User' : 'MagicStick'" />
          </el-icon>
        </div>
        <div class="message-content">
          <div
            v-if="msg.type === 'ai'"
            class="message-bubble markdown-body"
            v-html="renderMd(msg.content)"
          ></div>
          <div v-else class="message-bubble">{{ msg.content }}</div>
        </div>
      </div>
      <div v-if="store.isTyping" class="message ai">
        <div class="message-avatar">
          <el-icon :size="24"><MagicStick /></el-icon>
        </div>
        <div class="message-content">
          <div class="message-bubble typing">
            <span>思考中</span>
            <el-icon class="is-loading"><Loading /></el-icon>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区 -->
    <div class="input-area">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="2"
        placeholder="输入您的问题...（Enter 发送，Shift+Enter 换行）"
        resize="none"
        @keydown.enter.exact="handleEnterKey"
      />
      <el-button
        type="primary"
        :disabled="!inputText.trim() || store.isTyping"
        @click="handleSend"
      >发送</el-button>
      <el-button
        circle
        :disabled="store.isTyping"
        @click="handleNewChat"
        class="new-chat-btn"
      >
        <el-icon><Plus /></el-icon>
      </el-button>
    </div>

    <!-- 抽屉 -->
    <el-drawer
      v-model="store.drawerOpen"
      direction="ltr"
      size="80%"
      :with-header="false"
      :modal="true"
    >
      <div class="drawer-content">
        <div class="drawer-header">
          <h2 class="drawer-title">历史会话</h2>
          <el-input
            v-model="searchInput"
            placeholder="搜索 title 或内容"
            clearable
            @input="handleSearchInput"
            @clear="handleSearchClear"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <div class="drawer-list" v-loading="store.sessionListLoading">
          <!-- 搜索模式 -->
          <template v-if="store.searchKeyword">
            <div
              v-for="item in store.searchResults"
              :key="item.id"
              class="drawer-item"
              @click="handleSelect(item.id)"
            >
              <el-icon class="drawer-item-icon"><ChatDotRound /></el-icon>
              <div class="drawer-item-body">
                <div class="drawer-item-title">{{ item.title || '新会话' }}</div>
                <div class="drawer-item-time">{{ formatTime(item.updatedAt) }}</div>
              </div>
              <el-button
                text
                type="danger"
                size="small"
                @click.stop="handleDelete(item.id)"
              >删除</el-button>
            </div>
            <div v-if="store.searchResults.length === 0" class="empty-state">
              <p>没有匹配结果</p>
            </div>
          </template>

          <!-- 普通列表 -->
          <template v-else>
            <div
              v-for="item in store.sessionList"
              :key="item.id"
              class="drawer-item"
              @click="handleSelect(item.id)"
            >
              <el-icon class="drawer-item-icon"><ChatDotRound /></el-icon>
              <div class="drawer-item-body">
                <div class="drawer-item-title">{{ item.title || '新会话' }}</div>
                <div class="drawer-item-time">
                  {{ formatTime(item.updatedAt) }} · {{ item.messageCount }} 条消息
                </div>
              </div>
              <el-button
                text
                type="danger"
                size="small"
                @click.stop="handleDelete(item.id)"
              >删除</el-button>
            </div>
            <div v-if="store.sessionList.length === 0 && !store.sessionListLoading" class="empty-state">
              <p>暂无历史会话</p>
            </div>
          </template>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ChatDotSquare,
  ChatDotRound,
  User,
  MagicStick,
  Loading,
  Memo,
  Close,
  Plus,
  Search,
} from '@element-plus/icons-vue'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'
import { useAiChatStore } from '@/pinia/aiChatStore'

const store = useAiChatStore()

const md = new MarkdownIt({ html: false, linkify: true, breaks: true })
const renderMd = (text: string) => {
  if (!text) return ''
  return DOMPurify.sanitize(md.render(text))
}

const inputText = ref('')
const searchInput = ref('')
const chatContainer = ref<HTMLElement | null>(null)

const handleEnterKey = (e: KeyboardEvent) => {
  if (e.shiftKey || e.isComposing || e.keyCode === 229) return
  if (store.isTyping) return
  e.preventDefault()
  handleSend()
}

const handleSend = async () => {
  const text = inputText.value.trim()
  if (!text || store.isTyping) return
  inputText.value = ''
  await store.send(text)
  await nextTick()
  scrollToBottom()
}

const handleNewChat = () => {
  store.newChat()
  inputText.value = ''
}

const handleSelect = async (sessionId: number) => {
  await store.loadSession(sessionId)
}

const handleDelete = async (sessionId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这条对话吗？', '提示', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await store.removeSession(sessionId)
    ElMessage.success('已删除')
  } catch {
    // 用户取消
  }
}

// 抽屉打开时拉取列表
watch(
  () => store.drawerOpen,
  (open) => {
    if (open && store.sessionList.length === 0) {
      store.fetchSessionList(true)
    }
  }
)

// 搜索框防抖
let searchTimer: number | null = null
const handleSearchInput = (val: string) => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = window.setTimeout(() => {
    store.searchSession(val)
  }, 300)
}
const handleSearchClear = () => {
  store.searchSession('')
}

const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

// 抽屉打开后默认滚动到底
watch(
  () => store.messages.length,
  async () => {
    await nextTick()
    scrollToBottom()
  }
)

// 时间格式化（刚刚 / X 分钟前 / 昨天 / YYYY-MM-DD）
const formatTime = (iso: string): string => {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return ''
  const now = Date.now()
  const diff = Math.floor((now - date.getTime()) / 1000)
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
  if (diff < 86400) return '昨天'
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}
</script>

<style lang="scss" scoped>
.ai-chat-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f5f5f5;

  .header {
    background: #fff;
    padding: 12px 15px;
    border-bottom: 1px solid #e8e8e8;
    display: flex;
    align-items: center;
    gap: 10px;

    .header-icon {
      font-size: 20px;
      color: #666;
      cursor: pointer;
    }

    .title {
      font-size: 1rem;
      font-weight: 600;
      color: #333;
      flex: 1;
    }
  }

  .chat-container {
    flex: 1;
    overflow-y: auto;
    padding: 15px;

    .empty-chat {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: #999;

      .el-icon {
        margin-bottom: 15px;
      }
    }

    .message {
      display: flex;
      margin-bottom: 15px;

      &.user {
        flex-direction: row-reverse;

        .message-content {
          margin-right: 0;
          margin-left: 10px;
        }

        .message-bubble {
          background: #e63946;
          color: #fff;
          border-radius: 18px 18px 0 18px;
        }
      }

      &.ai {
        .message-bubble {
          background: #fff;
          color: #333;
          border-radius: 18px 18px 18px 0;
        }

        .message-bubble.markdown-body {
          :deep(p) { margin: 0 0 8px; &:last-child { margin-bottom: 0; } }
          :deep(h1), :deep(h2), :deep(h3) {
            font-size: 1rem;
            font-weight: 600;
            margin: 10px 0 6px;
            line-height: 1.4;
          }
          :deep(ul), :deep(ol) { margin: 6px 0; padding-left: 20px; }
          :deep(li) { margin: 2px 0; }
          :deep(code) {
            background: #f3f3f3;
            color: #e63946;
            padding: 1px 5px;
            border-radius: 3px;
            font-size: 0.85em;
          }
          :deep(pre) {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 10px 12px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 8px 0;
            code { background: transparent; color: inherit; padding: 0; }
          }
          :deep(blockquote) {
            margin: 8px 0;
            padding: 4px 10px;
            border-left: 3px solid #e63946;
            background: #f9f9f9;
            color: #666;
          }
          :deep(strong) { font-weight: 600; color: #222; }
          :deep(a) { color: #e63946; text-decoration: underline; }
        }
      }

      .message-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        background: #f0f0f0;

        .el-icon { color: #999; }
      }

      .message-content {
        max-width: 70%;

        .message-bubble {
          padding: 10px 15px;
          line-height: 1.5;
          font-size: 0.9375rem;

          &.typing {
            display: flex;
            align-items: center;
            gap: 5px;

            span { font-size: 0.75rem; }
          }
        }
      }
    }
  }

  .input-area {
    background: #fff;
    padding: 10px 15px;
    padding-bottom: calc(10px + env(safe-area-inset-bottom));
    display: flex;
    gap: 10px;
    align-items: flex-end;

    .el-input { flex: 1; }

    .el-button { flex-shrink: 0; }

    .new-chat-btn {
      background: #f5f5f5;
      border-color: #e8e8e8;
      color: #666;

      &:hover {
        background: #e63946;
        color: #fff;
        border-color: #e63946;
      }
    }
  }
}

// 抽屉内容样式
.drawer-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #fff;

  .drawer-header {
    padding: 15px;
    border-bottom: 1px solid #f0f0f0;
    flex-shrink: 0;

    .drawer-title {
      font-size: 1rem;
      font-weight: 600;
      color: #333;
      margin: 0 0 10px;
    }
  }

  .drawer-list {
    flex: 1;
    overflow-y: auto;

    .drawer-item {
      display: flex;
      align-items: center;
      padding: 12px 15px;
      border-bottom: 1px solid #f5f5f5;
      cursor: pointer;
      gap: 10px;

      &:active {
        background: #f9f9f9;
      }

      .drawer-item-icon {
        font-size: 18px;
        color: #e63946;
        flex-shrink: 0;
      }

      .drawer-item-body {
        flex: 1;
        min-width: 0;

        .drawer-item-title {
          font-size: 0.9375rem;
          color: #333;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .drawer-item-time {
          font-size: 0.75rem;
          color: #999;
          margin-top: 2px;
        }
      }
    }

    .empty-state {
      padding: 60px 20px;
      text-align: center;
      color: #999;
    }
  }
}
</style>
```

**验证方式**：IDE 无模板/脚本/样式报错。

**完成标准**：组件可挂载运行；抽屉 / 列表 / 删除 / 搜索 / +按钮 全部按设计运行。

---

### 任务 11：路由加 `requiresAuth`

**涉及文件**：`toutiao_front_end\src\router\index.ts`

**实施步骤**：

将 `/ai-chat` 路由的 `meta` 加 `requiresAuth: true`：

```ts
{
  path: '/ai-chat',
  name: 'AiChat',
  component: AiChat,
  meta: { title: 'AI问答', requiresAuth: true }
}
```

**验证方式**：未登录访问 `/ai-chat` → 被守卫跳到 `/login`。

**完成标准**：未登录态不可用，符合 Spec 验收标准 1。

---

### 任务 12：浏览器端到端验证

**涉及文件**：无（仅运行时验证）

**实施步骤**：

1. **后端**：`cd toutiao_back_end && python main.py`，确认 `http://127.0.0.1:10001/docs` 出现 `ai-chat` 6 个接口。
2. **执行 DDL**：在 MySQL 中执行 `database.sql` 的新增段（或使用项目既有 migrate 流程）。
3. **前端**：`cd toutiao_front_end && npm run dev`，浏览器登录后进入 `/ai-chat`。
4. 按 Spec 验收标准逐条验证：
   - 1: 未登录跳登录页
   - 2: 发消息等 AI 回 → Network 看到 POST `/api/ai-chat/sessions`
   - 3: 继续发第二条 → PUT
   - 4: 切首页再切回 → messages 仍在
   - 5: 点 Memo 图标 → 抽屉滑入 + 展示历史
   - 6: 搜索"红烧" → ≤5 条匹配
   - 7: 清空搜索 → 列表恢复 + 分页
   - 8: 点列表项 → 加载 + 可继续问
   - 9: 点删除 → 二次确认 → 列表移除
   - 10: 点 + → 清空 + 可开始新会话
   - 11: 点遮罩 → 抽屉关闭
   - 12: 抽屉打开时点 Close 图标 → 关闭
   - 13: AI 失败 → toast 提示，pinia 保留已发消息

**验证方式**：DevTools Network + 肉眼操作。

**完成标准**：Spec 验收标准 1~13 全部通过。

---

## 自检清单

- [x] Spec 的每条要求都有对应任务（任务 1-12 覆盖 DDL、model、schema、crud、router、文档、API 封装、store、UI 重构、路由、验证）
- [x] 无 `TODO` / `TBD` / "后续实现" / "参考上一个任务"
- [x] 函数名 / 接口名 / 状态名 前后一致：`send / newChat / loadSession / removeSession / toggleDrawer / fetchSessionList / searchSession`
- [x] 包含验证步骤（任务 12）
- [x] 所有 CRUD 都有对应的 router 路由
- [x] API 文档更新已纳入（任务 7）

## 后续出口

- 执行阶段：`executing-plans` 或 `subagent-driven-development`
- 执行完成后：`requesting-code-review` → `verification-before-completion` → `finishing-a-development-branch`