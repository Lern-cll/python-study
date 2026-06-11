/**
 * 新闻状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getCategories as getCategoriesApi, getNewsList as getNewsListApi, getNewsDetail as getNewsDetailApi } from '@/api/news'

export const useNewsStore = defineStore('news', () => {
  // 状态
  const categories = ref([])
  const newsList = ref([])
  const currentNews = ref(null)
  const loading = ref(false)
  const currentPage = ref(1)
  const pageSize = ref(10)
  const total = ref(0)

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
  const fetchNewsList = async (params = {}) => {
    loading.value = true
    try {
      const res = await getNewsListApi({
        page: currentPage.value,
        pageSize: pageSize.value,
        ...params
      })
      const list = res.data || res.list || res.newsList || []
      if (params.page === 1 || !params.page) {
        newsList.value = list
      } else {
        newsList.value = [...newsList.value, ...list]
      }
      total.value = res.total || res.count || 0
    } catch (error) {
      console.error('获取新闻列表失败', error)
    } finally {
      loading.value = false
    }
  }

  // 获取新闻详情
  const fetchNewsDetail = async (id) => {
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
  const loadMore = async (params = {}) => {
    currentPage.value++
    await fetchNewsList(params)
  }

  // 重置分页
  const resetPage = () => {
    currentPage.value = 1
    newsList.value = []
  }

  return {
    categories,
    newsList,
    currentNews,
    loading,
    currentPage,
    pageSize,
    total,
    fetchCategories,
    fetchNewsList,
    fetchNewsDetail,
    loadMore,
    resetPage
  }
})