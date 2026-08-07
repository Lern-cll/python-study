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