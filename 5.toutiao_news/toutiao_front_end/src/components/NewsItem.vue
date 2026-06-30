<template>
  <div class="news-item" @click="handleClick">
    <div class="news-content">
      <h3 class="news-title text-ellipsis-2">{{ news.title }}</h3>
      <p class="news-desc text-ellipsis-2">{{ news.description }}</p>
      <div class="news-info">
        <span class="news-source">{{ news.author || '头条号' }}</span>
        <span class="news-time">{{ formatTime(news.publish_time || news.created_at) }}</span>
        <span class="news-views">
          <el-icon><View /></el-icon>
          {{ formatViews(news.views) }}
        </span>
      </div>
    </div>
    <div v-if="news.image" class="news-image" :class="{ 'is-loading': !imageLoaded }">
      <img 
        v-show="imageLoaded"
        :src="news.image" 
        :alt="news.title"
        @load="onImageLoad"
        @error="onImageError"
      />
      <div v-if="!imageLoaded" class="image-placeholder">
        <el-icon class="is-loading"><Loading /></el-icon>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { View, Loading } from '@element-plus/icons-vue'

const props = defineProps({
  // 单条新闻数据（必传）
  news: {
    type: Object,
    required: true
  }
})

const router = useRouter()
// 缩略图是否已加载完成（用于占位图与图片的切换）
const imageLoaded = ref(false)

/** 图片加载成功：隐藏占位图、显示真实图 */
const onImageLoad = () => {
  imageLoaded.value = true
}

/** 图片加载失败：同样隐藏占位图，避免无限 loading */
const onImageError = () => {
  imageLoaded.value = true
}

/** 点击新闻条目：跳转至详情页 */
const handleClick = () => {
  router.push(`/news/${props.news.id}`)
}

/**
 * 将时间格式化为「刚刚 / N分钟前 / N小时前 / N天前 / 日期」
 * @param time - 时间字符串或时间戳
 * @returns 友好时间文案
 */
const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString()
}

/**
 * 格式化阅读量，超过 1 万显示为「X.X万」
 * @param views - 原始阅读量
 * @returns 数字或带「万」单位的字符串
 */
const formatViews = (views) => {
  const n = Number(views) || 0
  if (n >= 10000) return `${(n / 10000).toFixed(1)}万`
  return n
}
</script>

<style lang="scss" scoped>
.news-item {
  display: flex;
  padding: 15px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;

  .news-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    margin-right: 12px;
    min-width: 0;

    .news-title {
      font-size: 1rem;
      line-height: 1.4;
      color: #333;
      margin: 0 0 6px;
      font-weight: 600;
    }

    .news-desc {
      font-size: 0.8125rem;
      line-height: 1.4;
      color: #666;
      margin: 0 0 8px;
    }

    .news-info {
      display: flex;
      align-items: center;
      font-size: 0.75rem;
      color: #999;

      span {
        margin-right: 10px;
      }

      .news-views {
        display: flex;
        align-items: center;

        .el-icon {
          margin-right: 3px;
        }
      }
    }
  }

  .news-image {
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

    .image-placeholder {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #f0f0f0;
      color: #ccc;
      font-size: 20px;
    }
  }
}

.text-ellipsis-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>