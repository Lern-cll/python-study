<!--
  单条收藏项
  - 布局：左图 + 右侧（标题 / 作者 / 收藏时间）+ 最右操作按钮
  - 整行点击跳转新闻详情，操作按钮区域阻止冒泡
  - 通过 emit('click') / emit('cancel') 把行为交给父组件
-->
<template>
  <div class="favorite-item" @click="handleRowClick">
    <!-- 左侧：缩略图 -->
    <div class="thumb" :class="{ 'is-loading': !imageLoaded }">
      <img
        v-show="imageLoaded"
        :src="item.image"
        :alt="item.title"
        @load="onImageLoad"
        @error="onImageError"
      />
      <div v-if="!imageLoaded" class="thumb-placeholder">
        <el-icon class="is-loading"><Loading /></el-icon>
      </div>
    </div>

    <!-- 右侧主体 -->
    <div class="body">
      <h3 class="title text-ellipsis-2">{{ item.title }}</h3>
      <p class="author text-ellipsis-1">{{ item.author || '头条号' }}</p>
      <p class="meta">收藏时间：{{ formatTime(item.favoriteTime) }}</p>
    </div>

    <!-- 最右：取消收藏按钮 -->
    <div class="actions" @click.stop>
      <el-button
        text
        type="danger"
        size="small"
        @click="handleCancelClick"
      >
        取消收藏
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Loading } from '@element-plus/icons-vue'

const props = defineProps({
  // 单条收藏数据
  item: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['click', 'cancel'])

// 缩略图是否加载完成（用于占位兜底）
const imageLoaded = ref(false)

/** 图片加载成功，隐藏占位图 */
const onImageLoad = () => {
  imageLoaded.value = true
}

/** 图片加载失败：同样隐藏占位图，避免无限 loading */
const onImageError = () => {
  imageLoaded.value = true
}

/** 整行点击 → 通知父组件跳转 */
const handleRowClick = () => {
  emit('click')
}

/** 取消收藏按钮点击 → 通知父组件弹窗确认 */
const handleCancelClick = () => {
  emit('cancel')
}

/**
 * 收藏时间格式化（友好时间）：
 *   < 1 分钟 → 刚刚
 *   < 60 分钟 → N 分钟前
 *   < 24 小时 → N 小时前
 *   < 7 天   → N 天前
 *   其他     → yyyy-mm-dd hh:mm
 */
const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  if (Number.isNaN(date.getTime())) return ''
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}
</script>

<style lang="scss" scoped>
.favorite-item {
  display: flex;
  align-items: stretch;
  padding: 15px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  gap: 12px;

  .thumb {
    width: 90px;
    height: 70px;
    border-radius: 6px;
    overflow: hidden;
    flex-shrink: 0;
    background: #f0f0f0;
    position: relative;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: opacity 0.3s ease;
    }

    .thumb-placeholder {
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #f0f0f0;
      color: #ccc;
      font-size: 20px;
    }
  }

  .body {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    justify-content: space-between;

    .title {
      font-size: 1rem;
      line-height: 1.4;
      color: #333;
      margin: 0 0 6px;
      font-weight: 600;
    }

    .author {
      font-size: 0.8125rem;
      line-height: 1.4;
      color: #666;
      margin: 0 0 6px;
    }

    .meta {
      font-size: 0.75rem;
      color: #999;
      margin: 0;
    }
  }

  .actions {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    padding-left: 4px;
  }
}

/* 文本省略 */
.text-ellipsis-1 {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.text-ellipsis-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
