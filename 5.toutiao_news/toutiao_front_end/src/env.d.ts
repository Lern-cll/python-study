/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

interface UserInfo {
  id?: number
  username?: string
  nickname?: string
  avatar?: string
  email?: string
  phone?: string
}

interface NewsItem {
  id: number
  title: string
  source?: string
  coverImage?: string
  content?: string
  views?: number
  publishTime?: string
  createTime?: string
  categoryId?: number
}

interface CategoryItem {
  id: number
  name: string
}

interface ApiResponse<T = any> {
  code: number
  message: string
  data?: T
  list?: T[]
  total?: number
}