from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import Integer, DateTime, ForeignKey, Index, text
from models.base import Base


# 浏览历史表
class History(Base):
    __tablename__ = "history"

    # 创建索引
    __table_args__ = (
        Index("fk_history_news_idx", "news_id"),
        Index("fk_history_user_idx", "user_id"),
        Index("idx_view_time", text("view_time desc")),
        {"comment": "浏览历史表"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="历史ID")
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
    view_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
        comment="浏览时间",
    )

    def __repr__(self):
        return f"<History(id={self.id}, user_id={self.user_id}, news_id={self.news_id})>"
