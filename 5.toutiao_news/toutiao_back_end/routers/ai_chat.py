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


# AI 会话路由：所有接口都需要登录，按当前用户隔离数据
router = APIRouter(
    prefix="/api/ai-chat",
    tags=["ai-chat"],
)


# 搜索接口必须放在 `/sessions/{session_id}` 之前，否则会被误识别为 session_id
@router.get("/sessions/search")
async def search_sessions(
    keyword: str = Query(..., min_length=1, description="搜索关键词，1 字符起"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    搜索当前用户的会话（title 或 messages 内容命中），最多返回 5 条。
    """
    rows, total = await ai_chat.search_sessions(db, user, keyword, limit=5)
    items = [
        SessionSearchItemResponse.model_validate({
            "id": r.id,
            "title": r.title,
            "updated_at": r.updated_at,
        })
        for r in rows
    ]
    return success_response(
        message="搜索会话成功",
        data=SessionSearchResponse(list=items, total=total),
    )


# 创建会话（首条 AI 回复成功后由前端调用）
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


# 更新会话（后续每轮 AI 回复成功后由前端调用）
@router.put("/sessions/{session_id}")
async def update_session(
    session_id: int,
    data: SessionUpdateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = await ai_chat.update_session(db, user, session_id, data)
    if not row:
        raise HTTPException(status_code=404, detail="会话不存在或无权访问")
    return success_response(
        message="更新会话成功",
        data=SessionDetailResponse.model_validate(row),
    )


# 获取会话列表（分页，按 updated_at 倒序）
@router.get("/sessions")
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    pageSize: int = Query(10, ge=1, le=100, description="每页条数，最大 100"),
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


# 获取会话详情（含完整 messages）
@router.get("/sessions/{session_id}")
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = await ai_chat.get_session(db, user, session_id)
    if not row:
        raise HTTPException(status_code=404, detail="会话不存在或无权访问")
    return success_response(
        message="获取会话详情成功",
        data=SessionDetailResponse.model_validate(row),
    )


# 删除会话
@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    count = await ai_chat.delete_session(db, user, session_id)
    if count == 0:
        raise HTTPException(status_code=404, detail="会话不存在或无权访问")
    return success_response(message=f"删除会话成功，共 {count} 条")