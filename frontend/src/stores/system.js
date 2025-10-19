import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/utils/api'

export const useSystemStore = defineStore('system', () => {
  // 状态
  const systemStatus = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const lastUpdate = ref(null)

  // 计算属性
  const isHealthy = computed(() => {
    return systemStatus.value?.status === 'healthy'
  })

  const clickhouseStatus = computed(() => {
    return systemStatus.value?.clickhouse || {}
  })

  const totalTables = computed(() => {
    return clickhouseStatus.value?.total_tables || 0
  })

  // 操作
  const initialize = async () => {
    await checkSystemHealth()
  }

  const checkSystemHealth = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get('/health')
      systemStatus.value = response.data
      lastUpdate.value = new Date()
    } catch (err) {
      error.value = err.message || '系统健康检查失败'
      console.error('Health check failed:', err)
    } finally {
      loading.value = false
    }
  }

  const getSystemStatus = async () => {
    try {
      const response = await api.get('/api/v1/bmos/status')
      return response.data
    } catch (err) {
      console.error('Get system status failed:', err)
      throw err
    }
  }

  return {
    // 状态
    systemStatus,
    loading,
    error,
    lastUpdate,
    
    // 计算属性
    isHealthy,
    clickhouseStatus,
    totalTables,
    
    // 操作
    initialize,
    checkSystemHealth,
    getSystemStatus
  }
})

