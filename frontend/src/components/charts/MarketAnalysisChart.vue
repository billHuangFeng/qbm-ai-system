<template>
  <div class="market-analysis-chart">
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" size="32"><Loading /></el-icon>
      <p>正在分析市场数据...</p>
    </div>
    
    <div v-else class="analysis-content">
      <!-- 市场趋势分析 -->
      <el-card class="analysis-card">
        <template #header>
          <div class="card-header">
            <span>市场趋势分析</span>
            <el-button type="text" @click="refreshAnalysis">刷新</el-button>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="chart-container">
              <h4>月度市场趋势</h4>
              <div ref="marketTrendChart" class="chart"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <h4>市场增长率</h4>
              <div ref="growthRateChart" class="chart"></div>
            </div>
          </el-col>
        </el-row>
      </el-card>
      
      <!-- 竞争分析 -->
      <el-card class="analysis-card">
        <template #header>
          <div class="card-header">
            <span>竞争分析</span>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="chart-container">
              <h4>市场份额分析</h4>
              <div ref="marketShareChart" class="chart"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <h4>竞争地位</h4>
              <div ref="competitivePositionChart" class="chart"></div>
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
              <h4>客户价值分布</h4>
              <div ref="customerValueChart" class="chart"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <h4>需求预测</h4>
              <div ref="demandPredictionChart" class="chart"></div>
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
              <h5>市场增长强劲</h5>
              <p>月度增长率超过10%，市场前景良好</p>
            </div>
          </div>
          
          <div class="insight-item">
            <el-icon class="insight-icon"><Warning /></el-icon>
            <div class="insight-text">
              <h5>竞争激烈</h5>
              <p>市场份额为25%，需要加强竞争优势</p>
            </div>
          </div>
          
          <div class="insight-item">
            <el-icon class="insight-icon"><Star /></el-icon>
            <div class="insight-text">
              <h5>客户价值提升</h5>
              <p>高价值客户占比25%，客户结构持续优化</p>
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
const marketTrendChart = ref(null)
const growthRateChart = ref(null)
const marketShareChart = ref(null)
const competitivePositionChart = ref(null)
const customerValueChart = ref(null)
const demandPredictionChart = ref(null)

// 图表实例
let marketTrendChartInstance = null
let growthRateChartInstance = null
let marketShareChartInstance = null
let competitivePositionChartInstance = null
let customerValueChartInstance = null
let demandPredictionChartInstance = null

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
  initMarketTrendChart()
  initGrowthRateChart()
  initMarketShareChart()
  initCompetitivePositionChart()
  initCustomerValueChart()
  initDemandPredictionChart()
}

// 月度市场趋势图表
const initMarketTrendChart = () => {
  if (!marketTrendChart.value) return
  
  marketTrendChartInstance = echarts.init(marketTrendChart.value)
  
  const data = props.analysisData.trend_analysis?.time_trends?.monthly_trends || {
    '2024-01': { amount: { sum: 1000000, count: 50 } },
    '2024-02': { amount: { sum: 1200000, count: 60 } },
    '2024-03': { amount: { sum: 1500000, count: 75 } },
    '2024-04': { amount: { sum: 1800000, count: 90 } }
  }
  
  const months = Object.keys(data)
  const amounts = Object.values(data).map(item => item.amount.sum)
  const counts = Object.values(data).map(item => item.amount.count)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['市场金额', '交易数量']
    },
    xAxis: {
      type: 'category',
      data: months
    },
    yAxis: [
      {
        type: 'value',
        name: '市场金额 (¥)',
        position: 'left'
      },
      {
        type: 'value',
        name: '交易数量',
        position: 'right'
      }
    ],
    series: [
      {
        name: '市场金额',
        type: 'line',
        data: amounts,
        smooth: true,
        itemStyle: {
          color: '#409eff'
        }
      },
      {
        name: '交易数量',
        type: 'bar',
        yAxisIndex: 1,
        data: counts,
        itemStyle: {
          color: '#67c23a'
        }
      }
    ]
  }
  
  marketTrendChartInstance.setOption(option)
}

// 市场增长率图表
const initGrowthRateChart = () => {
  if (!growthRateChart.value) return
  
  growthRateChartInstance = echarts.init(growthRateChart.value)
  
  // 计算增长率
  const data = props.analysisData.trend_analysis?.time_trends?.monthly_trends || {
    '2024-01': { amount: { sum: 1000000, count: 50 } },
    '2024-02': { amount: { sum: 1200000, count: 60 } },
    '2024-03': { amount: { sum: 1500000, count: 75 } },
    '2024-04': { amount: { sum: 1800000, count: 90 } }
  }
  
  const months = Object.keys(data)
  const amounts = Object.values(data).map(item => item.amount.sum)
  const growthRates = []
  
  for (let i = 1; i < amounts.length; i++) {
    const growthRate = ((amounts[i] - amounts[i-1]) / amounts[i-1] * 100).toFixed(1)
    growthRates.push(parseFloat(growthRate))
  }
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        return `${params[0].name}<br/>增长率: ${params[0].value}%`
      }
    },
    xAxis: {
      type: 'category',
      data: months.slice(1) // 去掉第一个月，因为没有增长率
    },
    yAxis: {
      type: 'value',
      name: '增长率 (%)'
    },
    series: [
      {
        name: '增长率',
        type: 'bar',
        data: growthRates,
        itemStyle: {
          color: function(params) {
            const value = params.value
            if (value > 0) return '#67c23a'
            return '#f56c6c'
          }
        }
      }
    ]
  }
  
  growthRateChartInstance.setOption(option)
}

// 市场份额分析图表
const initMarketShareChart = () => {
  if (!marketShareChart.value) return
  
  marketShareChartInstance = echarts.init(marketShareChart.value)
  
  const data = props.analysisData.competition_analysis?.market_share_analysis || {
    avg_market_share: 25
  }
  
  const ourShare = data.avg_market_share || 25
  const competitorShare = 100 - ourShare
  
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
        name: '市场份额',
        type: 'pie',
        radius: '50%',
        data: [
          { value: ourShare, name: '我们的份额' },
          { value: competitorShare, name: '竞争对手份额' }
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
            return params.name === '我们的份额' ? '#409eff' : '#e0e0e0'
          }
        }
      }
    ]
  }
  
  marketShareChartInstance.setOption(option)
}

// 竞争地位图表
const initCompetitivePositionChart = () => {
  if (!competitivePositionChart.value) return
  
  competitivePositionChartInstance = echarts.init(competitivePositionChart.value)
  
  // 模拟竞争地位数据
  const competitors = ['我们', '竞争对手A', '竞争对手B', '竞争对手C']
  const marketShares = [25, 30, 20, 25]
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: competitors
    },
    yAxis: {
      type: 'value',
      name: '市场份额 (%)',
      max: 35
    },
    series: [
      {
        name: '市场份额',
        type: 'bar',
        data: marketShares,
        itemStyle: {
          color: function(params) {
            return params.name === '我们' ? '#409eff' : '#e0e0e0'
          }
        }
      }
    ]
  }
  
  competitivePositionChartInstance.setOption(option)
}

// 客户价值分布图表
const initCustomerValueChart = () => {
  if (!customerValueChart.value) return
  
  customerValueChartInstance = echarts.init(customerValueChart.value)
  
  const data = props.analysisData.segmentation_analysis?.customer_segments || {
    '高价值': { amount: { count: 250 } },
    '中价值': { amount: { count: 500 } },
    '低价值': { amount: { count: 250 } }
  }
  
  const categories = Object.keys(data)
  const counts = Object.values(data).map(item => item.amount.count)
  
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
        data: categories.map((category, index) => ({
          value: counts[index],
          name: category
        })),
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
  
  customerValueChartInstance.setOption(option)
}

// 需求预测图表
const initDemandPredictionChart = () => {
  if (!demandPredictionChart.value) return
  
  demandPredictionChartInstance = echarts.init(demandPredictionChart.value)
  
  const data = props.analysisData.demand_prediction || {
    predictions: [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
  }
  
  const predictions = data.predictions || [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
  const months = predictions.map((_, index) => `${index + 1}月`)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    xAxis: {
      type: 'category',
      data: months
    },
    yAxis: {
      type: 'value',
      name: '预测需求'
    },
    series: [
      {
        name: '需求预测',
        type: 'line',
        data: predictions,
        smooth: true,
        itemStyle: {
          color: '#409eff'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0, color: 'rgba(64, 158, 255, 0.3)'
            }, {
              offset: 1, color: 'rgba(64, 158, 255, 0.1)'
            }]
          }
        }
      }
    ]
  }
  
  demandPredictionChartInstance.setOption(option)
}

// 刷新分析
const refreshAnalysis = () => {
  // 这里可以触发重新分析
  console.log('刷新市场分析')
}

// 组件卸载时销毁图表实例
onUnmounted(() => {
  if (marketTrendChartInstance) {
    marketTrendChartInstance.dispose()
  }
  if (growthRateChartInstance) {
    growthRateChartInstance.dispose()
  }
  if (marketShareChartInstance) {
    marketShareChartInstance.dispose()
  }
  if (competitivePositionChartInstance) {
    competitivePositionChartInstance.dispose()
  }
  if (customerValueChartInstance) {
    customerValueChartInstance.dispose()
  }
  if (demandPredictionChartInstance) {
    demandPredictionChartInstance.dispose()
  }
})
</script>

<style scoped>
.market-analysis-chart {
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