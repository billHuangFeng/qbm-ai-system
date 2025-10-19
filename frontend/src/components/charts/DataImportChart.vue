<template>
  <div class="data-import-chart">
    <div class="import-header">
      <h3>数据导入向导</h3>
      <p>选择要导入的数据类型和文件</p>
    </div>
    
    <el-steps :active="currentStep" finish-status="success" align-center>
      <el-step title="选择数据类型" description="选择要导入的数据类型"></el-step>
      <el-step title="上传文件" description="上传数据文件"></el-step>
      <el-step title="数据预览" description="预览和验证数据"></el-step>
      <el-step title="导入完成" description="完成数据导入"></el-step>
    </el-steps>
    
    <div class="step-content">
      <!-- 步骤1：选择数据类型 -->
      <div v-if="currentStep === 0" class="step-panel">
        <h4>选择数据类型</h4>
        <el-radio-group v-model="selectedDataType" @change="handleDataTypeChange">
          <el-radio label="customers">客户数据</el-radio>
          <el-radio label="products">产品数据</el-radio>
          <el-radio label="orders">订单数据</el-radio>
          <el-radio label="financials">财务数据</el-radio>
          <el-radio label="contracts">合同数据</el-radio>
        </el-radio-group>
        
        <div class="data-type-info">
          <h5>支持的文件格式：</h5>
          <ul>
            <li>CSV文件 (.csv)</li>
            <li>Excel文件 (.xlsx, .xls)</li>
            <li>JSON文件 (.json)</li>
          </ul>
        </div>
      </div>
      
      <!-- 步骤2：上传文件 -->
      <div v-if="currentStep === 1" class="step-panel">
        <h4>上传数据文件</h4>
        <el-upload
          ref="uploadRef"
          class="upload-demo"
          drag
          :auto-upload="false"
          :on-change="handleFileChange"
          :before-upload="beforeUpload"
          accept=".csv,.xlsx,.xls,.json"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              只能上传 csv/xlsx/xls/json 文件，且不超过 10MB
            </div>
          </template>
        </el-upload>
        
        <div v-if="selectedFile" class="file-info">
          <h5>已选择文件：</h5>
          <p><strong>文件名：</strong>{{ selectedFile.name }}</p>
          <p><strong>文件大小：</strong>{{ formatFileSize(selectedFile.size) }}</p>
          <p><strong>文件类型：</strong>{{ selectedFile.type || '未知' }}</p>
        </div>
      </div>
      
      <!-- 步骤3：数据预览 -->
      <div v-if="currentStep === 2" class="step-panel">
        <h4>数据预览</h4>
        <div v-if="previewData.length > 0" class="preview-table">
          <el-table :data="previewData.slice(0, 10)" style="width: 100%" max-height="400">
            <el-table-column 
              v-for="(column, index) in previewColumns" 
              :key="index"
              :prop="column"
              :label="column"
              :width="150"
            />
          </el-table>
          <p class="preview-note">显示前10行数据，共{{ previewData.length }}行</p>
        </div>
        
        <div class="import-options">
          <h5>导入选项：</h5>
          <el-checkbox v-model="importOptions.skipHeader">跳过标题行</el-checkbox>
          <el-checkbox v-model="importOptions.updateExisting">更新已存在记录</el-checkbox>
          <el-checkbox v-model="importOptions.validateData">验证数据格式</el-checkbox>
        </div>
      </div>
      
      <!-- 步骤4：导入完成 -->
      <div v-if="currentStep === 3" class="step-panel">
        <div class="import-result">
          <el-icon v-if="importSuccess" class="success-icon" size="64"><CircleCheck /></el-icon>
          <el-icon v-else class="error-icon" size="64"><CircleClose /></el-icon>
          
          <h4>{{ importSuccess ? '导入成功！' : '导入失败！' }}</h4>
          
          <div v-if="importReport" class="import-report">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="总记录数">{{ importReport.total_records }}</el-descriptions-item>
              <el-descriptions-item label="成功记录数">{{ importReport.successful_records }}</el-descriptions-item>
              <el-descriptions-item label="失败记录数">{{ importReport.failed_records }}</el-descriptions-item>
              <el-descriptions-item label="成功率">
                {{ ((importReport.successful_records / importReport.total_records) * 100).toFixed(1) }}%
              </el-descriptions-item>
            </el-descriptions>
          </div>
          
          <div v-if="importErrors.length > 0" class="import-errors">
            <h5>错误信息：</h5>
            <ul>
              <li v-for="(error, index) in importErrors.slice(0, 5)" :key="index">{{ error }}</li>
            </ul>
            <p v-if="importErrors.length > 5">... 还有{{ importErrors.length - 5 }}个错误</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="step-actions">
      <el-button v-if="currentStep > 0" @click="prevStep">上一步</el-button>
      <el-button 
        v-if="currentStep < 3" 
        type="primary" 
        @click="nextStep"
        :disabled="!canProceed"
      >
        下一步
      </el-button>
      <el-button 
        v-if="currentStep === 2" 
        type="success" 
        @click="startImport"
        :loading="importing"
      >
        开始导入
      </el-button>
      <el-button v-if="currentStep === 3" @click="resetImport">重新导入</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, CircleCheck, CircleClose } from '@element-plus/icons-vue'

// 定义事件
const emit = defineEmits(['import-complete'])

// 响应式数据
const currentStep = ref(0)
const selectedDataType = ref('customers')
const selectedFile = ref(null)
const previewData = ref([])
const previewColumns = ref([])
const importing = ref(false)
const importSuccess = ref(false)
const importReport = ref(null)
const importErrors = ref([])

const importOptions = ref({
  skipHeader: true,
  updateExisting: false,
  validateData: true
})

// 计算属性
const canProceed = computed(() => {
  switch (currentStep.value) {
    case 0:
      return selectedDataType.value !== ''
    case 1:
      return selectedFile.value !== null
    case 2:
      return previewData.value.length > 0
    default:
      return true
  }
})

// 方法
const handleDataTypeChange = (value) => {
  console.log('选择数据类型:', value)
}

const handleFileChange = (file) => {
  selectedFile.value = file.raw
  console.log('选择文件:', file.name)
}

const beforeUpload = (file) => {
  const isValidType = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/json'].includes(file.type)
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isValidType) {
    ElMessage.error('只能上传 CSV、Excel 或 JSON 文件!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB!')
    return false
  }
  return false // 阻止自动上传
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const nextStep = () => {
  if (currentStep.value === 1 && selectedFile.value) {
    // 模拟数据预览
    generatePreviewData()
  }
  currentStep.value++
}

const prevStep = () => {
  currentStep.value--
}

const generatePreviewData = () => {
  // 模拟生成预览数据
  const mockData = {
    customers: [
      { id: 1, name: '张三', email: 'zhangsan@example.com', phone: '13800138001', company: 'ABC公司' },
      { id: 2, name: '李四', email: 'lisi@example.com', phone: '13800138002', company: 'XYZ公司' },
      { id: 3, name: '王五', email: 'wangwu@example.com', phone: '13800138003', company: 'DEF公司' }
    ],
    products: [
      { id: 1, name: '产品A', price: 100, category: '软件', description: '软件产品A' },
      { id: 2, name: '产品B', price: 200, category: '硬件', description: '硬件产品B' },
      { id: 3, name: '产品C', price: 150, category: '服务', description: '服务产品C' }
    ],
    orders: [
      { id: 1, customer_id: 1, product_id: 1, quantity: 2, total_amount: 200, order_date: '2024-01-01' },
      { id: 2, customer_id: 2, product_id: 2, quantity: 1, total_amount: 200, order_date: '2024-01-02' },
      { id: 3, customer_id: 3, product_id: 3, quantity: 3, total_amount: 450, order_date: '2024-01-03' }
    ],
    financials: [
      { id: 1, type: '收入', amount: 10000, description: '产品销售', date: '2024-01-01' },
      { id: 2, type: '支出', amount: 5000, description: '运营成本', date: '2024-01-02' },
      { id: 3, type: '收入', amount: 8000, description: '服务收入', date: '2024-01-03' }
    ],
    contracts: [
      { id: 1, customer_id: 1, contract_number: 'C001', start_date: '2024-01-01', end_date: '2024-12-31', amount: 50000 },
      { id: 2, customer_id: 2, contract_number: 'C002', start_date: '2024-02-01', end_date: '2024-11-30', amount: 30000 },
      { id: 3, customer_id: 3, contract_number: 'C003', start_date: '2024-03-01', end_date: '2024-10-31', amount: 40000 }
    ]
  }
  
  previewData.value = mockData[selectedDataType.value] || []
  previewColumns.value = previewData.value.length > 0 ? Object.keys(previewData.value[0]) : []
}

const startImport = async () => {
  importing.value = true
  
  try {
    // 模拟导入过程
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    // 模拟导入结果
    const success = Math.random() > 0.2 // 80% 成功率
    
    if (success) {
      importSuccess.value = true
      importReport.value = {
        total_records: previewData.value.length,
        successful_records: Math.floor(previewData.value.length * 0.95),
        failed_records: Math.floor(previewData.value.length * 0.05)
      }
      importErrors.value = []
      ElMessage.success('数据导入成功！')
    } else {
      importSuccess.value = false
      importReport.value = {
        total_records: previewData.value.length,
        successful_records: Math.floor(previewData.value.length * 0.7),
        failed_records: Math.floor(previewData.value.length * 0.3)
      }
      importErrors.value = [
        '第5行：邮箱格式不正确',
        '第12行：电话号码格式不正确',
        '第18行：必填字段缺失'
      ]
      ElMessage.error('数据导入失败，请检查错误信息！')
    }
    
    currentStep.value = 3
    
    // 发送导入完成事件
    emit('import-complete', {
      success: importSuccess.value,
      import_report: importReport.value,
      message: importSuccess.value ? '导入成功' : '导入失败'
    })
    
  } catch (error) {
    importSuccess.value = false
    importErrors.value = ['导入过程中发生错误：' + error.message]
    ElMessage.error('导入过程中发生错误！')
  } finally {
    importing.value = false
  }
}

const resetImport = () => {
  currentStep.value = 0
  selectedDataType.value = 'customers'
  selectedFile.value = null
  previewData.value = []
  previewColumns.value = []
  importSuccess.value = false
  importReport.value = null
  importErrors.value = []
  importing.value = false
}
</script>

<style scoped>
.data-import-chart {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.import-header {
  text-align: center;
  margin-bottom: 30px;
}

.import-header h3 {
  color: #2c3e50;
  margin: 0 0 10px 0;
}

.import-header p {
  color: #7f8c8d;
  margin: 0;
}

.step-content {
  margin: 30px 0;
  min-height: 400px;
}

.step-panel {
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.step-panel h4 {
  color: #2c3e50;
  margin: 0 0 20px 0;
}

.data-type-info {
  margin-top: 20px;
  padding: 15px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.data-type-info h5 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.data-type-info ul {
  margin: 0;
  padding-left: 20px;
}

.upload-demo {
  margin: 20px 0;
}

.file-info {
  margin-top: 20px;
  padding: 15px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.file-info h5 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.file-info p {
  margin: 5px 0;
  color: #666;
}

.preview-table {
  margin: 20px 0;
}

.preview-note {
  margin: 10px 0 0 0;
  color: #666;
  font-size: 14px;
}

.import-options {
  margin-top: 20px;
  padding: 15px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.import-options h5 {
  margin: 0 0 15px 0;
  color: #2c3e50;
}

.import-result {
  text-align: center;
  padding: 40px 20px;
}

.success-icon {
  color: #67c23a;
  margin-bottom: 20px;
}

.error-icon {
  color: #f56c6c;
  margin-bottom: 20px;
}

.import-result h4 {
  margin: 0 0 30px 0;
  color: #2c3e50;
}

.import-report {
  margin: 20px 0;
  text-align: left;
}

.import-errors {
  margin: 20px 0;
  text-align: left;
}

.import-errors h5 {
  color: #f56c6c;
  margin: 0 0 10px 0;
}

.import-errors ul {
  margin: 0;
  padding-left: 20px;
  color: #f56c6c;
}

.step-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 30px;
}
</style>