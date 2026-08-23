import json
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, ForeignKey, Index, text, Text, DateTime

from models.base import Base


# AI 会话表
# ----------------------------------------------------------------------
# 数据库真实结构（ai_chat）：
#   id          INT UNSIGNED  PK
#   user_id     INT UNSIGNED  FK -> user.id
#   message     TEXT          # 此处存放 messages 数组的 JSON 字符串
#   response    TEXT          # 最后一条 assistant 回复（兼容旧语义）
#   created_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
#
# 历史 ORM 设计中还有 title / model / updated_at / messages 列，
# 实际表里并不存在。本模型通过 Python 属性派生，避免再加列。
# ----------------------------------------------------------------------
class AiChat(Base):
    __tablename__ = "ai_chat"

    __table_args__ = (
        Index("fk_ai_chat_user_idx", "user_id"),
        Index("idx_created_at", "created_at"),
        {"comment": "AI 会话表"},
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="会话ID"
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        comment="用户ID",
    )
    # message 字段：把整个 messages 列表序列化成 JSON 字符串存到 TEXT 中
    message: Mapped[str] = mapped_column(
        Text, nullable=False, default="[]", comment="完整消息数组的 JSON 字符串"
    )
    # response 字段：最后一条 assistant 的回复，便于快速读取
    response: Mapped[str] = mapped_column(
        Text, nullable=False, default="", comment="最后一次 AI 回复"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
        comment="创建时间",
    )

    # -------- 派生属性：API 层需要 title/model/messages/updated_at --------
    # 这些不是 DB 列，SQLAlchemy 会忽略未带 Mapped[] 注解的成员。

    @property
    def messages(self) -> list:
        """反序列化 message 字段得到消息数组；解析失败时返回空数组。"""
        try:
            data = json.loads(self.message or "[]")
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, TypeError):
            return []

    @messages.setter
    def messages(self, value: list) -> None:
        """设置时把列表序列化回 message 字段。"""
        self.message = json.dumps(value or [], ensure_ascii=False)

    @property
    def title(self) -> str:
        """从首条 user 消息截取前 30 字符（去换行）作为标题。"""
        for m in self.messages:
            if isinstance(m, dict) and m.get("role") == "user":
                content = (m.get("content") or "").strip().replace("\n", " ")
                return content[:30]
        return ""

    @property
    def model(self) -> str:
        """DB 中无 model 列；为兼容 API 返回空字符串。"""
        return ""

    @property
    def updated_at(self) -> datetime:
        """DB 中无 updated_at；用 created_at 兜底，保持 API 形状不变。"""
        return self.created_at

    def __repr__(self):
        return f"<AiChat(id={self.id}, user_id={self.user_id}, title='{self.title[:20]}')>"
