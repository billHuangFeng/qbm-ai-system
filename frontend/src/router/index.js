import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layout/index.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表板', icon: 'Dashboard' }
      },
      {
        path: 'customers',
        name: 'Customers',
        component: () => import('@/views/customer/index.vue'),
        meta: { title: '客户管理', icon: 'User' }
      },
      {
        path: 'customers/create',
        name: 'CustomerCreate',
        component: () => import('@/views/customer/Create.vue'),
        meta: { title: '创建客户', hidden: true }
      },
      {
        path: 'customers/:id/edit',
        name: 'CustomerEdit',
        component: () => import('@/views/customer/Edit.vue'),
        meta: { title: '编辑客户', hidden: true }
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('@/views/product/index.vue'),
        meta: { title: '产品管理', icon: 'Box' }
      },
      {
        path: 'products/create',
        name: 'ProductCreate',
        component: () => import('@/views/product/Create.vue'),
        meta: { title: '创建产品', hidden: true }
      },
      {
        path: 'products/:id/edit',
        name: 'ProductEdit',
        component: () => import('@/views/product/Edit.vue'),
        meta: { title: '编辑产品', hidden: true }
      },
      {
        path: 'contracts',
        name: 'Contracts',
        component: () => import('@/views/contract/index.vue'),
        meta: { title: '合同管理', icon: 'Document' }
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('@/views/order/index.vue'),
        meta: { title: '订单管理', icon: 'ShoppingCart' }
      },
      {
        path: 'financials',
        name: 'Financials',
        component: () => import('@/views/financial/index.vue'),
        meta: { title: '财务管理', icon: 'Money' }
      },
      {
        path: 'analysis',
        name: 'Analysis',
        component: () => import('@/views/analysis/index.vue'),
        meta: { title: '分析报告', icon: 'TrendCharts' }
      },
      {
        path: 'data-import',
        name: 'DataImport',
        component: () => import('@/views/data-import/index.vue'),
        meta: { title: '数据导入', icon: 'Upload' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/user/index.vue'),
        meta: { title: '用户管理', icon: 'UserFilled', requiresAdmin: true }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/404.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  // 检查是否需要认证
  if (to.meta.requiresAuth !== false) {
    if (!userStore.token) {
      ElMessage.warning('请先登录')
      next('/login')
      return
    }
    
    // 检查用户信息是否存在
    if (!userStore.userInfo) {
      try {
        await userStore.getUserInfo()
      } catch (error) {
        next('/login')
        return
      }
    }
    
    // 检查管理员权限
    if (to.meta.requiresAdmin && !userStore.isAdmin) {
      ElMessage.error('权限不足')
      next('/dashboard')
      return
    }
  }
  
  // 如果已登录且访问登录页，重定向到仪表板
  if (to.path === '/login' && userStore.isLoggedIn) {
    next('/dashboard')
    return
  }
  
  next()
})

export default router
