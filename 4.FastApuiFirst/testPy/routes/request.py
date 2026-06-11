"""请求体示例：演示 POST 接口如何接收 Pydantic 模型。"""
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from dataBase.database import get_db_session, Book

from .models import BookItem, User, BookAdd, BookUpdate

router = APIRouter(tags=["请求体"])


# ========== 数据库接口 ============
# 添加图书接口
# 用户输入图书信息(id, name, author, price, type) -> 
@router.post("/book/add")
async def add_book_item(
    book: BookAdd,
    db_session: AsyncSession=Depends(get_db_session)
):
    # Pydantic 模型 -> ORM 对象 -> add -> commit
    db_book = Book(**book.model_dump())
    db_session.add(db_book)
    await db_session.commit()
    return book

# 更新图书
@router.post('/book/update')
async def update_book(
    book_id: int,
    book: BookUpdate,
    db_session: AsyncSession=Depends(get_db_session)
):
    # 使用 select 查询数据库中的书籍
    result = await db_session.execute(select(Book).where(Book.id == book_id))
    db_book = result.scalar_one_or_none()
    if not db_book:
        raise HTTPException(status_code=404, detail="图书不存在")
    # 合并更新数据
    update_data = book.model_dump()
    for key, value in update_data.items():
        setattr(db_book, key, value)
    return book


# 删除图书
@router.post('/book/delete')
async def delete_book(
    book_id: int,
    db_session: AsyncSession=Depends(get_db_session)
):
    # 使用 select 查询数据库中的书籍
    db_book = await db_session.execute(select(Book).where(Book.id == book_id))
    db_book = db_book.scalar_one_or_none()
    if not db_book:
        raise HTTPException(status_code=404, detail="图书不存在")
    # 删除书籍
    await db_session.delete(db_book)
    await db_session.commit()
    return book



@router.post("/register")
def register(user: User):
    return user


@router.post("/add_book")
def add_book(item: BookItem):
    return item


