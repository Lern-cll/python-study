<template>
  <div class="search-page">
    <!-- 顶部：返回 + 输入框 + 搜索按钮 -->
    <div class="search-header">
      <el-icon class="back-icon" @click="goBack"><ArrowLeft /></el-icon>
      <el-input
        ref="inputRef"
        v-model="keyword"
        placeholder="搜索新闻"
        :clearable="true"
        size="default"
        class="search-input"
        @keyup.enter="handleSearch"
        @clear="onInputClear"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <button class="search-btn" @click="handleSearch">搜索</button>
    </div>

    <!-- 未输入关键词时的初始态：热门 + 历史 -->
    <div v-if="!hasSearched" class="initial-state">
      <!-- 热门搜索 -->
      <div class="section">
        <h3 class="section-title">热门搜索</h3>
        <div class="tag-list">
          <span
            v-for="(kw, idx) in hotKeywords"
            :key="idx"
            class="tag tag-hot"
            @click="quickSearch(kw)"
          >{{ kw }}</span>
        </div>
      </div>
      <!-- 历史搜索：仅登录用户可见 -->
      <div v-if="isLoggedIn && historyList.length > 0" class="section">
        <div class="section-header">
          <h3 class="section-title">历史搜索</h3>
          <el-icon class="clear-icon" @click="onClearHistory"><Delete /></el-icon>
        </div>
        <div class="tag-list">
          <span
            v-for="item in historyList"
            :key="item.id"
            class="tag"
            @click="quickSearch(item.keyword)"
          >{{ item.keyword }}</span>
        </div>
      </div>
    </div>

    <!-- 已发起搜索：结果列表 -->
    <div v-else class="result-state">
      <!-- 加载中 -->
      <div v-if="loading" v-loading="true" class="result-loading">
        <span>搜索中...</span>
      </div>
      <!-- 0 条结果：空态 + 推荐热门词 -->
      <div v-else-if="newsList.length === 0" class="empty">
        <el-empty description="没有找到相关内容">
          <template #default>
            <p class="empty-tip">试试这些热门搜索：</p>
            <div class="tag-list">
              <span
                v-for="(kw, idx) in hotKeywords"
                :key="idx"
                class="tag tag-hot"
                @click="quickSearch(kw)"
              >{{ kw }}</span>
            </div>
          </template>
        </el-empty>
      </div>
      <!-- 有结果：复用 NewsItem -->
      <div v-else class="news-list">
        <NewsItem
          v-for="item in newsList"
          :key="item.id"
          :news="item"
        />
        <div v-if="!hasMore" class="no-more">
          <span>没有更多了</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default { name: 'SearchResult' }
</script>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search, ArrowLeft, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { searchNews } from '@/api/news'
import { addSearchHistory, getSearchHistoryList, clearSearchHistory as clearSearchHistoryApi } from '@/api/searchHistory'
import NewsItem from '@/components/NewsItem.vue'
import { useUserStore } from '@/pinia/userStore'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// ============== 状态 ==============
// 用户当前输入的关键词
const keyword = ref('')
// 是否已经发起过搜索（用于切换「初始态 / 结果态」）
const hasSearched = ref(false)
// 搜索结果列表（统一字段名，兼容 NewsItem 组件的 publish_time 字段）
const newsList = ref([])
// 是否还有更多结果
const hasMore = ref(true)
// 加载中
const loading = ref(false)

// 热门搜索关键词（前端硬编码；改这里就能调整）
const hotKeywords = [
  '人工智能',
  'SpaceX',
  '苹果发布会',
  '量子计算',
  '华为',
  '特斯拉',
  '三星',
  '新能源汽车',
  '世界杯',
  'AI绘画'
]

// 当前登录状态（控制是否展示「历史搜索」区块）
const isLoggedIn = ref(userStore.isLoggedIn)
// 当前用户的服务端搜索历史
const historyList = ref([])

// ============== 历史搜索（绑定服务端） ==============
/** 拉取当前登录用户的服务端搜索历史 */
const loadHistory = async () => {
  if (!isLoggedIn.value) {
    historyList.value = []
    return
  }
  try {
    const res = await getSearchHistoryList(10)
    historyList.value = (res.data && res.data.list) || []
  } catch {
    // 拦截器已统一弹错，这里静默兜底
    historyList.value = []
  }
}

/** 上报一条搜索历史到服务端（仅登录用户） */
const reportHistory = async (kw) => {
  if (!isLoggedIn.value) return
  try {
    await addSearchHistory(kw)
    // 重新拉一次，保证顺序与去重与后端一致
    await loadHistory()
  } catch {
    // 上报失败不影响搜索结果展示
  }
}

/** 清空历史搜索（带二次确认 + 调服务端接口） */
const onClearHistory = async () => {
  if (!isLoggedIn.value) return
  try {
    await ElMessageBox.confirm('确定要清空所有搜索历史吗？', '提示', {
      confirmButtonText: '清空',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch {
    return // 用户取消
  }
  try {
    await clearSearchHistoryApi()
    historyList.value = []
    ElMessage.success('已清空搜索历史')
  } catch {
    // 拦截器已弹错
  }
}

// ============== 搜索行为 ==============
/**
 * 执行搜索：关键词校验 + 调接口 + 上报历史
 */
const doSearch = async () => {
  // 去掉空格后的真实关键词，用于判定有效长度
  const clean = keyword.value.replace(/\s+/g, '').trim()
  if (clean.length < 2) {
    ElMessage.warning('请输入至少 2 个字符')
    return
  }

  loading.value = true
  newsList.value = []
  hasMore.value = true
  hasSearched.value = true

  // 把当前关键词同步到 URL（刷新 / 分享时保留状态）
  router.replace({ name: 'SearchResult', query: { keyword: clean } })

  try {
    const res = await searchNews({ keyword: clean, page: 1, pageSize: 10 })
    const data = res.data || {}
    // 统一字段命名：把后端返回的 publishTime / categoryId 转成 NewsItem 期待的 publish_time / category_id
    newsList.value = (data.list || []).map((n) => ({
      ...n,
      publish_time: n.publishTime,
      category_id: n.categoryId
    }))
    hasMore.value = !!data.hasMore
    // 搜索成功后再上报历史（登录用户才会真正写入服务端）
    reportHistory(clean)
  } catch (e) {
    // request 拦截器已统一弹错提示，这里保持 loading 收尾即可
    newsList.value = []
    hasMore.value = false
  } finally {
    loading.value = false
  }
}

/** 点击搜索按钮 / 输入框回车 */
const handleSearch = () => doSearch()

/** 点击热门词 / 历史词：先填入输入框，立即触发搜索 */
const quickSearch = (kw) => {
  keyword.value = kw
  doSearch()
}

/** 清空输入框时，回到初始态 */
const onInputClear = () => {
  hasSearched.value = false
  newsList.value = []
  router.replace({ name: 'SearchResult' })
}

/** 点击返回：优先回上一页，否则回首页 */
const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.replace('/home')
  }
}

// 监听 URL 上的 keyword query：支持外链直接打开带关键词的搜索页
watch(
  () => route.query.keyword,
  (val) => {
    if (typeof val === 'string' && val.length >= 2) {
      keyword.value = val
      doSearch()
    }
  },
  { immediate: true }
)

// 监听登录态变化：登入时拉历史，登出时清空本地缓存
watch(
  () => userStore.isLoggedIn,
  (val) => {
    isLoggedIn.value = val
    if (val) loadHistory()
    else historyList.value = []
  }
)

// 进入页面即尝试拉一次历史（未登录时由 loadHistory 内部兜底）
onMounted(() => {
  loadHistory()
})
</script>

<style lang="scss" scoped>
.search-page {
  background: #f5f5f5;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

// 顶部 header
.search-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: #e63946;
  color: #fff;
  flex-shrink: 0;

  .back-icon {
    font-size: 22px;
    cursor: pointer;
    flex-shrink: 0;
  }

  .search-input {
    flex: 1;

    // 覆盖 element-plus 输入框内部颜色，与红色 header 协调
    :deep(.el-input__wrapper) {
      background: #fff;
      border-radius: 18px;
      padding: 4px 12px;
    }
    :deep(.el-input__inner) {
      height: 32px;
      font-size: 0.875rem;
    }
  }

  .search-btn {
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.85);
    color: #fff;
    border-radius: 16px;
    padding: 6px 14px;
    font-size: 0.875rem;
    cursor: pointer;
    flex-shrink: 0;

    &:active {
      background: rgba(255, 255, 255, 0.18);
    }
  }
}

// 初始态 / 结果态通用容器
.initial-state,
.result-state {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

// 区块（热门 / 历史）
.section {
  margin-bottom: 22px;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .section-title {
    font-size: 0.9375rem;
    color: #333;
    font-weight: 600;
    margin: 0 0 12px;
  }

  .clear-icon {
    font-size: 18px;
    color: #999;
    cursor: pointer;
  }

  .tag-list {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }

  .tag {
    display: inline-block;
    padding: 6px 14px;
    background: #fff;
    border: 1px solid #eee;
    border-radius: 16px;
    font-size: 0.8125rem;
    color: #555;
    cursor: pointer;
    transition: all 0.15s ease;

    &:active {
      background: #f0f0f0;
    }

    &.tag-hot {
      color: #e63946;
      border-color: #fbd0d4;
    }
  }
}

// 结果态
.result-loading {
  text-align: center;
  color: #999;
  font-size: 0.875rem;
  padding: 40px 0;
}

.empty {
  padding: 30px 0;

  .empty-tip {
    color: #999;
    font-size: 0.875rem;
    margin: 0 0 12px;
  }
}

.news-list {
  background: transparent;
}

.no-more {
  text-align: center;
  padding: 18px;
  color: #bbb;
  font-size: 0.8125rem;
}
</style>