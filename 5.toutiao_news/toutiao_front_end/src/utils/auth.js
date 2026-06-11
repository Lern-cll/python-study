/**
 * Token 管理工具
 * 负责 Token 的存储、获取、验证
 */

const TOKEN_KEY = 'toutiao_token'
const TOKEN_EXPIRES_KEY = 'toutiao_token_expires'

/**
 * 获取 Token
 * @returns {string|null} Token值
 */
export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

/**
 * 设置 Token
 * @param {string} token - Token值
 * @param {number} expiresIn - 有效期（秒），默认7天
 */
export function setToken(token, expiresIn = 7 * 24 * 60 * 60) {
  localStorage.setItem(TOKEN_KEY, token)
  const expiresTime = Date.now() + expiresIn * 1000
  localStorage.setItem(TOKEN_EXPIRES_KEY, expiresTime.toString())
}

/**
 * 移除 Token
 */
export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(TOKEN_EXPIRES_KEY)
}

/**
 * 检查 Token 是否过期
 * @returns {boolean} 是否过期
 */
export function isTokenExpired() {
  const expiresTime = localStorage.getItem(TOKEN_EXPIRES_KEY)
  if (!expiresTime) return true
  return Date.now() > parseInt(expiresTime)
}

/**
 * 获取用户信息
 * @returns {object|null} 用户信息
 */
export function getUserInfo() {
  const userInfoStr = localStorage.getItem('toutiao_user_info')
  return userInfoStr ? JSON.parse(userInfoStr) : null
}

/**
 * 设置用户信息
 * @param {object} userInfo - 用户信息
 */
export function setUserInfo(userInfo) {
  localStorage.setItem('toutiao_user_info', JSON.stringify(userInfo))
}

/**
 * 清除所有认证信息
 */
export function clearAuth() {
  removeToken()
  localStorage.removeItem('toutiao_user_info')
}