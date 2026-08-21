import axios, { AxiosError } from 'axios'
import { aiChatConfig } from '@/config/api'

/**
 * 千问消息条目（兼容 OpenAI Chat Completions 协议）
 * - role: 'system' | 'user' | 'assistant'
 */
export interface ChatMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
}

/**
 * 单独为千问创建的 axios 实例：
 * 1) baseURL 走 vite dev 代理 /qwen（避免浏览器 CORS）
 * 2) 不挂全局拦截器，不会被自动加上用户登录态的 Authorization 头
 */
const qwenClient = axios.create({
  baseURL: '/qwen',
  timeout: 60_000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * 调用千问 chat completions（非流式）
 * @param messages 完整对话上下文（含 system / user / assistant）
 * @returns AI 回复的纯文本
 */
export const chat = async (messages: ChatMessage[]): Promise<string> => {
  try {
    const res = await qwenClient.post(aiChatConfig.apiEndpoint, {
      model: aiChatConfig.model,
      messages,
      stream: false
    }, {
      headers: {
        Authorization: `Bearer ${aiChatConfig.apiKey}`
      }
    })

    const choice = res.data?.choices?.[0]
    const content: string | undefined = choice?.message?.content
    if (!content) {
      throw new Error('千问返回数据格式异常，未找到 choices[0].message.content')
    }
    return content
  } catch (err) {
    const error = err as AxiosError<{ message?: string; error?: { message?: string } }>
    const apiMsg =
      error.response?.data?.error?.message ||
      error.response?.data?.message ||
      error.message
    throw new Error(`千问调用失败：${apiMsg || '未知错误'}`)
  }
}
