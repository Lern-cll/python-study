<template>
  <div class="news-detail-page">
    <!-- 顶部：返回 + 标题 -->
    <div class="header">
      <el-icon class="back-icon" @click="router.back()"><ArrowLeft /></el-icon>
      <span class="title">新闻详情</span>
    </div>

    <div class="content" v-loading="loading">
      <template v-if="news">
        <!-- 标题与收藏按钮 -->
        <div class="title-row">
          <h1 class="title-text">{{ news.title }}</h1>
          <div
            class="favorite-btn"
            :class="{ active: isFavorited }"
            @click="handleToggleFavorite"
          >
            <el-icon :size="22">
              <StarFilled v-if="isFavorited" />
              <Star v-else />
            </el-icon>
          </div>
        </div>

        <!-- 作者、发表时间、阅读量 -->
        <div class="meta">
          <span class="author">{{ news.author || '央视新闻' }}</span>
          <span class="time">{{ formatDateTime(news.publishTime || news.publish_time) }}</span>
          <span class="views">
            {{ formatViews(news.views) }} 阅读
          </span>
        </div>

        <!-- 封面图：默认 16:9 占位，加载完成后按真实比例展示 -->
        <div class="cover" v-if="news.image">
          <div class="cover-inner" :style="coverAspect">
            <img
              :src="news.image"
              :alt="news.title"
              :class="{ loaded: coverLoaded }"
              @load="onCoverLoad"
              @error="onCoverError"
            />
          </div>
        </div>

        <!-- 新闻正文（HTML 字符串，直接由后端渲染） -->
        <div class="article" v-html="news.content"></div>

        <!-- 相关推荐 -->
        <div class="related" v-if="news.relatedNews && news.relatedNews.length > 0">
          <div class="divider"></div>
          <h2 class="related-title">相关推荐</h2>
          <div
            v-for="item in news.relatedNews"
            :key="item.id"
            class="related-item"
            @click="goRelated(item.id)"
          >
            <div class="related-image" v-if="item.image">
              <img :src="item.image" :alt="item.title" />
            </div>
            <div class="related-image placeholder" v-else>
              <el-icon :size="20"><Picture /></el-icon>
            </div>
            <div class="related-info">
              <p class="related-name text-ellipsis-2">{{ item.title }}</p>
            </div>
          </div>
        </div>
      </template>
      <el-empty v-else-if="!loading" description="内容不存在" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNewsStore } from '@/pinia/newsStore'
import { ArrowLeft, Star, StarFilled, Picture } from '@element-plus/icons-vue'
import { addHistory } from '@/api/history'
import { checkFavorite, addFavorite, removeFavorite } from '@/api/favorite'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const newsStore = useNewsStore()

// 当前展示的新闻详情
const news = ref(null)
// 详情加载中标记
const loading = ref(false)
// 当前新闻是否已被当前用户收藏
const isFavorited = ref(false)
// 封面图容器默认占位宽高比，避免图片加载过程中挤压下方内容
const coverAspect = ref({ aspectRatio: '16 / 9' })
// 封面图是否加载完成（用于淡入显示）
const coverLoaded = ref(false)

/**
 * 封面图加载完成：按图片真实宽高比调整容器，避免拉伸
 * @param e - img 元素的 load 事件
 */
const onCoverLoad = (e) => {
  const img = e.target
  if (img.naturalWidth && img.naturalHeight) {
    coverAspect.value = {
      aspectRatio: `${img.naturalWidth} / ${img.naturalHeight}`
    }
  }
  coverLoaded.value = true
}

/** 封面图加载失败：保持默认占位，不再继续闪烁 */
const onCoverError = () => {
  // 加载失败时保持默认占位，不再继续闪烁
  coverLoaded.value = true
}

/** 进入页面：拉取详情 + 自动添加浏览记录 */
onMounted(async () => {
  await fetchDetail()
  await addViewHistory()
})

/**
 * 拉取新闻详情并同步收藏状态
 */
const fetchDetail = async () => {
  loading.value = true
  coverLoaded.value = false
  coverAspect.value = { aspectRatio: '16 / 9' }
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

/** 拉取当前新闻的收藏状态以同步图标 */
const checkFavoriteStatus = async () => {
  try {
    const res = await checkFavorite(route.params.id)
    const data = res.data || res
    isFavorited.value = !!(data.isFavorite ?? data.isFavorited)
  } catch (e) {
    isFavorited.value = false
  }
}

/** 添加浏览记录：失败仅打印日志，不影响详情页主流程 */
const addViewHistory = async () => {
  try {
    await addHistory(route.params.id)
  } catch (e) {
    console.error('添加浏览记录失败', e)
  }
}

/** 切换收藏状态：已收藏则取消，未收藏则添加 */
const handleToggleFavorite = async () => {
  const newsId = Number(route.params.id)
  try {
    if (isFavorited.value) {
      await removeFavorite(newsId)
      isFavorited.value = false
      ElMessage.success('已取消收藏')
    } else {
      await addFavorite(newsId)
      isFavorited.value = true
      ElMessage.success('收藏成功')
    }
  } catch (e) {
    ElMessage.error(isFavorited.value ? '取消收藏失败' : '收藏失败')
  }
}

/**
 * 点击相关推荐：跳转到对应新闻详情
 * @param id - 推荐新闻 ID
 */
const goRelated = (id) => {
  router.push(`/news/${id}`)
}

/**
 * 将时间格式化为 YYYY-MM-DD HH:mm
 * @param time - 时间字符串或时间戳
 * @returns 格式化后的字符串，无效输入返回原值
 */
const formatDateTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  if (isNaN(date.getTime())) return time
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
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
.news-detail-page {
  min-height: 100vh;
  background: #fff;
  display: flex;
  flex-direction: column;

  .header {
    position: sticky;
    top: 0;
    display: flex;
    align-items: center;
    padding: 12px 15px;
    background: #fff;
    border-bottom: 1px solid #f0f0f0;
    z-index: 10;

    .back-icon {
      font-size: 20px;
      cursor: pointer;
      color: #333;
    }

    .title {
      flex: 1;
      text-align: center;
      font-size: 1rem;
      font-weight: 600;
      color: #333;
      margin-right: 20px;
    }
  }

  .content {
    flex: 1;
    padding: 15px;
    overflow-y: auto;

    .title-row {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
      margin-bottom: 12px;

      .title-text {
        flex: 1;
        font-size: 1.25rem;
        font-weight: 700;
        line-height: 1.4;
        color: #333;
        margin: 0;
      }

      .favorite-btn {
        flex-shrink: 0;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #c0c4cc;
        cursor: pointer;
        transition: color 0.2s;

        &.active {
          color: #e63946;
        }

        &:active {
          transform: scale(0.9);
        }
      }
    }

    .meta {
      display: flex;
      align-items: center;
      font-size: 0.75rem;
      color: #999;
      margin-bottom: 15px;
      flex-wrap: wrap;
      gap: 4px 12px;

      .author {
        color: #333;
      }

      .views {
        margin-left: auto;
      }
    }

    .cover {
      margin-bottom: 15px;
      border-radius: 6px;
      overflow: hidden;
      background: #f5f5f5;

      .cover-inner {
        width: 100%;
        // 默认按 16/9 占位，加载完成后由 coverAspect 动态更新为图片真实宽高比
        aspect-ratio: 16 / 9;
        position: relative;
        // 占位背景：浅灰底 + 骨架闪烁效果
        background:
          linear-gradient(90deg, #f0f0f0 0%, #e6e6e6 50%, #f0f0f0 100%);
        background-size: 200% 100%;
        animation: cover-skeleton 1.4s ease-in-out infinite;
      }

      img {
        // 加载完成前不显示，避免先展示再挤压
        opacity: 0;
        transition: opacity 0.25s ease;
        width: 100%;
        height: 100%;
        display: block;
        position: absolute;
        inset: 0;
        object-fit: cover;
      }

      img.loaded {
        opacity: 1;
      }
    }

    // 图片加载完毕后停止骨架屏动画
    .cover-inner:has(img.loaded) {
      animation: none;
      background: transparent;
    }

    .article {
      font-size: 1rem;
      line-height: 1.8;
      color: #333;
      margin-bottom: 20px;
      word-break: break-word;

      :deep(p) {
        margin-bottom: 15px;
        text-indent: 0;
      }

      :deep(img) {
        max-width: 100%;
        margin: 15px 0;
        border-radius: 4px;
      }
    }

    .related {
      .divider {
        height: 1px;
        background: #f0f0f0;
        margin: 20px 0 15px;
      }

      .related-title {
        font-size: 1rem;
        font-weight: 700;
        color: #333;
        margin: 0 0 12px;
      }

      .related-item {
        display: flex;
        padding: 10px 0;
        cursor: pointer;

        &:active {
          opacity: 0.7;
        }

        .related-image {
          width: 100px;
          height: 70px;
          border-radius: 4px;
          overflow: hidden;
          flex-shrink: 0;
          background: #f5f5f5;

          img {
            width: 100%;
            height: 100%;
            object-fit: cover;
          }

          &.placeholder {
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ccc;
          }
        }

        .related-info {
          flex: 1;
          min-width: 0;
          margin-left: 12px;
          display: flex;
          align-items: center;

          .related-name {
            font-size: 0.9375rem;
            line-height: 1.4;
            color: #333;
            margin: 0;
          }
        }
      }
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

@keyframes cover-skeleton {
  0% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0 50%;
  }
}
</style>