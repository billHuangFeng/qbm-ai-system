<template>
  <div class="attribution-page">
    <el-row :gutter="20">
      <!-- 归因分析配置 -->
      <el-col :span="8">
        <el-card>
          <template #header>
            <h3>归因分析配置</h3>
          </template>
          
          <el-form :model="config" label-width="100px">
            <el-form-item label="分析时间">
              <el-date-picker
                v-model="config.dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                style="width: 100%"
              />
            </el-form-item>
            
            <el-form-item label="归因模型">
              <el-select v-model="config.model" style="width: 100%">
                <el-option label="Shapley值" value="shapley" />
                <el-option label="首次点击" value="first_click" />
                <el-option label="最后点击" value="last_click" />
                <el-option label="线性归因" value="linear" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="采样次数">
              <el-input-number v-model="config.samples" :min="1000" :max="100000" style="width: 100%" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="runAnalysis" :loading="analyzing">
                <el-icon><Play /></el-icon>
                开始分析
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 归因结果 -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <h3>归因结果</h3>
          </template>
          
          <div v-if="!analysisResult" class="empty-state">
            <el-empty description="请先运行归因分析" />
          </div>
          
          <div v-else>
            <!-- 归因权重图表 -->
            <div class="chart-container">
              <v-chart :option="attributionChartOption" style="height: 300px;" />
            </div>
            
            <!-- 归因结果表格 -->
            <el-table :data="attributionData" border style="margin-top: 20px;">
              <el-table-column prop="media_id" label="媒体渠道" />
              <el-table-column prop="attribution_weight" label="归因权重">
                <template #default="{ row }">
                  <el-progress :percentage="row.attribution_weight * 100" :show-text="false" />
                  <span style="margin-left: 10px;">{{ (row.attribution_weight * 100).toFixed(2) }}%</span>
                </template>
              </el-table-column>
              <el-table-column prop="conversion_value" label="转化价值">
                <template #default="{ row }">
                  ¥{{ row.conversion_value.toLocaleString() }}
                </template>
              </el-table-column>
              <el-table-column prop="touchpoint_count" label="触点数量" />
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细分析 -->
    <el-row style="margin-top: 20px;" v-if="analysisResult">
      <el-col :span="24">
        <el-card>
          <template #header>
            <h3>详细分析</h3>
          </template>
          
          <el-tabs v-model="activeTab">
            <el-tab-pane label="归因路径" name="path">
              <el-table :data="attributionPaths" border>
                <el-table-column prop="customer_id" label="客户ID" />
                <el-table-column prop="touchpoint_sequence" label="触点序列" />
                <el-table-column prop="conversion_value" label="转化价值" />
                <el-table-column prop="attribution_weights" label="归因权重" />
              </el-table>
            </el-tab-pane>
            
            <el-tab-pane label="媒体效果" name="media">
              <div class="chart-container">
                <v-chart :option="mediaEffectChartOption" style="height: 400px;" />
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="时间分布" name="time">
              <div class="chart-container">
                <v-chart :option="timeDistributionChartOption" style="height: 400px;" />
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

use([
  CanvasRenderer,
  PieChart,
  BarChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

// 响应式数据
const analyzing = ref(false)
const analysisResult = ref(null)
const activeTab = ref('path')

// 配置
const config = reactive({
  dateRange: [new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), new Date()],
  model: 'shapley',
  samples: 10000
})

// 模拟归因数据
const attributionData = ref([
  { media_id: 'douyin', attribution_weight: 0.35, conversion_value: 35000, touchpoint_count: 150 },
  { media_id: 'xiaohongshu', attribution_weight: 0.28, conversion_value: 28000, touchpoint_count: 120 },
  { media_id: 'tmall', attribution_weight: 0.22, conversion_value: 22000, touchpoint_count: 80 },
  { media_id: 'baidu', attribution_weight: 0.15, conversion_value: 15000, touchpoint_count: 60 }
])

const attributionPaths = ref([
  { customer_id: 'cust001', touchpoint_sequence: 'douyin -> xiaohongshu -> tmall', conversion_value: 1000, attribution_weights: '0.4, 0.3, 0.3' },
  { customer_id: 'cust002', touchpoint_sequence: 'baidu -> douyin', conversion_value: 800, attribution_weights: '0.2, 0.8' }
])

// 图表配置
const attributionChartOption = computed(() => {
  return {
    title: {
      text: '媒体渠道归因权重',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    series: [
      {
        name: '归因权重',
        type: 'pie',
        radius: '50%',
        data: attributionData.value.map(item => ({
          value: item.attribution_weight * 100,
          name: item.media_id
        })),
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
})

const mediaEffectChartOption = computed(() => {
  return {
    title: {
      text: '媒体渠道效果对比',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: attributionData.value.map(item => item.media_id)
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '转化价值',
        type: 'bar',
        data: attributionData.value.map(item => item.conversion_value)
      }
    ]
  }
})

const timeDistributionChartOption = computed(() => {
  return {
    title: {
      text: '触点时间分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['0-1天', '1-3天', '3-7天', '7-14天', '14-30天', '30天+']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '触点数量',
        type: 'line',
        data: [120, 200, 150, 80, 70, 30]
      }
    ]
  }
})

// 方法
const runAnalysis = async () => {
  analyzing.value = true
  try {
    // 模拟分析过程
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    analysisResult.value = {
      model: config.model,
      samples: config.samples,
      dateRange: config.dateRange,
      timestamp: new Date()
    }
    
    ElMessage.success('归因分析完成')
  } catch (error) {
    ElMessage.error('归因分析失败')
  } finally {
    analyzing.value = false
  }
}
</script>

<style scoped>
.attribution-page {
  padding: 0;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}

.chart-container {
  width: 100%;
}
</style>

