from fastapi import Header
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from config.db_conf import get_db
from crud import users
from fastapi import HTTPException, status

# 整合   根据Token 查询用户，返回用户
async def get_current_user(
        authorization: str = Header(..., alias= "Authorization", description="用户认证信息"),
        db: AsyncSession = Depends(get_db)
):
    # Bearer xxx
    # token = authorization.split(" ")[1]
    token =  authorization.replace("Bearer ", "")
    user = await users.get_user_by_token(db, token)
    if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的令牌或者是过期的令牌")

    return user
