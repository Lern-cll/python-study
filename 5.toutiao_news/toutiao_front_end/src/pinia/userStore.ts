/**
 * 用户状态管理
 * 负责：登录、注册、用户信息拉取/更新、修改密码、退出登录
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  login as loginApi,
  register as registerApi,
  getUserInfo as getUserInfoApi,
  updateUserInfo as updateUserInfoApi,
  updatePassword as updatePasswordApi
} from '@/api/user'
import { setToken, setUserInfo, clearAuth, getUserInfo, getToken } from '@/utils/auth'

/**
 * 提取 token 字符串。
 * 后端接口返回不一致：
 *  - /user/login    → token 为字符串
 *  - /user/register → token 为对象 { id, user_id, token, expires_at, created_at }
 * 这里统一从两种形态中取出真正的 token 字符串。
 * @param raw - 接口返回的 token 字段
 * @returns token 字符串，无法解析时返回空串
 */
const extractToken = (raw: unknown): string => {
  if (typeof raw === 'string') return raw
  if (raw && typeof raw === 'object' && 'token' in (raw as Record<string, unknown>)) {
    return String((raw as Record<string, unknown>).token ?? '')
  }
  return ''
}

export const useUserStore = defineStore('user', () => {
  // ============ 状态 ============
  // 当前登录用户信息（null 表示未登录）
  const userInfo = ref<UserInfo | null>(null)
  // 是否已登录（与 userInfo 联动，供模板直接读取）
  const isLoggedIn = ref(false)
  // 当前登录用户的 token（运行时态，与 localStorage 同步；供拦截器读取）
  const token = ref<string>('')

  // ============ 内部方法 ============
  /**
   * 从本地缓存恢复用户信息，用于刷新页面或首次加载时保持登录态
   */
  const initUserInfo = () => {
    const cachedInfo = getUserInfo()
    if (cachedInfo) {
      userInfo.value = cachedInfo
      isLoggedIn.value = true
    }
  }

  // ============ Action ============
  /**
   * 登录：调用登录接口，提取 token 写入 Pinia 与 localStorage，并缓存用户信息
   * @param data - 用户名与密码
   * @returns 原始接口响应
   */
  const login = async (data: { username: string; password: string }) => {
    const res = await loginApi(data)
    const payload = res?.data ?? {}
    // 字段名以后端为准：后端返回 userInfo（非 user）
    const tk = extractToken(payload.token)
    // 同步写入 Pinia（运行时态，供拦截器直接读取）
    token.value = tk
    // 同步写入 localStorage（持久化，刷新页面后仍能恢复登录态）
    setToken(tk)
    userInfo.value = payload.userInfo ?? null
    if (userInfo.value) {
      setUserInfo(userInfo.value)
    }
    isLoggedIn.value = !!userInfo.value
    return res
  }

  /**
   * 注册：与登录保持一致；data.token 实际是对象 { id, user_id, token, expires_at, created_at }
   * @param data - 用户名与密码
   * @returns 原始接口响应
   */
  const register = async (data: { username: string; password: string }) => {
    const res = await registerApi(data)
    const payload = res?.data ?? {}
    const tk = extractToken(payload.token)
    // 同步写入 Pinia（运行时态，供拦截器直接读取）
    token.value = tk
    // 同步写入 localStorage（持久化，刷新页面后仍能恢复登录态）
    setToken(tk)
    userInfo.value = payload.userInfo ?? null
    if (userInfo.value) {
      setUserInfo(userInfo.value)
    }
    isLoggedIn.value = !!userInfo.value
    return res
  }

  /**
   * 拉取最新用户信息并同步到本地缓存（应用启动或登录后刷新使用）
   */
  const fetchUserInfo = async () => {
    try {
      const res = await getUserInfoApi()
      const payload = res?.data ?? {}
      // 字段名统一为 userInfo；旧字段 user 留作兼容
      userInfo.value = payload.userInfo ?? payload.user ?? null
      if (userInfo.value) {
        setUserInfo(userInfo.value)
      }
      isLoggedIn.value = !!userInfo.value
    } catch (error) {
      console.error('获取用户信息失败', error)
    }
  }

  /**
   * 更新用户信息（昵称、头像、简介等），成功后本地缓存同步覆盖
   * @param data - 要更新的字段
   * @returns 原始接口响应
   */
  const updateUserInfo = async (data: Partial<UserInfo>) => {
    const res = await updateUserInfoApi(data)
    if (userInfo.value) {
      userInfo.value = { ...userInfo.value, ...data }
      setUserInfo(userInfo.value)
    }
    return res
  }

  /**
   * 修改密码
   * @param data - 旧密码与新密码
   * @returns 原始接口响应
   */
  const changePassword = async (data: { oldPassword: string; newPassword: string }) => {
    return await updatePasswordApi(data)
  }

  /**
   * 退出登录：清空本地凭证与 store 状态，不发起接口请求
   */
  const logout = () => {
    clearAuth()
    userInfo.value = null
    isLoggedIn.value = false
    // 同步清空 Pinia 中的 token，避免退出后仍被拦截器误带
    token.value = ''
  }

  /**
   * 从 localStorage 恢复 token（与 userInfo 一起，在 initUserInfo 中调用）
   * 保证刷新页面后拦截器依然能读到 token
   */
  const initToken = () => {
    const cached = getToken()
    if (cached) token.value = cached
  }

  // 初始化：从 localStorage 恢复登录态
  initUserInfo()
  initToken()

  return {
    userInfo,
    isLoggedIn,
    token,
    login,
    register,
    fetchUserInfo,
    updateUserInfo,
    changePassword,
    logout
  }
})