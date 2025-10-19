<template>
  <div class="pft-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>产品特性管理</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建产品特性
          </el-button>
        </div>
      </template>
      
      <!-- 搜索和筛选 -->
      <div class="search-bar">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索产品特性名称"
          style="width: 300px; margin-right: 16px;"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="searchForm.module"
          placeholder="选择模块"
          style="width: 150px; margin-right: 16px;"
          clearable
        >
          <el-option label="核心功能" value="core" />
          <el-option label="用户体验" value="ux" />
          <el-option label="性能指标" value="performance" />
          <el-option label="安全特性" value="security" />
        </el-select>
        
        <el-button type="primary" @click="loadData">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        
        <el-button @click="resetSearch">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </div>
      
      <!-- 数据表格 -->
      <el-table 
        :data="pftList" 
        style="margin-top: 20px;"
        v-loading="loading"
        stripe
        border
      >
        <el-table-column prop="pft_id" label="ID" width="120" />
        <el-table-column prop="pft_name" label="名称" min-width="200" />
        <el-table-column prop="unit" label="单位" width="100" />
        <el-table-column prop="module" label="模块" width="120">
          <template #default="scope">
            <el-tag :type="getModuleType(scope.row.module)">
              {{ getModuleLabel(scope.row.module) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>
    
    <!-- 创建/编辑对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form 
        :model="form" 
        :rules="rules"
        ref="formRef"
        label-width="100px"
      >
        <el-form-item label="产品特性ID" prop="pft_id" v-if="!isEdit">
          <el-input v-model="form.pft_id" placeholder="请输入产品特性ID" />
        </el-form-item>
        
        <el-form-item label="名称" prop="pft_name">
          <el-input v-model="form.pft_name" placeholder="请输入产品特性名称" />
        </el-form-item>
        
        <el-form-item label="单位" prop="unit">
          <el-input v-model="form.unit" placeholder="请输入单位" />
        </el-form-item>
        
        <el-form-item label="模块" prop="module">
          <el-select v-model="form.module" placeholder="请选择模块" style="width: 100%;">
            <el-option label="核心功能" value="core" />
            <el-option label="用户体验" value="ux" />
            <el-option label="性能指标" value="performance" />
            <el-option label="安全特性" value="security" />
            <el-option label="兼容性" value="compatibility" />
            <el-option label="可扩展性" value="scalability" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, Edit, Delete } from '@element-plus/icons-vue'
import { 
  getPFTList, 
  createPFT, 
  updatePFT, 
  deletePFT 
} from '@/api/bmos/dimensions'

// 响应式数据
const pftList = ref([])
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()

// 搜索表单
const searchForm = reactive({
  keyword: '',
  module: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 表单数据
const form = reactive({
  pft_id: '',
  pft_name: '',
  unit: '',
  module: ''
})

// 表单验证规则
const rules = {
  pft_id: [
    { required: true, message: '请输入产品特性ID', trigger: 'blur' }
  ],
  pft_name: [
    { required: true, message: '请输入产品特性名称', trigger: 'blur' }
  ],
  module: [
    { required: true, message: '请选择模块', trigger: 'change' }
  ]
}

// 计算属性
const dialogTitle = computed(() => isEdit.value ? '编辑产品特性' : '新建产品特性')

// 方法
const loadData = async () => {
  try {
    loading.value = true
    
    const params = {
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size,
      ...(searchForm.module && { module: searchForm.module })
    }
    
    const response = await getPFTList(params)
    pftList.value = response.data || []
    pagination.total = response.total || 0
    
  } catch (error) {
    ElMessage.error('获取数据失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  searchForm.keyword = ''
  searchForm.module = ''
  pagination.page = 1
  loadData()
}

const handleCreate = () => {
  isEdit.value = false
  Object.assign(form, {
    pft_id: '',
    pft_name: '',
    unit: '',
    module: ''
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(form, {
    pft_id: row.pft_id,
    pft_name: row.pft_name,
    unit: row.unit,
    module: row.module
  })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (isEdit.value) {
      await updatePFT(form.pft_id, form)
      ElMessage.success('更新成功')
    } else {
      await createPFT(form)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    await loadData()
    
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    console.error(error)
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除产品特性"${row.pft_name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deletePFT(row.pft_id)
    ElMessage.success('删除成功')
    await loadData()
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(error)
    }
  }
}

const getModuleType = (module) => {
  const types = {
    'core': 'primary',
    'ux': 'success',
    'performance': 'warning',
    'security': 'danger',
    'compatibility': 'info',
    'scalability': 'success'
  }
  return types[module] || 'info'
}

const getModuleLabel = (module) => {
  const labels = {
    'core': '核心功能',
    'ux': '用户体验',
    'performance': '性能指标',
    'security': '安全特性',
    'compatibility': '兼容性',
    'scalability': '可扩展性'
  }
  return labels[module] || module
}

const formatDateTime = (dateTime) => {
  if (!dateTime) return ''
  return new Date(dateTime).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.pft-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-bar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>


