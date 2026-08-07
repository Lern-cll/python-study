from fastapi import  APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from config.db_conf import get_db
from models.users import User
from schemas.history import HistoryAddResponse, HistoryItmResponse
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
