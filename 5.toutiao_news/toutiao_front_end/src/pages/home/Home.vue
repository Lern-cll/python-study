<template>
  <div class="home-page">
    <!-- 顶部 Logo + 搜索入口 -->
    <div class="header">
      <h1 class="logo">头条</h1>
      <!-- 搜索框：点击跳转到搜索页（输入关键词后回车在搜索页触发） -->
      <div class="search-bar" @click="goSearch">
        <el-icon class="search-icon"><Search /></el-icon>
        <span class="search-placeholder">搜索新闻</span>
      </div>
    </div>
    <!-- 分类导航 -->
    <CategoryNav
      v-model="currentCategory"
      :categories="categories"
      @change="handleCategoryChange"
    />
    <!-- 新闻列表滚动容器：兼作下拉刷新与触底加载 -->
    <div
      class="news-scroll"
      ref="scrollRef"
      @scroll="onScroll"
      @touchstart="onTouchStart"
      @touchmove="onTouchMove"
      @touchend="onTouchEnd"
    >
      <!-- 下拉刷新头部：根据 pullDistance 动态展开 -->
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
      <!-- 新闻列表 -->
      <div class="news-list" v-loading="loading">
        <NewsItem
          v-for="item in newsList"
          :key="item.id"
          :news="item"
        />
        <!-- 空数据 -->
        <div v-if="!loading && newsList.length === 0" class="empty-state">
          <el-empty description="暂无数据" />
        </div>
        <!-- 加载更多中 -->
        <div v-if="loading && newsList.length > 0" class="loading-more">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>
        <!-- 没有更多 -->
        <div v-if="!loading && !hasMore && newsList.length > 0" class="no-more">
          <span>没有更多了</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// 必须用普通 <script> 块显式声明组件名：<script setup> 默认不向组件选项暴露 name，
// 而 MainLayout 里的 <keep-alive :include="cachedViews"> 是按"组件选项.name"匹配的。
// 这里不写 name 会导致 Home 永远匹配不上 include、keep-alive 不生效，
// 表现为"再次进入 Home 时滚动位置丢失 + onMounted 重复触发"。
// 相比之下 defineOptions 在某些编译环境下也可能不生效，双 <script> 写法最稳。
export default { name: 'Home' }
</script>

<script setup>
import { ref, onMounted, onActivated, onDeactivated, computed, watch, nextTick } from 'vue'
import { useNewsStore } from '@/pinia/newsStore'
import CategoryNav from '@/components/CategoryNav.vue'
import NewsItem from '@/components/NewsItem.vue'
import { Loading, ArrowDown, Search } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

const newsStore = useNewsStore()
const router = useRouter()

// 跳转到搜索页（无关键词时直接进入，搜索页会展示热门/历史）
const goSearch = () => {
  router.push({ name: 'SearchResult' })
}

// 当前选中的分类 ID（与 CategoryNav v-model 双向绑定）
const currentCategory = ref(null)
// 从 store 取分类、新闻列表、加载中、是否还有更多
const categories = computed(() => newsStore.categories)
const newsList = computed(() => newsStore.newsList)
const loading = computed(() => newsStore.loading)
const hasMore = computed(() => newsStore.hasMore)

// ============ 下拉刷新相关 ============
// 滚动容器 DOM 引用
const scrollRef = ref(null)
// 真正发生滚动的父容器（可能被外层包了滚动）
const scrollContainer = ref(null)
// 当前下拉距离（px）
const pullDistance = ref(0)
// 是否处于刷新中
const refreshing = ref(false)
// 触摸起始 Y 坐标
const startY = ref(0)
// 触摸起始时的滚动位置（用于判断是否在顶部）
const startScrollTop = ref(0)
// 触发刷新的下拉阈值（px）
const threshold = 60
// 下拉最大距离（px，超出后阻尼效果封顶）
const maxDistance = 100

// 离开 Home 时保存滚动位置（keep-alive 场景下 onDeactivated 触发）
const savedScrollTop = ref(0)

// 滚动自动加载：闭包变量避免多次触发加载
let isLoadingMore = false
// 上次触发加载更多的时间戳（用于节流）
let lastLoadMoreAt = 0

/**
 * 计算滚动容器距离底部的距离
 * @param container - 滚动容器 DOM
 * @returns 距离底部像素
 */
const getScrollBottom = (container) =>
  container.scrollHeight - container.scrollTop - container.clientHeight

/**
 * 尝试加载下一页：去重 + 节流后调用 store.loadMore
 */
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

/** 列表滚动事件：触底时触发加载更多 */
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

// 下拉提示文案
const refreshText = computed(() => {
  if (refreshing.value) return '正在刷新...'
  if (pullDistance.value >= threshold) return '松开立即刷新'
  return '下拉刷新'
})

// 下拉箭头旋转角度：过阈值时翻转为向上
const iconTransform = computed(() => {
  if (refreshing.value) return {}
  const deg = pullDistance.value >= threshold ? 180 : pullDistance.value * 2
  return { transform: `rotate(${deg}deg)` }
})

/**
 * 向上查找最近的纵向可滚动父元素（overflow-y 为 auto/scroll）
 * @param el - 起始 DOM 元素
 * @returns 找到的滚动容器，未找到返回 null
 */
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

/**
 * 触摸开始：记录起始 Y 与起始滚动位置
 * @param e - TouchEvent
 */
const onTouchStart = (e) => {
  if (refreshing.value) return
  if (!scrollContainer.value) {
    scrollContainer.value = findScrollParent(scrollRef.value)
  }
  startY.value = e.touches[0].clientY
  startScrollTop.value = scrollContainer.value?.scrollTop || 0
}

/**
 * 触摸移动：仅在列表顶部时响应下拉，并加入阻尼
 * @param e - TouchEvent
 */
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

/** 触摸结束：超过阈值则触发刷新 */
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

/**
 * 组件挂载：拉取分类并定位滚动容器
 */
onMounted(async () => {
  await newsStore.fetchCategories()
  scrollContainer.value = scrollRef.value || findScrollParent(scrollRef.value)
})

/** 被 keep-alive 激活时：恢复离开时保存的滚动位置 */
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

/** 被 keep-alive 缓存离开时：保存当前滚动位置 */
onDeactivated(() => {
  // 跳到详情页时把当前滚动位置存下来
  if (scrollContainer.value) {
    savedScrollTop.value = scrollContainer.value.scrollTop
  }
})

/** 分类加载完成后，自动选中第一个并加载对应新闻 */
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

/**
 * 切换分类：重置分页后重新拉取第一页
 * @param category - 选中的分类对象
 */
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
    display: flex;
    align-items: center;
    gap: 12px;

    .logo {
      font-size: 1.25rem;
      font-weight: 700;
      flex-shrink: 0;
    }

    // 搜索入口（占满剩余空间，伪装成输入框）
    .search-bar {
      flex: 1;
      height: 36px;
      background: rgba(255, 255, 255, 0.92);
      border-radius: 18px;
      display: flex;
      align-items: center;
      padding: 0 14px;
      gap: 6px;
      color: #999;
      font-size: 0.875rem;
      cursor: pointer;
      // 轻微的按下反馈，提升点击感
      &:active {
        background: rgba(255, 255, 255, 0.78);
      }

      .search-icon {
        font-size: 16px;
      }
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