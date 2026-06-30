import axios, { AxiosInstance, AxiosError, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { getToken, removeToken } from './auth'
import router from '@/router'

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
    // 添加 Token
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