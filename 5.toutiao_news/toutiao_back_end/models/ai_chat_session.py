from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, Index, text, JSON
from models.base import Base


# AI 会话表：每个会话包含完整 messages JSON 数组，按用户隔离
class AiChatSession(Base):
    __tablename__ = "ai_chat_session"

    # 创建索引：user_id 单列索引便于按用户过滤；复合索引用于按用户+更新时间倒序取列表
    __table_args__ = (
        Index("fk_ai_chat_session_user_idx", "user_id"),
        Index("idx_user_updated", "user_id", text("updated_at desc")),
        {"comment": "AI 会话表"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="会话ID")
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        comment="用户ID",
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="", comment="会话标题")
    model: Mapped[str] = mapped_column(String(64), nullable=False, default="", comment="AI 模型标识")
    # messages 形如 [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    messages: Mapped[list] = mapped_column(JSON, nullable=False, comment="消息数组")
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
        comment="创建时间",
    )
    # ORM 层 onupdate 兜底（DDL 已带 ON UPDATE CURRENT_TIMESTAMP）
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=datetime.now,
        nullable=False,
        comment="更新时间",
    )

    def __repr__(self):
        return f"<AiChatSession(id={self.id}, user_id={self.user_id}, title='{self.title[:20]}')>"