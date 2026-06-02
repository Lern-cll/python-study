"""Pydantic 数据模型，统一在此定义，供各路由文件复用。"""
from pydantic import BaseModel, Field


class News(BaseModel):
    id: int
    title: str
    content: str


class User(BaseModel):
    username: str
    password: str


class BookItem(BaseModel):
    title: str = Field(..., le=20, ge=2)
    author: str = Field(ge=2, le=10)
    publisher: str = Field(default="这是一个安静的晚上", le=2)
    price: float = Field(..., gt=0.01, le=100000)
