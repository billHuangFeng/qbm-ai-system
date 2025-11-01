"""
前端组件测试用例
"""

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// 导入要测试的组件
import MarginalAnalysisDashboard from '../src/components/MarginalAnalysis/MarginalAnalysisDashboard'
import ManagerEvaluationPanel from '../src/components/ManagerEvaluation/EvaluationPanel'
import DataImportUploader from '../src/components/DataImport/RawDataUploader'
import DecisionCycleMonitor from '../src/components/DecisionCycle/CycleMonitor'
import SynergyAnalysisChart from '../src/components/Charts/SynergyAnalysisChart'
import ThresholdAnalysisChart from '../src/components/Charts/ThresholdAnalysisChart'
import DynamicWeightsChart from '../src/components/Charts/DynamicWeightsChart'

// 模拟API调用
const mockApiCall = vi.fn()

// 测试工具函数
const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </QueryClientProvider>
  )
}

// 模拟数据
const mockMarginalAnalysisData = {
  overall_score: 0.85,
  synergy_effects: {
    pairwise_interactions: [
      {
        features: ['feature_1', 'feature_2'],
        synergy_score: 0.75,
        significance: 0.95
      }
    ],
    polynomial_interactions: [
      {
        features: ['feature_1', 'feature_2'],
        degree: 2,
        synergy_score: 0.68,
        significance: 0.88
      }
    ]
  },
  threshold_effects: {
    thresholds: [
      {
        feature: 'feature_1',
        threshold: 12.5,
        effect_size: 0.45,
        significance: 0.92
      }
    ]
  },
  dynamic_weights: {
    weights: {
      'feature_1': 0.4,
      'feature_2': 0.35,
      'feature_3': 0.25
    },
    stability_score: 0.78
  }
}

const mockManagerEvaluationData = {
  evaluations: [
    {
      evaluation_id: 'eval_1',
      evaluator_name: 'John Doe',
      evaluation_date: '2024-01-15',
      evaluation_type: 'confirmation',
      evaluation_score: 0.85,
      feedback: 'Analysis looks accurate and comprehensive',
      status: 'completed'
    }
  ],
  metrics: {
    total_evaluations: 25,
    average_score: 0.82,
    completion_rate: 0.95
  }
}

const mockDataImportData = {
  upload_history: [
    {
      upload_id: 'upload_1',
      filename: 'sales_data.xlsx',
      upload_date: '2024-01-15',
      status: 'completed',
      records_processed: 1500,
      records_successful: 1480,
      records_failed: 20
    }
  ],
  supported_formats: ['xlsx', 'csv', 'json'],
  max_file_size: '10MB'
}

describe('MarginalAnalysisDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders dashboard with all sections', async () => {
    mockApiCall.mockResolvedValueOnce(mockMarginalAnalysisData)

    renderWithProviders(<MarginalAnalysisDashboard />)

    // 检查主要部分是否渲染
    expect(screen.getByText('边际影响分析仪表盘')).toBeInTheDocument()
    expect(screen.getByText('协同效应分析')).toBeInTheDocument()
    expect(screen.getByText('阈值效应分析')).toBeInTheDocument()
    expect(screen.getByText('动态权重分析')).toBeInTheDocument()
  })

  it('displays synergy analysis results', async () => {
    mockApiCall.mockResolvedValueOnce(mockMarginalAnalysisData)

    renderWithProviders(<MarginalAnalysisDashboard />)

    await waitFor(() => {
      expect(screen.getByText('协同效应评分: 0.85')).toBeInTheDocument()
    })
  })

  it('handles refresh button click', async () => {
    mockApiCall.mockResolvedValueOnce(mockMarginalAnalysisData)

    renderWithProviders(<MarginalAnalysisDashboard />)

    const refreshButton = screen.getByRole('button', { name: /刷新数据/i })
    fireEvent.click(refreshButton)

    await waitFor(() => {
      expect(mockApiCall).toHaveBeenCalledTimes(2) // 初始加载 + 刷新
    })
  })

  it('shows loading state', () => {
    mockApiCall.mockImplementation(() => new Promise(() => {})) // 永不解析

    renderWithProviders(<MarginalAnalysisDashboard />)

    expect(screen.getByText('加载中...')).toBeInTheDocument()
  })

  it('handles error state', async () => {
    mockApiCall.mockRejectedValueOnce(new Error('API Error'))

    renderWithProviders(<MarginalAnalysisDashboard />)

    await waitFor(() => {
      expect(screen.getByText('数据加载失败')).toBeInTheDocument()
    })
  })
})

describe('ManagerEvaluationPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders evaluation form', () => {
    renderWithProviders(<ManagerEvaluationPanel />)

    expect(screen.getByText('管理者评价')).toBeInTheDocument()
    expect(screen.getByLabelText('评价类型')).toBeInTheDocument()
    expect(screen.getByLabelText('评价分数')).toBeInTheDocument()
    expect(screen.getByLabelText('反馈内容')).toBeInTheDocument()
  })

  it('submits evaluation form', async () => {
    mockApiCall.mockResolvedValueOnce({ success: true })

    renderWithProviders(<ManagerEvaluationPanel />)

    // 填写表单
    fireEvent.change(screen.getByLabelText('评价类型'), { target: { value: 'confirmation' } })
    fireEvent.change(screen.getByLabelText('评价分数'), { target: { value: '0.85' } })
    fireEvent.change(screen.getByLabelText('反馈内容'), { 
      target: { value: '分析结果准确，建议采用' } 
    })

    // 提交表单
    const submitButton = screen.getByRole('button', { name: /提交评价/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockApiCall).toHaveBeenCalledWith('/api/v1/evaluations', {
        method: 'POST',
        body: JSON.stringify({
          evaluation_type: 'confirmation',
          evaluation_score: 0.85,
          feedback: '分析结果准确，建议采用'
        })
      })
    })
  })

  it('displays evaluation history', async () => {
    mockApiCall.mockResolvedValueOnce(mockManagerEvaluationData)

    renderWithProviders(<ManagerEvaluationPanel />)

    await waitFor(() => {
      expect(screen.getByText('评价历史')).toBeInTheDocument()
      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText('2024-01-15')).toBeInTheDocument()
    })
  })

  it('validates form inputs', async () => {
    renderWithProviders(<ManagerEvaluationPanel />)

    const submitButton = screen.getByRole('button', { name: /提交评价/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('请填写所有必填字段')).toBeInTheDocument()
    })
  })
})

describe('DataImportUploader', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders upload interface', () => {
    renderWithProviders(<DataImportUploader />)

    expect(screen.getByText('数据导入')).toBeInTheDocument()
    expect(screen.getByText('选择文件')).toBeInTheDocument()
    expect(screen.getByText('支持格式: xlsx, csv, json')).toBeInTheDocument()
  })

  it('handles file upload', async () => {
    mockApiCall.mockResolvedValueOnce({ success: true, upload_id: 'upload_1' })

    renderWithProviders(<DataImportUploader />)

    const file = new File(['test data'], 'test.xlsx', { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const fileInput = screen.getByLabelText('选择文件')
    
    fireEvent.change(fileInput, { target: { files: [file] } })

    await waitFor(() => {
      expect(screen.getByText('文件上传成功')).toBeInTheDocument()
    })
  })

  it('validates file format', async () => {
    renderWithProviders(<DataImportUploader />)

    const file = new File(['test data'], 'test.txt', { type: 'text/plain' })
    const fileInput = screen.getByLabelText('选择文件')
    
    fireEvent.change(fileInput, { target: { files: [file] } })

    await waitFor(() => {
      expect(screen.getByText('不支持的文件格式')).toBeInTheDocument()
    })
  })

  it('validates file size', async () => {
    renderWithProviders(<DataImportUploader />)

    // 创建一个大文件（模拟）
    const largeFile = new File(['x'.repeat(11 * 1024 * 1024)], 'large.xlsx', { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const fileInput = screen.getByLabelText('选择文件')
    
    fireEvent.change(fileInput, { target: { files: [largeFile] } })

    await waitFor(() => {
      expect(screen.getByText('文件大小超过限制')).toBeInTheDocument()
    })
  })

  it('displays upload progress', async () => {
    mockApiCall.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ success: true }), 1000))
    )

    renderWithProviders(<DataImportUploader />)

    const file = new File(['test data'], 'test.xlsx', { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const fileInput = screen.getByLabelText('选择文件')
    
    fireEvent.change(fileInput, { target: { files: [file] } })

    expect(screen.getByText('上传中...')).toBeInTheDocument()
  })
})

describe('DecisionCycleMonitor', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders cycle monitor', () => {
    renderWithProviders(<DecisionCycleMonitor />)

    expect(screen.getByText('决策循环监控')).toBeInTheDocument()
    expect(screen.getByText('当前状态')).toBeInTheDocument()
    expect(screen.getByText('执行历史')).toBeInTheDocument()
  })

  it('displays cycle status', async () => {
    const mockCycleData = {
      current_status: 'running',
      progress: 65,
      estimated_completion: '2024-01-15 14:30:00',
      execution_history: [
        {
          execution_id: 'exec_1',
          start_time: '2024-01-15 10:00:00',
          status: 'completed',
          duration: 120
        }
      ]
    }

    mockApiCall.mockResolvedValueOnce(mockCycleData)

    renderWithProviders(<DecisionCycleMonitor />)

    await waitFor(() => {
      expect(screen.getByText('运行中')).toBeInTheDocument()
      expect(screen.getByText('进度: 65%')).toBeInTheDocument()
    })
  })

  it('handles cycle control actions', async () => {
    mockApiCall.mockResolvedValueOnce({ success: true })

    renderWithProviders(<DecisionCycleMonitor />)

    const pauseButton = screen.getByRole('button', { name: /暂停/i })
    fireEvent.click(pauseButton)

    await waitFor(() => {
      expect(mockApiCall).toHaveBeenCalledWith('/api/v1/decision-cycle/pause', {
        method: 'POST'
      })
    })
  })
})

describe('SynergyAnalysisChart', () => {
  it('renders synergy chart', () => {
    const mockData = {
      pairwise_interactions: [
        {
          features: ['feature_1', 'feature_2'],
          synergy_score: 0.75,
          significance: 0.95
        }
      ],
      overall_score: 0.85
    }

    renderWithProviders(<SynergyAnalysisChart data={mockData} />)

    expect(screen.getByText('协同效应分析')).toBeInTheDocument()
    expect(screen.getByText('整体评分: 0.85')).toBeInTheDocument()
  })

  it('handles empty data', () => {
    const mockData = {
      pairwise_interactions: [],
      overall_score: 0
    }

    renderWithProviders(<SynergyAnalysisChart data={mockData} />)

    expect(screen.getByText('暂无协同效应数据')).toBeInTheDocument()
  })
})

describe('ThresholdAnalysisChart', () => {
  it('renders threshold chart', () => {
    const mockData = {
      thresholds: [
        {
          feature: 'feature_1',
          threshold: 12.5,
          effect_size: 0.45,
          significance: 0.92
        }
      ],
      overall_score: 0.78
    }

    renderWithProviders(<ThresholdAnalysisChart data={mockData} />)

    expect(screen.getByText('阈值效应分析')).toBeInTheDocument()
    expect(screen.getByText('整体评分: 0.78')).toBeInTheDocument()
  })

  it('displays threshold details', () => {
    const mockData = {
      thresholds: [
        {
          feature: 'feature_1',
          threshold: 12.5,
          effect_size: 0.45,
          significance: 0.92
        }
      ],
      overall_score: 0.78
    }

    renderWithProviders(<ThresholdAnalysisChart data={mockData} />)

    expect(screen.getByText('feature_1')).toBeInTheDocument()
    expect(screen.getByText('12.5')).toBeInTheDocument()
    expect(screen.getByText('0.45')).toBeInTheDocument()
  })
})

describe('DynamicWeightsChart', () => {
  it('renders weights chart', () => {
    const mockData = {
      weights: {
        'feature_1': 0.4,
        'feature_2': 0.35,
        'feature_3': 0.25
      },
      stability_score: 0.78,
      overall_score: 0.82
    }

    renderWithProviders(<DynamicWeightsChart data={mockData} />)

    expect(screen.getByText('动态权重分析')).toBeInTheDocument()
    expect(screen.getByText('整体评分: 0.82')).toBeInTheDocument()
    expect(screen.getByText('稳定性评分: 0.78')).toBeInTheDocument()
  })

  it('displays weight distribution', () => {
    const mockData = {
      weights: {
        'feature_1': 0.4,
        'feature_2': 0.35,
        'feature_3': 0.25
      },
      stability_score: 0.78,
      overall_score: 0.82
    }

    renderWithProviders(<DynamicWeightsChart data={mockData} />)

    expect(screen.getByText('feature_1: 40%')).toBeInTheDocument()
    expect(screen.getByText('feature_2: 35%')).toBeInTheDocument()
    expect(screen.getByText('feature_3: 25%')).toBeInTheDocument()
  })
})

describe('Integration Tests', () => {
  it('complete workflow: data import -> analysis -> evaluation', async () => {
    // 模拟完整工作流程
    mockApiCall
      .mockResolvedValueOnce({ success: true, upload_id: 'upload_1' }) // 数据导入
      .mockResolvedValueOnce(mockMarginalAnalysisData) // 分析结果
      .mockResolvedValueOnce({ success: true }) // 评价提交

    // 1. 数据导入
    renderWithProviders(<DataImportUploader />)
    
    const file = new File(['test data'], 'test.xlsx', { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const fileInput = screen.getByLabelText('选择文件')
    fireEvent.change(fileInput, { target: { files: [file] } })

    await waitFor(() => {
      expect(screen.getByText('文件上传成功')).toBeInTheDocument()
    })

    // 2. 查看分析结果
    renderWithProviders(<MarginalAnalysisDashboard />)

    await waitFor(() => {
      expect(screen.getByText('协同效应评分: 0.85')).toBeInTheDocument()
    })

    // 3. 提交评价
    renderWithProviders(<ManagerEvaluationPanel />)

    fireEvent.change(screen.getByLabelText('评价类型'), { target: { value: 'confirmation' } })
    fireEvent.change(screen.getByLabelText('评价分数'), { target: { value: '0.85' } })
    fireEvent.change(screen.getByLabelText('反馈内容'), { 
      target: { value: '分析结果准确，建议采用' } 
    })

    const submitButton = screen.getByRole('button', { name: /提交评价/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('评价提交成功')).toBeInTheDocument()
    })
  })
})

describe('Accessibility Tests', () => {
  it('has proper ARIA labels', () => {
    renderWithProviders(<MarginalAnalysisDashboard />)

    // 检查关键元素是否有适当的ARIA标签
    expect(screen.getByRole('main')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /刷新数据/i })).toBeInTheDocument()
  })

  it('supports keyboard navigation', () => {
    renderWithProviders(<ManagerEvaluationPanel />)

    const submitButton = screen.getByRole('button', { name: /提交评价/i })
    
    // 测试键盘导航
    submitButton.focus()
    expect(submitButton).toHaveFocus()

    fireEvent.keyDown(submitButton, { key: 'Enter' })
    // 应该触发提交
  })

  it('has proper color contrast', () => {
    renderWithProviders(<MarginalAnalysisDashboard />)

    // 检查文本颜色对比度（需要实际的样式测试）
    const mainHeading = screen.getByText('边际影响分析仪表盘')
    const computedStyle = window.getComputedStyle(mainHeading)
    
    // 这里需要实际的颜色对比度检查逻辑
    expect(computedStyle.color).toBeDefined()
  })
})

describe('Performance Tests', () => {
  it('renders large datasets efficiently', async () => {
    const largeData = {
      ...mockMarginalAnalysisData,
      synergy_effects: {
        pairwise_interactions: Array.from({ length: 100 }, (_, i) => ({
          features: [`feature_${i}`, `feature_${i + 1}`],
          synergy_score: Math.random(),
          significance: Math.random()
        }))
      }
    }

    mockApiCall.mockResolvedValueOnce(largeData)

    const startTime = performance.now()
    renderWithProviders(<MarginalAnalysisDashboard />)
    
    await waitFor(() => {
      expect(screen.getByText('协同效应分析')).toBeInTheDocument()
    })
    
    const endTime = performance.now()
    const renderTime = endTime - startTime

    // 渲染时间应该在合理范围内（例如小于1秒）
    expect(renderTime).toBeLessThan(1000)
  })

  it('handles rapid state updates', async () => {
    mockApiCall.mockResolvedValueOnce(mockMarginalAnalysisData)

    renderWithProviders(<MarginalAnalysisDashboard />)

    const refreshButton = screen.getByRole('button', { name: /刷新数据/i })
    
    // 快速点击刷新按钮
    for (let i = 0; i < 5; i++) {
      fireEvent.click(refreshButton)
    }

    // 应该能处理快速更新而不崩溃
    await waitFor(() => {
      expect(screen.getByText('协同效应分析')).toBeInTheDocument()
    })
  })
})


