import asyncio
import time

from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def root():
    return {'message': 'Hello World'}

@app.get('/items/{item_id}')
async def read_item(item_id: int):
    return {'item_id': item_id}

# 异步
@app.get('/async')
async def fn_async ():
    start = time.time()
    tasks = [asyncio.sleep(1) for i in range(10) ]
    await asyncio.gather(*tasks)
    end = time.time()
    return { "time": f"{end - start: .2f}s" }

# 同步
@app.get("/sync")
def fn_sync():
    start = time.time()
    for i in range(3):
        time.sleep(1)
    end = time.time()
    return { "time": f"{end - start: .2f}s" }