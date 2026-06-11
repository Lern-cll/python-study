<template>
  <div class="news-item" @click="handleClick">
    <div class="news-content">
      <h3 class="news-title text-ellipsis-2">{{ news.title }}</h3>
      <div class="news-info">
        <span class="news-source">{{ news.source || '头条号' }}</span>
        <span class="news-time">{{ formatTime(news.publishTime || news.createTime) }}</span>
        <span class="news-views">
          <el-icon><View /></el-icon>
          {{ news.views || 0 }}
        </span>
      </div>
    </div>
    <div v-if="news.coverImage" class="news-image">
      <img :src="news.coverImage" :alt="news.title" />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { View } from '@element-plus/icons-vue'

const props = defineProps({
  news: {
    type: Object,
    required: true
  }
})

const router = useRouter()

const handleClick = () => {
  router.push(`/news/${props.news.id}`)
}

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

    .news-title {
      font-size: 1rem;
      line-height: 1.4;
      color: #333;
      margin-bottom: 8px;
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

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }
}
</style>