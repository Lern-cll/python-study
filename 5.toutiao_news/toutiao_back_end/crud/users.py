import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdateRequest
from utils.security import get_password_hash, verify_password


# 通过用户名查询信息
async def get_user_by_name( db: AsyncSession, username: str):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()

# 创建用户
# 思路： 先加密处理 - 添加到库里
async def create_user(db: AsyncSession, user_data: UserRequest ):
    password_hash = get_password_hash(user_data.password)
    user = User(username=user_data.username, password=password_hash)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

# 生成token
async def create_token (db: AsyncSession, user_id: int):
    # 生成 Token + 设置过期时间 → 查询数据库当前用户是否有 Token → 有:更新;没有:添加
    token = str(uuid.uuid4())
    # timedelta(days=7, hours=0, minutes=0, seconds=0)
    expires_at = datetime.now() + timedelta(days=7)
    query = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()

    if user_token:
        user_token.token = token
        user_token.expires_at = expires_at
        await db.commit()
    else:
        user_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)
        db.add(user_token)
        await db.commit()

    await db.refresh(user_token)
    return token

# 验证用户
async def authenticate_user(db: AsyncSession, username: str, password: str):
    user =  await get_user_by_name(db, username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None

    return user


# 根据Token 查询用户： 验证 Token -> 查询用户
async def get_user_by_token(db: AsyncSession, token: str):

    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    db_token = result.scalar_one_or_none()
    #  如果token不存在，或者token已过期，返回 None
    if not db_token or db_token.expires_at < datetime.now():
        return None
    # 通过userId 查询用户消息
    query_user = select(User).where(User.id == db_token.user_id)
    result_user = await db.execute(query_user)
    user = result_user.scalar_one_or_none()
    if not user:
        return None
    return user


# 修改用户信息
async def update_user(db: AsyncSession, username: str, update_data: UserUpdateRequest):
    user = await get_user_by_name(db, username)
    if not user:
        return None

    #update(User).where(User.username == username).values(字段=值，字段=值)
    # update_data本身是pydantic类型，得到字典 -> **解包
    # exclude_unset: 是否排除未设置的字段
    query = update(User).where(User.username == username).values(**update_data.model_dump(exclude_unset=True, exclude_none=True))
    result = await db.execute(query)
    await db.commit()  # 提交更改

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = await get_user_by_name(db, username)
    return updated_user

# 修改用户密码:  验证用户存在-验证老密码-修改密码
async def update_user_password(db: AsyncSession, username: str, password_data: UserUpdateRequest):
    user = await get_user_by_name(db, username)
    if not user:
        return None
    #
    if not verify_password(password_data.password, user.password):
        return None
    user.password = get_password_hash(password_data.password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
