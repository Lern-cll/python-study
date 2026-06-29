# JSONResponse 是 FastAPI 提供的一个响应类，它的作用是直接返回一个 JSON 格式的 HTTP 响应
from fastapi.responses import JSONResponse

#  是一个序列化工具，它的作用是把 Python 中各种复杂对象转成可以被 JSON 编码的类型（如 dict、list、str、int 等）
# 为什么需要它？因为 Python 中很多对象是不能直接转 JSON 的，比如：
# Pydantic 模型（如 User(name="Tom", age=18)）
# SQLAlchemy ORM 对象（数据库查询结果）
# datetime 对象（如 datetime.now()）
from fastapi.encoders import jsonable_encoder

#
def success_response(message: str = 'success', data=None):
    # 目标：将任何的 FastApi, Pydantic, ORM对象，都要正常响应： code、message、data
    content = {
        "code": 200,
        "message": message,
        "data": data
    }

    return JSONResponse(content=jsonable_encoder(content))



