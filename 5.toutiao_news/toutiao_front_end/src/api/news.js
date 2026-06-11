/**
 * 新闻相关 API 接口封装
 */
import request from '@/utils/request'

/**
 * 获取新闻分类列表
 * @returns {promise} 返回分类列表
 */
export function getCategories() {
  return request({
    url: '/news/categories',
    method: 'get'
  })
}

/**
 * 获取新闻列表
 * @param {object} params - 查询参数 { page, pageSize, categoryId }
 * @returns {promise} 返回新闻列表
 */
export function getNewsList(params) {
  return request({
    url: '/news/list',
    method: 'get',
    params
  })
}

/**
 * 获取新闻详情
 * @param {number} id - 新闻ID
 * @returns {promise} 返回新闻详情
 */
export function getNewsDetail(id) {
  return request({
    url: `/news/detail/${id}`,
    method: 'get'
  })
}