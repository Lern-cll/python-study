/**
 * 浏览历史相关 API 接口封装
 */
import request from '@/utils/request'

// 请求参数类型
interface HistoryListParams {
  page?: number
  pageSize?: number
}

/**
 * 获取浏览历史列表
 */
export function getHistoryList(params: HistoryListParams): Promise<ApiResponse> {
  return request({
    url: '/history/list',
    method: 'get',
    params
  })
}

/**
 * 添加浏览记录
 */
export function addHistory(newsId: number): Promise<ApiResponse> {
  return request({
    url: '/history/add',
    method: 'post',
    data: { newsId }
  })
}

/**
 * 删除单条浏览历史
 */
export function deleteHistory(historyId: number): Promise<ApiResponse> {
  return request({
    url: `/history/delete/${historyId}`,
    method: 'delete'
  })
}

/**
 * 清空所有浏览历史
 */
export function clearHistory(): Promise<ApiResponse> {
  return request({
    url: '/history/clear',
    method: 'delete'
  })
}