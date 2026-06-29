/**
 * 用户相关 API 接口封装
 */
import request from '@/utils/request'

// 请求参数类型
interface LoginData {
  username: string
  password: string
}

interface RegisterData extends LoginData {}

interface UpdateUserData {
  nickname?: string
  avatar?: string
  email?: string
  phone?: string
}

interface PasswordData {
  oldPassword: string
  newPassword: string
}

/**
 * 用户注册
 */
export function register(data: RegisterData): Promise<ApiResponse> {
  return request({
    url: '/user/register',
    method: 'post',
    data
  })
}

/**
 * 用户登录
 */
export function login(data: LoginData): Promise<ApiResponse> {
  return request({
    url: '/user/login',
    method: 'post',
    data
  })
}

/**
 * 获取用户信息
 * 后端返回 data: { userInfo: UserInfo, ... }
 */
export function getUserInfo(): Promise<ApiResponse<{ userInfo?: UserInfo; user?: UserInfo }>> {
  return request({
    url: '/user/info',
    method: 'get'
  })
}

/**
 * 更新用户信息
 */
export function updateUserInfo(data: UpdateUserData): Promise<ApiResponse> {
  return request({
    url: '/user/update',
    method: 'put',
    data
  })
}

/**
 * 修改密码
 */
export function updatePassword(data: PasswordData): Promise<ApiResponse> {
  return request({
    url: '/user/password',
    method: 'put',
    data
  })
}