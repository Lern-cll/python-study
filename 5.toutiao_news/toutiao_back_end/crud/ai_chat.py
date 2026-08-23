import json
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio.session import AsyncSession

from models.users import User
from models.ai_chat import AiChat


# 搜索结果硬上限
SEARCH_LIMIT = 5


def _gen_title(messages: list) -> str:
    """从 messages 列表中提取首条 user 消息作为标题（前 30 字符，去换行）"""
    for m in messages or []:
        if isinstance(m, dict) and m.get("role") == "user":
            content = (m.get("content") or "").strip().replace("\n", " ")
            return content[:30]
    return ""


def _extract_last_response(messages: list) -> str:
    """从 messages 列表中提取最后一条 assistant 回复"""
    for m in reversed(messages or []):
        if isinstance(m, dict) and m.get("role") == "assistant":
            return m.get("content") or ""
    return ""


async def create_session(db: AsyncSession, user: User, payload) -> AiChat:
    """
    创建会话；
    - title 缺省时自动从首条 user 消息生成（持久化时塞入 messages 首条）
    - message 字段存 messages 数组的 JSON
    - response 字段存最后一条 assistant 回复
    """
    messages = [m.model_dump() for m in payload.messages]

    # 如果前端显式给了 title 且非空，就把首条 user 消息的内容替换为 title（便于后续派生保持一致）
    explicit_title = (payload.title or "").strip()
    if explicit_title:
        replaced = False
        for m in messages:
            if m.get("role") == "user":
                m["content"] = explicit_title
                replaced = True
                break
        if not replaced:
            messages.insert(0, {"role": "user", "content": explicit_title})

    row = AiChat(
        user_id=user.id,
        message=json.dumps(messages, ensure_ascii=False),
        response=_extract_last_response(messages),
        # model / updated_at 不持久化；created_at 由 DB 默认值填充
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def update_session(db: AsyncSession, user: User, session_id: int, payload):
    """
    全量覆盖更新会话；找不到记录或非当前用户返回 None。
    """
    stmt = select(AiChat).where(
        AiChat.id == session_id,
        AiChat.user_id == user.id,
    )
    row = (await db.execute(stmt)).scalar_one_or_none()
    if not row:
        return None
    messages = [m.model_dump() for m in payload.messages]

    explicit_title = (payload.title or "").strip()
    if explicit_title:
        replaced = False
        for m in messages:
            if m.get("role") == "user":
                m["content"] = explicit_title
                replaced = True
                break
        if not replaced:
            messages.insert(0, {"role": "user", "content": explicit_title})

    row.message = json.dumps(messages, ensure_ascii=False)
    row.response = _extract_last_response(messages)
    # model 字段不持久化；title 来自 messages，由 ORM 属性派生
    await db.commit()
    await db.refresh(row)
    return row


async def get_session(db: AsyncSession, user: User, session_id: int):
    """按 id + user 查一条会话；不存在返回 None"""
    stmt = select(AiChat).where(
        AiChat.id == session_id,
        AiChat.user_id == user.id,
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def get_session_list(db: AsyncSession, user: User, page: int, page_size: int):
    """
    分页获取当前用户的会话列表，按 created_at 倒序。
    返回 (rows, total)
    """
    offset = (page - 1) * page_size

    total_stmt = select(func.count()).where(AiChat.user_id == user.id)
    total = (await db.execute(total_stmt)).scalar_one()

    list_stmt = (
        select(AiChat)
        .where(AiChat.user_id == user.id)
        .order_by(AiChat.created_at.desc())
        .limit(page_size)
        .offset(offset)
    )
    rows = (await db.execute(list_stmt)).scalars().all()
    return list(rows), total


async def search_sessions(
    db: AsyncSession, user: User, keyword: str, limit: int = SEARCH_LIMIT
):
    """
    在 message JSON 文本中搜索关键词；返回最多 limit 条（默认 5）。
    - keyword 为空时返回 ([], 0)
    - 命中规则：message 列 LIKE '%kw%'（JSON 内含首条 user 消息与全部 assistant 回复，等价于原 title/messages 搜索）
    """
    keyword = keyword.strip()
    if not keyword:
        return [], 0
    like = f"%{keyword}%"

    where_clause = (
        AiChat.user_id == user.id,
        AiChat.message.like(like),
    )

    total_stmt = select(func.count()).where(*where_clause)
    total = (await db.execute(total_stmt)).scalar_one()

    list_stmt = (
        select(AiChat)
        .where(*where_clause)
        .order_by(AiChat.created_at.desc())
        .limit(min(limit, SEARCH_LIMIT))
    )
    rows = (await db.execute(list_stmt)).scalars().all()
    return list(rows), total


async def delete_session(db: AsyncSession, user: User, session_id: int) -> int:
    """硬删除一条会话；返回受影响行数（0 表示记录不存在或非当前用户）"""
    stmt = delete(AiChat).where(
        AiChat.id == session_id,
        AiChat.user_id == user.id,
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0
