from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from crud import news
from typing import Optional
from fastapi import Query
from crud import news_cache

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
    categories = await news_cache.get_categories(db, skip=(page - 1) * page_size, limit=page_size)
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


# 获取新闻列表
# 思路： 处理分页规则 -> 查询新闻列表 -> 计算总量 -> 计算是否还有更多
@router.get('/list')
async def get_news_list(
    db: AsyncSession = Depends(get_db),
    # 分类参数  ... 表示可以不传, alias="categoryId" 表示在请求参数中用 categoryId 替换 category_id 参数
    category_id: int = Query(..., alias="categoryId"),
    # 分页参数
    page: int = 1,
    page_size: int = Query(10, le=100, alias="pageSize"),
):
    news_list = await news.get_news_list(db, category_id, page, page_size)
    total_count = await news.get_news_total(db, category_id)
    # 总量 > 跳过的 + 当前列表中的数量
    has_more = total_count > len(news_list) + page_size
    return {
        "code": 200,
        "message":"success",
        "data":{
            "list": news_list,
            "total": total_count,
            "hasMore": has_more
        }
    }


# 新闻搜索：跨 title/description/content/author 模糊匹配
# 排序：title 命中 > description 命中 > author 命中 > content 命中，同级别内 views DESC
@router.get('/search')
async def search_news(
    db: AsyncSession = Depends(get_db),
    # 搜索关键词：至少 2 个字符（去掉空格后的有效长度也由 crud 内做容错）
    keyword: str = Query(..., min_length=2, alias="keyword"),
    page: int = 1,
    page_size: int = Query(10, le=100, alias="pageSize"),
):
    news_list = await news.search_news(db, keyword, page, page_size)
    total_count = await news.search_news_total(db, keyword)
    # 总量 > 跳过的 + 当前列表中的数量
    has_more = total_count > len(news_list) + (page - 1) * page_size
    return {
        "code": 200,
        "message": "success",
        "data": {
            "list": [
                {
                    "id": n.id,
                    "title": n.title,
                    "description": n.description,
                    "content": n.content,
                    "image": n.image,
                    "author": n.author,
                    "publishTime": n.publish_time,
                    "categoryId": n.category_id,
                    "views": n.views,
                } for n in news_list
            ],
            "total": total_count,
            "hasMore": has_more,
        }
    }


# 获取新闻详情
@router.get('/detail')
async def get_news_detail(
    db: AsyncSession = Depends(get_db),
    id: int = Query(..., alias="id"),
):
    # 获取新闻详情 + 浏览量+1  + 相关新闻

    news_detail = await news.get_news_detail(db, id)
    # 更新浏览量
    await news.increase_news_views(db, id)
    # 获取相关新闻
    related_news = await news.get_related_news(db, id, news_detail.category_id)
 
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_news
        }
    }
