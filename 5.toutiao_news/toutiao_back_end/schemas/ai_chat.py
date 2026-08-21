from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ChatMessage(BaseModel):
    """单条消息（与千问 ChatMessage 协议一致）"""
    role: str = Field(..., description="system | user | assistant")
    content: str = Field(..., description="消息内容")


class SessionCreateRequest(BaseModel):
    """创建会话请求体：首条 AI 回复成功后由前端调用"""
    model: str = Field(..., min_length=1, max_length=64, description="AI 模型标识")
    messages: list[ChatMessage] = Field(..., min_length=1, description="完整消息数组（不含 system）")
    title: Optional[str] = Field(default=None, max_length=255, description="可选，会话标题")


class SessionUpdateRequest(BaseModel):
    """更新会话请求体（覆盖式）：后续每轮 AI 回复成功后调用"""
    model: str = Field(..., min_length=1, max_length=64, description="AI 模型标识")
    messages: list[ChatMessage] = Field(..., min_length=1, description="完整消息数组（不含 system）")
    title: Optional[str] = Field(default=None, max_length=255, description="可选，会话标题")


class SessionDetailResponse(BaseModel):
    """会话详情：含完整 messages"""
    id: int
    title: str
    model: str
    messages: list[ChatMessage]
    createdAt: datetime = Field(..., alias="created_at")
    updatedAt: datetime = Field(..., alias="updated_at")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class SessionListItemResponse(BaseModel):
    """会话列表项：不含 messages，减少 payload"""
    id: int
    title: str
    model: str
    updatedAt: datetime = Field(..., alias="updated_at")
    messageCount: int

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class SessionListResponse(BaseModel):
    list: list[SessionListItemResponse]
    total: int
    hasMore: bool = Field(..., alias="has_more")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class SessionSearchItemResponse(BaseModel):
    """搜索结果项（极简字段）"""
    id: int
    title: str
    updatedAt: datetime = Field(..., alias="updated_at")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class SessionSearchResponse(BaseModel):
    list: list[SessionSearchItemResponse]
    total: int

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )