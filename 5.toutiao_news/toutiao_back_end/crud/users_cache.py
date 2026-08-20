import json
import random
import uuid
from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from config.cache_conf import delete_cache, get_cache, set_cache
from models.users import User, UserToken
from schemas.users import (
    UserChangePasswordRequest,
    UserInfoResponse,
    UserRequest,
    UserUpdateRequest,
)
from utils.security import get_password_hash, verify_password


# ===================== 缓存 Key & TTL 配置 =====================
# 双 key 策略：同一个用户对象可由 username 或 id 命中
USERNAME_KEY_TPL = "user:by_username:{username}"
USER_ID_KEY_TPL = "user:by_id:{id}"

# 缓存穿透防护：DB 中不存在的用户名，缓存空标记
NULL_MARKER = "__NULL__"

# TTL（秒）
USER_CACHE_TTL_BASE = 1800      # 30 分钟（用户要求下限）
USER_CACHE_JITTER = 300         # 0~5 分钟随机抖动，规避雪崩
NULL_CACHE_TTL = 60             # 空标记 60 秒


# ===================== 内部工具 =====================
def _username_key(username: str) -> str:
    return USERNAME_KEY_TPL.format(username=username)


def _user_id_key(user_id: int) -> str:
    return USER_ID_KEY_TPL.format(id=user_id)


def _ttl_with_jitter() -> int:
    """基础 TTL + 随机抖动（防雪崩）"""
    return USER_CACHE_TTL_BASE + random.randint(0, USER_CACHE_JITTER)


def _serialize_user(user: User) -> str:
    """按 UserInfoResponse 序列化（不含 password，敏感字段不进 Redis）"""
    return UserInfoResponse.model_validate(user).model_dump_json()

# 反序列化
def _deserialize_user(raw: str) -> dict:
    return json.loads(raw)


async def _set_user_cache(user: User, ttl: Optional[int] = None) -> None:
    """双 key 写入：username 与 id 各一份，共享同一份 JSON 负载"""
    if ttl is None:
        ttl = _ttl_with_jitter()
    payload = _serialize_user(user)
    await set_cache(_username_key(user.username), payload, ttl)
    if user.id is not None:
        await set_cache(_user_id_key(user.id), payload, ttl)


async def _delete_user_cache(username: Optional[str] = None, user_id: Optional[int] = None) -> None:
    """删除指定 key（不传则都不删）"""
    if username is not None:
        await delete_cache(_username_key(username))
    if user_id is not None:
        await delete_cache(_user_id_key(user_id))


async def _set_null_cache(username: str) -> None:
    """防穿透：DB 也不存在的用户，缓存一个空标记"""
    await set_cache(_username_key(username), NULL_MARKER, NULL_CACHE_TTL)


# ===================== 对外 CRUD（Cache-Aside） =====================
# 通过用户名查询信息：缓存 → DB → 回填；NULL 走穿透防护
async def get_user_by_name(db: AsyncSession, username: str):
    cache_key = _username_key(username)

    # 1) 先读缓存
    cached = await get_cache(cache_key)
    if cached == NULL_MARKER:
        return None
    if cached:
        try:
            data = _deserialize_user(cached)
            # 返回 Pydantic 模型实例（dict-like，路由侧 .id / model_validate 都能用）
            return UserInfoResponse.model_validate(data)
        except Exception:
            # 反序列化异常视为缓存失效，继续回源 DB
            pass

    # 2) 缓存未命中，回源 DB
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        # 3) DB 也不存在：写 NULL marker 60s 防穿透
        await _set_null_cache(username)
        return None

    # 4) DB 命中：回填双 key
    await _set_user_cache(user)
    return user


# 创建用户：DB 写入后预热双 key 缓存
async def create_user(db: AsyncSession, user_data: UserRequest):
    password_hash = get_password_hash(user_data.password)
    user = User(username=user_data.username, password=password_hash)
    db.add(user)
    await db.commit()
    await db.refresh(user)  # 拿 id
    await _set_user_cache(user)  # 预热：注册完立即可读
    return user


# 生成 token：保持原 DB 逻辑（token 不进缓存，调用方已写入过 user 缓存）
async def create_token(db: AsyncSession, user_id: int):
    token = str(uuid.uuid4())
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


# 验证用户：必须读 password，登录路径不打用户缓存，直接查 DB；成功后顺手预热
async def authenticate_user(db: AsyncSession, username: str, password: str):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    # 登录成功后预热：后续请求能直接命中缓存
    await _set_user_cache(user)
    return user


# 通过 token 查用户：先验证 token 必走 DB；user 走 by_id 缓存
async def get_user_by_token(db: AsyncSession, token: str):
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    db_token = result.scalar_one_or_none()

    # token 不存在或已过期
    if not db_token or db_token.expires_at < datetime.now():
        return None

    user_id = db_token.user_id

    # 先按 id 查缓存（已登录用户热点路径）
    cached = await get_cache(_user_id_key(user_id))
    if cached and cached != NULL_MARKER:
        try:
            data = _deserialize_user(cached)
            return UserInfoResponse.model_validate(data)
        except Exception:
            pass

    # 回源 DB
    query_user = select(User).where(User.id == user_id)
    result_user = await db.execute(query_user)
    user = result_user.scalar_one_or_none()
    if not user:
        return None

    # 回填双 key 缓存
    await _set_user_cache(user)
    return user


# 修改用户信息：先写 DB，commit 后失效双 key（标准 Cache-Aside 失效顺序）
async def update_user(db: AsyncSession, username: str, update_data: UserUpdateRequest):
    user = await get_user_by_name(db, username)
    if not user:
        return None

    user_id = user.id  # UserInfoResponse 同样有 id 字段

    # 1) DB 写
    query = update(User).where(User.username == username).values(
        **update_data.model_dump(exclude_unset=True, exclude_none=True)
    )
    result = await db.execute(query)
    await db.commit()

    # 2) 写成功后再失效缓存（避免脏写）
    await _delete_user_cache(username=username, user_id=user_id)

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")

    # 3) 回读最新值（DB 真源）并回填缓存
    updated_user = await get_user_by_name(db, username)
    return updated_user


# 修改用户密码：user 来自 Depends 注入（ORM 对象）；写后失效双 key
async def update_user_password(db: AsyncSession, user, password_data: UserChangePasswordRequest):
    if not verify_password(password_data.old_password, user.password):
        return False

    user.password = get_password_hash(password_data.new_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # password 不在缓存里，但保守策略：任何 user 表写操作都失效缓存
    await _delete_user_cache(username=user.username, user_id=user.id)
    return True
