<template>
  <div class="ai-chat-page">
    <!-- 顶部：左侧抽屉触发图标 + 标题 -->
    <div class="header">
      <el-icon class="header-icon" @click="handleToggleDrawer">
        <component :is="store.drawerOpen ? Close : Memo" />
      </el-icon>
      <h1 class="title">AI 问答助手</h1>
    </div>

    <!-- 对话列表 -->
    <div class="chat-container" ref="chatContainer">
      <!-- 空状态 -->
      <div v-if="store.messages.length === 0" class="empty-chat">
        <el-icon :size="48"><ChatDotSquare /></el-icon>
        <p>有什么问题可以问我哦~</p>
      </div>
      <!-- 消息气泡列表：type=user 为右侧用户消息，type=ai 为左侧 AI 回复 -->
      <div
        v-for="(msg, index) in store.messages"
        :key="index"
        :class="['message', msg.type]"
      >
        <div class="message-avatar">
          <el-icon :size="24">
            <component :is="msg.type === 'user' ? 'User' : 'MagicStick'" />
          </el-icon>
        </div>
        <div class="message-content">
          <!-- AI 回复走 markdown 渲染；用户消息保持纯文本 -->
          <div
            v-if="msg.type === 'ai'"
            class="message-bubble markdown-body"
            v-html="renderMd(msg.content)"
          ></div>
          <div v-else class="message-bubble">{{ msg.content }}</div>
        </div>
      </div>
      <!-- AI 思考中气泡 -->
      <div v-if="store.isTyping" class="message ai">
        <div class="message-avatar">
          <el-icon :size="24"><MagicStick /></el-icon>
        </div>
        <div class="message-content">
          <div class="message-bubble typing">
            <span>思考中</span>
            <el-icon class="is-loading"><Loading /></el-icon>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区：多行输入 + 发送按钮 + 新建会话圆形 +按钮 -->
    <div class="input-area">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="2"
        placeholder="输入您的问题...（Enter 发送，Shift+Enter 换行）"
        resize="none"
        @keydown.enter.exact="handleEnterKey"
      />
      <el-button type="primary" :disabled="!inputText.trim() || store.isTyping" @click="handleSend">
        发送
      </el-button>
      <el-button
        circle
        :disabled="store.isTyping"
        class="new-chat-btn"
        title="新会话"
        @click="handleNewChat"
      >
        <el-icon><Plus /></el-icon>
      </el-button>
    </div>

    <!-- 历史会话抽屉：从左侧滑入，宽度 80% -->
    <el-drawer
      :model-value="store.drawerOpen"
      direction="ltr"
      size="80%"
      :with-header="false"
      :modal="true"
      @update:model-value="handleDrawerUpdate"
    >
      <div class="drawer-content">
        <div class="drawer-header">
          <h2 class="drawer-title">历史会话</h2>
          <el-input
            v-model="searchInput"
            placeholder="搜索会话（title 或内容）"
            clearable
            @input="handleSearchInput"
            @clear="handleSearchClear"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <div
          class="drawer-list"
          ref="drawerScrollRef"
          v-loading="store.sessionListLoading"
          @scroll="handleDrawerScroll"
        >
          <!-- 搜索模式：渲染 searchResults（最多 5 条） -->
          <template v-if="store.searchKeyword">
            <div
              v-for="item in store.searchResults"
              :key="item.id"
              class="drawer-item"
              @click="handleSelectSession(item.id)"
            >
              <el-icon class="drawer-item-icon"><ChatDotRound /></el-icon>
              <div class="drawer-item-body">
                <div class="drawer-item-title">{{ item.title || '新会话' }}</div>
                <div class="drawer-item-time">{{ formatRelativeTime(item.updatedAt) }}</div>
              </div>
              <el-button
                text
                type="danger"
                size="small"
                @click.stop="handleDeleteSession(item.id)"
              >删除</el-button>
            </div>
            <div v-if="store.searchResults.length === 0" class="empty-state">
              <el-icon :size="36"><Search /></el-icon>
              <p>没有匹配结果</p>
            </div>
          </template>

          <!-- 普通列表模式：分页渲染 sessionList -->
          <template v-else>
            <div
              v-for="item in store.sessionList"
              :key="item.id"
              :class="['drawer-item', { active: store.currentSessionId === item.id }]"
              @click="handleSelectSession(item.id)"
            >
              <el-icon class="drawer-item-icon"><ChatDotRound /></el-icon>
              <div class="drawer-item-body">
                <div class="drawer-item-title">{{ item.title || '新会话' }}</div>
                <div class="drawer-item-time">
                  {{ formatRelativeTime(item.updatedAt) }} · {{ item.messageCount }} 条消息
                </div>
              </div>
              <el-button
                text
                type="danger"
                size="small"
                @click.stop="handleDeleteSession(item.id)"
              >删除</el-button>
            </div>
            <div
              v-if="store.sessionList.length === 0 && !store.sessionListLoading"
              class="empty-state"
            >
              <el-icon :size="36"><ChatDotRound /></el-icon>
              <p>暂无历史会话</p>
            </div>
          </template>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import {
  ChatDotSquare,
  ChatDotRound,
  User,
  MagicStick,
  Loading,
  Memo,
  Close,
  Plus,
  Search
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'
import { useAiChatStore } from '@/pinia/aiChatStore'

// ============ 状态 ============
const store = useAiChatStore()

// markdown-it 实例（启用链接新窗口打开，保留代码块语言提示）
const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true
})

/**
 * 把 markdown 文本渲染为安全 HTML
 */
const renderMd = (text: string) => {
  if (!text) return ''
  return DOMPurify.sanitize(md.render(text))
}

// 输入框绑定值（页面级，不入 store）
const inputText = ref('')
// 抽屉内搜索框本地值（store.searchKeyword 是搜索动作后的真实状态）
const searchInput = ref('')
// 对话列表容器 DOM（用于滚到底部）
const chatContainer = ref<HTMLElement | null>(null)
// 抽屉内列表容器 DOM（用于触底加载更多）
const drawerScrollRef = ref<HTMLElement | null>(null)

// ============ 事件处理 ============
/**
 * Enter 键统一入口
 */
const handleEnterKey = (e: KeyboardEvent) => {
  if (e.shiftKey) return
  if (e.isComposing || e.keyCode === 229) return
  if (store.isTyping) return
  e.preventDefault()
  handleSend()
}

/**
 * 发送：委托给 store.send
 */
const handleSend = async () => {
  const text = inputText.value.trim()
  if (!text || store.isTyping) return
  inputText.value = ''
  await store.send(text)
  await nextTick()
  scrollToBottom()
}

/**
 * 新建会话：清空 pinia 状态 + 清空输入框
 */
const handleNewChat = () => {
  store.newChat()
  inputText.value = ''
  searchInput.value = ''
}

/**
 * 抽屉开关（标题图标点击）
 */
const handleToggleDrawer = () => {
  store.toggleDrawer()
}

/**
 * 抽屉内部双向绑定的 model-value 更新
 */
const handleDrawerUpdate = (val: boolean) => {
  if (!val) store.closeDrawer()
}

/**
 * 选择某条历史会话
 */
const handleSelectSession = async (sessionId: number) => {
  await store.loadSession(sessionId)
  await nextTick()
  scrollToBottom()
}

/**
 * 删除单条历史会话（二次确认）
 */
const handleDeleteSession = async (sessionId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这条对话吗？', '提示', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await store.removeSession(sessionId)
    ElMessage.success('已删除')
  } catch {
    // 用户取消
  }
}

// ============ 搜索（防抖）============
let searchTimer: number | null = null
/**
 * 抽屉搜索框输入：300ms 防抖触发 store.searchSession
 */
const handleSearchInput = (val: string | number) => {
  if (searchTimer) clearTimeout(searchTimer)
  const kw = String(val)
  searchTimer = window.setTimeout(() => {
    store.searchSession(kw)
  }, 300)
}

/**
 * 抽屉搜索框清空
 */
const handleSearchClear = () => {
  if (searchTimer) clearTimeout(searchTimer)
  store.searchSession('')
  searchInput.value = ''
}

// ============ 抽屉列表触底加载更多 ============
/**
 * 抽屉列表滚动触底：自动加载下一页
 */
const handleDrawerScroll = async () => {
  // 搜索模式下不分页，不触发
  if (store.searchKeyword) return
  const container = drawerScrollRef.value
  if (!container) return
  if (container.scrollHeight <= container.clientHeight) return
  const scrollBottom =
    container.scrollHeight - container.scrollTop - container.clientHeight
  if (scrollBottom < 80) {
    await store.loadMoreSessions()
  }
}

// ============ 抽屉打开时拉取列表 ============
watch(
  () => store.drawerOpen,
  (open) => {
    if (open && store.sessionList.length === 0 && !store.searchKeyword) {
      store.fetchSessionList(true)
    }
  }
)

// ============ 工具 ============
/**
 * 把对话列表滚到最底部
 */
const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

/**
 * 友好时间格式化：刚刚 / X 分钟前 / 昨天 / YYYY-MM-DD
 */
const formatRelativeTime = (iso: string): string => {
  if (!iso) return ''
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return ''
  const now = Date.now()
  const diff = Math.floor((now - date.getTime()) / 1000)
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
  if (diff < 86400) return '昨天'
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}

// ============ 消息新增时自动滚到底 ============
watch(
  () => store.messages.length,
  async () => {
    await nextTick()
    scrollToBottom()
  }
)
</script>

<style lang="scss" scoped>
.ai-chat-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f5f5f5;

  .header {
    background: #fff;
    padding: 12px 15px;
    border-bottom: 1px solid #e8e8e8;
    display: flex;
    align-items: center;
    gap: 10px;

    .header-icon {
      font-size: 20px;
      color: #666;
      cursor: pointer;
      padding: 4px;

      &:hover {
        color: #e63946;
      }
    }

    .title {
      font-size: 1rem;
      font-weight: 600;
      color: #333;
      flex: 1;
      margin: 0;
    }
  }

  .chat-container {
    flex: 1;
    overflow-y: auto;
    padding: 15px;

    .empty-chat {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: #999;

      .el-icon {
        margin-bottom: 15px;
      }
    }

    .message {
      display: flex;
      margin-bottom: 15px;

      &.user {
        flex-direction: row-reverse;

        .message-content {
          margin-right: 0;
          margin-left: 10px;
        }

        .message-bubble {
          background: #e63946;
          color: #fff;
          border-radius: 18px 18px 0 18px;
        }
      }

      &.ai {
        .message-bubble {
          background: #fff;
          color: #333;
          border-radius: 18px 18px 18px 0;
        }

        .message-bubble.markdown-body {
          :deep(p) {
            margin: 0 0 8px;
            &:last-child { margin-bottom: 0; }
          }
          :deep(h1), :deep(h2), :deep(h3) {
            font-size: 1rem;
            font-weight: 600;
            margin: 10px 0 6px;
            line-height: 1.4;
          }
          :deep(ul), :deep(ol) {
            margin: 6px 0;
            padding-left: 20px;
          }
          :deep(li) {
            margin: 2px 0;
          }
          :deep(code) {
            background: #f3f3f3;
            color: #e63946;
            padding: 1px 5px;
            border-radius: 3px;
            font-size: 0.85em;
          }
          :deep(pre) {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 10px 12px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 8px 0;
            code {
              background: transparent;
              color: inherit;
              padding: 0;
            }
          }
          :deep(blockquote) {
            margin: 8px 0;
            padding: 4px 10px;
            border-left: 3px solid #e63946;
            background: #f9f9f9;
            color: #666;
          }
          :deep(strong) {
            font-weight: 600;
            color: #222;
          }
          :deep(a) {
            color: #e63946;
            text-decoration: underline;
          }
        }
      }

      .message-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        background: #f0f0f0;

        .el-icon {
          color: #999;
        }
      }

      .message-content {
        max-width: 70%;

        .message-bubble {
          padding: 10px 15px;
          line-height: 1.5;
          font-size: 0.9375rem;

          &.typing {
            display: flex;
            align-items: center;
            gap: 5px;

            span {
              font-size: 0.75rem;
            }
          }
        }
      }
    }
  }

  .input-area {
    background: #fff;
    padding: 10px 15px;
    padding-bottom: calc(10px + env(safe-area-inset-bottom));
    display: flex;
    gap: 10px;
    align-items: flex-end;

    .el-input {
      flex: 1;
    }

    .el-button {
      flex-shrink: 0;
    }

    .new-chat-btn {
      background: #f5f5f5;
      border-color: #e8e8e8;
      color: #666;

      &:hover:not(.is-disabled) {
        background: #e63946;
        color: #fff;
        border-color: #e63946;
      }
    }
  }
}

// 抽屉内容（el-drawer 自带遮罩与滑入动画，这里只覆盖内部）
:deep(.el-drawer__body) {
  padding: 0;
}

.drawer-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #fff;

  .drawer-header {
    padding: 15px;
    border-bottom: 1px solid #f0f0f0;
    flex-shrink: 0;

    .drawer-title {
      font-size: 1rem;
      font-weight: 600;
      color: #333;
      margin: 0 0 10px;
    }
  }

  .drawer-list {
    flex: 1;
    overflow-y: auto;

    .drawer-item {
      display: flex;
      align-items: center;
      padding: 12px 15px;
      border-bottom: 1px solid #f5f5f5;
      cursor: pointer;
      gap: 10px;

      &:active {
        background: #f9f9f9;
      }

      &.active {
        background: #fef2f2;

        .drawer-item-title {
          color: #e63946;
        }
      }

      .drawer-item-icon {
        font-size: 18px;
        color: #e63946;
        flex-shrink: 0;
      }

      .drawer-item-body {
        flex: 1;
        min-width: 0;

        .drawer-item-title {
          font-size: 0.9375rem;
          color: #333;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .drawer-item-time {
          font-size: 0.75rem;
          color: #999;
          margin-top: 2px;
        }
      }
    }

    .empty-state {
      padding: 60px 20px;
      text-align: center;
      color: #999;

      .el-icon {
        margin-bottom: 10px;
      }

      p {
        margin: 0;
        font-size: 0.875rem;
      }
    }
  }
}
</style>