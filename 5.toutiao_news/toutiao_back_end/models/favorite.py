from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import Integer, DateTime, ForeignKey, Index, UniqueConstraint
from models.base import Base


# 收藏表
class Favorite(Base):
    __tablename__ = "favorite"

    # 创建索引和唯一约束
    # UniqueConstraint： 创建唯一约束， 当前用户，当前新闻，只能收藏一次
    __table_args__ = (
        UniqueConstraint("user_id", "news_id", name="user_news_unique"),
        Index("fk_favorite_news_idx", "news_id"),
        Index("fk_favorite_user_idx", "user_id"),
        {"comment": "收藏表"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="收藏ID")
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        comment="用户ID",
    )
    news_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("news.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        comment="新闻ID",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
        comment="收藏时间",
    )

    def __repr__(self):
        return f"<Favorite(id={self.id}, user_id={self.user_id}, news_id={self.news_id})>"
