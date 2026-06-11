import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import Home from '@/pages/Home.vue'
import AiChat from '@/pages/AiChat.vue'
import Mine from '@/pages/Mine.vue'
import NewsDetail from '@/pages/NewsDetail.vue'
import Login from '@/pages/Login.vue'
import Register from '@/pages/Register.vue'
import UserInfo from '@/pages/UserInfo.vue'
import FavoriteList from '@/pages/FavoriteList.vue'
import HistoryList from '@/pages/HistoryList.vue'
import { getToken, isTokenExpired } from '@/utils/auth'
import { ElMessage } from 'element-plus'

const routes = [
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
        meta: { title: '首页' }
      },
      {
        path: '/ai-chat',
        name: 'AiChat',
        component: AiChat,
        meta: { title: 'AI问答' }
      },
      {
        path: '/mine',
        name: 'Mine',
        component: Mine,
        meta: { title: '我的', requiresAuth: true }
      }
    ]
  },
  {
    path: '/news/:id',
    name: 'NewsDetail',
    component: NewsDetail,
    meta: { title: '新闻详情' }
  },
  {
    path: '/user-info',
    name: 'UserInfo',
    component: UserInfo,
    meta: { title: '个人信息', requiresAuth: true }
  },
  {
    path: '/favorites',
    name: 'FavoriteList',
    component: FavoriteList,
    meta: { title: '我的收藏', requiresAuth: true }
  },
  {
    path: '/history',
    name: 'HistoryList',
    component: HistoryList,
    meta: { title: '浏览历史', requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
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