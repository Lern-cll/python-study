/**
 * 新闻相关 API 接口封装
 */
import request from '@/utils/request'

// 请求参数类型
interface NewsListParams {
  page?: number
  pageSize?: number
  categoryId?: number | null
}

/**
 * 获取新闻分类列表
 */
export function getCategories(): Promise<ApiResponse<CategoryItem[]>> {
  return request({
    url: '/news/categories',
    method: 'get'
  })
}

/**
 * 获取新闻列表
 */
export function getNewsList(params: NewsListParams): Promise<ApiResponse<NewsItem[]>> {
  return request({
    url: '/news/list',
    method: 'get',
    params
  })
}

/**
 * 获取新闻详情
 */
export function getNewsDetail(id: number): Promise<ApiResponse<NewsItem>> {
  return request({
    url: `/news/detail/${id}`,
    method: 'get'
  })
}