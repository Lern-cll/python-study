/**
 * 收藏相关 API 接口封装
 */
import request from '@/utils/request'

// 请求参数类型
interface FavoriteListParams {
  page?: number
  pageSize?: number
}

/**
 * 获取收藏列表
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
 */
export function removeFavorite(favoriteId: number): Promise<ApiResponse> {
  return request({
    url: '/favorite/remove',
    method: 'delete',
    data: { favoriteId }
  })
}

/**
 * 清空所有收藏
 */
export function clearFavorites(): Promise<ApiResponse> {
  return request({
    url: '/favorite/clear',
    method: 'delete'
  })
}

/**
 * 检查收藏状态
 */
export function checkFavorite(newsId: number): Promise<ApiResponse<{ isFavorited: boolean }>> {
  return request({
    url: '/favorite/check',
    method: 'get',
    params: { newsId }
  })
}