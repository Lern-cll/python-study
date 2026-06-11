/**
 * 用户状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, register as registerApi, getUserInfo as getUserInfoApi, updateUserInfo as updateUserInfoApi, updatePassword as updatePasswordApi } from '@/api/user'
import { setToken, removeToken, setUserInfo, clearAuth, getUserInfo } from '@/utils/auth'

export const useUserStore = defineStore('user', () => {
  // 状态
  const userInfo = ref(null)
  const isLoggedIn = ref(false)

  // 初始化用户信息
  const initUserInfo = () => {
    const cachedInfo = getUserInfo()
    if (cachedInfo) {
      userInfo.value = cachedInfo
      isLoggedIn.value = true
    }
  }

  // 登录
  const login = async (data) => {
    const res = await loginApi(data)
    setToken(res.token)
    userInfo.value = res.user
    setUserInfo(res.user)
    isLoggedIn.value = true
    return res
  }

  // 注册
  const register = async (data) => {
    const res = await registerApi(data)
    setToken(res.token)
    userInfo.value = res.user
    setUserInfo(res.user)
    isLoggedIn.value = true
    return res
  }

  // 获取用户信息
  const fetchUserInfo = async () => {
    try {
      const res = await getUserInfoApi()
      userInfo.value = res.user || res
      setUserInfo(userInfo.value)
      isLoggedIn.value = true
    } catch (error) {
      console.error('获取用户信息失败', error)
    }
  }

  // 更新用户信息
  const updateUserInfo = async (data) => {
    const res = await updateUserInfoApi(data)
    userInfo.value = { ...userInfo.value, ...data }
    setUserInfo(userInfo.value)
    return res
  }

  // 修改密码
  const changePassword = async (data) => {
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