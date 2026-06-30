<template>
  <div class="history-list-page">
    <!-- 顶部：返回 + 标题 + 清空按钮（仅在有数据时显示） -->
    <div class="header">
      <el-icon @click="router.back()"><ArrowLeft /></el-icon>
      <span>浏览历史</span>
      <el-button text size="small" @click="handleClear" v-if="list.length > 0">
        清空
      </el-button>
    </div>
    <div class="content" v-loading="loading">
      <!-- 历史列表：每项含新闻卡片 + 删除按钮，删除按钮 .stop 阻止冒泡 -->
      <div
        v-for="item in list"
        :key="item.id"
        class="history-item"
        @click="handleClick(item)"
      >
        <NewsItem :news="item.news || item" />
        <div class="delete-btn" @click.stop="handleDelete(item.id)">
          <el-icon><Delete /></el-icon>
        </div>
      </div>
      <!-- 空状态 -->
      <div v-if="!loading && list.length === 0" class="empty-state">
        <el-icon :size="48"><Clock /></el-icon>
        <p>暂无浏览记录</p>
      </div>
      <!-- 加载更多 -->
      <div v-if="hasMore" class="load-more" @click="loadMore">
        <span v-if="loadingMore">加载中...</span>
        <span v-else>加载更多</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Clock, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getHistoryList, deleteHistory, clearHistory } from '@/api/history'
import NewsItem from '@/components/NewsItem.vue'

const router = useRouter()

// 首次加载列表的 loading
const loading = ref(false)
// 加载更多时的 loading
const loadingMore = ref(false)
// 浏览历史列表
const list = ref([])
// 当前页码（分页）
const page = ref(1)
// 每页条数
const pageSize = ref(10)
// 是否还有更多可加载
const hasMore = ref(false)

/** 进入页面：拉取第一页历史记录 */
onMounted(() => {
  fetchList()
})

/** 拉取第一页浏览历史（重置页码 1） */
const fetchList = async () => {
  loading.value = true
  try {
    const res = await getHistoryList({ page: 1, pageSize: pageSize.value })
    list.value = res.data || res.list || []
    hasMore.value = list.value.length >= (res.total || res.count || 0)
  } catch (e) {
    ElMessage.error('获取浏览历史失败')
  } finally {
    loading.value = false
  }
}

/** 加载下一页：追加到 list 末尾 */
const loadMore = async () => {
  if (loadingMore.value) return
  loadingMore.value = true
  page.value++
  try {
    const res = await getHistoryList({ page: page.value, pageSize: pageSize.value })
    list.value = [...list.value, ...(res.data || res.list || [])]
    hasMore.value = list.value.length < (res.total || res.count || 0)
  } catch (e) {
    ElMessage.error('加载更多失败')
  } finally {
    loadingMore.value = false
  }
}

/**
 * 点击某条历史：跳转到对应新闻详情
 * @param item - 历史记录项
 */
const handleClick = (item) => {
  const newsId = item.newsId || item.id
  router.push(`/news/${newsId}`)
}

/**
 * 删除单条浏览历史：调接口成功后从本地列表移除
 * @param historyId - 历史记录 ID
 */
const handleDelete = async (historyId) => {
  try {
    await deleteHistory(historyId)
    list.value = list.value.filter(item => item.id !== historyId)
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
    // 取消操作
  }
}
</script>

<style lang="scss" scoped>
.history-list-page {
  min-height: 100vh;
  background: #f5f5f5;

  .header {
    display: flex;
    align-items: center;
    padding: 12px 15px;
    background: #fff;
    border-bottom: 1px solid #f0f0f0;

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

  .content {
    min-height: calc(100vh - 50px);

    .history-item {
      position: relative;

      .delete-btn {
        position: absolute;
        top: 10px;
        right: 10px;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        opacity: 0;
        transition: opacity 0.3s;

        .el-icon {
          color: #fff;
          font-size: 14px;
        }
      }

      &:hover .delete-btn {
        opacity: 1;
      }
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
  }
}
</style>