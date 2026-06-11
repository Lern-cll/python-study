<template>
  <div class="history-list-page">
    <div class="header">
      <el-icon @click="router.back()"><ArrowLeft /></el-icon>
      <span>浏览历史</span>
      <el-button text size="small" @click="handleClear" v-if="list.length > 0">
        清空
      </el-button>
    </div>
    <div class="content" v-loading="loading">
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
      <div v-if="!loading && list.length === 0" class="empty-state">
        <el-icon :size="48"><Clock /></el-icon>
        <p>暂无浏览记录</p>
      </div>
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

const loading = ref(false)
const loadingMore = ref(false)
const list = ref([])
const page = ref(1)
const pageSize = ref(10)
const hasMore = ref(false)

onMounted(() => {
  fetchList()
})

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

const handleClick = (item) => {
  const newsId = item.newsId || item.id
  router.push(`/news/${newsId}`)
}

const handleDelete = async (historyId) => {
  try {
    await deleteHistory(historyId)
    list.value = list.value.filter(item => item.id !== historyId)
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