/**
 * 浏览历史相关 API 接口封装
 */
import request from '@/utils/request'

// ============ 请求参数类型 ============
/** 浏览历史列表分页参数 */
interface HistoryListParams {
  /** 当前页码 */
  page?: number
  /** 每页条数 */
  pageSize?: number
}

/**
 * 获取浏览历史列表（分页）
 * @param params - 分页参数
 * @returns 历史列表的接口响应
 */
export function getHistoryList(params: HistoryListParams): Promise<ApiResponse> {
  return request({
    url: '/history/list',
    method: 'get',
    params
  })
}

/**
 * 添加浏览记录（进入新闻详情页时调用）
 * @param newsId - 被浏览的新闻ID
 * @returns 接口响应
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
 * @param historyId - 历史记录ID
 * @returns 接口响应
 */
export function deleteHistory(historyId: number): Promise<ApiResponse> {
  return request({
    url: `/history/delete/${historyId}`,
    method: 'delete'
  })
}

/**
 * 清空所有浏览历史
 * @returns 接口响应
 */
export function clearHistory(): Promise<ApiResponse> {
  return request({
    url: '/history/clear',
    method: 'delete'
  })
}