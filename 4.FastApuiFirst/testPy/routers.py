from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse, FileResponse

router = APIRouter()


class News(BaseModel):
    id: int
    title: str
    content: str


class User(BaseModel):
    username: str
    password: str


class BookItem(BaseModel):
    title: str = Field(..., le = 20, ge = 2)
    author: str = Field(ge = 2, le = 10)
    publisher: str = Field(default = "这是一个安静的晚上", le = 2)
    price: float = Field(..., gt = 0.01, le = 100000)


@router.get("/exception/{id}")
async def exception(id: int):
    id_list = list(range(10))
    if id not in id_list:
        raise HTTPException(status_code=404, detail=f"报错了，找不到这个{id}.")
    return {"id": id}


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


@router.post('/register')
def register(user: User):
    return user


@router.post('/add_book')
def add_book(item: BookItem):
    return item


@router.get("/book/item")
async def query_book_item(type: int = Query("Python开发", description = "书籍的类别", ge = 5, le = 255 ), price: int = Query(0, description="返回的记录数", ge = 50, le = 100)):
    return { "type": type, "price": price }


@router.get("/news/news_list")
async def query_news_list(skip: int = Query(0, description = "跳过的记录数", lt = 100), limit: int = Query(10, description="返回的记录数")):
    return { "skip": skip, "limit": limit }


@router.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@router.get("/hello/user")
async def say_hello():
    return {"message": f"我正在学习FastApi..."}