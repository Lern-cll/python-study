from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import Integer, DateTime, String, ForeignKey, Index, text
from models.base import Base


# 用户搜索历史表：记录每个用户最近搜过的关键词，用于跨设备同步与账号绑定
class SearchHistory(Base):
    __tablename__ = "user_search_history"

    # 创建索引：user_id 单列索引便于按用户查询；复合索引用于按用户+时间倒序取最近记录
    __table_args__ = (
        Index("fk_search_history_user_idx", "user_id"),
        Index("idx_user_time", "user_id", text("search_time desc")),
        {"comment": "用户搜索历史表"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="历史ID")
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        comment="用户ID",
    )
    keyword: Mapped[str] = mapped_column(String(255), nullable=False, comment="搜索关键词")
    search_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
        comment="搜索时间",
    )

    def __repr__(self):
        return f"<SearchHistory(id={self.id}, user_id={self.user_id}, keyword='{self.keyword}')>"