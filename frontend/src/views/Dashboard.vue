<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>仪表板</h1>
      <p>欢迎使用QBM AI System，这里是您的业务概览</p>
    </div>
    
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon customer">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ stats.customers?.total_customers || 0 }}</h3>
            <p>总客户数</p>
            <span class="stat-change positive">+12%</span>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon product">
            <el-icon><Box /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ stats.products?.total_products || 0 }}</h3>
            <p>产品数量</p>
            <span class="stat-change positive">+8%</span>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon revenue">
            <el-icon><Money /></el-icon>
          </div>
          <div class="stat-info">
            <h3>¥{{ formatNumber(stats.products?.total_revenue || 0) }}</h3>
            <p>总收入</p>
            <span class="stat-change positive">+15%</span>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon satisfaction">
            <el-icon><Star /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ stats.customers?.average_satisfaction?.toFixed(1) || '0.0' }}</h3>
            <p>客户满意度</p>
            <span class="stat-change positive">+3%</span>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 图表区域 -->
    <div class="charts-grid">
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>客户价值分布</span>
            <el-button type="text" @click="refreshCustomerStats">刷新</el-button>
          </div>
        </template>
        <div class="chart-container">
          <v-chart 
            :option="customerValueChart" 
            style="height: 300px;"
            v-if="customerValueChart"
          />
        </div>
      </el-card>
      
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>产品收入趋势</span>
            <el-button type="text" @click="refreshProductStats">刷新</el-button>
          </div>
        </template>
        <div class="chart-container">
          <v-chart 
            :option="productRevenueChart" 
            style="height: 300px;"
            v-if="productRevenueChart"
          />
        </div>
      </el-card>
    </div>
    
    <!-- 最近活动 -->
    <div class="recent-activities">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>最近活动</span>
            <el-button type="text">查看全部</el-button>
          </div>
        </template>
        <el-timeline>
          <el-timeline-item
            v-for="activity in recentActivities"
            :key="activity.id"
            :timestamp="activity.timestamp"
            :type="activity.type"
          >
            <h4>{{ activity.title }}</h4>
            <p>{{ activity.description }}</p>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { getCustomerStats, getProductStats } from '@/api/customer'
import { ElMessage } from 'element-plus'
import { User, Box, Money, Star } from '@element-plus/icons-vue'

// 注册ECharts组件
use([
  CanvasRenderer,
  PieChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

// 统计数据
const stats = ref({
  customers: null,
  products: null
})

// 图表配置
const customerValueChart = ref(null)
const productRevenueChart = ref(null)

// 最近活动
const recentActivities = ref([
  {
    id: 1,
    title: '新客户注册',
    description: '北京科技有限公司已完成注册',
    timestamp: '2024-01-15 10:30',
    type: 'primary'
  },
  {
    id: 2,
    title: '合同签署',
    description: '与上海制造有限公司签署了新的服务合同',
    timestamp: '2024-01-15 09:15',
    type: 'success'
  },
  {
    id: 3,
    title: '产品更新',
    description: 'AI数据分析平台已更新到v2.1版本',
    timestamp: '2024-01-14 16:45',
    type: 'warning'
  },
  {
    id: 4,
    title: '财务记录',
    description: '新增一笔收入记录：¥150,000',
    timestamp: '2024-01-14 14:20',
    type: 'info'
  }
])

// 格式化数字
const formatNumber = (num) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toLocaleString()
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const [customerStats, productStats] = await Promise.all([
      getCustomerStats(),
      getProductStats()
    ])
    
    stats.value = {
      customers: customerStats.data,
      products: productStats.data
    }
    
    // 更新图表
    updateCharts()
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败')
  }
}

// 更新图表
const updateCharts = () => {
  // 客户价值分布饼图
  customerValueChart.value = {
    title: {
      text: '客户价值分布',
      left: 'center',
      textStyle: {
        fontSize: 16
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '客户价值',
        type: 'pie',
        radius: '50%',
        data: [
          { value: stats.value.customers?.vip_customers || 0, name: 'VIP客户' },
          { value: (stats.value.customers?.total_customers || 0) - (stats.value.customers?.vip_customers || 0), name: '普通客户' }
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
  
  // 产品收入趋势线图
  productRevenueChart.value = {
    title: {
      text: '产品收入趋势',
      left: 'center',
      textStyle: {
        fontSize: 16
      }
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月']
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [
      {
        name: '收入',
        type: 'line',
        data: [1200000, 1500000, 1800000, 1600000, 2000000, 2200000],
        smooth: true,
        itemStyle: {
          color: '#409eff'
        }
      }
    ]
  }
}

// 刷新客户统计
const refreshCustomerStats = () => {
  fetchStats()
  ElMessage.success('客户统计数据已刷新')
}

// 刷新产品统计
const refreshProductStats = () => {
  fetchStats()
  ElMessage.success('产品统计数据已刷新')
}

// 组件挂载时获取数据
onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 30px;
}

.dashboard-header h1 {
  color: #2c3e50;
  font-size: 28px;
  margin: 0 0 10px 0;
}

.dashboard-header p {
  color: #7f8c8d;
  font-size: 16px;
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 10px 0;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  font-size: 24px;
  color: white;
}

.stat-icon.customer {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.product {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.revenue {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.satisfaction {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info h3 {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
  margin: 0 0 5px 0;
}

.stat-info p {
  color: #7f8c8d;
  font-size: 14px;
  margin: 0 0 5px 0;
}

.stat-change {
  font-size: 12px;
  font-weight: bold;
}

.stat-change.positive {
  color: #67c23a;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.chart-card {
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  color: #2c3e50;
}

.chart-container {
  width: 100%;
}

.recent-activities {
  margin-bottom: 30px;
}

.recent-activities .el-card {
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.recent-activities h4 {
  color: #2c3e50;
  font-size: 16px;
  margin: 0 0 5px 0;
}

.recent-activities p {
  color: #7f8c8d;
  font-size: 14px;
  margin: 0;
}
</style>
