<template>
  <div class="system-monitor-chart">
    <div class="monitor-header">
      <h3>系统监控</h3>
      <div class="header-actions">
        <el-button type="primary" size="small" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-switch
          v-model="autoRefresh"
          active-text="自动刷新"
          @change="toggleAutoRefresh"
        />
      </div>
    </div>
    
    <el-row :gutter="20">
      <!-- 系统状态概览 -->
      <el-col :span="24">
        <el-card class="status-overview">
          <template #header>
            <span>系统状态概览</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="status-item">
                <div class="status-icon backend">
                  <el-icon><Monitor /></el-icon>
                </div>
                <div class="status-info">
                  <h4>后端服务</h4>
                  <p :class="systemStatus.backend.status">{{ systemStatus.backend.text }}</p>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="status-item">
                <div class="status-icon database">
                  <el-icon><Database /></el-icon>
                </div>
                <div class="status-info">
                  <h4>数据库</h4>
                  <p :class="systemStatus.database.status">{{ systemStatus.database.text }}</p>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="status-item">
                <div class="status-icon redis">
                  <el-icon><Connection /></el-icon>
                </div>
                <div class="status-info">
                  <h4>Redis缓存</h4>
                  <p :class="systemStatus.redis.status">{{ systemStatus.redis.text }}</p>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="status-item">
                <div class="status-icon ai">
                  <el-icon><Cpu /></el-icon>
                </div>
                <div class="status-info">
                  <h4>AI引擎</h4>
                  <p :class="systemStatus.ai.status">{{ systemStatus.ai.text }}</p>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 性能指标 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>性能指标</span>
          </template>
          <div ref="performanceChart" class="chart"></div>
        </el-card>
      </el-col>
      
      <!-- 资源使用率 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>资源使用率</span>
          </template>
          <div ref="resourceChart" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 请求统计 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>API请求统计</span>
          </template>
          <div ref="requestChart" class="chart"></div>
        </el-card>
      </el-col>
      
      <!-- 错误日志 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>错误日志</span>
          </template>
          <div class="error-log">
            <div v-for="(error, index) in errorLogs" :key="index" class="error-item">
              <div class="error-time">{{ error.time }}</div>
              <div class="error-message">{{ error.message }}</div>
              <div class="error-level" :class="error.level">{{ error.level }}</div>
            </div>
            <div v-if="errorLogs.length === 0" class="no-errors">
              <el-icon><Check /></el-icon>
              <p>暂无错误日志</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { Refresh, Monitor, Database, Connection, Cpu, Check } from '@element-plus/icons-vue'

// 响应式数据
const autoRefresh = ref(false)
const refreshInterval = ref(null)

const systemStatus = ref({
  backend: { status: 'success', text: '运行正常' },
  database: { status: 'success', text: '连接正常' },
  redis: { status: 'success', text: '缓存正常' },
  ai: { status: 'success', text: '引擎正常' }
})

const errorLogs = ref([
  {
    time: '2024-01-15 10:30:15',
    message: '数据库连接超时',
    level: 'warning'
  },
  {
    time: '2024-01-15 09:15:22',
    message: 'API请求失败',
    level: 'error'
  }
])

// 图表引用
const performanceChart = ref(null)
const resourceChart = ref(null)
const requestChart = ref(null)

// 图表实例
let performanceChartInstance = null
let resourceChartInstance = null
let requestChartInstance = null

// 组件挂载时初始化
onMounted(() => {
  nextTick(() => {
    initCharts()
    refreshData()
  })
})

// 组件卸载时清理
onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
  if (performanceChartInstance) {
    performanceChartInstance.dispose()
  }
  if (resourceChartInstance) {
    resourceChartInstance.dispose()
  }
  if (requestChartInstance) {
    requestChartInstance.dispose()
  }
})

// 初始化所有图表
const initCharts = () => {
  initPerformanceChart()
  initResourceChart()
  initRequestChart()
}

// 性能指标图表
const initPerformanceChart = () => {
  if (!performanceChart.value) return
  
  performanceChartInstance = echarts.init(performanceChart.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['响应时间', '吞吐量', '错误率']
    },
    xAxis: {
      type: 'category',
      data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']
    },
    yAxis: [
      {
        type: 'value',
        name: '响应时间(ms)',
        position: 'left'
      },
      {
        type: 'value',
        name: '吞吐量(req/s)',
        position: 'right'
      }
    ],
    series: [
      {
        name: '响应时间',
        type: 'line',
        data: [120, 150, 180, 200, 160, 140],
        itemStyle: { color: '#409eff' }
      },
      {
        name: '吞吐量',
        type: 'line',
        yAxisIndex: 1,
        data: [1000, 1200, 1500, 1800, 1600, 1400],
        itemStyle: { color: '#67c23a' }
      },
      {
        name: '错误率',
        type: 'line',
        data: [0.1, 0.2, 0.5, 0.3, 0.2, 0.1],
        itemStyle: { color: '#f56c6c' }
      }
    ]
  }
  
  performanceChartInstance.setOption(option)
}

// 资源使用率图表
const initResourceChart = () => {
  if (!resourceChart.value) return
  
  resourceChartInstance = echarts.init(resourceChart.value)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c}% ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '资源使用率',
        type: 'pie',
        radius: '50%',
        data: [
          { value: 45, name: 'CPU使用率' },
          { value: 60, name: '内存使用率' },
          { value: 30, name: '磁盘使用率' },
          { value: 25, name: '网络使用率' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  
  resourceChartInstance.setOption(option)
}

// API请求统计图表
const initRequestChart = () => {
  if (!requestChart.value) return
  
  requestChartInstance = echarts.init(requestChart.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    },
    yAxis: {
      type: 'value',
      name: '请求数量'
    },
    series: [
      {
        name: '请求统计',
        type: 'bar',
        data: [1200, 800, 300, 100, 50],
        itemStyle: {
          color: function(params) {
            const colors = ['#67c23a', '#409eff', '#e6a23c', '#f56c6c', '#909399']
            return colors[params.dataIndex]
          }
        }
      }
    ]
  }
  
  requestChartInstance.setOption(option)
}

// 刷新数据
const refreshData = () => {
  // 模拟数据更新
  console.log('刷新系统监控数据')
  
  // 更新图表数据
  if (performanceChartInstance) {
    // 这里可以更新图表数据
  }
}

// 切换自动刷新
const toggleAutoRefresh = (value) => {
  if (value) {
    refreshInterval.value = setInterval(refreshData, 30000) // 30秒刷新一次
  } else {
    if (refreshInterval.value) {
      clearInterval(refreshInterval.value)
      refreshInterval.value = null
    }
  }
}
</script>

<style scoped>
.system-monitor-chart {
  padding: 20px;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.monitor-header h3 {
  margin: 0;
  color: #2c3e50;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.status-overview {
  margin-bottom: 20px;
}

.status-item {
  display: flex;
  align-items: center;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.status-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
  color: white;
}

.status-icon.backend {
  background: #67c23a;
}

.status-icon.database {
  background: #409eff;
}

.status-icon.redis {
  background: #e6a23c;
}

.status-icon.ai {
  background: #f56c6c;
}

.status-info h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 16px;
}

.status-info p {
  margin: 0;
  font-size: 14px;
}

.status-info p.success {
  color: #67c23a;
}

.status-info p.warning {
  color: #e6a23c;
}

.status-info p.error {
  color: #f56c6c;
}

.chart {
  width: 100%;
  height: 300px;
}

.error-log {
  max-height: 300px;
  overflow-y: auto;
}

.error-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #f0f0f0;
  gap: 15px;
}

.error-item:last-child {
  border-bottom: none;
}

.error-time {
  font-size: 12px;
  color: #999;
  min-width: 120px;
}

.error-message {
  flex: 1;
  font-size: 14px;
  color: #333;
}

.error-level {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.error-level.error {
  background: #fef0f0;
  color: #f56c6c;
}

.error-level.warning {
  background: #fdf6ec;
  color: #e6a23c;
}

.no-errors {
  text-align: center;
  padding: 40px;
  color: #67c23a;
}

.no-errors .el-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.no-errors p {
  margin: 0;
  font-size: 16px;
}
</style>


