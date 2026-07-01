/**
 * 用户相关 API 接口封装
 */
import request from '@/utils/request'

// ============ 请求参数类型 ============
/** 登录入参 */
interface LoginData {
  /** 用户名 */
  username: string
  /** 密码 */
  password: string
}

/** 注册入参（与登录一致） */
interface RegisterData extends LoginData {}

/** 更新用户信息入参（字段均可选） */
interface UpdateUserData {
  /** 昵称 */
  nickname?: string
  /** 头像 URL */
  avatar?: string
  /** 个人简介 */
  bio?: string
  /** 邮箱 */
  email?: string
  /** 手机号 */
  phone?: string
}

/** 修改密码入参 */
interface PasswordData {
  /** 旧密码 */
  oldPassword: string
  /** 新密码 */
  newPassword: string
}

/**
 * 用户注册
 * @param data - 用户名与密码
 * @returns 接口响应（data 中包含 token 与 userInfo）
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
 * @param data - 用户名与密码
 * @returns 接口响应（data 中包含 token 与 userInfo）
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
 * 后端直接返回用户信息对象作为 data
 * @returns 接口响应，data 即为用户信息
 */
export function getUserInfo(): Promise<ApiResponse<UserInfo>> {
  return request({
    url: '/user/info',
    method: 'get'
  })
}

/**
 * 更新用户信息（昵称、头像、邮箱、手机号等）
 * @param data - 要更新的字段
 * @returns 接口响应
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
 * @param data - 旧密码与新密码
 * @returns 接口响应
 */
export function updatePassword(data: PasswordData): Promise<ApiResponse> {
  return request({
    url: '/user/password',
    method: 'put',
    data
  })
}