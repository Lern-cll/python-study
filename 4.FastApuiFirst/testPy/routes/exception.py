"""异常处理示例：演示如何主动抛出 HTTPException。"""
from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["异常处理"])


@router.get("/exception/{id}")
async def exception(id: int):
    id_list = list(range(10))
    if id not in id_list:
        raise HTTPException(status_code=404, detail=f"报错了，找不到这个{id}.")
    return {"id": id}
