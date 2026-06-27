<template>
  <div class="home-page">
    <div class="header">
      <h1 class="logo">头条</h1>
    </div>
    <CategoryNav
      v-model="currentCategory"
      :categories="categories"
      @change="handleCategoryChange"
    />
    <div
      class="news-scroll"
      ref="scrollRef"
      @scroll="onScroll"
      @touchstart="onTouchStart"
      @touchmove="onTouchMove"
      @touchend="onTouchEnd"
    >
      <div
        class="pull-refresh"
        :class="{ active: pullDistance > 0, refreshing: refreshing }"
        :style="{ height: pullDistance + 'px' }"
      >
        <div class="pull-refresh-inner">
          <el-icon
            :class="{ 'is-loading': refreshing }"
            :style="iconTransform"
          >
            <Loading v-if="refreshing" />
            <ArrowDown v-else />
          </el-icon>
          <span class="pull-text">{{ refreshText }}</span>
        </div>
      </div>
      <div class="news-list" v-loading="loading">
        <NewsItem
          v-for="item in newsList"
          :key="item.id"
          :news="item"
        />
        <div v-if="!loading && newsList.length === 0" class="empty-state">
          <el-empty description="暂无数据" />
        </div>
        <div v-if="loading && newsList.length > 0" class="loading-more">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>
        <div v-if="!loading && !hasMore && newsList.length > 0" class="no-more">
          <span>没有更多了</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onActivated, onDeactivated, computed, watch, nextTick } from 'vue'
import { useNewsStore } from '@/pinia/newsStore'
import CategoryNav from '@/components/CategoryNav.vue'
import NewsItem from '@/components/NewsItem.vue'
import { Loading, ArrowDown } from '@element-plus/icons-vue'

const newsStore = useNewsStore()

const currentCategory = ref(null)
const categories = computed(() => newsStore.categories)
const newsList = computed(() => newsStore.newsList)
const loading = computed(() => newsStore.loading)
const hasMore = computed(() => newsStore.hasMore)

// 下拉刷新
const scrollRef = ref(null)
const scrollContainer = ref(null)
const pullDistance = ref(0)
const refreshing = ref(false)
const startY = ref(0)
const startScrollTop = ref(0)
const threshold = 60
const maxDistance = 100

// 离开 Home 时保存滚动位置（keep-alive 场景下 onDeactivated 触发）
const savedScrollTop = ref(0)

// 滚动自动加载
let isLoadingMore = false
let lastLoadMoreAt = 0

const getScrollBottom = (container) =>
  container.scrollHeight - container.scrollTop - container.clientHeight

const tryLoadMore = async () => {
  if (isLoadingMore || loading.value || refreshing.value || !hasMore.value) return
  const now = Date.now()
  if (now - lastLoadMoreAt < 500) return
  lastLoadMoreAt = now
  isLoadingMore = true
  try {
    await newsStore.loadMore({ categoryId: currentCategory.value })
  } finally {
    isLoadingMore = false
  }
}

const onScroll = async (e) => {
  if (isLoadingMore || loading.value || refreshing.value || !hasMore.value) return

  // 使用真正的滚动容器
  if (!scrollContainer.value && scrollRef.value) {
    scrollContainer.value = findScrollParent(scrollRef.value)
  }
  const container = scrollContainer.value || scrollRef.value
  if (!container || container.scrollHeight <= container.clientHeight) return
  
  const scrollBottom = getScrollBottom(container)
  // 距离底部 200px 时触发加载
  if (scrollBottom < 80) {
    await tryLoadMore()
  }
}

const refreshText = computed(() => {
  if (refreshing.value) return '正在刷新...'
  if (pullDistance.value >= threshold) return '松开立即刷新'
  return '下拉刷新'
})

const iconTransform = computed(() => {
  if (refreshing.value) return {}
  const deg = pullDistance.value >= threshold ? 180 : pullDistance.value * 2
  return { transform: `rotate(${deg}deg)` }
})

const findScrollParent = (el) => {
  if (!el) return null
  let node = el
  while (node) {
    const style = window.getComputedStyle(node)
    if (style.overflowY === 'auto' || style.overflowY === 'scroll') {
      return node
    }
    node = node.parentElement
  }
  return null
}

const onTouchStart = (e) => {
  if (refreshing.value) return
  if (!scrollContainer.value) {
    scrollContainer.value = findScrollParent(scrollRef.value)
  }
  startY.value = e.touches[0].clientY
  startScrollTop.value = scrollContainer.value?.scrollTop || 0
}

const onTouchMove = (e) => {
  if (refreshing.value) return
  // 只在列表处于顶部时响应下拉
  if (startScrollTop.value > 0) return
  const currentY = e.touches[0].clientY
  const diff = currentY - startY.value
  if (diff <= 0) {
    pullDistance.value = 0
    return
  }
  // 阻尼效果
  pullDistance.value = Math.min(diff * 0.4, maxDistance)
}

const onTouchEnd = async () => {
  if (refreshing.value) return
  if (pullDistance.value >= threshold) {
    refreshing.value = true
    pullDistance.value = threshold
    try {
      newsStore.resetPage()
      await newsStore.fetchNewsList({ categoryId: currentCategory.value })
    } finally {
      refreshing.value = false
      pullDistance.value = 0
    }
  } else {
    pullDistance.value = 0
  }
}

onMounted(async () => {
  await newsStore.fetchCategories()
  scrollContainer.value = scrollRef.value || findScrollParent(scrollRef.value)
})

// 被 keep-alive 缓存后，离开时记录滚动位置，回来时恢复
onActivated(() => {
  // 已经在 Home 中时不做处理（首次进入会触发 onMounted）
  if (scrollRef.value) {
    scrollContainer.value = scrollRef.value || findScrollParent(scrollRef.value)
  }
  if (savedScrollTop.value > 0 && scrollContainer.value) {
    nextTick(() => {
      scrollContainer.value?.scrollTo(0, savedScrollTop.value)
    })
  }
})

onDeactivated(() => {
  // 跳到详情页时把当前滚动位置存下来
  if (scrollContainer.value) {
    savedScrollTop.value = scrollContainer.value.scrollTop
  }
})

// 分类加载完成后，自动选中第一个
watch(
  () => newsStore.categories,
  (list) => {
    if (currentCategory.value == null && list.length > 0) {
      currentCategory.value = list[0].id
      newsStore.resetPage()
      newsStore.fetchNewsList({ categoryId: currentCategory.value })
    }
  },
  { immediate: true, flush: 'post' }
)

const handleCategoryChange = async (category) => {
  newsStore.resetPage()
  await newsStore.fetchNewsList({ categoryId: category.id })
}
</script>

<style lang="scss" scoped>
.home-page {
  background: #f5f5f5;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .header {
    background: #e63946;
    color: #fff;
    padding: 12px 15px;
    flex-shrink: 0;

    .logo {
      font-size: 1.25rem;
      font-weight: 700;
    }
  }

  .news-scroll {
    flex: 1;
    position: relative;
    min-height: 0;
    touch-action: pan-y;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }

  .pull-refresh {
    width: 100%;
    overflow: hidden;
    transition: height 0.2s ease;

    .pull-refresh-inner {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 60px;
      color: #999;
      font-size: 0.8125rem;
      gap: 6px;
    }

    .el-icon {
      font-size: 16px;
      transition: transform 0.2s ease;
    }
  }

  .news-list {
    padding-bottom: 10px;
  }

  .loading-more {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 15px;
    color: #999;
    font-size: 0.875rem;

    .el-icon {
      margin-right: 8px;
    }
  }

  .load-more {
    text-align: center;
    padding: 15px;
    color: #666;
    font-size: 0.875rem;
    background: #fff;
    cursor: pointer;

    &:hover {
      background: #fafafa;
    }
  }

  .no-more {
    text-align: center;
    padding: 15px;
    color: #bbb;
    font-size: 0.8125rem;
  }
}
</style>
