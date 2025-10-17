import request from './request'

// 用户登录
export function login(data) {
  const formData = new FormData()
  formData.append('username', data.username)
  formData.append('password', data.password)
  
  return request({
    url: '/v1/auth/login',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

// 用户注册
export function register(data) {
  return request({
    url: '/v1/auth/register',
    method: 'post',
    data
  })
}

// 获取当前用户信息
export function getCurrentUser() {
  return request({
    url: '/v1/auth/me',
    method: 'get'
  })
}

// 修改密码
export function changePassword(data) {
  return request({
    url: '/v1/auth/change-password',
    method: 'post',
    data
  })
}
