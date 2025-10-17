import request from './request'

// 获取产品列表
export function getProducts(params) {
  return request({
    url: '/v1/products/',
    method: 'get',
    params
  })
}

// 获取产品详情
export function getProduct(id) {
  return request({
    url: `/v1/products/${id}`,
    method: 'get'
  })
}

// 创建产品
export function createProduct(data) {
  return request({
    url: '/v1/products/',
    method: 'post',
    data
  })
}

// 更新产品
export function updateProduct(id, data) {
  return request({
    url: `/v1/products/${id}`,
    method: 'put',
    data
  })
}

// 删除产品
export function deleteProduct(id) {
  return request({
    url: `/v1/products/${id}`,
    method: 'delete'
  })
}

// 获取产品统计信息
export function getProductStats() {
  return request({
    url: '/v1/products/stats/overview',
    method: 'get'
  })
}

// 获取推荐产品列表
export function getFeaturedProducts(params) {
  return request({
    url: '/v1/products/featured/list',
    method: 'get',
    params
  })
}
