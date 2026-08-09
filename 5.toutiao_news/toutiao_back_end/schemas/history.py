from datetime import datetime

from pydantic import BaseModel,Field,ConfigDict


class HistoryAddResponse(BaseModel):
    news_id: int = Field(..., alias="newsId")


class HistoryItmResponse(BaseModel):
    """返回给前端的浏览历史"""
    id: int
    newsId: int = Field(..., alias="news_id")
    userId: int = Field(..., alias="user_id")
    viewTime: datetime = Field(..., alias="view_time")

    model_config = ConfigDict(
        from_attributes=True,        # 允许从 ORM 对象构造
        populate_by_name=True,
    )


class HistoryListItemResponse(BaseModel):
    id: int
    title: str
    description: str
    image: str
    author: str
    publishTime: datetime
    categoryId: int
    views: int
    viewTime: datetime = Field(..., alias="view_time")

    model_config = ConfigDict(
        from_attributes=True,        # 允许从 ORM 对象构造
        populate_by_name=True,
    )

class HistoryListResponse(BaseModel):
    list: list[HistoryListItemResponse]
    total: int
    has_more: bool = Field(alias="hasMore", description="是否还有更多")
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )
