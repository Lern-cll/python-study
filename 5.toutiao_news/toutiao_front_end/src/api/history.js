/**
 * 浏览历史相关 API 接口封装
 */
import request from '@/utils/request'

/**
 * 获取浏览历史列表
 * @param {object} params - 查询参数 { page, pageSize }
 * @returns {promise} 返回历史列表
 */
export function getHistoryList(params) {
  return request({
    url: '/history/list',
    method: 'get',
    params
  })
}

/**
 * 添加浏览记录
 * @param {number} newsId - 新闻ID
 * @returns {promise} 返回添加结果
 */
export function addHistory(newsId) {
  return request({
    url: '/history/add',
    method: 'post',
    data: { newsId }
  })
}

/**
 * 删除单条浏览历史
 * @param {number} historyId - 历史记录ID
 * @returns {promise} 返回删除结果
 */
export function deleteHistory(historyId) {
  return request({
    url: `/history/delete/${historyId}`,
    method: 'delete'
  })
}

/**
 * 清空所有浏览历史
 * @returns {promise} 返回清空结果
 */
export function clearHistory() {
  return request({
    url: '/history/clear',
    method: 'delete'
  })
}