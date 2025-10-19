<template>
  <div class="base-chart">
    <div class="chart-header" v-if="title || $slots.header">
      <h3 v-if="title" class="chart-title">{{ title }}</h3>
      <slot name="header"></slot>
    </div>
    
    <div class="chart-container" :style="{ height: height + 'px' }">
      <v-chart 
        :option="chartOption" 
        :style="{ width: '100%', height: '100%' }"
        @click="handleChartClick"
        v-if="chartOption"
      />
      
      <div v-else class="chart-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
    </div>
    
    <div class="chart-footer" v-if="$slots.footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { 
  BarChart, LineChart, PieChart, ScatterChart, RadarChart,
  TitleComponent, TooltipComponent, LegendComponent, GridComponent,
  DataZoomComponent, ToolboxComponent, MarkPointComponent, MarkLineComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { Loading } from '@element-plus/icons-vue'

// 注册ECharts组件
use([
  CanvasRenderer,
  BarChart, LineChart, PieChart, ScatterChart, RadarChart,
  TitleComponent, TooltipComponent, LegendComponent, GridComponent,
  DataZoomComponent, ToolboxComponent, MarkPointComponent, MarkLineComponent
])

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  height: {
    type: Number,
    default: 400
  },
  data: {
    type: Object,
    default: () => ({})
  },
  type: {
    type: String,
    default: 'line',
    validator: (value) => ['line', 'bar', 'pie', 'scatter', 'radar'].includes(value)
  },
  options: {
    type: Object,
    default: () => ({})
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click', 'legendselectchanged', 'datazoom'])

const chartOption = ref(null)

// 计算图表配置
const computedChartOption = computed(() => {
  if (props.loading || !props.data) {
    return null
  }
  
  const baseOption = {
    title: {
      text: props.title,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: '#333',
      textStyle: {
        color: '#fff'
      }
    },
    legend: {
      top: 30,
      left: 'center'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    ...props.options
  }
  
  // 根据图表类型设置具体配置
  switch (props.type) {
    case 'line':
      return {
        ...baseOption,
        xAxis: {
          type: 'category',
          data: props.data.categories || [],
          axisLine: {
            lineStyle: {
              color: '#e0e0e0'
            }
          }
        },
        yAxis: {
          type: 'value',
          axisLine: {
            lineStyle: {
              color: '#e0e0e0'
            }
          }
        },
        series: props.data.series || []
      }
    
    case 'bar':
      return {
        ...baseOption,
        xAxis: {
          type: 'category',
          data: props.data.categories || [],
          axisLine: {
            lineStyle: {
              color: '#e0e0e0'
            }
          }
        },
        yAxis: {
          type: 'value',
          axisLine: {
            lineStyle: {
              color: '#e0e0e0'
            }
          }
        },
        series: props.data.series || []
      }
    
    case 'pie':
      return {
        ...baseOption,
        series: [{
          type: 'pie',
          radius: '50%',
          center: ['50%', '60%'],
          data: props.data.series || [],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      }
    
    case 'scatter':
      return {
        ...baseOption,
        xAxis: {
          type: 'value',
          scale: true,
          axisLine: {
            lineStyle: {
              color: '#e0e0e0'
            }
          }
        },
        yAxis: {
          type: 'value',
          scale: true,
          axisLine: {
            lineStyle: {
              color: '#e0e0e0'
            }
          }
        },
        series: props.data.series || []
      }
    
    case 'radar':
      return {
        ...baseOption,
        radar: {
          indicator: props.data.indicators || []
        },
        series: props.data.series || []
      }
    
    default:
      return baseOption
  }
})

// 监听数据变化
watch(computedChartOption, (newOption) => {
  chartOption.value = newOption
}, { immediate: true })

// 处理图表点击事件
const handleChartClick = (params) => {
  emit('click', params)
}

// 处理图例选择变化
const handleLegendSelectChanged = (params) => {
  emit('legendselectchanged', params)
}

// 处理数据缩放
const handleDataZoom = (params) => {
  emit('datazoom', params)
}
</script>

<style scoped>
.base-chart {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chart-header {
  padding: 20px 20px 0 20px;
  border-bottom: 1px solid #f0f0f0;
}

.chart-title {
  margin: 0 0 15px 0;
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
}

.chart-container {
  padding: 20px;
  position: relative;
}

.chart-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  font-size: 14px;
}

.chart-loading .el-icon {
  font-size: 24px;
  margin-bottom: 10px;
}

.chart-footer {
  padding: 0 20px 20px 20px;
  border-top: 1px solid #f0f0f0;
}
</style>



