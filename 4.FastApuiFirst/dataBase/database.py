from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# my_test_db 数据库连接字符串
# 注意：密码里的 @ 必须 URL 编码为 %40，否则 SQLAlchemy 解析 URL 时会出错
ASYNC_DATABASE_URL = "mysql+aiomysql://root:Lern%40185@localhost:3306/test_db?charset=utf8mb4"

# 1.创建异步数据库引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,          # 可选:输出SQL日志
    pool_size=10,       # 设置连接池中保持的持久连接数
    max_overflow=20,    # 设置连接池允许创建的额外连接数
)


# 2.定义模型类
# 基类： 创建时间，更新时间； 书籍表： id，书名，作者，价格，类别
class Base(DeclarativeBase):
    """所有 ORM 模型的基类，包含公共字段 create_time / update_time"""
    create_time: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间",
    )
    update_time: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(),
        onupdate=func.now(), comment="更新时间",
    )


class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, comment="书籍ID")
    name: Mapped[str] = mapped_column(String(255), index=True, comment="书名")
    author: Mapped[str] = mapped_column(String(255), index=True, comment="作者")
    price: Mapped[int] = mapped_column(Integer, index=True, comment="价格")
    type: Mapped[int] = mapped_column(Integer, index=True, comment="类别")


# 3.创建数据库表 -> FastAPI 启动的时候调用建表
async def create_tables():
    """异步建表：异步连接里必须用 run_sync 来执行同步的 ORM 操作"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("数据库表创建完成")
