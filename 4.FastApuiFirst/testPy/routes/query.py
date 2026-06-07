"""查询参数示例：演示 Query 校验、默认值、范围限制等。"""
from fastapi import APIRouter, Query, Depends
from .dependencies import Pagination


router = APIRouter(tags=["查询参数"])


@router.get("/book/item")
async def query_book_item(
    type: int = Query("Python开发", description="书籍的类别", ge=5, le=255),
    price: int = Query(0, description="返回的记录数", ge=50, le=100),
    pagination: Pagination = Depends(),
):
    return {"type": type, "price": price, "pagination": pagination}


@router.get("/news/news_list")
async def query_news_list(
    skip: int = Query(0, description="跳过的记录数", lt=100),
    limit: int = Query(10, description="返回的记录数"),
):
    return {"skip": skip, "limit": limit}
