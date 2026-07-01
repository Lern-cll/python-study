/// <reference types="vite/client" />

// 全局类型声明文件：声明 .vue 单文件组件与项目共用的接口类型

declare module '*.vue' {
  // 让 TS 识别 .vue 导入为 Vue 组件
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

/** 当前登录用户信息 */
interface UserInfo {
  /** 用户ID */
  id?: number
  /** 用户名（登录账号） */
  username?: string
  /** 昵称 */
  nickname?: string
  /** 头像 URL（后端可能返回 null） */
  avatar?: string | null
  /** 性别：unknown / male / female */
  gender?: string
  /** 个人简介 */
  bio?: string
  /** 邮箱 */
  email?: string
  /** 手机号 */
  phone?: string
}

/** 新闻条目（同时兼容后端返回的多种字段命名） */
interface NewsItem {
  /** 新闻ID */
  id: number
  /** 新闻标题 */
  title: string
  /** 摘要描述 */
  description?: string
  /** 作者/来源 */
  author?: string
  /** 封面图 URL */
  image?: string
  /** 正文 HTML */
  content?: string
  /** 浏览量 */
  views?: number
  /** 发布时间（后端驼峰命名） */
  publish_time?: string
  /** 发布时间（后端驼峰命名，部分接口使用） */
  publishTime?: string
  /** 创建时间（后端下划线命名） */
  created_at?: string
  /** 更新时间（后端下划线命名） */
  updated_at?: string
  /** 分类ID（驼峰） */
  category_id?: number
  /** 分类ID（部分接口使用驼峰） */
  categoryId?: number
  /** 相关推荐列表 */
  relatedNews?: RelatedNewsItem[]
}

/** 相关推荐新闻条目（详情页底部使用） */
interface RelatedNewsItem {
  /** 新闻ID */
  id: number
  /** 标题 */
  title: string
  /** 缩略图 URL */
  image?: string
  /** 作者 */
  author?: string
  /** 发布时间 */
  publishTime?: string
  /** 浏览量 */
  views?: number
}

/** 新闻分类 */
interface CategoryItem {
  /** 分类ID */
  id: number
  /** 分类名称 */
  name: string
}

/** 统一接口响应格式 */
interface ApiResponse<T = any> {
  /** 业务状态码（200/0 表示成功） */
  code: number
  /** 提示信息 */
  message: string
  /** 业务数据 */
  data?: T
  /** 列表数据（部分接口直接返回 list） */
  list?: T[]
  /** 总条数（分页时使用） */
  total?: number
}