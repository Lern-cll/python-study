from datetime import datetime

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User
from models.search_history import SearchHistory


# 每个用户最多保留的搜索历史条数（超出后自动删除最早的）
HISTORY_LIMIT = 10


# 添加一条搜索历史：
# - 同用户同关键词已存在：把 search_time 更新为 now，等同于"挪到最前"
# - 否则新增一条
# - 写入后检查是否超过 HISTORY_LIMIT，超出则删除最旧的记录
async def add_search_history(db: AsyncSession, user: User, keyword: str):
    clean = keyword.strip()
    stmt = select(SearchHistory).where(
        SearchHistory.user_id == user.id,
        SearchHistory.keyword == clean,
    )
    row = (await db.execute(stmt)).scalar_one_or_none()

    if row:
        row.search_time = datetime.now()
    else:
        row = SearchHistory(user_id=user.id, keyword=clean, search_time=datetime.now())
        db.add(row)

    await db.commit()
    await db.refresh(row)

    # 兜底清理：保留最近 HISTORY_LIMIT 条
    await _trim_history(db, user.id)
    return row


# 内部辅助：删除超出上限的历史记录（仅保留 search_time 最近 N 条）
async def _trim_history(db: AsyncSession, user_id: int):
    count_stmt = select(func.count()).where(SearchHistory.user_id == user_id)
    total = (await db.execute(count_stmt)).scalar_one()
    if total <= HISTORY_LIMIT:
        return

    # 找出需要保留的 N 条 ID（search_time 最新的 N 条）
    keep_stmt = (
        select(SearchHistory.id)
        .where(SearchHistory.user_id == user_id)
        .order_by(SearchHistory.search_time.desc())
        .limit(HISTORY_LIMIT)
    )
    keep_ids = {row[0] for row in (await db.execute(keep_stmt)).all()}

    # 删除不在 keep_ids 集合里的旧记录
    delete_stmt = delete(SearchHistory).where(
        SearchHistory.user_id == user_id,
        SearchHistory.id.notin_(keep_ids),
    )
    await db.execute(delete_stmt)
    await db.commit()


# 获取当前用户的搜索历史列表（按 search_time 倒序）
async def get_search_history_list(db: AsyncSession, user: User, limit: int = HISTORY_LIMIT):
    count_stmt = select(func.count()).where(SearchHistory.user_id == user.id)
    total = (await db.execute(count_stmt)).scalar_one()

    list_stmt = (
        select(SearchHistory)
        .where(SearchHistory.user_id == user.id)
        .order_by(SearchHistory.search_time.desc())
        .limit(limit)
    )
    rows = (await db.execute(list_stmt)).scalars().all()
    return list(rows), total


# 清空当前用户的所有搜索历史
async def clear_search_history(db: AsyncSession, user: User):
    stmt = delete(SearchHistory).where(SearchHistory.user_id == user.id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0