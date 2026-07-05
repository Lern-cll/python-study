from pydantic import BaseModel, Field, ConfigDict


class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(..., alias="isFavorite", description="是否已收藏")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class FavoriteAddResponse(BaseModel):
    news_id: int = Field(..., alias="newsId")