"""响应类型示例：response_model、FileResponse、HTMLResponse。"""
from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse

from .models import News

router = APIRouter(tags=["响应类型"])


@router.get("/news/{id}", response_model=News)
async def get_news(id: int):
    return {
        "id": id,
        "title": f"这是第{id}本书",
        "content": "这是一本好书",
    }


@router.get("/file")
async def get_file():
    path = "./test.txt"
    return FileResponse(path)


@router.get("/html", response_class=HTMLResponse)
async def get_html():
    return "<h1>这是一个安静的晚上， 我坐在摇椅里乘凉</h1>"
