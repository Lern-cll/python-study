<template>
  <div class="news-detail-page">
    <div class="header">
      <el-icon @click="router.back()"><ArrowLeft /></el-icon>
      <span>新闻详情</span>
    </div>
    <div class="content" v-loading="loading">
      <template v-if="news">
        <h1 class="title">{{ news.title }}</h1>
        <div class="meta">
          <span class="source">{{ news.source }}</span>
          <span class="time">{{ formatTime(news.publishTime) }}</span>
          <span class="views">
            <el-icon><View /></el-icon>
            {{ news.views }}
          </span>
        </div>
        <div class="cover" v-if="news.coverImage">
          <img :src="news.coverImage" :alt="news.title" />
        </div>
        <div class="article" v-html="news.content"></div>
        <div class="actions">
          <div class="action-item" @click="handleFavorite">
            <el-icon><Star /></el-icon>
            <span>{{ isFavorited ? '已收藏' : '收藏' }}</span>
          </div>
          <div class="action-item" @click="handleShare">
            <el-icon><Share /></el-icon>
            <span>分享</span>
          </div>
        </div>
      </template>
      <el-empty v-else description="内容不存在" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNewsStore } from '@/pinia/newsStore'
import { ArrowLeft, View, Star, Share } from '@element-plus/icons-vue'
import { addHistory } from '@/api/history'
import { checkFavorite, addFavorite } from '@/api/favorite'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const newsStore = useNewsStore()

const news = ref(null)
const loading = ref(false)
const isFavorited = ref(false)

onMounted(async () => {
  await fetchDetail()
  await addViewHistory()
})

const fetchDetail = async () => {
  loading.value = true
  try {
    await newsStore.fetchNewsDetail(route.params.id)
    news.value = newsStore.currentNews
    if (news.value) {
      await checkFavoriteStatus()
    }
  } finally {
    loading.value = false
  }
}

const checkFavoriteStatus = async () => {
  try {
    const res = await checkFavorite(route.params.id)
    isFavorited.value = res.isFavorited || res.data?.isFavorited
  } catch (e) {
    isFavorited.value = false
  }
}

const addViewHistory = async () => {
  try {
    await addHistory(route.params.id)
  } catch (e) {
    console.error('添加浏览记录失败', e)
  }
}

const handleFavorite = async () => {
  if (isFavorited.value) {
    ElMessage.info('您已收藏过此文章')
    return
  }
  try {
    await addFavorite(route.params.id)
    isFavorited.value = true
    ElMessage.success('收藏成功')
  } catch (e) {
    ElMessage.error('收藏失败')
  }
}

const handleShare = () => {
  ElMessage.info('分享功能开发中')
}

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString()
}
</script>

<style lang="scss" scoped>
.news-detail-page {
  min-height: 100vh;
  background: #fff;

  .header {
    position: sticky;
    top: 0;
    display: flex;
    align-items: center;
    padding: 12px 15px;
    background: #fff;
    border-bottom: 1px solid #f0f0f0;
    z-index: 10;

    .el-icon {
      font-size: 20px;
      cursor: pointer;
    }

    span {
      flex: 1;
      text-align: center;
      font-size: 1rem;
      font-weight: 600;
    }
  }

  .content {
    padding: 15px;

    .title {
      font-size: 1.25rem;
      font-weight: 700;
      line-height: 1.4;
      color: #333;
      margin-bottom: 12px;
    }

    .meta {
      display: flex;
      align-items: center;
      font-size: 0.75rem;
      color: #999;
      margin-bottom: 15px;

      span {
        margin-right: 12px;
      }

      .views {
        display: flex;
        align-items: center;

        .el-icon {
          margin-right: 3px;
        }
      }
    }

    .cover {
      margin-bottom: 15px;
      border-radius: 8px;
      overflow: hidden;

      img {
        width: 100%;
        display: block;
      }
    }

    .article {
      font-size: 1rem;
      line-height: 1.8;
      color: #333;
      margin-bottom: 30px;

      :deep(p) {
        margin-bottom: 15px;
      }

      :deep(img) {
        max-width: 100%;
        margin: 15px 0;
      }
    }

    .actions {
      display: flex;
      justify-content: center;
      gap: 50px;
      padding: 15px 0;
      border-top: 1px solid #f0f0f0;

      .action-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        color: #666;
        cursor: pointer;

        .el-icon {
          font-size: 24px;
          margin-bottom: 5px;
        }

        span {
          font-size: 0.75rem;
        }
      }
    }
  }
}
</style>