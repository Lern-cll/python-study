/**
 * 收藏相关 API 接口封装
 */
import request from '@/utils/request'

// ============ 请求参数类型 ============
/** 收藏列表分页参数 */
interface FavoriteListParams {
  /** 当前页码 */
  page?: number
  /** 每页条数 */
  pageSize?: number
}

/**
 * 获取收藏列表（分页）
 * @param params - 分页参数
 * @returns 收藏列表的接口响应
 */
export function getFavoriteList(params: FavoriteListParams): Promise<ApiResponse> {
  return request({
    url: '/favorite/list',
    method: 'get',
    params
  })
}

/**
 * 添加收藏
 * @param newsId - 要收藏的新闻ID
 * @returns 接口响应
 */
export function addFavorite(newsId: number): Promise<ApiResponse> {
  return request({
    url: '/favorite/add',
    method: 'post',
    data: { newsId }
  })
}

/**
 * 取消收藏
 * @param newsId - 要取消收藏的新闻ID
 * @returns 接口响应
 */
export function removeFavorite(newsId: number): Promise<ApiResponse> {
  return request({
    url: '/favorite/remove',
    method: 'delete',
    params: { newsId }
  })
}

/**
 * 清空所有收藏
 * @returns 接口响应，data.count 表示本次清空的收藏条数
 */
export function clearFavorites(): Promise<ApiResponse<{ count: number }>> {
  return request({
    url: '/favorite/clear_all_favorite',
    method: 'delete'
  })
}

/**
 * 检查某条新闻是否已收藏（详情页进入时判断收藏状态）
 * @param newsId - 新闻ID
 * @returns 接口响应，data.isFavorited 表示是否已收藏
 */
export function checkFavorite(newsId: number): Promise<ApiResponse<{ isFavorited: boolean }>> {
  return request({
    url: '/favorite/check',
    method: 'get',
    params: { newsId }
  })
}