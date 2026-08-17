from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class SearchHistoryAddRequest(BaseModel):
    """添加搜索历史请求体"""
    keyword: str = Field(..., min_length=2, max_length=255, description="搜索关键词，至少 2 个字符")


class SearchHistoryItemResponse(BaseModel):
    """单条搜索历史响应"""
    id: int
    keyword: str
    searchTime: datetime = Field(..., alias="search_time")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class SearchHistoryListResponse(BaseModel):
    """搜索历史列表响应"""
    list: list[SearchHistoryItemResponse]
    total: int
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )