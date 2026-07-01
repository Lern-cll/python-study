import axios, { AxiosInstance, AxiosError, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { getToken, removeToken } from './auth'
import router from '@/router'

/**
 * 请求白名单：命中下列路径的接口不需要携带 token（首页相关免登录）
 * - /news/categories 首页分类导航
 * - /news/list       首页新闻列表
 * - /news/detail     新闻详情
 * 注意：使用 includes 做模糊匹配，因 axios 内部已拼接 baseURL('/api')，
 * 所以 url 形如 '/api/news/list'，直接用 '/news/list' 即可匹配
 */
const WHITELIST: string[] = ['/news/categories', '/news/list', '/news/detail']

// 创建 Axios 实例：统一 baseURL、超时、请求头
const service: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器：每次请求自动从 localStorage 取出 Token 放入 Authorization 头
service.interceptors.request.use(
  (config) => {
    // 白名单内的请求直接放行，不加 token（首页可随意访问）
    const url = config.url || ''
    if (WHITELIST.some((path) => url.includes(path))) {
      return config
    }

    // 非白名单请求：自动追加 Authorization 头
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    // 请求阶段异常直接 reject，由调用方处理
    return Promise.reject(error)
  }
)

// 响应拦截器：
// 1) 业务状态码 200/0 视为成功，否则弹错误并 reject
// 2) HTTP 状态码非 2xx 时按 401/404/500 等分类提示
service.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data

    // 根据业务状态码判断
    if (res.code !== 200 && res.code !== 0) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }

    // 成功时直接返回业务数据，调用方通过 res.data 访问
    return res
  },
  (error: AxiosError) => {
    // 处理 HTTP 状态码
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // Token 失效：清掉本地凭证并跳转登录页
          ElMessage.error('登录已过期，请重新登录')
          removeToken()
          router.push('/login')
          break
        case 404:
          ElMessage.error('请求资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error((error.message as string) || '网络请求失败')
      }
    } else {
      // 无 response：通常是网络中断或超时
      ElMessage.error((error.message as string) || '网络请求失败')
    }

    return Promise.reject(error)
  }
)

export default service