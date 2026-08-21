from datetime import datetime
from sqlalchemy import select, func, delete, or_, Text
from sqlalchemy.ext.asyncio.session import AsyncSession

from models.users import User
from models.ai_chat_session import AiChatSession


# 搜索结果硬上限
SEARCH_LIMIT = 5


def _gen_title(messages: list[dict]) -> str:
    """从 messages 列表中提取首条 user 消息作为标题（前 30 字符，去换行）"""
    for m in messages:
        if m.get("role") == "user":
            content = (m.get("content") or "").strip().replace("\n", " ")
            return content[:30]
    return ""


async def create_session(db: AsyncSession, user: User, payload) -> AiChatSession:
    """
    创建会话；title 缺省时自动从首条 user 消息生成。
    """
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


async def update_session(db: AsyncSession, user: User, session_id: int, payload):
    """
    全量覆盖更新会话；找不到记录或非当前用户返回 None。
    """
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


async def get_session(db: AsyncSession, user: User, session_id: int):
    """按 id + user 查一条会话；不存在返回 None"""
    stmt = select(AiChatSession).where(
        AiChatSession.id == session_id,
        AiChatSession.user_id == user.id,
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def get_session_list(db: AsyncSession, user: User, page: int, page_size: int):
    """
    分页获取当前用户的会话列表，按 updated_at 倒序。
    返回 (rows, total)
    """
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
    return list(rows), total


async def search_sessions(
    db: AsyncSession, user: User, keyword: str, limit: int = SEARCH_LIMIT
):
    """
    搜索 title 或 messages 内容；返回最多 limit 条（默认 5）。
    - keyword 为空时返回 ([], 0)
    - 命中规则：title LIKE '%kw%' OR JSON 字段转文本后 LIKE '%kw%'
    """
    keyword = keyword.strip()
    if not keyword:
        return [], 0
    like = f"%{keyword}%"

    where_clause = (
        AiChatSession.user_id == user.id,
        or_(
            AiChatSession.title.like(like),
            func.cast(AiChatSession.messages, Text).like(like),
        ),
    )

    total_stmt = select(func.count()).where(*where_clause)
    total = (await db.execute(total_stmt)).scalar_one()

    list_stmt = (
        select(AiChatSession)
        .where(*where_clause)
        .order_by(AiChatSession.updated_at.desc())
        .limit(min(limit, SEARCH_LIMIT))
    )
    rows = (await db.execute(list_stmt)).scalars().all()
    return list(rows), total


async def delete_session(db: AsyncSession, user: User, session_id: int) -> int:
    """硬删除一条会话；返回受影响行数（0 表示记录不存在或非当前用户）"""
    stmt = delete(AiChatSession).where(
        AiChatSession.id == session_id,
        AiChatSession.user_id == user.id,
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0