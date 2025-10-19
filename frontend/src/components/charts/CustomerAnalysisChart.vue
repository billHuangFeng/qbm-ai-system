<template>
  <div class="customer-analysis-chart">
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" size="32"><Loading /></el-icon>
      <p>正在分析客户数据...</p>
    </div>
    
    <div v-else class="analysis-content">
      <!-- 客户价值分析 -->
      <el-card class="analysis-card">
        <template #header>
          <div class="card-header">
            <span>客户价值分析</span>
            <el-button type="text" @click="refreshAnalysis">刷新</el-button>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="chart-container">
              <h4>客户价值分布</h4>
              <div ref="valueDistributionChart" class="chart"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <h4>客户生命周期价值</h4>
              <div ref="lifetimeValueChart" class="chart"></div>
            </div>
          </el-col>
        </el-row>
      </el-card>
      
      <!-- 客户细分分析 -->
      <el-card class="analysis-card">
        <template #header>
          <div class="card-header">
            <span>客户细分分析</span>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="chart-container">
              <h4>客户聚类分析</h4>
              <div ref="clusterAnalysisChart" class="chart"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <h4>客户生命周期阶段</h4>
              <div ref="lifecycleStageChart" class="chart"></div>
            </div>
          </el-col>
        </el-row>
      </el-card>
      
      <!-- 客户流失风险分析 -->
      <el-card class="analysis-card">
        <template #header>
          <div class="card-header">
            <span>客户流失风险分析</span>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="chart-container">
              <h4>流失风险分布</h4>
              <div ref="churnRiskChart" class="chart"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <h4>客户满意度分析</h4>
              <div ref="satisfactionChart" class="chart"></div>
            </div>
          </el-col>
        </el-row>
      </el-card>
      
      <!-- 分析洞察 -->
      <el-card class="insights-card">
        <template #header>
          <span>分析洞察</span>
        </template>
        
        <div class="insights-content">
          <div class="insight-item">
            <el-icon class="insight-icon"><TrendCharts /></el-icon>
            <div class="insight-text">
              <h5>高价值客户占比</h5>
              <p>高价值客户占总客户数的25%，贡献了60%的收入</p>
            </div>
          </div>
          
          <div class="insight-item">
            <el-icon class="insight-icon"><Warning /></el-icon>
            <div class="insight-text">
              <h5>流失风险预警</h5>
              <p>有50个客户存在高流失风险，建议重点关注</p>
            </div>
          </div>
          
          <div class="insight-item">
            <el-icon class="insight-icon"><Star /></el-icon>
            <div class="insight-text">
              <h5>客户满意度</h5>
              <p>整体客户满意度为4.6分，忠诚期客户满意度最高</p>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { Loading, TrendCharts, Warning, Star } from '@element-plus/icons-vue'

// Props
const props = defineProps({
  analysisData: {
    type: Object,
    default: () => ({})
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// 响应式数据
const valueDistributionChart = ref(null)
const lifetimeValueChart = ref(null)
const clusterAnalysisChart = ref(null)
const lifecycleStageChart = ref(null)
const churnRiskChart = ref(null)
const satisfactionChart = ref(null)

// 图表实例
let valueDistributionChartInstance = null
let lifetimeValueChartInstance = null
let clusterAnalysisChartInstance = null
let lifecycleStageChartInstance = null
let churnRiskChartInstance = null
let satisfactionChartInstance = null

// 监听数据变化
watch(() => props.analysisData, (newData) => {
  if (newData && Object.keys(newData).length > 0) {
    nextTick(() => {
      initAllCharts()
    })
  }
}, { deep: true })

// 组件挂载时初始化图表
onMounted(() => {
  if (props.analysisData && Object.keys(props.analysisData).length > 0) {
    nextTick(() => {
      initAllCharts()
    })
  }
})

// 初始化所有图表
const initAllCharts = () => {
  initValueDistributionChart()
  initLifetimeValueChart()
  initClusterAnalysisChart()
  initLifecycleStageChart()
  initChurnRiskChart()
  initSatisfactionChart()
}

// 客户价值分布图表
const initValueDistributionChart = () => {
  if (!valueDistributionChart.value) return
  
  valueDistributionChartInstance = echarts.init(valueDistributionChart.value)
  
  const data = props.analysisData.value_analysis?.value_distribution || {
    high_value_customers: 250,
    medium_value_customers: 500,
    low_value_customers: 250
  }
  
  const option = {
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
        name: '客户价值分布',
        type: 'pie',
        radius: '50%',
        data: [
          { value: data.high_value_customers, name: '高价值客户' },
          { value: data.medium_value_customers, name: '中价值客户' },
          { value: data.low_value_customers, name: '低价值客户' }
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
  
  valueDistributionChartInstance.setOption(option)
}

// 客户生命周期价值图表
const initLifetimeValueChart = () => {
  if (!lifetimeValueChart.value) return
  
  lifetimeValueChartInstance = echarts.init(lifetimeValueChart.value)
  
  const data = props.analysisData.segmentation?.cluster_analysis || {
    cluster_0: { size: 300, avg_lifetime_value: 500000 },
    cluster_1: { size: 400, avg_lifetime_value: 300000 },
    cluster_2: { size: 300, avg_lifetime_value: 200000 }
  }
  
  const categories = Object.keys(data).map(key => `客户群${key.split('_')[1]}`)
  const values = Object.values(data).map(item => item.avg_lifetime_value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: categories
    },
    yAxis: {
      type: 'value',
      name: '平均生命周期价值'
    },
    series: [
      {
        name: '生命周期价值',
        type: 'bar',
        data: values,
        itemStyle: {
          color: '#409eff'
        }
      }
    ]
  }
  
  lifetimeValueChartInstance.setOption(option)
}

// 客户聚类分析图表
const initClusterAnalysisChart = () => {
  if (!clusterAnalysisChart.value) return
  
  clusterAnalysisChartInstance = echarts.init(clusterAnalysisChart.value)
  
  const data = props.analysisData.segmentation?.cluster_analysis || {
    cluster_0: { size: 300, avg_lifetime_value: 500000 },
    cluster_1: { size: 400, avg_lifetime_value: 300000 },
    cluster_2: { size: 300, avg_lifetime_value: 200000 }
  }
  
  const categories = Object.keys(data).map(key => `客户群${key.split('_')[1]}`)
  const sizes = Object.values(data).map(item => item.size)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: categories
    },
    yAxis: {
      type: 'value',
      name: '客户数量'
    },
    series: [
      {
        name: '客户数量',
        type: 'bar',
        data: sizes,
        itemStyle: {
          color: '#67c23a'
        }
      }
    ]
  }
  
  clusterAnalysisChartInstance.setOption(option)
}

// 客户生命周期阶段图表
const initLifecycleStageChart = () => {
  if (!lifecycleStageChart.value) return
  
  lifecycleStageChartInstance = echarts.init(lifecycleStageChart.value)
  
  const data = props.analysisData.lifecycle_analysis?.lifecycle_analysis || {
    '新客户': { customer_lifetime_value: { count: 200 }, customer_satisfaction: { mean: 4.2 } },
    '成长期': { customer_lifetime_value: { count: 300 }, customer_satisfaction: { mean: 4.5 } },
    '成熟期': { customer_lifetime_value: { count: 400 }, customer_satisfaction: { mean: 4.8 } },
    '忠诚期': { customer_lifetime_value: { count: 100 }, customer_satisfaction: { mean: 4.9 } }
  }
  
  const categories = Object.keys(data)
  const counts = Object.values(data).map(item => item.customer_lifetime_value.count)
  const satisfaction = Object.values(data).map(item => item.customer_satisfaction.mean)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['客户数量', '满意度']
    },
    xAxis: {
      type: 'category',
      data: categories
    },
    yAxis: [
      {
        type: 'value',
        name: '客户数量',
        position: 'left'
      },
      {
        type: 'value',
        name: '满意度',
        position: 'right',
        min: 0,
        max: 5
      }
    ],
    series: [
      {
        name: '客户数量',
        type: 'bar',
        data: counts,
        itemStyle: {
          color: '#409eff'
        }
      },
      {
        name: '满意度',
        type: 'line',
        yAxisIndex: 1,
        data: satisfaction,
        itemStyle: {
          color: '#67c23a'
        }
      }
    ]
  }
  
  lifecycleStageChartInstance.setOption(option)
}

// 客户流失风险图表
const initChurnRiskChart = () => {
  if (!churnRiskChart.value) return
  
  churnRiskChartInstance = echarts.init(churnRiskChart.value)
  
  const data = props.analysisData.lifecycle_analysis?.churn_risk || {
    high_risk_count: 50,
    medium_risk_count: 150,
    low_risk_count: 800
  }
  
  const option = {
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
        name: '流失风险分布',
        type: 'pie',
        radius: '50%',
        data: [
          { value: data.high_risk_count, name: '高风险' },
          { value: data.medium_risk_count, name: '中风险' },
          { value: data.low_risk_count, name: '低风险' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        itemStyle: {
          color: function(params) {
            const colors = ['#f56c6c', '#e6a23c', '#67c23a']
            return colors[params.dataIndex]
          }
        }
      }
    ]
  }
  
  churnRiskChartInstance.setOption(option)
}

// 客户满意度图表
const initSatisfactionChart = () => {
  if (!satisfactionChart.value) return
  
  satisfactionChartInstance = echarts.init(satisfactionChart.value)
  
  const data = props.analysisData.lifecycle_analysis?.lifecycle_analysis || {
    '新客户': { customer_lifetime_value: { count: 200 }, customer_satisfaction: { mean: 4.2 } },
    '成长期': { customer_lifetime_value: { count: 300 }, customer_satisfaction: { mean: 4.5 } },
    '成熟期': { customer_lifetime_value: { count: 400 }, customer_satisfaction: { mean: 4.8 } },
    '忠诚期': { customer_lifetime_value: { count: 100 }, customer_satisfaction: { mean: 4.9 } }
  }
  
  const categories = Object.keys(data)
  const satisfaction = Object.values(data).map(item => item.customer_satisfaction.mean)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: categories
    },
    yAxis: {
      type: 'value',
      name: '满意度',
      min: 0,
      max: 5
    },
    series: [
      {
        name: '满意度',
        type: 'bar',
        data: satisfaction,
        itemStyle: {
          color: '#67c23a'
        }
      }
    ]
  }
  
  satisfactionChartInstance.setOption(option)
}

// 刷新分析
const refreshAnalysis = () => {
  // 这里可以触发重新分析
  console.log('刷新客户分析')
}

// 组件卸载时销毁图表实例
onUnmounted(() => {
  if (valueDistributionChartInstance) {
    valueDistributionChartInstance.dispose()
  }
  if (lifetimeValueChartInstance) {
    lifetimeValueChartInstance.dispose()
  }
  if (clusterAnalysisChartInstance) {
    clusterAnalysisChartInstance.dispose()
  }
  if (lifecycleStageChartInstance) {
    lifecycleStageChartInstance.dispose()
  }
  if (churnRiskChartInstance) {
    churnRiskChartInstance.dispose()
  }
  if (satisfactionChartInstance) {
    satisfactionChartInstance.dispose()
  }
})
</script>

<style scoped>
.customer-analysis-chart {
  padding: 20px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #666;
}

.loading-container p {
  margin-top: 15px;
  font-size: 16px;
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.analysis-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  padding: 20px;
}

.chart-container h4 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 16px;
  text-align: center;
}

.chart {
  width: 100%;
  height: 300px;
}

.insights-card {
  margin-top: 20px;
}

.insights-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.insight-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.insight-icon {
  color: #409eff;
  font-size: 24px;
  margin-top: 5px;
}

.insight-text h5 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 16px;
}

.insight-text p {
  margin: 0;
  color: #666;
  line-height: 1.5;
}
</style>