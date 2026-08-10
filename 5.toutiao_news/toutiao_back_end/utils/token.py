from datetime import datetime
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import UserToken


async def clean_expired_tokens(db: AsyncSession) -> int:
    """
    物理删除 user_token 表中已过期的 token。
    :param db: 异步数据库会话
    :return: 被删除的记录条数
    """
    stmt = delete(UserToken).where(UserToken.expires_at < datetime.now())
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount