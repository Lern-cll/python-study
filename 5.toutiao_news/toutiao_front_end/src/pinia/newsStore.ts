/**
 * 新闻状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getCategories as getCategoriesApi,
  getNewsList as getNewsListApi,
  getNewsDetail as getNewsDetailApi
} from '@/api/news'

export const useNewsStore = defineStore('news', () => {
  // 状态
  const categories = ref<CategoryItem[]>([])
  const newsList = ref<NewsItem[]>([])
  const currentNews = ref<NewsItem | null>(null)
  const loading = ref(false)
  const currentPage = ref(1)
  const pageSize = ref(10)
  const total = ref(0)
  const hasMore = ref(false)

  // 获取分类列表
  const fetchCategories = async () => {
    try {
      const res = await getCategoriesApi()
      categories.value = res.data || res.list || []
    } catch (error) {
      console.error('获取分类失败', error)
    }
  }

  // 获取新闻列表
  const fetchNewsList = async (params: { categoryId?: number | null; page?: number } = {}) => {
    loading.value = true
    try {
      const res = await getNewsListApi({
        page: currentPage.value,
        pageSize: pageSize.value,
        ...params
      })
      const payload = res.data || res
      const list = payload.list || payload.newsList || []
      const isFirstPage = params.page === 1 || !params.page
      if (isFirstPage) {
        newsList.value = list
      } else {
        newsList.value = [...newsList.value, ...list]
      }
      total.value = payload.total || payload.count || 0
      // 加载更多时若后端返回空数据，强制认为没有更多，避免 page 一直被自增
      if (!isFirstPage && list.length === 0) {
        hasMore.value = false
      } else {
        hasMore.value = !!payload.hasMore
      }
    } catch (error) {
      console.error('获取新闻列表失败', error)
    } finally {
      loading.value = false
    }
  }

  // 获取新闻详情
  const fetchNewsDetail = async (id: number) => {
    loading.value = true
    try {
      const res = await getNewsDetailApi(id)
      currentNews.value = res.data || res
    } catch (error) {
      console.error('获取新闻详情失败', error)
    } finally {
      loading.value = false
    }
  }

  // 分页加载更多
  const loadMore = async (params: { categoryId?: number | null } = {}) => {
    currentPage.value++
    await fetchNewsList({ ...params, page: currentPage.value })
  }

  // 重置分页
  const resetPage = () => {
    currentPage.value = 1
    newsList.value = []
    hasMore.value = false
  }

  return {
    categories,
    newsList,
    currentNews,
    loading,
    currentPage,
    pageSize,
    total,
    hasMore,
    fetchCategories,
    fetchNewsList,
    fetchNewsDetail,
    loadMore,
    resetPage
  }
})