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
    name: str = Field(..., max_length=20, min_length=2)
    author: str = Field(min_length=2, max_length=10)
    publisher: str = Field(default="这是一个安静的晚上", max_length=2)
    price: float = Field(..., gt=0.01, le=100000)

class BookAdd(BaseModel):
    id: int
    name: str
    author: str
    price: int
    type: int

class BookUpdate(BaseModel):
    name: str
    author: str
    price: int
    type: int