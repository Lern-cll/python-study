/**
 * Token 管理工具
 * 负责 Token 的存储、获取、验证
 */

const TOKEN_KEY = 'toutiao_token'
const TOKEN_EXPIRES_KEY = 'toutiao_token_expires'

/**
 * 获取 Token
 */
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

/**
 * 设置 Token
 * @param token - Token值
 * @param expiresIn - 有效期（秒），默认7天
 */
export function setToken(token: string, expiresIn: number = 7 * 24 * 60 * 60): void {
  localStorage.setItem(TOKEN_KEY, token)
  const expiresTime = Date.now() + expiresIn * 1000
  localStorage.setItem(TOKEN_EXPIRES_KEY, expiresTime.toString())
}

/**
 * 移除 Token
 */
export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(TOKEN_EXPIRES_KEY)
}

/**
 * 检查 Token 是否过期
 */
export function isTokenExpired(): boolean {
  const expiresTime = localStorage.getItem(TOKEN_EXPIRES_KEY)
  if (!expiresTime) return true
  return Date.now() > parseInt(expiresTime)
}

/**
 * 获取用户信息
 */
export function getUserInfo(): UserInfo | null {
  const userInfoStr = localStorage.getItem('toutiao_user_info')
  return userInfoStr ? JSON.parse(userInfoStr) : null
}

/**
 * 设置用户信息
 */
export function setUserInfo(userInfo: UserInfo): void {
  localStorage.setItem('toutiao_user_info', JSON.stringify(userInfo))
}

/**
 * 清除所有认证信息
 */
export function clearAuth(): void {
  removeToken()
  localStorage.removeItem('toutiao_user_info')
}