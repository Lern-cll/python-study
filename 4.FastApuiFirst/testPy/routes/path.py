"""路径参数示例：演示 {name} 占位符的用法。"""
from fastapi import APIRouter

router = APIRouter(tags=["路径参数"])


@router.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@router.get("/hello/user")
async def say_hello_user():
    return {"message": "我正在学习FastApi..."}
