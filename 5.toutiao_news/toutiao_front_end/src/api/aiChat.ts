/**
 * AI 会话历史接口封装（与后端 /api/ai-chat/* 对接）
 * 千问调用由 src/api/ai.ts 的 chat() 负责，不在此处
 */
import request from '@/utils/request'

/** 单条消息（与千问 ChatMessage 协议对齐） */
export interface ChatMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
}

/** 会话详情（含完整 messages） */
export interface SessionDetail {
  id: number
  title: string
  model: string
  messages: ChatMessage[]
  createdAt: string
  updatedAt: string
}

/** 会话列表项（不含 messages） */
export interface SessionListItem {
  id: number
  title: string
  model: string
  updatedAt: string
  messageCount: number
}

/** 会话列表响应 */
export interface SessionListPayload {
  list: SessionListItem[]
  total: number
  hasMore: boolean
}

/** 搜索结果项（极简字段） */
export interface SessionSearchItem {
  id: number
  title: string
  updatedAt: string
}

/** 搜索响应 */
export interface SessionSearchPayload {
  list: SessionSearchItem[]
  total: number
}

/** 创建会话入参 */
export interface SessionCreatePayload {
  model: string
  messages: ChatMessage[]
  title?: string
}

/** 更新会话入参 */
export interface SessionUpdatePayload {
  model: string
  messages: ChatMessage[]
  title?: string
}

/**
 * 创建会话（首条 AI 回复成功后调用）
 */
export function createSession(
  payload: SessionCreatePayload
): Promise<ApiResponse<SessionDetail>> {
  return request({
    url: '/ai-chat/sessions',
    method: 'post',
    data: payload
  })
}

/**
 * 更新会话（后续每轮 AI 回复成功后调用，语义为全量覆盖 messages）
 */
export function updateSession(
  sessionId: number,
  payload: SessionUpdatePayload
): Promise<ApiResponse<SessionDetail>> {
  return request({
    url: `/ai-chat/sessions/${sessionId}`,
    method: 'put',
    data: payload
  })
}

/**
 * 获取会话列表（分页，按 updatedAt DESC）
 */
export function getSessionList(params?: {
  page?: number
  pageSize?: number
}): Promise<ApiResponse<SessionListPayload>> {
  return request({
    url: '/ai-chat/sessions',
    method: 'get',
    params: { page: 1, pageSize: 10, ...params }
  })
}

/**
 * 搜索会话（title + messages 内容命中，最多 5 条）
 */
export function searchSessions(
  keyword: string
): Promise<ApiResponse<SessionSearchPayload>> {
  return request({
    url: '/ai-chat/sessions/search',
    method: 'get',
    params: { keyword }
  })
}

/**
 * 获取会话详情（含完整 messages）
 */
export function getSessionDetail(
  sessionId: number
): Promise<ApiResponse<SessionDetail>> {
  return request({
    url: `/ai-chat/sessions/${sessionId}`,
    method: 'get'
  })
}

/**
 * 删除会话（硬删）
 */
export function deleteSession(
  sessionId: number
): Promise<ApiResponse<{ deletedCount: number }>> {
  return request({
    url: `/ai-chat/sessions/${sessionId}`,
    method: 'delete'
  })
}