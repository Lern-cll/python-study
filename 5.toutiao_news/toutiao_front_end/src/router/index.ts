import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import Home from '@/pages/home/Home.vue'
import AiChat from '@/pages/ai/AiChat.vue'
import Mine from '@/pages/user/Mine.vue'
import NewsDetail from '@/pages/news/NewsDetail.vue'
import SearchResult from '@/pages/search/SearchResult.vue'
import Login from '@/pages/auth/Login.vue'
import Register from '@/pages/auth/Register.vue'
import UserInfo from '@/pages/user/UserInfo.vue'
import FavoriteList from '@/pages/user/FavoriteList.vue'
import HistoryList from '@/pages/user/HistoryList.vue'
import { getToken, isTokenExpired } from '@/utils/auth'
import { ElMessage } from 'element-plus'

// 路由表：
// - meta.title       浏览器标题
// - meta.requiresAuth 需要登录后才能访问
// - meta.keepAlive   是否被 MainLayout 的 keep-alive 缓存
// - meta.hideTabBar  是否隐藏底部 TabBar（详情页等）
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { title: '注册' }
  },
  {
    path: '/',
    component: MainLayout,
    redirect: '/home',
    children: [
      {
        path: '/home',
        name: 'Home',
        component: Home,
        meta: { title: '首页', keepAlive: true }
      },
      {
        path: '/ai-chat',
        name: 'AiChat',
        component: AiChat,
        meta: { title: 'AI问答', requiresAuth: true }
      },
      {
        path: '/mine',
        name: 'Mine',
        component: Mine,
        meta: { title: '我的', requiresAuth: true }
      },
      {
        path: '/news/:id',
        name: 'NewsDetail',
        component: NewsDetail,
        meta: { title: '新闻详情', hideTabBar: true }
      },
      {
        path: '/search',
        name: 'SearchResult',
        component: SearchResult,
        meta: { title: '搜索', hideTabBar: true }
      },
      {
        path: '/user-info',
        name: 'UserInfo',
        component: UserInfo,
        meta: { title: '个人信息', requiresAuth: true, hideTabBar: true }
      },
      {
        path: '/favorites',
        name: 'FavoriteList',
        component: FavoriteList,
        meta: { title: '我的收藏', requiresAuth: true, hideTabBar: true }
      },
      {
        path: '/history',
        name: 'HistoryList',
        component: HistoryList,
        meta: { title: '浏览历史', requiresAuth: true, hideTabBar: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫：
// 1) 每次跳转都更新 document.title
// 2) 需要登录的页面：未登录或 Token 过期则跳登录，并带上 redirect 参数便于登录后回跳
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 头条App` : '头条App'

  if (to.meta.requiresAuth) {
    const token = getToken()
    if (!token || isTokenExpired()) {
      ElMessage.warning('请先登录')
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
  }

  next()
})

export default router