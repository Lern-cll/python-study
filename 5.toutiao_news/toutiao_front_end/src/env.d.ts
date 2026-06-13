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
  description?: string
  author?: string
  image?: string
  content?: string
  views?: number
  publish_time?: string
  publishTime?: string
  created_at?: string
  updated_at?: string
  category_id?: number
  categoryId?: number
  relatedNews?: RelatedNewsItem[]
}

interface RelatedNewsItem {
  id: number
  title: string
  image?: string
  author?: string
  publishTime?: string
  views?: number
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