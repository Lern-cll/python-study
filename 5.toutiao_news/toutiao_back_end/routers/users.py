from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import null
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette import status

from config.db_conf import get_db
from crud.users import get_user_by_name, create_user, create_token
from models.users import User
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse
from utils.response import success_response

router = APIRouter(
    prefix="/api/user",
    tags=["user"],
    # dependencies=[Depends(get_current_user)],
)


# 用户注册接口
@router.post("/register")
async def register(
        user_info: UserRequest,
        db: AsyncSession = Depends(get_db)
):
    # 注册逻辑： 验证用户是否存在 -> 创建用户 -> 生成token -> 返回token和用户信息
    exit_user = await get_user_by_name(db, user_info.username)
    if exit_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")
    user = await create_user(db, user_info)
    token = await create_token(db, user.id)
    # return {
    #     "code": 200,
    #     "message": "注册成功",
    #     "data": {
    #         "token": token,
    #         "userInfo": {
    #             "id": user.id,
    #             "username": user.username,
    #             "bio": user.bio,
    #             "avatar": user.avatar
    #         }
    #     }
    # }
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功", data=response_data)


# 用户登录
@router.post("/login")
async def login():
    return {
      "code": 200,
      "message": "登录成功",
      "data": {
        "token": "用户访问令牌",
        "userInfo": {
          "id": 1,
          "username": "example_user",
          "nickname": null,
          "avatar": "https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg",
          "bio": "这个人很懒，什么都没留下"
        }
      }
    }

# 通过用户名获取用户信息
@router.get("/info")
async def user_info(username: str, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_name(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
