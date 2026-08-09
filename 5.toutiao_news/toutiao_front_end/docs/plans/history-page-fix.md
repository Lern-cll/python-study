# 浏览历史页面修复 - 实施计划

## 功能目标

修复 `http://localhost:3000/history` 浏览历史页：
1. 接入与 `FavoriteList.vue` 一致的下拉刷新 + 触底自动加载。
2. 新建 `HistoryItem.vue` 精准展示 `title / description / image / author / views / view_time`。
3. 单条删除 + 一键清空操作在移动端可正常使用。

## 架构说明

- 复用 `FavoriteList.vue` 的下拉刷新与触底加载模板结构（阈值、阻尼、文案、icon 一致）。
- 复用 `FavoriteItem.vue` 的 props/emits 模式，事件交由父组件处理。
- 不引入新依赖，不引入 pinia store，状态保持在 HistoryList 页面级。

## 技术栈

- Vue 3 `<script setup>`
- Element Plus（图标、消息、确认框、loading）
- 现有 SCSS（与 FavoriteList 一致的样式令牌）

## 存放路径

- Spec：`docs/specs/history-page-fix.md`
- 本计划：`docs/plans/history-page-fix.md`
- 新增文件：`src/pages/user/HistoryItem.vue`
- 修改文件：`src/pages/user/HistoryList.vue`

---

## 任务清单

### 任务 1：新增 HistoryItem.vue 组件骨架

**涉及文件**：`src/pages/user/HistoryItem.vue`（新建）

**实施步骤**：

1. 在 `src/pages/user/` 下创建 `HistoryItem.vue`。
2. 写入以下 `<script setup>` 内容：

   ```js
   import { ref } from 'vue'
   import { View, Loading } from '@element-plus/icons-vue'

   const props = defineProps({
     item: { type: Object, required: true }
   })
   const emit = defineEmits(['click', 'delete'])

   const imageLoaded = ref(false)
   const onImageLoad = () => { imageLoaded.value = true }
   const onImageError = () => { imageLoaded.value = true }

   const handleRowClick = () => emit('click')
   const handleDeleteClick = () => emit('delete')

   const formatViewTime = (time) => {
     if (!time) return ''
     const date = new Date(time)
     if (Number.isNaN(date.getTime())) return ''
     const pad = (n) => String(n).padStart(2, '0')
     return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
   }

   const formatViews = (views) => {
     const n = Number(views) || 0
     if (n >= 10000) return `${(n / 10000).toFixed(1)}万`
     return n
   }
   ```

**完成标准**：文件存在，script 无语法错误（IDE 无报错）。

---

### 任务 2：完成 HistoryItem.vue 模板

**涉及文件**：`src/pages/user/HistoryItem.vue`

**实施步骤**：

在 `<script setup>` 之上写入 `<template>`：

```html
<template>
  <div class="history-item" @click="handleRowClick">
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

    <div class="body">
      <h3 class="title text-ellipsis-2">{{ item.title }}</h3>
      <p class="author text-ellipsis-1">{{ item.author || '头条号' }}</p>
      <p class="meta">
        <span class="view-time">浏览时间：{{ formatViewTime(item.view_time) }}</span>
        <span class="views">
          <el-icon><View /></el-icon>
          {{ formatViews(item.views) }}
        </span>
      </p>
    </div>

    <div class="actions" @click.stop>
      <el-button text type="danger" size="small" @click="handleDeleteClick">
        删除
      </el-button>
    </div>
  </div>
</template>
```

**测试与验证方式**：
- IDE 无模板语法报错。
- 字段全部对应 `test.json` 的 key（`title / description / image / author / views / view_time`）。

**完成标准**：模板可被 `<HistoryItem :item="row" />` 实例化且不出错。

---

### 任务 3：完成 HistoryItem.vue 样式

**涉及文件**：`src/pages/user/HistoryItem.vue`

**实施步骤**：

在文件末尾追加 `<style lang="scss" scoped>`，镜像 `FavoriteItem.vue` 的布局样式并替换 meta 行结构：

```scss
.history-item {
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
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.75rem;
      color: #999;
      margin: 0;

      .views {
        display: flex;
        align-items: center;
        flex-shrink: 0;

        .el-icon {
          margin-right: 3px;
          font-size: 12px;
        }
      }
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
```

注意：`description` 字段根据用户选择"只展示 view_time"的范围被排除，**不展示 description**。

**测试与验证方式**：保存后 IDE 无 CSS/SCSS 报错。

**完成标准**：HistoryItem.vue 整体可独立渲染 mock 数据中的一条历史记录。

---

### 任务 4：重写 HistoryList.vue 模板

**涉及文件**：`src/pages/user/HistoryList.vue`

**实施步骤**：

将整个 `<template>` 替换为：

```html
<template>
  <div class="history-list-page">
    <div class="header">
      <el-icon @click="router.back()"><ArrowLeft /></el-icon>
      <span>浏览历史</span>
      <el-button text size="small" @click="handleClear" v-if="list.length > 0">
        清空
      </el-button>
    </div>

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

      <div class="history-list" v-loading="loading">
        <HistoryItem
          v-for="item in list"
          :key="item.id"
          :item="item"
          @click="handleClick(item)"
          @delete="handleDelete(item.id)"
        />
        <div v-if="!loading && list.length === 0" class="empty-state">
          <el-icon :size="48"><Clock /></el-icon>
          <p>暂无浏览记录</p>
        </div>
        <div v-if="loadingMore" class="loading-more">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>
        <div v-if="!loading && !hasMore && list.length > 0" class="no-more">
          <span>没有更多了</span>
        </div>
      </div>
    </div>
  </div>
</template>
```

**测试与验证方式**：保存后 IDE 无模板报错。

**完成标准**：模板内所有引用（HistoryItem / 状态 / 方法）在 script 中已存在或即将补齐。

---

### 任务 5：重写 HistoryList.vue script

**涉及文件**：`src/pages/user/HistoryList.vue`

**实施步骤**：

将整个 `<script setup>` 替换为（镜像 FavoriteList 状态机与下拉/触底逻辑）：

```js
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Clock, Loading, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getHistoryList, deleteHistory, clearHistory } from '@/api/history'
import HistoryItem from './HistoryItem.vue'

const router = useRouter()

// 列表与分页状态
const loading = ref(false)
const loadingMore = ref(false)
const refreshing = ref(false)
const list = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const hasMore = ref(false)

// 下拉刷新状态
const scrollRef = ref(null)
const scrollContainer = ref(null)
const pullDistance = ref(0)
const startY = ref(0)
const startScrollTop = ref(0)
const threshold = 60
const maxDistance = 100

// 并发去重
let isLoadingMore = false
let lastLoadMoreAt = 0

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
    if (style.overflowY === 'auto' || style.overflowY === 'scroll') return node
    node = node.parentElement
  }
  return null
}

const getScrollBottom = (container) =>
  container.scrollHeight - container.scrollTop - container.clientHeight

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

const loadMore = async () => {
  page.value++
  await fetchList(false)
}

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

const onScroll = async () => {
  if (isLoadingMore || loading.value || refreshing.value || !hasMore.value) return
  if (!scrollContainer.value && scrollRef.value) {
    scrollContainer.value = findScrollParent(scrollRef.value)
  }
  const container = scrollContainer.value || scrollRef.value
  if (!container || container.scrollHeight <= container.clientHeight) return
  const scrollBottom = getScrollBottom(container)
  if (scrollBottom < 80) {
    await tryLoadMore()
  }
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
  if (startScrollTop.value > 0) return
  const currentY = e.touches[0].clientY
  const diff = currentY - startY.value
  if (diff <= 0) {
    pullDistance.value = 0
    return
  }
  pullDistance.value = Math.min(diff * 0.4, maxDistance)
}

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

onMounted(async () => {
  loading.value = true
  await fetchList(true)
  loading.value = false
  nextTick(() => {
    scrollContainer.value = scrollRef.value || findScrollParent(scrollRef.value)
  })
})

const handleClick = (item) => {
  router.push(`/news/${item.id}`)
}

const handleDelete = async (historyId) => {
  try {
    await deleteHistory(historyId)
    list.value = list.value.filter((x) => x.id !== historyId)
    ElMessage.success('删除成功')
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

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
    // 用户取消
  }
}
```

**测试与验证方式**：
- IDE 无 script 报错。
- 所有 import 已存在（`@/api/history`、`./HistoryItem.vue`）。

**完成标准**：组件能成功 mount、首次 fetch 与 mock 数据正常。

---

### 任务 6：重写 HistoryList.vue 样式

**涉及文件**：`src/pages/user/HistoryList.vue`

**实施步骤**：

将整个 `<style lang="scss" scoped>` 替换为：

```scss
.history-list-page {
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

  .history-list {
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
```

**测试与验证方式**：保存后 IDE 无 SCSS 报错。

**完成标准**：HistoryList 与 FavoriteList 视觉风格保持一致。

---

### 任务 7：浏览器手工验收

**涉及文件**：无（仅运行时验证）

**实施步骤**：

1. 启动 dev：`npm run dev`，浏览器打开 `http://localhost:3000/history`。
2. 按 Spec 验收标准 1-12 逐条验证：
   - 数据展示、字段完整性
   - 空态显示
   - 下拉刷新（≥60px 触发）
   - 触底自动加载（验证方法：临时修改 `test.json` 让 `hasMore = true`、`total = 30`，观察滚动行为）
   - 单条删除不触发整行跳转
   - 清空二次确认
   - 接口失败提示

**测试与验证方式**：在浏览器 DevTools Mobile 模式下肉眼检查 + 操作。

**完成标准**：Spec 验收标准全部通过。

---

## 自检清单

- [x] Spec 的每条要求都有对应任务（任务 1-7 覆盖字段展示、交互、删除、清空、刷新、加载更多）
- [x] 无 `TODO` / `TBD` / "后续实现" / "参考上一个任务"
- [x] 函数名 / 接口名前后一致：`fetchList / loadMore / tryLoadMore / onScroll / onTouchStart / onTouchMove / onTouchEnd / handleClick / handleDelete / handleClear`
- [x] 包含验证步骤（任务 7）

## 后续出口

- 执行阶段：`executing-plans` 或 `subagent-driven-development`
- 执行完成后：`requesting-code-review` → `verification-before-completion` → `finishing-a-development-branch`
