/**
 * 用户相关 API 接口封装
 */
import request from '@/utils/request'

/**
 * 用户注册
 * @param {object} data - 注册参数 { username, password, email, phone }
 * @returns {promise} 返回用户信息和Token
 */
export function register(data) {
  return request({
    url: '/user/register',
    method: 'post',
    data
  })
}

/**
 * 用户登录
 * @param {object} data - 登录参数 { username, password }
 * @returns {promise} 返回用户信息和Token
 */
export function login(data) {
  return request({
    url: '/user/login',
    method: 'post',
    data
  })
}

/**
 * 获取用户信息
 * @returns {promise} 返回用户信息
 */
export function getUserInfo() {
  return request({
    url: '/user/info',
    method: 'get'
  })
}

/**
 * 更新用户信息
 * @param {object} data - 用户信息 { nickname, avatar, email, phone }
 * @returns {promise} 返回更新结果
 */
export function updateUserInfo(data) {
  return request({
    url: '/user/update',
    method: 'put',
    data
  })
}

/**
 * 修改密码
 * @param {object} data - 密码参数 { oldPassword, newPassword }
 * @returns {promise} 返回修改结果
 */
export function updatePassword(data) {
  return request({
    url: '/user/password',
    method: 'put',
    data
  })
}