<template>
  <div class="financial-analysis-chart">
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" size="32"><Loading /></el-icon>
      <p>正在分析财务数据...</p>
    </div>
    
    <div v-else class="analysis-content">
      <!-- 财务性能分析 -->
      <el-card class="analysis-card">
        <template #header>
          <div class="card-header">
            <span>财务性能分析</span>
            <el-button type="text" @click="refreshAnalysis">刷新</el-button>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="chart-container">
              <h4>收入支出分析</h4>
              <div ref="incomeExpenseChart" class="chart"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <h4>财务类型分布</h4>
              <div ref="financialTypeChart" class="chart"></div>
            </div>
          </el-col>
        </el-row>
      </el-card>
      
      <!-- 盈利能力分析 -->
      <el-card class="analysis-card">
        <template #header>
          <div class="card-header">
            <span>盈利能力分析</span>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="chart-container">
              <h4>收入趋势分析</h4>
              <div ref="revenueTrendChart" class="chart"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <h4>利润率分析</h4>
              <div ref="profitMarginChart" class="chart"></div>
            </div>
          </el-col>
        </el-row>
      </el-card>
      
      <!-- 现金流分析 -->
      <el-card class="analysis-card">
        <template #header>
          <div class="card-header">
            <span>现金流分析</span>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="chart-container">
              <h4>月度现金流</h4>
              <div ref="cashFlowChart" class="chart"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <h4>财务健康度</h4>
              <div ref="financialHealthChart" class="chart"></div>
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
              <h5>盈利能力良好</h5>
              <p>利润率保持在25%以上，收入增长趋势稳定</p>
            </div>
          </div>
          
          <div class="insight-item">
            <el-icon class="insight-icon"><Warning /></el-icon>
            <div class="insight-text">
              <h5>成本控制</h5>
              <p>成本控制比例为75%，建议进一步优化运营效率</p>
            </div>
          </div>
          
          <div class="insight-item">
            <el-icon class="insight-icon"><Star /></el-icon>
            <div class="insight-text">
              <h5>财务健康度</h5>
              <p>财务健康度评分为85分，整体财务状况良好</p>
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
const incomeExpenseChart = ref(null)
const financialTypeChart = ref(null)
const revenueTrendChart = ref(null)
const profitMarginChart = ref(null)
const cashFlowChart = ref(null)
const financialHealthChart = ref(null)

// 图表实例
let incomeExpenseChartInstance = null
let financialTypeChartInstance = null
let revenueTrendChartInstance = null
let profitMarginChartInstance = null
let cashFlowChartInstance = null
let financialHealthChartInstance = null

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
  initIncomeExpenseChart()
  initFinancialTypeChart()
  initRevenueTrendChart()
  initProfitMarginChart()
  initCashFlowChart()
  initFinancialHealthChart()
}

// 收入支出分析图表
const initIncomeExpenseChart = () => {
  if (!incomeExpenseChart.value) return
  
  incomeExpenseChartInstance = echarts.init(incomeExpenseChart.value)
  
  const data = props.analysisData.performance_analysis?.type_analysis || {
    '收入': { amount: { count: 100, sum: 2000000 } },
    '支出': { amount: { count: 80, sum: 1500000 } }
  }
  
  const categories = Object.keys(data)
  const amounts = Object.values(data).map(item => item.amount.sum)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        return `${params[0].name}<br/>金额: ¥${params[0].value.toLocaleString()}`
      }
    },
    xAxis: {
      type: 'category',
      data: categories
    },
    yAxis: {
      type: 'value',
      name: '金额 (¥)'
    },
    series: [
      {
        name: '金额',
        type: 'bar',
        data: amounts,
        itemStyle: {
          color: function(params) {
            return params.name === '收入' ? '#67c23a' : '#f56c6c'
          }
        }
      }
    ]
  }
  
  incomeExpenseChartInstance.setOption(option)
}

// 财务类型分布图表
const initFinancialTypeChart = () => {
  if (!financialTypeChart.value) return
  
  financialTypeChartInstance = echarts.init(financialTypeChart.value)
  
  const data = props.analysisData.performance_analysis?.type_analysis || {
    '收入': { amount: { count: 100, sum: 2000000 } },
    '支出': { amount: { count: 80, sum: 1500000 } }
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
        name: '财务类型',
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
            const colors = ['#67c23a', '#f56c6c']
            return colors[params.dataIndex]
          }
        }
      }
    ]
  }
  
  financialTypeChartInstance.setOption(option)
}

// 收入趋势分析图表
const initRevenueTrendChart = () => {
  if (!revenueTrendChart.value) return
  
  revenueTrendChartInstance = echarts.init(revenueTrendChart.value)
  
  const data = props.analysisData.profitability_analysis || {
    revenue_analysis: { total_revenue: 2000000 },
    expense_analysis: { total_expenses: 1500000 },
    profit_margin: 25
  }
  
  // 模拟月度收入数据
  const months = ['1月', '2月', '3月', '4月', '5月', '6月']
  const revenues = [1500000, 1800000, 2000000, 2200000, 2100000, 2000000]
  
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
      name: '收入 (¥)'
    },
    series: [
      {
        name: '收入',
        type: 'line',
        data: revenues,
        smooth: true,
        itemStyle: {
          color: '#67c23a'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0, color: 'rgba(103, 194, 58, 0.3)'
            }, {
              offset: 1, color: 'rgba(103, 194, 58, 0.1)'
            }]
          }
        }
      }
    ]
  }
  
  revenueTrendChartInstance.setOption(option)
}

// 利润率分析图表
const initProfitMarginChart = () => {
  if (!profitMarginChart.value) return
  
  profitMarginChartInstance = echarts.init(profitMarginChart.value)
  
  const data = props.analysisData.profitability_analysis || {
    revenue_analysis: { total_revenue: 2000000 },
    expense_analysis: { total_expenses: 1500000 },
    profit_margin: 25
  }
  
  const profitMargin = data.profit_margin || 25
  
  const option = {
    tooltip: {
      formatter: '{a} <br/>{b}: {c}%'
    },
    series: [
      {
        name: '利润率',
        type: 'gauge',
        center: ['50%', '60%'],
        startAngle: 200,
        endAngle: -20,
        min: 0,
        max: 100,
        splitNumber: 10,
        itemStyle: {
          color: '#67c23a'
        },
        progress: {
          show: true,
          width: 30
        },
        pointer: {
          show: false
        },
        axisLine: {
          lineStyle: {
            width: 30
          }
        },
        axisTick: {
          distance: -30,
          splitNumber: 5,
          lineStyle: {
            width: 2,
            color: '#999'
          }
        },
        splitLine: {
          distance: -30,
          length: 30,
          lineStyle: {
            width: 4,
            color: '#999'
          }
        },
        axisLabel: {
          distance: -20,
          color: '#999',
          fontSize: 20
        },
        detail: {
          valueAnimation: true,
          formatter: '{value}%',
          color: 'inherit'
        },
        data: [
          {
            value: profitMargin
          }
        ]
      }
    ]
  }
  
  profitMarginChartInstance.setOption(option)
}

// 月度现金流图表
const initCashFlowChart = () => {
  if (!cashFlowChart.value) return
  
  cashFlowChartInstance = echarts.init(cashFlowChart.value)
  
  const data = props.analysisData.cash_flow_analysis?.monthly_cash_flow || {
    '2024-01': 100000,
    '2024-02': 120000,
    '2024-03': 150000,
    '2024-04': 180000
  }
  
  const months = Object.keys(data)
  const cashFlows = Object.values(data)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: months
    },
    yAxis: {
      type: 'value',
      name: '现金流 (¥)'
    },
    series: [
      {
        name: '现金流',
        type: 'bar',
        data: cashFlows,
        itemStyle: {
          color: '#409eff'
        }
      }
    ]
  }
  
  cashFlowChartInstance.setOption(option)
}

// 财务健康度图表
const initFinancialHealthChart = () => {
  if (!financialHealthChart.value) return
  
  financialHealthChartInstance = echarts.init(financialHealthChart.value)
  
  const data = props.analysisData.health_analysis || {
    financial_ratios: {
      profit_margin: 25,
      revenue_growth_rate: 15,
      cost_control_ratio: 75
    },
    health_score: 85
  }
  
  const ratios = data.financial_ratios
  const categories = ['利润率', '收入增长率', '成本控制率']
  const values = [ratios.profit_margin, ratios.revenue_growth_rate, ratios.cost_control_ratio]
  
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
      name: '比率 (%)',
      max: 100
    },
    series: [
      {
        name: '财务比率',
        type: 'bar',
        data: values,
        itemStyle: {
          color: function(params) {
            const value = params.value
            if (value >= 80) return '#67c23a'
            if (value >= 60) return '#e6a23c'
            return '#f56c6c'
          }
        }
      }
    ]
  }
  
  financialHealthChartInstance.setOption(option)
}

// 刷新分析
const refreshAnalysis = () => {
  // 这里可以触发重新分析
  console.log('刷新财务分析')
}

// 组件卸载时销毁图表实例
onUnmounted(() => {
  if (incomeExpenseChartInstance) {
    incomeExpenseChartInstance.dispose()
  }
  if (financialTypeChartInstance) {
    financialTypeChartInstance.dispose()
  }
  if (revenueTrendChartInstance) {
    revenueTrendChartInstance.dispose()
  }
  if (profitMarginChartInstance) {
    profitMarginChartInstance.dispose()
  }
  if (cashFlowChartInstance) {
    cashFlowChartInstance.dispose()
  }
  if (financialHealthChartInstance) {
    financialHealthChartInstance.dispose()
  }
})
</script>

<style scoped>
.financial-analysis-chart {
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