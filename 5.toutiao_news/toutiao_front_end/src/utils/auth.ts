/**
 * Token 管理工具
 * 负责 Token 的存储、获取、验证
 */

// localStorage 中存储 Token 与过期时间的 key
const TOKEN_KEY = 'toutiao_token'
const TOKEN_EXPIRES_KEY = 'toutiao_token_expires'

/**
 * 获取本地存储中的 Token
 * @returns Token 字符串，未登录返回 null
 */
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

/**
 * 设置 Token 并记录过期时间
 * @param token - Token值
 * @param expiresIn - 有效期（秒），默认7天
 */
export function setToken(token: string, expiresIn: number = 7 * 24 * 60 * 60): void {
  localStorage.setItem(TOKEN_KEY, token)
  const expiresTime = Date.now() + expiresIn * 1000
  localStorage.setItem(TOKEN_EXPIRES_KEY, expiresTime.toString())
}

/**
 * 移除 Token 与过期时间
 */
export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(TOKEN_EXPIRES_KEY)
}

/**
 * 检查 Token 是否过期
 * @returns true 表示已过期或未设置过期时间
 */
export function isTokenExpired(): boolean {
  const expiresTime = localStorage.getItem(TOKEN_EXPIRES_KEY)
  if (!expiresTime) return true
  return Date.now() > parseInt(expiresTime)
}

/**
 * 获取本地缓存的用户信息
 * @returns 解析后的 UserInfo；解析失败或未设置返回 null
 */
export function getUserInfo(): UserInfo | null {
  try {
    const userInfoStr = localStorage.getItem('toutiao_user_info')
    if (!userInfoStr || userInfoStr === 'undefined' || userInfoStr === 'null') {
      return null
    }
    return JSON.parse(userInfoStr)
  } catch {
    // 如果 JSON 解析失败，清除无效数据
    localStorage.removeItem('toutiao_user_info')
    return null
  }
}

/**
 * 将用户信息写入本地缓存
 * @param userInfo - 用户信息对象
 */
export function setUserInfo(userInfo: UserInfo): void {
  localStorage.setItem('toutiao_user_info', JSON.stringify(userInfo))
}

/**
 * 清除所有认证信息（Token + 用户信息）
 */
export function clearAuth(): void {
  removeToken()
  localStorage.removeItem('toutiao_user_info')
}