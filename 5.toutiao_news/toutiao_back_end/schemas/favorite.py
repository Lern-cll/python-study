from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewsItemBase


class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(..., alias="isFavorite", description="是否已收藏")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class FavoriteAddResponse(BaseModel):
    news_id: int = Field(..., alias="newsId")


class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id: int = Field(..., alias="favoriteId")
    favorite_time: datetime = Field(..., alias="favoriteTime")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )

    # 收藏列表接口响应模型类
class FavoriteListResponse(BaseModel):
    list: list[FavoriteNewsItemResponse]  # 把 xx 替换为具体的列表项模型
    total: int
    has_more: bool = Field(alias="hasMore", description="是否还有更多")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )
