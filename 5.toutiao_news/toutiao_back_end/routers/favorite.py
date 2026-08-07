from fastapi import HTTPException

from fastapi import APIRouter
from fastapi import Depends
from config.db_conf import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from crud import  favorite
from models.users import User
from schemas.favorite import FavoriteCheckResponse, FavoriteAddResponse, FavoriteListResponse
from utils.auth import get_current_user
from fastapi import Query, Body

from utils.response import success_response

router = APIRouter(
    prefix="/api/favorite",
    tags=["favorite"],
    # dependencies=[Depends(get_current_user)],
)

# 检查新闻收藏状态
@router.get('/check')
async def check_favorite(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
        new_id: int = Query(..., alias="newsId", description="新闻ID"),
):
    checked = await favorite.is_new_favorite(db, user, new_id)

    return success_response(message="未收藏", data=FavoriteCheckResponse(isFavorite=checked))


# 收藏新闻
@router.post('/add')
async def add_favorite(
        data: FavoriteAddResponse,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    result = await favorite.add_new_favorite(db, user, data.news_id)
    return success_response(message="收藏成功", data=result)

# 取消收藏
@router.delete('/remove')
async def remove_favorite(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
        news_id: int = Query(..., alias="newsId", description="新闻ID"),
):
    result = await favorite.remove_new_favorite(db, user, news_id)
    if not result:
        raise HTTPException(status_code=404, detail="收藏记录不存在")
    return success_response(message="删除收藏成功")

#  查询收藏列表
@router.get('/list')
async def get_favorite_list(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
        page_size: int = Query(10, alias="pageSize", description="每页数量"),
        page: int = Query(1, alias="page", description="页码"),
):
    rows, total = await favorite.get_favorite_list(db, user.id, page, page_size)
    # [expression for item in iterable]
    favorite_list = [{
        **news.__dict__,
        "favorite_time": favorite_time,
        "favorite_id": favorite_id
    } for news, favorite_time, favorite_id in rows]
    has_more = total > page_size * page
    data = FavoriteListResponse(list=favorite_list, total=total, hasMore=has_more)
    return success_response(message="获取收藏列表成功", data=data)


#  取消收藏列表
@router.delete('/clear_all_favorite')
async def clear_all_favorite(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    count = await favorite.remove_all_favorite(db, user.id)
    return success_response(message=f"清空了{count}条数据", data=count)