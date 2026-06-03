"""请求体示例：演示 POST 接口如何接收 Pydantic 模型。"""
from fastapi import APIRouter

from .models import BookItem, User

router = APIRouter(tags=["请求体"])


@router.post("/register")
def register(user: User):
    return user


@router.post("/add_book")
def add_book(item: BookItem):
    return item
