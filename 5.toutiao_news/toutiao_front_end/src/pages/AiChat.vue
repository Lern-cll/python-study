<template>
  <div class="ai-chat-page">
    <div class="header">
      <h1 class="title">AI 问答助手</h1>
    </div>
    <div class="chat-container" ref="chatContainer">
      <div v-if="messages.length === 0" class="empty-chat">
        <el-icon :size="48"><ChatDotSquare /></el-icon>
        <p>有什么问题可以问我哦~</p>
      </div>
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="['message', msg.type]"
      >
        <div class="message-avatar">
          <el-icon :size="24">
            <component :is="msg.type === 'user' ? 'User' : 'MagicStick'" />
          </el-icon>
        </div>
        <div class="message-content">
          <div class="message-bubble">{{ msg.content }}</div>
        </div>
      </div>
      <div v-if="isTyping" class="message ai">
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
    <div class="input-area">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="2"
        placeholder="输入您的问题..."
        resize="none"
        @keyup.enter.ctrl="handleSend"
      />
      <el-button type="primary" :disabled="!inputText.trim() || isTyping" @click="handleSend">
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { ChatDotSquare, User, MagicStick, Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const messages = ref([])
const inputText = ref('')
const isTyping = ref(false)
const chatContainer = ref(null)

// 模拟AI回复
const mockAIResponse = (question) => {
  const responses = [
    '这是一个很好的问题！根据我的分析，这涉及到多个方面的考量。',
    '让我来帮您解答这个问题。首先，我们需要了解基本概念...',
    '您提到的这个问题非常有意思。我建议可以从以下几个方面入手：',
    '感谢您的提问。关于这个问题，我的建议是...',
    '好的，让我为您详细解答。这是一个复杂的问题，我们需要逐步分析...'
  ]
  return responses[Math.floor(Math.random() * responses.length)]
}

const handleSend = async () => {
  const text = inputText.value.trim()
  if (!text) return

  // 添加用户消息
  messages.value.push({
    type: 'user',
    content: text
  })
  inputText.value = ''

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  // 模拟AI思考
  isTyping.value = true
  await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000))
  isTyping.value = false

  // 添加AI回复
  messages.value.push({
    type: 'ai',
    content: mockAIResponse(text)
  })

  await nextTick()
  scrollToBottom()
}

const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}
</script>

<style lang="scss" scoped>
.ai-chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;

  .header {
    background: #fff;
    padding: 12px 15px;
    border-bottom: 1px solid #e8e8e8;

    .title {
      font-size: 1rem;
      font-weight: 600;
      color: #333;
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
  }
}
</style>