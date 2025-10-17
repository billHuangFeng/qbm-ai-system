import { defineStore } from 'pinia'
import { login, getCurrentUser } from '@/api/auth'
import Cookies from 'js-cookie'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: Cookies.get('token') || '',
    userInfo: null,
    isLoggedIn: false
  }),

  getters: {
    isAdmin: (state) => state.userInfo?.is_admin || false,
    username: (state) => state.userInfo?.username || '',
    fullName: (state) => state.userInfo?.full_name || ''
  },

  actions: {
    // 登录
    async login(loginData) {
      try {
        const response = await login(loginData)
        const { access_token } = response.data
        
        this.token = access_token
        this.isLoggedIn = true
        
        // 保存token到cookie
        Cookies.set('token', access_token, { expires: 7 })
        
        // 获取用户信息
        await this.getUserInfo()
        
        return response
      } catch (error) {
        throw error
      }
    },

    // 获取用户信息
    async getUserInfo() {
      try {
        const response = await getCurrentUser()
        this.userInfo = response.data
        return response
      } catch (error) {
        this.logout()
        throw error
      }
    },

    // 登出
    logout() {
      this.token = ''
      this.userInfo = null
      this.isLoggedIn = false
      Cookies.remove('token')
    },

    // 检查登录状态
    async checkAuth() {
      if (this.token) {
        try {
          await this.getUserInfo()
          this.isLoggedIn = true
        } catch (error) {
          this.logout()
        }
      }
    }
  }
})
