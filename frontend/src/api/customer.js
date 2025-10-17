import request from './request'

// 获取客户列表
export function getCustomers(params) {
  return request({
    url: '/v1/customers/',
    method: 'get',
    params
  })
}

// 获取客户详情
export function getCustomer(id) {
  return request({
    url: `/v1/customers/${id}`,
    method: 'get'
  })
}

// 创建客户
export function createCustomer(data) {
  return request({
    url: '/v1/customers/',
    method: 'post',
    data
  })
}

// 更新客户
export function updateCustomer(id, data) {
  return request({
    url: `/v1/customers/${id}`,
    method: 'put',
    data
  })
}

// 删除客户
export function deleteCustomer(id) {
  return request({
    url: `/v1/customers/${id}`,
    method: 'delete'
  })
}

// 搜索客户
export function searchCustomers(params) {
  return request({
    url: '/v1/customers/search/',
    method: 'get',
    params
  })
}

// 获取VIP客户列表
export function getVipCustomers(params) {
  return request({
    url: '/v1/customers/vip/list',
    method: 'get',
    params
  })
}

// 获取高价值客户列表
export function getHighValueCustomers(params) {
  return request({
    url: '/v1/customers/high-value/list',
    method: 'get',
    params
  })
}

// 获取客户统计信息
export function getCustomerStats() {
  return request({
    url: '/v1/customers/stats/overview',
    method: 'get'
  })
}

// 根据行业获取客户
export function getCustomersByIndustry(industry, params) {
  return request({
    url: `/v1/customers/by-industry/${industry}`,
    method: 'get',
    params
  })
}

// 根据地区获取客户
export function getCustomersByRegion(params) {
  return request({
    url: '/v1/customers/by-region/',
    method: 'get',
    params
  })
}
