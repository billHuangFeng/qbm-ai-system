<template>
  <div class="vpt-matrix">
    <!-- 投入-口碑错位矩阵 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>投入-口碑错位矩阵</span>
          <div class="header-controls">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="loadMatrixData"
            />
            <el-button type="primary" @click="loadMatrixData" style="margin-left: 16px;">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <div ref="chartRef" style="width: 100%; height: 600px;"></div>
    </el-card>
    
    <!-- 错位TOP5预警 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>错位TOP5预警</span>
      </template>
      
      <el-table :data="alerts" stripe border>
        <el-table-column prop="vpt_id" label="价值主张ID" width="120" />
        <el-table-column prop="vpt_name" label="价值主张名称" min-width="200" />
        <el-table-column prop="total_cost" label="投入金额" width="120">
          <template #default="scope">
            ¥{{ formatMoney(scope.row.total_cost) }}
          </template>
        </el-table-column>
        <el-table-column prop="avg_cvrs_score" label="口碑评分" width="120">
          <template #default="scope">
            <el-rate 
              v-model="scope.row.avg_cvrs_score" 
              disabled 
              show-score
              :max="5"
            />
          </template>
        </el-table-column>
        <el-table-column prop="total_sales" label="销售额" width="120">
          <template #default="scope">
            ¥{{ formatMoney(scope.row.total_sales) }}
          </template>
        </el-table-column>
        <el-table-column prop="roi" label="ROI" width="100">
          <template #default="scope">
            <span :class="getROIClass(scope.row.roi)">
              {{ (scope.row.roi * 100).toFixed(1) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="cvrs_elasticity" label="弹性系数" width="120">
          <template #default="scope">
            <el-tag :type="getElasticityType(scope.row.cvrs_elasticity)">
              {{ scope.row.cvrs_elasticity.toFixed(3) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="严重程度" width="100">
          <template #default="scope">
            <el-tag :type="getSeverityType(scope.row.severity)">
              {{ getSeverityLabel(scope.row.severity) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" type="primary" @click="showVPTDetail(scope.row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 价值主张详情对话框 -->
    <el-dialog 
      v-model="detailDialogVisible" 
      title="价值主张详情"
      width="800px"
    >
      <div v-if="selectedVPT">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="价值主张ID">
            {{ selectedVPT.vpt_id }}
          </el-descriptions-item>
          <el-descriptions-item label="价值主张名称">
            {{ selectedVPT.vpt_name }}
          </el-descriptions-item>
          <el-descriptions-item label="投入金额">
            ¥{{ formatMoney(selectedVPT.total_cost) }}
          </el-descriptions-item>
          <el-descriptions-item label="口碑评分">
            <el-rate 
              v-model="selectedVPT.avg_cvrs_score" 
              disabled 
              show-score
              :max="5"
            />
          </el-descriptions-item>
          <el-descriptions-item label="销售额">
            ¥{{ formatMoney(selectedVPT.total_sales) }}
          </el-descriptions-item>
          <el-descriptions-item label="ROI">
            <span :class="getROIClass(selectedVPT.roi)">
              {{ (selectedVPT.roi * 100).toFixed(1) }}%
            </span>
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 趋势图表 -->
        <div style="margin-top: 20px;">
          <h4>投入-口碑趋势</h4>
          <div ref="trendChartRef" style="width: 100%; height: 300px;"></div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { 
  getVPTPerformance, 
  getMarginalAlerts 
} from '@/api/bmos/analytics'

// 响应式数据
const chartRef = ref()
const trendChartRef = ref()
const dateRange = ref([])
const alerts = ref([])
const detailDialogVisible = ref(false)
const selectedVPT = ref(null)

// 图表实例
let matrixChart = null
let trendChart = null

// 初始化日期范围（默认最近30天）
const initDateRange = () => {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)
  
  dateRange.value = [
    start.toISOString().split('T')[0],
    end.toISOString().split('T')[0]
  ]
}

// 加载矩阵数据
const loadMatrixData = async () => {
  try {
    if (!dateRange.value || dateRange.value.length !== 2) {
      ElMessage.warning('请选择日期范围')
      return
    }
    
    const [startDate, endDate] = dateRange.value
    
    // 获取VPT性能数据
    const performanceData = await getVPTPerformance(startDate, endDate)
    
    // 获取边际警报数据
    const alertsData = await getMarginalAlerts()
    
    // 更新警报数据
    alerts.value = alertsData.slice(0, 5) // 只显示TOP5
    
    // 初始化矩阵图表
    await nextTick()
    initMatrixChart(performanceData)
    
  } catch (error) {
    ElMessage.error('加载数据失败')
    console.error(error)
  }
}

// 初始化矩阵图表
const initMatrixChart = (data) => {
  if (!chartRef.value) return
  
  // 销毁现有图表
  if (matrixChart) {
    matrixChart.dispose()
  }
  
  matrixChart = echarts.init(chartRef.value)
  
  // 准备图表数据
  const chartData = data.map(item => [
    item.total_cost / 10000, // 投入金额（万元）
    item.avg_cvrs_score,     // 口碑评分
    item.total_sales,        // 销售额（用于气泡大小）
    item.vpt_id,             // VPT ID（用于标签）
    item.roi                 // ROI（用于颜色）
  ])
  
  const option = {
    title: {
      text: '投入-口碑矩阵（气泡大小=销售额）',
      left: 'center'
    },
    tooltip: {
      formatter: (params) => {
        const [cost, cvrs, sales, vptId, roi] = params.data
        return `
          <div>
            <strong>${vptId}</strong><br/>
            投入: ¥${(cost * 10000).toFixed(0)}<br/>
            口碑: ${cvrs.toFixed(2)}<br/>
            销售: ¥${sales.toFixed(0)}<br/>
            ROI: ${(roi * 100).toFixed(1)}%
          </div>
        `
      }
    },
    xAxis: {
      name: '投入金额（万元）',
      nameLocation: 'middle',
      nameGap: 30,
      type: 'value',
      axisLine: {
        lineStyle: {
          color: '#666'
        }
      }
    },
    yAxis: {
      name: '口碑评分',
      nameLocation: 'middle',
      nameGap: 50,
      type: 'value',
      min: 0,
      max: 5,
      axisLine: {
        lineStyle: {
          color: '#666'
        }
      }
    },
    series: [{
      type: 'scatter',
      data: chartData,
      symbolSize: (data) => {
        // 销售额映射为气泡大小（最小10，最大50）
        const minSales = Math.min(...chartData.map(d => d[2]))
        const maxSales = Math.max(...chartData.map(d => d[2]))
        const size = 10 + (data[2] - minSales) / (maxSales - minSales) * 40
        return Math.max(10, Math.min(50, size))
      },
      itemStyle: {
        color: (params) => {
          // ROI映射为颜色
          const roi = params.data[4]
          if (roi > 0.2) return '#67c23a'      // 绿色：高ROI
          else if (roi > 0.1) return '#e6a23c' // 橙色：中等ROI
          else if (roi > 0) return '#f56c6c'   // 红色：低ROI
          else return '#909399'                // 灰色：负ROI
        },
        opacity: 0.7
      },
      emphasis: {
        itemStyle: {
          opacity: 1,
          borderColor: '#333',
          borderWidth: 2
        }
      },
      label: {
        show: true,
        formatter: (params) => params.data[3], // 显示VPT ID
        position: 'top',
        fontSize: 10
      }
    }],
    grid: {
      left: '10%',
      right: '10%',
      bottom: '15%',
      top: '15%'
    }
  }
  
  matrixChart.setOption(option)
  
  // 添加点击事件
  matrixChart.on('click', (params) => {
    const vptId = params.data[3]
    const vptData = data.find(item => item.vpt_id === vptId)
    if (vptData) {
      showVPTDetail(vptData)
    }
  })
}

// 显示VPT详情
const showVPTDetail = async (vptData) => {
  selectedVPT.value = vptData
  detailDialogVisible.value = true
  
  // 等待对话框打开后初始化趋势图表
  await nextTick()
  initTrendChart(vptData)
}

// 初始化趋势图表
const initTrendChart = (vptData) => {
  if (!trendChartRef.value) return
  
  // 销毁现有图表
  if (trendChart) {
    trendChart.dispose()
  }
  
  trendChart = echarts.init(trendChartRef.value)
  
  // 模拟趋势数据（实际应该从API获取）
  const dates = []
  const costData = []
  const cvrsData = []
  
  for (let i = 29; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    dates.push(date.toISOString().split('T')[0])
    
    // 模拟数据
    costData.push(vptData.total_cost / 30 + Math.random() * 1000)
    cvrsData.push(vptData.avg_cvrs_score + (Math.random() - 0.5) * 0.5)
  }
  
  const option = {
    title: {
      text: '投入-口碑趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['投入金额', '口碑评分'],
      top: 30
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: [
      {
        type: 'value',
        name: '投入金额（元）',
        position: 'left'
      },
      {
        type: 'value',
        name: '口碑评分',
        position: 'right',
        min: 0,
        max: 5
      }
    ],
    series: [
      {
        name: '投入金额',
        type: 'line',
        yAxisIndex: 0,
        data: costData,
        itemStyle: {
          color: '#409eff'
        }
      },
      {
        name: '口碑评分',
        type: 'line',
        yAxisIndex: 1,
        data: cvrsData,
        itemStyle: {
          color: '#67c23a'
        }
      }
    ]
  }
  
  trendChart.setOption(option)
}

// 工具方法
const formatMoney = (amount) => {
  if (!amount) return '0'
  return Number(amount).toLocaleString()
}

const getROIClass = (roi) => {
  if (roi > 0.2) return 'roi-high'
  else if (roi > 0.1) return 'roi-medium'
  else if (roi > 0) return 'roi-low'
  else return 'roi-negative'
}

const getElasticityType = (elasticity) => {
  if (elasticity < -0.2) return 'danger'
  else if (elasticity < -0.1) return 'warning'
  else return 'success'
}

const getSeverityType = (severity) => {
  return severity === 'HIGH' ? 'danger' : 'warning'
}

const getSeverityLabel = (severity) => {
  return severity === 'HIGH' ? '高' : '中'
}

// 生命周期
onMounted(() => {
  initDateRange()
  loadMatrixData()
})
</script>

<style scoped>
.vpt-matrix {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-controls {
  display: flex;
  align-items: center;
}

.roi-high {
  color: #67c23a;
  font-weight: bold;
}

.roi-medium {
  color: #e6a23c;
  font-weight: bold;
}

.roi-low {
  color: #f56c6c;
  font-weight: bold;
}

.roi-negative {
  color: #909399;
  font-weight: bold;
}
</style>


