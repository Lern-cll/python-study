from fastapi import FastAPI
from testPy.routers import router

app = FastAPI()

# 13.自定义响应数据格式

# 新闻接口，响应格式，id + title + content
class News(BaseModel):
    id: int
    title: str
    content: str

@app.get("/news/{id}", response_model=News)
async def get_news(id: int):
    return {
        "id": id,
        "title": f"这是第{id}本书",
        "content": f"这是一本绝世好书"
    }




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
app.include_router(router)

@app.middleware("http")
async def add_middleware2(request, call_next):
    print("中间件2触发了")
    response = await call_next(request)
    print("中间件2执行完毕了")
    return response

@app.middleware("http")
async def add_middleware(request, call_next):
    print("中间件1触发了")
    response = await call_next(request)
    print("中间件1执行完毕了")
    return response


@app.get("/")
async def root():
    return {"message": "Hello World"}