<template>
  <div class="favorite-list-page">
    <div class="header">
      <el-icon @click="router.back()"><ArrowLeft /></el-icon>
      <span>我的收藏</span>
      <el-button text size="small" @click="handleClear" v-if="list.length > 0">
        清空
      </el-button>
    </div>
    <div class="content" v-loading="loading">
      <NewsItem
        v-for="item in list"
        :key="item.id"
        :news="item.news || item"
        @click="handleClick(item)"
      />
      <div v-if="!loading && list.length === 0" class="empty-state">
        <el-icon :size="48"><Star /></el-icon>
        <p>暂无收藏内容</p>
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
import { ArrowLeft, Star } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getFavoriteList, removeFavorite, clearFavorites } from '@/api/favorite'
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
    const res = await getFavoriteList({ page: 1, pageSize: pageSize.value })
    list.value = res.data || res.list || []
    hasMore.value = list.value.length >= (res.total || res.count || 0)
  } catch (e) {
    ElMessage.error('获取收藏列表失败')
  } finally {
    loading.value = false
  }
}

const loadMore = async () => {
  if (loadingMore.value) return
  loadingMore.value = true
  page.value++
  try {
    const res = await getFavoriteList({ page: page.value, pageSize: pageSize.value })
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

const handleClear = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有收藏吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await clearFavorites()
    list.value = []
    ElMessage.success('已清空收藏')
  } catch (e) {
    // 取消操作
  }
}
</script>

<style lang="scss" scoped>
.favorite-list-page {
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