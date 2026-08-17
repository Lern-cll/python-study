from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import search_history
from models.users import User
from schemas.search_history import (
    SearchHistoryAddRequest,
    SearchHistoryItemResponse,
    SearchHistoryListResponse,
)
from utils.auth import get_current_user
from utils.response import success_response

# 搜索历史路由：所有接口都需要登录，按当前用户隔离数据
router = APIRouter(
    prefix="/api/search-history",
    tags=["search-history"],
)


# 添加一条搜索历史（搜索接口成功后由前端调用）
@router.post('/add')
async def add_search_history(
    data: SearchHistoryAddRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = await search_history.add_search_history(db, user, data.keyword)
    return success_response(
        message="记录搜索历史成功",
        data=SearchHistoryItemResponse.model_validate(row),
    )


# 获取当前用户的最近搜索历史（默认 10 条）
@router.get('/list')
async def get_search_history_list(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = Query(10, le=50, description="返回条数，最大 50"),
):
    rows, total = await search_history.get_search_history_list(db, user, limit)
    return success_response(
        message="获取搜索历史成功",
        data=SearchHistoryListResponse(
            list=[SearchHistoryItemResponse.model_validate(r) for r in rows],
            total=total,
        ),
    )


# 清空当前用户的所有搜索历史
@router.delete('/clear')
async def clear_search_history(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    count = await search_history.clear_search_history(db, user)
    return success_response(message=f"成功删除{count}条搜索历史")