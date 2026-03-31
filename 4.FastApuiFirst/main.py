from fastapi import FastAPI,Query
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse, FileResponse

app = FastAPI()



# 11.响应体类型，HTML格式
@app.get("/file")
async def get_file():
    path = "./test.txt"
    return FileResponse(path)


# 11.响应体类型，HTML格式
@app.get("/html", response_class=HTMLResponse)
async def get_html():
    return "<h1>这是一个安静的晚上， 我坐在摇椅里乘凉</h1>"



# 08,注册： 用户名和密码
class User(BaseModel):
    username: str
    password: str

@app.post('/register')
def register(user: User):
    return user


# 新增图书： 图书信息包含:书名、作者、出版社、售价
class BookItem(BaseModel):
    title: str = Field(..., le = 20, ge = 2)
    author: str = Field(ge = 2, le = 10)
    publisher: str = Field(default = "这是一个安静的晚上", le = 2)
    price: float = Field(..., gt = 0.01, le = 100000)

@app.post('/add_book')
def add_book(item: BookItem):
    return item


# 07: 书籍的类别和价格，并且限制价格范围
# Query() 是引入的校验函数， ... 表示必填
@app.get("/book/item")
async def query_book_item(type: int = Query("Python开发", description = "书籍的类别", ge = 5, le = 255 ), price: int = Query(0, description="返回的记录数", ge = 50, le = 100)):
    return { "type": type, "price": price }

# 获取新闻列表消息，主要是拼接
@app.get("/news/news_list")
async def query_news_list(skip: int = Query(0, description = "跳过的记录数", lt = 100), limit: int = Query(10, description="返回的记录数")):
    return { "skip": skip, "limit": limit }


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/hello/user")
async def say_hello():
    return {"message": f"我正在学习FastApi..."}

@app.get("/")
async def root():
    return {"message": "Hello World"}






