from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class UserRequest(BaseModel):
    username: str
    password: str

# 用户信息基础数据模型
class UserInfoBase(BaseModel):
    """用户信息基础数据模型"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")


# 用户信息
# user_info 对应的类： 基础类 + InfoBase 类（id、用户名）
class UserInfoResponse(UserInfoBase):
    id: int
    username: str

    # 模型类配置
    model_config = ConfigDict(
        from_attributes=True  # 允许从ORM对象属性中获取字段值
    )


# 用户认证信息
class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse = Field(..., alias="userInfo", serialization_alias="userInfo")

    # 模型类配置
    model_config = ConfigDict(
        populate_by_name=True,   # 允许同时使用字段原名（user_info）和别名（userInfo）来传值
        # extra="forbid",   # 禁止传入模型中未定义的字段，多余字段会直接报错
        # arbitrary_types_allowed=True,   # 允许字段使用任意类型的对象（非标准JSON类型）
        from_attributes=True  # 允许从ORM对象属性中获取字段值
    )

# 更新用户信息的模型类
class UserUpdateRequest(BaseModel):
    """更新用户信息的模型类"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    phone: Optional[str] = Field(None, max_length=15, description="手机号")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")


# 修改用户密码的模型类
class UserChangePasswordRequest(BaseModel):
    old_password: str = Field(..., alias="oldPassword", description="旧密码")
    new_password: str = Field(..., min_length=6, alias="newPassword", description="新密码")