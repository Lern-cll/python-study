from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession

from config.db_conf import get_db
from models.users import User
from schemas.history import HistoryAddResponse, HistoryItmResponse, HistoryListItemResponse, HistoryListResponse
from utils.auth import get_current_user
from crud import history
from utils.response import success_response

router = APIRouter(
    prefix="/api/history",
    tags=["history"],
    # dependencies=[Depends(get_current_user)],
)

"""
添加历史记录
"""
@router.post('/add')
async def add_history(
        data: HistoryAddResponse,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
   result = await history.add_history(db, user, data.news_id)
   return success_response(message="添加历史成功", data=HistoryItmResponse.model_validate(result))

"""
获取历史列表
"""
@router.get('/list')
async def get_history_list(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
        page_size: int = Query(10, alias="pageSize", description="每页数量"),
        page: int = Query(1, alias="page", description="页码"),
):
    rows, total = await history.get_history_list(db, user, page, page_size)

    history_list = [
        HistoryListItemResponse.model_validate({
            "id": news_obj.id,
            "title": news_obj.title,
            "description": news_obj.description,
            "image": news_obj.image,
            "author": news_obj.author,
            "publishTime": news_obj.publish_time,
            "categoryId": news_obj.category_id,
            "views": news_obj.views,
            "viewTime": view_time,
        })
        for news_obj, history_id, view_time in rows
    ]

    has_more = total > page_size * page
    return success_response(
        message="查询历史列表成功",
        data=HistoryListResponse(list=history_list, total=total, hasMore=has_more)
    )

"""
删除某条历史记录
"""
@router.delete('/delete/{history_id}')
async def delete_history(
        history_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    count =  await history.delete_history(db, user, history_id)
    if not count:
        raise HTTPException(status_code=404, detail="历史记录不存在")
    return success_response(message=f"删除历史记录成功")

"""
删除所有历史记录
"""
@router.delete('/clear')
async def delete_all_history(
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    count = await history.delete_all_history(db, user)
    return success_response(message=f"删除{count}条历史记录成功")


