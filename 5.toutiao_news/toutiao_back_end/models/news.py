from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from sqlalchemy import Integer, DateTime, String

# 基础模型
class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now,
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
    )


# 新闻分类
class category(Base):
    __tablename__ = "news_category"
    # 分类ID  Integer：整形；
    #  primary_key：主键；
    #  autoincrement：自增；
    #  comment：介绍；
    #  unique:表示唯一；
    #  nullable=False:表示不能为空值
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="分类ID")
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="分类名称")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="排序顺序")

    # __repr__ 方法，用于在打印对象时显示对象的属性值
    def __repr__(self):
        return f"category(id={self.id}, name={self.name}, sort_order={self.sort_order})"
