/**
 * 搜索历史相关 API 接口封装（需要登录态）
 */
import request from '@/utils/request'

/** 单条搜索历史 */
export interface SearchHistoryItem {
  /** 历史ID */
  id: number
  /** 关键词 */
  keyword: string
  /** 搜索时间 */
  searchTime: string
}

/** 搜索历史列表响应 */
export interface SearchHistoryList {
  list: SearchHistoryItem[]
  total: number
}

/**
 * 添加一条搜索历史（搜索成功后调用，去重逻辑由后端处理）
 * @param keyword - 搜索关键词
 */
export function addSearchHistory(keyword: string): Promise<ApiResponse<SearchHistoryItem>> {
  return request({
    url: '/search-history/add',
    method: 'post',
    data: { keyword }
  })
}

/**
 * 获取当前用户的最近搜索历史
 * @param limit - 返回条数，默认 10
 */
export function getSearchHistoryList(limit = 10): Promise<ApiResponse<SearchHistoryList>> {
  return request({
    url: '/search-history/list',
    method: 'get',
    params: { limit }
  })
}

/**
 * 清空当前用户的所有搜索历史
 */
export function clearSearchHistory(): Promise<ApiResponse<null>> {
  return request({
    url: '/search-history/clear',
    method: 'delete'
  })
}