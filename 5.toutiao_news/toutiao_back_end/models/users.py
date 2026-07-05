from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, DateTime, String, Enum, Index


# 基础模型
class Base(DeclarativeBase):
    pass


# 用户信息表
class User(Base):
    __tablename__ = "user"

    # 创建索引
    __table_args__ = (
        # 创建索引
        Index("username_UNIQUE", "username", unique=True),
        Index("phone_UNIQUE", "phone", unique=True),
    )

    # Optional [str] 表示字段可以为 None
    # nullable=False 表示字段不能为空
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名")
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码（加密存储）")
    nickname: Mapped[Optional[str]] = mapped_column(String(50), comment="昵称")
    avatar: Mapped[Optional[str]] = mapped_column(String(255), comment="头像URL", default='https://img10.qianzhan.com/star/%E9%AB%98%E5%9C%86%E5%9C%86/%E9%AB%98%E5%9C%86%E5%9C%86.jpg')
    gender: Mapped[Optional[str]] = mapped_column(
        Enum("male", "female", "unknown", name="gender_enum"),
        default="unknown",
        comment="性别",
    )
    bio: Mapped[Optional[str]] = mapped_column(String(500), comment="个人简介")
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, comment="手机号")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', nickname='{self.nickname}')>"


# 用户令牌表
class UserToken(Base):
    """
    用户令牌表ORM模型
    """
    __tablename__ = "user_token"

    # 创建索引
    __table_args__ = (
        Index("token_UNIQUE", "token", unique=True),
        Index("fk_user_token_user_idx", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="令牌ID")
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="用户ID")
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, comment="令牌值")
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="过期时间")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, comment="创建时间")

    def __repr__(self):
        return f"<UserToken(id={self.id}, user_id={self.user_id}, token='{self.token[:10]}...')>"
