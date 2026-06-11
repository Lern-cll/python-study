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
    <div class="news-list" v-loading="loading">
      <NewsItem
        v-for="item in newsList"
        :key="item.id"
        :news="item"
      />
      <div v-if="!loading && newsList.length === 0" class="empty-state">
        <el-empty description="暂无数据" />
      </div>
      <div v-if="loading" class="loading-more">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
      <div v-if="!loading && hasMore" class="load-more" @click="loadMore">
        <span>加载更多</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useNewsStore } from '@/pinia/newsStore'
import CategoryNav from '@/components/CategoryNav.vue'
import NewsItem from '@/components/NewsItem.vue'
import { Loading } from '@element-plus/icons-vue'

const newsStore = useNewsStore()

const currentCategory = ref(null)
const categories = computed(() => [
  { id: null, name: '推荐' },
  ...newsStore.categories
])
const newsList = computed(() => newsStore.newsList)
const loading = computed(() => newsStore.loading)
const hasMore = computed(() => newsList.value.length < newsStore.total)

onMounted(async () => {
  await newsStore.fetchCategories()
  await newsStore.fetchNewsList()
})

const handleCategoryChange = async (category) => {
  newsStore.resetPage()
  await newsStore.fetchNewsList({ categoryId: category.id })
}

const loadMore = async () => {
  await newsStore.loadMore({ categoryId: currentCategory.value })
}
</script>

<style lang="scss" scoped>
.home-page {
  background: #f5f5f5;
  min-height: 100vh;

  .header {
    background: #e63946;
    color: #fff;
    padding: 12px 15px;

    .logo {
      font-size: 1.25rem;
      font-weight: 700;
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
}
</style>