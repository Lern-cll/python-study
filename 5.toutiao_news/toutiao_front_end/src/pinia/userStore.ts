/**
 * 用户状态管理
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
import { setToken, setUserInfo, clearAuth, getUserInfo } from '@/utils/auth'

/**
 * 提取 token 字符串。
 * 后端接口返回不一致：
 *  - /user/login    → token 为字符串
 *  - /user/register → token 为对象 { id, user_id, token, expires_at, created_at }
 * 这里统一从两种形态中取出真正的 token 字符串。
 */
const extractToken = (raw: unknown): string => {
  if (typeof raw === 'string') return raw
  if (raw && typeof raw === 'object' && 'token' in (raw as Record<string, unknown>)) {
    return String((raw as Record<string, unknown>).token ?? '')
  }
  return ''
}

export const useUserStore = defineStore('user', () => {
  // 状态
  const userInfo = ref<UserInfo | null>(null)
  const isLoggedIn = ref(false)

  // 初始化用户信息
  const initUserInfo = () => {
    const cachedInfo = getUserInfo()
    if (cachedInfo) {
      userInfo.value = cachedInfo
      isLoggedIn.value = true
    }
  }

  // 登录：res 为 { code, message, data: { token, userInfo } }，data.token 为字符串
  const login = async (data: { username: string; password: string }) => {
    const res = await loginApi(data)
    const payload = res?.data ?? {}
    // 字段名以后端为准：后端返回 userInfo（非 user）
    setToken(extractToken(payload.token))
    userInfo.value = payload.userInfo ?? null
    if (userInfo.value) {
      setUserInfo(userInfo.value)
    }
    isLoggedIn.value = !!userInfo.value
    return res
  }

  // 注册：与登录保持一致；data.token 实际是对象 { id, user_id, token, expires_at, created_at }
  const register = async (data: { username: string; password: string }) => {
    const res = await registerApi(data)
    const payload = res?.data ?? {}
    setToken(extractToken(payload.token))
    userInfo.value = payload.userInfo ?? null
    if (userInfo.value) {
      setUserInfo(userInfo.value)
    }
    isLoggedIn.value = !!userInfo.value
    return res
  }

  // 获取用户信息
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

  // 更新用户信息
  const updateUserInfo = async (data: Partial<UserInfo>) => {
    const res = await updateUserInfoApi(data)
    if (userInfo.value) {
      userInfo.value = { ...userInfo.value, ...data }
      setUserInfo(userInfo.value)
    }
    return res
  }

  // 修改密码
  const changePassword = async (data: { oldPassword: string; newPassword: string }) => {
    return await updatePasswordApi(data)
  }

  // 退出登录
  const logout = () => {
    clearAuth()
    userInfo.value = null
    isLoggedIn.value = false
  }

  // 初始化
  initUserInfo()

  return {
    userInfo,
    isLoggedIn,
    login,
    register,
    fetchUserInfo,
    updateUserInfo,
    changePassword,
    logout
  }
})