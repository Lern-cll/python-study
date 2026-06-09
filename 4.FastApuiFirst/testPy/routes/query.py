"""查询参数示例：演示 Query 校验、默认值、范围限制等。"""
from fastapi import APIRouter, Query, Depends, HTTPException, Path
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from dataBase.database import get_db_session, Book
from .dependencies import Pagination


router = APIRouter(tags=["查询参数"])

# ========== 数据库查询接口 ============

# ---------- 查询图书接口 ----------
@router.get("/book/books") # 查询图书接口
async def query_book_item(
    db_session: AsyncSession = Depends(get_db_session)
):
    # 查询，数据库的读写需要，异步会话
    result = await db_session.execute(select(Book))
    books = result.scalars().all()
    return {"books": books}

# 查询第一本图书
@router.get("/book/first")
async def query_first_book(
    db_session: AsyncSession = Depends(get_db_session)
):
    # 查询，数据库的读写需要，异步会话
    result = await db_session.execute(select(Book))
    book = result.scalars().first()
    if book is None:
        raise HTTPException(status_code=404, detail="图书不存在")
    return {"book": book}

# 根据ID查询图书接口
@router.get("/book/get/{book_id}")
async def query_book_by_id(
    db_session: AsyncSession = Depends(get_db_session),
    book_id: int = Path(..., description="图书的ID")
   ):
    # 查询，数据库的读写需要，异步会话
    result = await db_session.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none() # 只返回一条记录，没有则返回 None
    if book is None:
        raise HTTPException(status_code=404, detail="图书不存在")
    return {"book": book}


# 查询价格大于等于200的图书
@router.get("/book/price_greater_than_200")
async def query_price_greater_than_200(
    db_session: AsyncSession = Depends(get_db_session)
):
    # 查询，数据库的读写需要，异步会话
    result = await db_session.execute(select(Book).where(Book.price >= 200))
    books = result.scalars().all()
    if not books:
        raise HTTPException(status_code=404, detail="没有价格大于200的图书")
    return {"books": books}





# ---------- 查询图书接口 ----------
@router.get("/book/item")
async def query_book_item(
    type: int = Query(100, description="书籍的类别", ge=5, le=255),
    price: int = Query(0, description="返回的记录数", ge=50, le=100),
    pagination: Pagination = Depends(),
):
    return {"type": type, "price": price, "pagination": pagination}

# ---------- 查询新闻列表接口 ----------
@router.get("/news/news_list")
async def query_news_list(
    skip: int = Query(0, description="跳过的记录数", lt=100),
    limit: int = Query(10, description="返回的记录数"),
):
    return {"skip": skip, "limit": limit}


