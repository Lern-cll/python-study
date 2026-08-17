/**
 * 新闻相关 API 接口封装
 */
import request from '@/utils/request'

// ============ 请求参数类型 ============
/** 新闻列表分页与筛选参数 */
interface NewsListParams {
  /** 当前页码 */
  page?: number
  /** 每页条数 */
  pageSize?: number
  /** 分类ID；null/不传 表示全部分类 */
  categoryId?: number | null
}

/** 新闻搜索参数 */
interface NewsSearchParams {
  /** 搜索关键词（≥2 字符） */
  keyword: string
  /** 当前页码 */
  page?: number
  /** 每页条数 */
  pageSize?: number
}

/**
 * 获取新闻分类列表（首页顶部 Tab 数据源）
 * @returns 分类列表的接口响应
 */
export function getCategories(): Promise<ApiResponse<CategoryItem[]>> {
  return request({
    url: '/news/categories',
    method: 'get'
  })
}

/**
 * 获取新闻列表（分页）
 * @param params - 分页参数与分类筛选
 * @returns 新闻列表的接口响应
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
 * @param id - 新闻ID
 * @returns 新闻详情的接口响应
 */
export function getNewsDetail(id: number): Promise<ApiResponse<NewsItem>> {
  return request({
    url: '/news/detail',
    method: 'get',
    params: { id }
  })
}

/**
 * 新闻搜索：跨 title/description/content/author 模糊匹配
 * @param params - 搜索参数（keyword 必填，至少 2 个字符）
 * @returns 搜索结果的接口响应
 */
export function searchNews(params: NewsSearchParams): Promise<ApiResponse<NewsItem[]>> {
  return request({
    url: '/news/search',
    method: 'get',
    params
  })
}