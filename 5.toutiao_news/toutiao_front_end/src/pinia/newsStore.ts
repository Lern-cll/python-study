/**
 * 新闻状态管理
 * 负责：新闻分类列表、新闻列表分页、新闻详情
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getCategories as getCategoriesApi,
  getNewsList as getNewsListApi,
  getNewsDetail as getNewsDetailApi
} from '@/api/news'

/** 后端分页返回的负载（兼容多种字段命名） */
interface NewsListPayload {
  list?: NewsItem[]
  newsList?: NewsItem[]
  total?: number
  count?: number
  hasMore?: boolean
}

export const useNewsStore = defineStore('news', () => {
  // ============ 状态 ============
  // 新闻分类列表（顶部 Tab 切换使用）
  const categories = ref<CategoryItem[]>([])
  // 当前分类下的新闻列表（首页与加载更多共用）
  const newsList = ref<NewsItem[]>([])
  // 当前查看的新闻详情（详情页使用）
  const currentNews = ref<NewsItem | null>(null)
  // 列表/详情加载中标记
  const loading = ref(false)
  // 当前页码（分页）
  const currentPage = ref(1)
  // 每页条数
  const pageSize = ref(10)
  // 总条数（来自接口）
  const total = ref(0)
  // 是否还有更多数据可加载
  const hasMore = ref(false)

  // ============ Action ============
  /**
   * 拉取新闻分类列表，存入 categories
   */
  const fetchCategories = async () => {
    try {
      const res = await getCategoriesApi()
      const data = (res.data ?? res.list) as CategoryItem[] | undefined
      categories.value = data ?? []
    } catch (error) {
      console.error('获取分类失败', error)
    }
  }

  /**
   * 拉取新闻列表，根据 isFirstPage 决定是覆盖还是追加
   * @param params - 分类ID与页码
   */
  const fetchNewsList = async (params: { categoryId?: number | null; page?: number } = {}) => {
    loading.value = true
    try {
      const res = await getNewsListApi({
        page: currentPage.value,
        pageSize: pageSize.value,
        ...params
      })
      // res.data 兼容为 NewsItem[] / NewsListPayload（后端不同接口字段命名不同）
      const payload = (res.data ?? res) as unknown as NewsListPayload
      const list = payload.list || payload.newsList || []
      const isFirstPage = params.page === 1 || !params.page
      if (isFirstPage) {
        // 第一页：直接覆盖
        newsList.value = list
      } else {
        // 加载更多：追加到末尾
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

  /**
   * 拉取新闻详情并写入 currentNews
   * @param id - 新闻ID
   */
  const fetchNewsDetail = async (id: number) => {
    loading.value = true
    try {
      const res = await getNewsDetailApi(id)
      // 后端详情可能直接挂在 data，也可能整包返回，做一次类型规整
      currentNews.value = (res.data ?? res) as unknown as NewsItem
    } catch (error) {
      console.error('获取新闻详情失败', error)
    } finally {
      loading.value = false
    }
  }

  /**
   * 加载下一页（currentPage 自增 + 调用 fetchNewsList）
   * @param params - 分类ID
   */
  const loadMore = async (params: { categoryId?: number | null } = {}) => {
    currentPage.value++
    await fetchNewsList({ ...params, page: currentPage.value })
  }

  /**
   * 重置分页：切换分类或下拉刷新前调用
   */
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