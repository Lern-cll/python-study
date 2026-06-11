/**
 * 收藏相关 API 接口封装
 */
import request from '@/utils/request'

/**
 * 获取收藏列表
 * @param {object} params - 查询参数 { page, pageSize }
 * @returns {promise} 返回收藏列表
 */
export function getFavoriteList(params) {
  return request({
    url: '/favorite/list',
    method: 'get',
    params
  })
}

/**
 * 添加收藏
 * @param {number} newsId - 新闻ID
 * @returns {promise} 返回收藏结果
 */
export function addFavorite(newsId) {
  return request({
    url: '/favorite/add',
    method: 'post',
    data: { newsId }
  })
}

/**
 * 取消收藏
 * @param {number} favoriteId - 收藏ID
 * @returns {promise} 返回取消结果
 */
export function removeFavorite(favoriteId) {
  return request({
    url: '/favorite/remove',
    method: 'delete',
    data: { favoriteId }
  })
}

/**
 * 清空所有收藏
 * @returns {promise} 返回清空结果
 */
export function clearFavorites() {
  return request({
    url: '/favorite/clear',
    method: 'delete'
  })
}

/**
 * 检查收藏状态
 * @param {number} newsId - 新闻ID
 * @returns {promise} 返回是否已收藏
 */
export function checkFavorite(newsId) {
  return request({
    url: '/favorite/check',
    method: 'get',
    params: { newsId }
  })
}