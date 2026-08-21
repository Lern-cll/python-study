/**
 * AI 问答状态管理
 * 负责：
 * 1) 当前对话 messages 持久化在 pinia（切 tab 不丢）
 * 2) 历史会话的拉取 / 搜索 / 删除
 * 3) 抽屉开关状态
 * 4) 调用千问 + 首条成功后落库（POST），后续每轮成功后更新（PUT）
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { chat, type ChatMessage as QwenMessage } from '@/api/ai'
import { aiChatConfig } from '@/config/api'
import {
  createSession,
  updateSession,
  getSessionList,
  searchSessions,
  getSessionDetail,
  deleteSession as deleteSessionApi,
  type SessionListItem,
  type SessionSearchItem,
  type ChatMessage
} from '@/api/aiChat'

/** 千问 system prompt（与 AiChat.vue 历史约定一致） */
const SYSTEM_PROMPT =
  '你是头条新闻 App 的智能助手，回答简洁友好，必要时可结合新闻领域知识给出建议。'

/** 前端展示用消息类型（type 字段贴合 UI 渲染） */
interface UiMessage {
  type: 'user' | 'ai'
  content: string
}

export const useAiChatStore = defineStore('aiChat', () => {
  // ============ 状态 ============
  // 当前会话的全部消息气泡
  const messages = ref<UiMessage[]>([])
  // 当前会话 ID；null = 尚未入库（首次 AI 回成功后写入）
  const currentSessionId = ref<number | null>(null)
  // 千问是否正在生成回复
  const isTyping = ref(false)
  // 抽屉是否打开
  const drawerOpen = ref(false)
  // 当前搜索关键词（与抽屉内的 input 绑定）
  const searchKeyword = ref('')
  // 普通列表（分页）
  const sessionList = ref<SessionListItem[]>([])
  // 搜索结果列表（最多 5 条）
  const searchResults = ref<SessionSearchItem[]>([])
  // 普通列表加载态
  const sessionListLoading = ref(false)
  // 普通列表是否还有更多
  const sessionListHasMore = ref(false)
  // 普通列表下一页页码
  const sessionListPage = ref(1)

  // ============ 工具方法 ============
  /**
   * 从 UI 消息中提取首条 user 消息的前 30 字符作为标题
   */
  const genTitle = (msgs: UiMessage[]): string => {
    for (const m of msgs) {
      if (m.type === 'user') {
        return m.content.replace(/\n/g, ' ').trim().slice(0, 30)
      }
    }
    return ''
  }

  /**
   * UI 消息 → 千问消息（含 system 头）
   */
  const toQwenMessages = (msgs: UiMessage[]): QwenMessage[] => {
    const history: QwenMessage[] = msgs.map((m) => ({
      role: m.type === 'user' ? 'user' : 'assistant',
      content: m.content
    }))
    return [{ role: 'system', content: SYSTEM_PROMPT }, ...history]
  }

  /**
   * 千问/DB 消息 → UI 消息（过滤掉 system）
   */
  const toUiMessages = (msgs: ChatMessage[]): UiMessage[] =>
    msgs
      .filter((m) => m.role === 'user' || m.role === 'assistant')
      .map((m) => ({ type: m.role === 'user' ? 'user' : 'ai', content: m.content }))

  // ============ Action ============
  /**
   * 发送消息：调千问 → 成功后入库（首次 POST / 后续 PUT）
   */
  const send = async (text: string) => {
    if (isTyping.value) return
    const trimmed = text.trim()
    if (!trimmed) return

    // 1) 推入用户消息
    messages.value.push({ type: 'user', content: trimmed })
    isTyping.value = true

    try {
      // 2) 调千问
      const reply = await chat(toQwenMessages(messages.value))
      messages.value.push({ type: 'ai', content: reply })

      // 3) 落库：首次 POST，后续 PUT
      const basePayload = {
        model: aiChatConfig.model,
        messages: toQwenMessages(messages.value).slice(1) as ChatMessage[]
      }
      const title = genTitle(messages.value)
      try {
        if (currentSessionId.value === null) {
          const res = await createSession({ ...basePayload, title })
          currentSessionId.value = res.data.id
        } else {
          await updateSession(currentSessionId.value, {
            ...basePayload,
            title
          })
        }
      } catch (dbErr) {
        // 落库失败不阻断聊天，只在控制台告警；下次发送会重试
        console.warn('[aiChatStore] 会话落库失败：', dbErr)
      }
    } catch (err: any) {
      ElMessage.error(err?.message || '千问调用失败，请稍后重试')
    } finally {
      isTyping.value = false
    }
  }

  /**
   * 新会话：清空 messages / currentSessionId / searchKeyword
   */
  const newChat = () => {
    messages.value = []
    currentSessionId.value = null
    searchKeyword.value = ''
  }

  /**
   * 加载历史会话详情：写入 messages + 设置 currentSessionId
   */
  const loadSession = async (sessionId: number) => {
    try {
      const res = await getSessionDetail(sessionId)
      messages.value = toUiMessages(res.data.messages)
      currentSessionId.value = res.data.id
      drawerOpen.value = false
    } catch {
      ElMessage.error('加载会话失败')
    }
  }

  /**
   * 删除会话：同步从列表 / 搜索结果中移除；若当前会话被删则触发 newChat
   */
  const removeSession = async (sessionId: number) => {
    try {
      await deleteSessionApi(sessionId)
      sessionList.value = sessionList.value.filter((s) => s.id !== sessionId)
      searchResults.value = searchResults.value.filter((s) => s.id !== sessionId)
      if (currentSessionId.value === sessionId) {
        newChat()
      }
    } catch {
      ElMessage.error('删除失败')
    }
  }

  /**
   * 抽屉开关切换
   */
  const toggleDrawer = () => {
    drawerOpen.value = !drawerOpen.value
  }

  /**
   * 强制关闭抽屉
   */
  const closeDrawer = () => {
    drawerOpen.value = false
  }

  /**
   * 拉取普通列表（分页）
   * @param reset 是否从第一页开始
   */
  const fetchSessionList = async (reset = false) => {
    if (reset) {
      sessionListPage.value = 1
      sessionList.value = []
    }
    sessionListLoading.value = true
    try {
      const res = await getSessionList({
        page: sessionListPage.value,
        pageSize: 10
      })
      const payload = res.data
      sessionList.value = reset ? payload.list : [...sessionList.value, ...payload.list]
      sessionListHasMore.value = payload.hasMore
      sessionListPage.value++
    } catch {
      ElMessage.error('获取会话列表失败')
    } finally {
      sessionListLoading.value = false
    }
  }

  /**
   * 加载下一页（无限滚动用）
   */
  const loadMoreSessions = async () => {
    if (sessionListLoading.value || !sessionListHasMore.value) return
    await fetchSessionList(false)
  }

  /**
   * 搜索会话（最多 5 条）
   */
  const searchSession = async (keyword: string) => {
    searchKeyword.value = keyword
    const kw = keyword.trim()
    if (!kw) {
      searchResults.value = []
      return
    }
    try {
      const res = await searchSessions(kw)
      searchResults.value = res.data.list
    } catch {
      ElMessage.error('搜索失败')
    }
  }

  return {
    // 状态
    messages,
    currentSessionId,
    isTyping,
    drawerOpen,
    searchKeyword,
    sessionList,
    searchResults,
    sessionListLoading,
    sessionListHasMore,
    // action
    send,
    newChat,
    loadSession,
    removeSession,
    toggleDrawer,
    closeDrawer,
    fetchSessionList,
    loadMoreSessions,
    searchSession
  }
})