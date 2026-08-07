<!--
  我的收藏页
  列表：左图 / 右标题 / 作者 / 收藏时间 / 最右「取消收藏」
  交互：下拉刷新 + 触底加载更多 + 单条取消收藏二次确认
-->
<template>
  <div class="favorite-list-page">
    <!-- 顶部：返回 + 标题 + 清空按钮 -->
    <div class="header">
      <el-icon @click="router.back()"><ArrowLeft /></el-icon>
      <span>我的收藏</span>
      <el-button text size="small" @click="handleClear" v-if="list.length > 0">
        清空
      </el-button>
    </div>

    <!-- 滚动容器：兼作下拉刷新与触底加载 -->
    <div
      class="news-scroll"
      ref="scrollRef"
      @scroll="onScroll"
      @touchstart="onTouchStart"
      @touchmove="onTouchMove"
      @touchend="onTouchEnd"
    >
      <!-- 下拉刷新头部：高度随 pullDistance 展开 -->
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

      <!-- 收藏列表 -->
      <div class="favorite-list" v-loading="loading">
        <FavoriteItem
          v-for="item in list"
          :key="item.favoriteId"
          :item="item"
          @click="handleClick(item)"
          @cancel="handleCancel(item)"
        />
        <!-- 空状态 -->
        <div v-if="!loading && list.length === 0" class="empty-state">
          <el-icon :size="48"><Star /></el-icon>
          <p>暂无收藏内容</p>
        </div>
        <!-- 加载更多中 -->
        <div v-if="loadingMore" class="loading-more">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>
        <!-- 没有更多 -->
        <div v-if="!loading && !hasMore && list.length > 0" class="no-more">
          <span>没有更多了</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Star, Loading, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getFavoriteList, removeFavorite, clearFavorites } from '@/api/favorite'
import FavoriteItem from './FavoriteItem.vue'

const router = useRouter()

// ============ 列表数据 ============
const loading = ref(false)        // 首次/刷新时的全屏 loading
const loadingMore = ref(false)    // 加载更多时的局部 loading
const refreshing = ref(false)     // 下拉刷新状态
const list = ref([])              // 收藏列表数据
const page = ref(1)               // 当前页码
const pageSize = ref(10)          // 每页条数
const total = ref(0)              // 总条数（来自接口）
const hasMore = ref(false)        // 是否还有更多

// ============ 下拉刷新相关 ============
const scrollRef = ref(null)
const scrollContainer = ref(null)
const pullDistance = ref(0)
const startY = ref(0)
const startScrollTop = ref(0)
const threshold = 60              // 触发刷新的下拉阈值
const maxDistance = 100           // 下拉最大距离（阻尼封顶）

// 并发锁 + 节流，避免重复触发加载更多
let isLoadingMore = false
let lastLoadMoreAt = 0

// 下拉文案
const refreshText = computed(() => {
  if (refreshing.value) return '正在刷新...'
  if (pullDistance.value >= threshold) return '松开立即刷新'
  return '下拉刷新'
})

// 箭头旋转角度
const iconTransform = computed(() => {
  if (refreshing.value) return {}
  const deg = pullDistance.value >= threshold ? 180 : pullDistance.value * 2
  return { transform: `rotate(${deg}deg)` }
})

/**
 * 向上查找最近的纵向可滚动父元素（overflow-y 为 auto/scroll）
 * @param el - 起始 DOM 元素
 * @returns 找到的滚动容器；未找到返回 null
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
 * 计算滚动容器距离底部的像素值
 */
const getScrollBottom = (container) =>
  container.scrollHeight - container.scrollTop - container.clientHeight

/**
 * 拉取收藏列表
 * @param reset - true 表示重新拉第一页（覆盖），false 表示追加下一页
 */
const fetchList = async (reset = false) => {
  const targetPage = reset ? 1 : page.value
  try {
    const res = await getFavoriteList({ page: targetPage, pageSize: pageSize.value })
    // 接口成功响应：res = { code, message, data: { list, total, hasMore } }
    const payload = (res && res.data) || {}
    const newList = Array.isArray(payload.list) ? payload.list : []
    if (reset) {
      page.value = 1
      list.value = newList
    } else {
      list.value = [...list.value, ...newList]
    }
    total.value = typeof payload.total === 'number' ? payload.total : list.value.length
    hasMore.value =
      typeof payload.hasMore === 'boolean'
        ? payload.hasMore
        : list.value.length < total.value
  } catch (e) {
    ElMessage.error(reset ? '刷新失败' : '加载更多失败')
  }
}

/** 加载下一页 */
const loadMore = async () => {
  page.value++
  await fetchList(false)
}

/**
 * 触底自动加载：去重 + 节流后调用 loadMore
 */
const tryLoadMore = async () => {
  if (isLoadingMore || loading.value || refreshing.value || !hasMore.value) return
  const now = Date.now()
  if (now - lastLoadMoreAt < 500) return
  lastLoadMoreAt = now
  isLoadingMore = true
  loadingMore.value = true
  try {
    await loadMore()
  } finally {
    isLoadingMore = false
    loadingMore.value = false
  }
}

/** 列表滚动事件：触底时触发加载更多 */
const onScroll = async () => {
  if (isLoadingMore || loading.value || refreshing.value || !hasMore.value) return
  if (!scrollContainer.value && scrollRef.value) {
    scrollContainer.value = findScrollParent(scrollRef.value)
  }
  const container = scrollContainer.value || scrollRef.value
  if (!container || container.scrollHeight <= container.clientHeight) return
  const scrollBottom = getScrollBottom(container)
  // 距底 80px 触发
  if (scrollBottom < 80) {
    await tryLoadMore()
  }
}

/** 触摸开始：记录起始 Y 与起始滚动位置 */
const onTouchStart = (e) => {
  if (refreshing.value) return
  if (!scrollContainer.value) {
    scrollContainer.value = findScrollParent(scrollRef.value)
  }
  startY.value = e.touches[0].clientY
  startScrollTop.value = scrollContainer.value?.scrollTop || 0
}

/** 触摸移动：仅在列表顶部时响应下拉，并加入阻尼 */
const onTouchMove = (e) => {
  if (refreshing.value) return
  // 不在顶部不下拉
  if (startScrollTop.value > 0) return
  const currentY = e.touches[0].clientY
  const diff = currentY - startY.value
  if (diff <= 0) {
    pullDistance.value = 0
    return
  }
  // 阻尼：下拉距离被压缩到 0.4 倍，最大 100px
  pullDistance.value = Math.min(diff * 0.4, maxDistance)
}

/** 触摸结束：超过阈值则触发下拉刷新 */
const onTouchEnd = async () => {
  if (refreshing.value) return
  if (pullDistance.value >= threshold) {
    refreshing.value = true
    pullDistance.value = threshold
    loading.value = true
    try {
      await fetchList(true)
    } finally {
      refreshing.value = false
      pullDistance.value = 0
      loading.value = false
    }
  } else {
    pullDistance.value = 0
  }
}

/** 进入页面：拉取第一页 + 初始化滚动容器 */
onMounted(async () => {
  loading.value = true
  await fetchList(true)
  loading.value = false
  nextTick(() => {
    scrollContainer.value = scrollRef.value || findScrollParent(scrollRef.value)
  })
})

/** 点击某条收藏：跳转详情（item.id 即新闻 ID） */
const handleClick = (item) => {
  router.push(`/news/${item.id}`)
}

/**
 * 取消收藏：二次确认 → 调用接口 → 列表中移除该项
 * @param item - 收藏记录项（含 favoriteId / id）
 */
const handleCancel = async (item) => {
  try {
    await ElMessageBox.confirm('确定要取消这条收藏吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    // 按 favorite.ts 约定，传 newsId（即新闻 ID）
    await removeFavorite(item.id)
    list.value = list.value.filter((x) => x.favoriteId !== item.favoriteId)
    ElMessage.success('已取消收藏')
  } catch (e) {
    // 用户取消或接口异常，忽略
  }
}

/** 清空全部收藏：二次确认后调接口并清空本地列表 */
const handleClear = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有收藏吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const res = await clearFavorites()
    const count = res?.data ?? list.value.length
    list.value = []
    ElMessage.success(count > 0 ? `已清空 ${count} 条收藏` : '已清空收藏')
  } catch (e) {
    // 取消操作
  }
}
</script>

<style lang="scss" scoped>
.favorite-list-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;

  .header {
    display: flex;
    align-items: center;
    padding: 12px 15px;
    background: #fff;
    border-bottom: 1px solid #f0f0f0;
    flex-shrink: 0;

    .el-icon:first-child {
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

  .news-scroll {
    flex: 1;
    position: relative;
    min-height: 0;
    overflow-y: auto;
    touch-action: pan-y;
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

  .favorite-list {
    padding-bottom: 10px;
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
    color: #999;

    .el-icon {
      margin-bottom: 15px;
    }
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

  .no-more {
    text-align: center;
    padding: 15px;
    color: #bbb;
    font-size: 0.8125rem;
  }
}
</style>
