<template>
  <div class="product-analysis-chart">
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" size="32"><Loading /></el-icon>
      <p>正在分析产品数据...</p>
    </div>
    
    <div v-else class="analysis-content">
      <!-- 产品性能分析 -->
      <el-card class="analysis-card">
        <template #header>
          <div class="card-header">
            <span>产品性能分析</span>
            <el-button type="text" @click="refreshAnalysis">刷新</el-button>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="chart-container">
              <h4>产品类别收入分析</h4>
              <div ref="categoryRevenueChart" class="chart"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <h4>产品销量分析</h4>
              <div ref="salesVolumeChart" class="chart"></div>
            </div>
          </el-col>
        </el-row>
      </el-card>
      
      <!-- 产品组合分析 -->
      <el-card class="analysis-card">
        <template #header>
          <div class="card-header">
            <span>产品组合分析</span>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="chart-container">
              <h4>产品组合矩阵</h4>
              <div ref="portfolioMatrixChart" class="chart"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <h4>产品生命周期分析</h4>
              <div ref="lifecycleAnalysisChart" class="chart"></div>
            </div>
          </el-col>
        </el-row>
      </el-card>
      
      <!-- 产品成功预测 -->
      <el-card class="analysis-card">
        <template #header>
          <div class="card-header">
            <span>产品成功预测</span>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="chart-container">
              <h4>产品成功度预测</h4>
              <div ref="successPredictionChart" class="chart"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <h4>产品推荐度分析</h4>
              <div ref="recommendationChart" class="chart"></div>
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
              <h5>明星产品表现</h5>
              <p>软件产品类别表现最佳，占总收入的40%，建议加大投入</p>
            </div>
          </div>
          
          <div class="insight-item">
            <el-icon class="insight-icon"><Warning /></el-icon>
            <div class="insight-text">
              <h5>产品组合优化</h5>
              <p>发现2个问题产品需要重点关注，建议调整策略或淘汰</p>
            </div>
          </div>
          
          <div class="insight-item">
            <el-icon class="insight-icon"><Star /></el-icon>
            <div class="insight-text">
              <h5>产品生命周期</h5>
              <p>成熟期产品贡献最大，新上市产品需要更多市场推广</p>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
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
const categoryRevenueChart = ref(null)
const salesVolumeChart = ref(null)
const portfolioMatrixChart = ref(null)
const lifecycleAnalysisChart = ref(null)
const successPredictionChart = ref(null)
const recommendationChart = ref(null)

// 图表实例
let categoryRevenueChartInstance = null
let salesVolumeChartInstance = null
let portfolioMatrixChartInstance = null
let lifecycleAnalysisChartInstance = null
let successPredictionChartInstance = null
let recommendationChartInstance = null

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
  initCategoryRevenueChart()
  initSalesVolumeChart()
  initPortfolioMatrixChart()
  initLifecycleAnalysisChart()
  initSuccessPredictionChart()
  initRecommendationChart()
}

// 产品类别收入分析图表
const initCategoryRevenueChart = () => {
  if (!categoryRevenueChart.value) return
  
  categoryRevenueChartInstance = echarts.init(categoryRevenueChart.value)
  
  const data = props.analysisData.performance_analysis?.category_analysis || {
    '软件产品': { revenue: { sum: 1000000 }, sales_volume: { sum: 500 } },
    '硬件产品': { revenue: { sum: 800000 }, sales_volume: { sum: 200 } },
    '服务产品': { revenue: { sum: 600000 }, sales_volume: { sum: 300 } }
  }
  
  const categories = Object.keys(data)
  const revenues = Object.values(data).map(item => item.revenue.sum)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        return `${params[0].name}<br/>收入: ¥${params[0].value.toLocaleString()}`
      }
    },
    xAxis: {
      type: 'category',
      data: categories
    },
    yAxis: {
      type: 'value',
      name: '收入 (¥)'
    },
    series: [
      {
        name: '收入',
        type: 'bar',
        data: revenues,
        itemStyle: {
          color: '#409eff'
        }
      }
    ]
  }
  
  categoryRevenueChartInstance.setOption(option)
}

// 产品销量分析图表
const initSalesVolumeChart = () => {
  if (!salesVolumeChart.value) return
  
  salesVolumeChartInstance = echarts.init(salesVolumeChart.value)
  
  const data = props.analysisData.performance_analysis?.category_analysis || {
    '软件产品': { revenue: { sum: 1000000 }, sales_volume: { sum: 500 } },
    '硬件产品': { revenue: { sum: 800000 }, sales_volume: { sum: 200 } },
    '服务产品': { revenue: { sum: 600000 }, sales_volume: { sum: 300 } }
  }
  
  const categories = Object.keys(data)
  const volumes = Object.values(data).map(item => item.sales_volume.sum)
  
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
      name: '销量'
    },
    series: [
      {
        name: '销量',
        type: 'bar',
        data: volumes,
        itemStyle: {
          color: '#67c23a'
        }
      }
    ]
  }
  
  salesVolumeChartInstance.setOption(option)
}

// 产品组合矩阵图表
const initPortfolioMatrixChart = () => {
  if (!portfolioMatrixChart.value) return
  
  portfolioMatrixChartInstance = echarts.init(portfolioMatrixChart.value)
  
  const data = props.analysisData.portfolio_analysis?.portfolio_matrix?.distribution || {
    '明星产品': 3,
    '现金牛产品': 5,
    '问题产品': 2,
    '瘦狗产品': 1
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
        name: '产品组合',
        type: 'pie',
        radius: '50%',
        data: [
          { value: data['明星产品'], name: '明星产品' },
          { value: data['现金牛产品'], name: '现金牛产品' },
          { value: data['问题产品'], name: '问题产品' },
          { value: data['瘦狗产品'], name: '瘦狗产品' }
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
            const colors = ['#f56c6c', '#e6a23c', '#67c23a', '#409eff']
            return colors[params.dataIndex]
          }
        }
      }
    ]
  }
  
  portfolioMatrixChartInstance.setOption(option)
}

// 产品生命周期分析图表
const initLifecycleAnalysisChart = () => {
  if (!lifecycleAnalysisChart.value) return
  
  lifecycleAnalysisChartInstance = echarts.init(lifecycleAnalysisChart.value)
  
  const data = props.analysisData.lifecycle_analysis?.stage_performance || {
    '新上市': { revenue: { count: 2, mean: 100000 } },
    '成长期': { revenue: { count: 3, mean: 200000 } },
    '成熟期': { revenue: { count: 4, mean: 300000 } },
    '衰退期': { revenue: { count: 2, mean: 150000 } }
  }
  
  const categories = Object.keys(data)
  const counts = Object.values(data).map(item => item.revenue.count)
  const revenues = Object.values(data).map(item => item.revenue.mean)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['产品数量', '平均收入']
    },
    xAxis: {
      type: 'category',
      data: categories
    },
    yAxis: [
      {
        type: 'value',
        name: '产品数量',
        position: 'left'
      },
      {
        type: 'value',
        name: '平均收入 (¥)',
        position: 'right'
      }
    ],
    series: [
      {
        name: '产品数量',
        type: 'bar',
        data: counts,
        itemStyle: {
          color: '#409eff'
        }
      },
      {
        name: '平均收入',
        type: 'line',
        yAxisIndex: 1,
        data: revenues,
        itemStyle: {
          color: '#67c23a'
        }
      }
    ]
  }
  
  lifecycleAnalysisChartInstance.setOption(option)
}

// 产品成功预测图表
const initSuccessPredictionChart = () => {
  if (!successPredictionChart.value) return
  
  successPredictionChartInstance = echarts.init(successPredictionChart.value)
  
  const data = props.analysisData.success_prediction || {
    predictions: [0.8, 0.6, 0.9, 0.7, 0.5, 0.8, 0.6, 0.9, 0.7, 0.8],
    success_categories: ['高成功度', '中等成功度', '超高成功度', '高成功度', '低成功度', '高成功度', '中等成功度', '超高成功度', '高成功度', '高成功度']
  }
  
  const products = data.predictions.map((_, index) => `产品${index + 1}`)
  const predictions = data.predictions
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        const index = params[0].dataIndex
        return `${params[0].name}<br/>成功度: ${(params[0].value * 100).toFixed(1)}%<br/>分类: ${data.success_categories[index]}`
      }
    },
    xAxis: {
      type: 'category',
      data: products
    },
    yAxis: {
      type: 'value',
      name: '成功度',
      min: 0,
      max: 1
    },
    series: [
      {
        name: '成功度',
        type: 'bar',
        data: predictions,
        itemStyle: {
          color: function(params) {
            const value = params.value
            if (value >= 0.8) return '#67c23a'
            if (value >= 0.6) return '#e6a23c'
            return '#f56c6c'
          }
        }
      }
    ]
  }
  
  successPredictionChartInstance.setOption(option)
}

// 产品推荐度分析图表
const initRecommendationChart = () => {
  if (!recommendationChart.value) return
  
  recommendationChartInstance = echarts.init(recommendationChart.value)
  
  // 模拟推荐度数据
  const data = {
    '产品A': 0.9,
    '产品B': 0.7,
    '产品C': 0.8,
    '产品D': 0.6,
    '产品E': 0.5
  }
  
  const products = Object.keys(data)
  const recommendations = Object.values(data)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        return `${params[0].name}<br/>推荐度: ${(params[0].value * 100).toFixed(1)}%`
      }
    },
    xAxis: {
      type: 'category',
      data: products
    },
    yAxis: {
      type: 'value',
      name: '推荐度',
      min: 0,
      max: 1
    },
    series: [
      {
        name: '推荐度',
        type: 'bar',
        data: recommendations,
        itemStyle: {
          color: '#409eff'
        }
      }
    ]
  }
  
  recommendationChartInstance.setOption(option)
}

// 刷新分析
const refreshAnalysis = () => {
  // 这里可以触发重新分析
  console.log('刷新产品分析')
}

// 组件卸载时销毁图表实例
onUnmounted(() => {
  if (categoryRevenueChartInstance) {
    categoryRevenueChartInstance.dispose()
  }
  if (salesVolumeChartInstance) {
    salesVolumeChartInstance.dispose()
  }
  if (portfolioMatrixChartInstance) {
    portfolioMatrixChartInstance.dispose()
  }
  if (lifecycleAnalysisChartInstance) {
    lifecycleAnalysisChartInstance.dispose()
  }
  if (successPredictionChartInstance) {
    successPredictionChartInstance.dispose()
  }
  if (recommendationChartInstance) {
    recommendationChartInstance.dispose()
  }
})
</script>

<style scoped>
.product-analysis-chart {
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