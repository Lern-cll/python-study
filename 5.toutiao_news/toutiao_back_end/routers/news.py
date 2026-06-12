from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from crud import news

# 创建 APIRouter 实例
# prefix 前缀 (API 接口规范文档)
# tags 标签 分组（doc 文档中显示的分组）
router = APIRouter(
    prefix="/api/news",
    tags=["news"],
    # dependencies=[Depends(get_current_user)],
)

#接口实现流程
# 1.模块化路由 API接口规范文档
# 2.定义模型类 数据库表(数据库设计文档)
# 3.在 crud文件夹里面创建文件，封装操作数据库的方法
# 4.在路由处理函数里面调用 crud文件夹里面方法，返回结果


@router.get('/categories')
async def get_categories(
    db: AsyncSession = Depends(get_db),
    # 分页参数
    page: int = 1,
    page_size: int = 10,
):
    # 先获取数据库里面新闻分类数据 -> 先定义模型类 -> 封装查询数据的方法
    # 调用 crud文件夹里面方法，返回结果
    # skip=(page - 1) * page_size, limit=page_size
    categories = await news.get_categories(db, skip=(page - 1) * page_size, limit=page_size)
    # total = await news.get_total_categories(db)
    # total_page = total // page_size + (total % page_size > 0)
    return {
        "code": 200,
        "data": categories,
        "pagedata": {
            "page": page,
            "page_size": page_size,
            "total": 0,
            "total_page": 0,
        },
        "message": "获取新闻分类"
    }