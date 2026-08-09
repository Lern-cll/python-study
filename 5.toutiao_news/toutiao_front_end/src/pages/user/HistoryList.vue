<template>
  <!-- 浏览历史页：顶部 header + 滚动容器（下拉刷新 + 触底加载） -->
  <div class="history-list-page">
    <!-- 顶部：返回 + 标题 + 清空按钮（仅在有数据时显示） -->
    <div class="header">
      <el-icon @click="router.back()"><ArrowLeft /></el-icon>
      <span>浏览历史</span>
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

      <!-- 历史列表 -->
      <div class="history-list" v-loading="loading">
        <HistoryItem
          v-for="item in list"
          :key="item.id"
          :item="item"
          @click="handleClick(item)"
          @delete="handleDelete(item.id)"
        />
        <!-- 空状态 -->
        <div v-if="!loading && list.length === 0" class="empty-state">
          <el-icon :size="48"><Clock /></el-icon>
          <p>暂无浏览记录</p>
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
// 浏览历史列表页
// 交互：进入即拉取第一页；下拉刷新重置分页；触底加载更多；单条删除；一键清空
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Clock, Loading, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getHistoryList, deleteHistory, clearHistory } from '@/api/history'
import HistoryItem from './HistoryItem.vue'

const router = useRouter()

// ============ 列表与分页状态 ============
// 首次加载 / 下拉刷新时的全屏 loading
const loading = ref(false)
// 触底加载更多时的局部 loading
const loadingMore = ref(false)
// 下拉刷新状态（控制 pull-refresh 区域展开）
const refreshing = ref(false)
// 浏览历史列表数据
const list = ref([])
// 当前页码
const page = ref(1)
// 每页条数
const pageSize = ref(10)
// 服务端返回的总条数
const total = ref(0)
// 是否还有更多可加载
const hasMore = ref(false)

// ============ 下拉刷新状态 ============
// 滚动容器 DOM 引用
const scrollRef = ref(null)
// 真正发生滚动的父容器（可能被外层包了滚动）
const scrollContainer = ref(null)
// 当前下拉距离（px）
const pullDistance = ref(0)
// 触摸起始 Y 坐标
const startY = ref(0)
// 触摸起始时的滚动位置（用于判断是否在顶部）
const startScrollTop = ref(0)
// 触发刷新的下拉阈值（px）
const threshold = 60
// 下拉最大距离（px，超出后阻尼封顶）
const maxDistance = 100

// ============ 并发去重 ============
// 闭包变量避免多次触发加载更多
let isLoadingMore = false
// 上次触发加载更多的时间戳（用于节流）
let lastLoadMoreAt = 0

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
 * 计算滚动容器距离底部的像素值
 * @param container - 滚动容器 DOM
 * @returns 距离底部像素
 */
const getScrollBottom = (container) =>
  container.scrollHeight - container.scrollTop - container.clientHeight

/**
 * 拉取浏览历史列表
 * @param reset - true 表示重置到第一页（覆盖），false 表示追加下一页
 */
const fetchList = async (reset = false) => {
  const targetPage = reset ? 1 : page.value
  try {
    const res = await getHistoryList({ page: targetPage, pageSize: pageSize.value })
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
  // 距底 80px 触发加载
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

/** 组件挂载：拉取第一页 + 定位滚动容器 */
onMounted(async () => {
  loading.value = true
  await fetchList(true)
  loading.value = false
  nextTick(() => {
    scrollContainer.value = scrollRef.value || findScrollParent(scrollRef.value)
  })
})

/** 点击某条历史：跳转到对应新闻详情 */
const handleClick = (item) => {
  router.push(`/news/${item.id}`)
}

/**
 * 删除单条浏览历史：调接口成功后从本地列表移除
 * @param historyId - 历史记录 ID
 */
const handleDelete = async (historyId) => {
  try {
    await deleteHistory(historyId)
    list.value = list.value.filter((x) => x.id !== historyId)
    ElMessage.success('删除成功')
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

/** 清空所有浏览历史：二次确认后调接口并清空本地列表 */
const handleClear = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有浏览历史吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await clearHistory()
    list.value = []
    ElMessage.success('已清空浏览历史')
  } catch (e) {
    // 用户取消或接口异常，忽略
  }
}
</script>

<style lang="scss" scoped>
.history-list-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;

  // 顶部 header
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

  // 滚动容器：兼作下拉刷新与触底加载
  .news-scroll {
    flex: 1;
    position: relative;
    min-height: 0;
    overflow-y: auto;
    touch-action: pan-y;
    -webkit-overflow-scrolling: touch;
  }

  // 下拉刷新头部
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

  // 历史列表容器
  .history-list {
    padding-bottom: 10px;
  }

  // 空状态
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

  // 加载更多中
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

  // 没有更多
  .no-more {
    text-align: center;
    padding: 15px;
    color: #bbb;
    font-size: 0.8125rem;
  }
}
</style>
