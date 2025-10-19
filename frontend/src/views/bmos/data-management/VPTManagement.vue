<template>
  <div class="vpt-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>价值主张管理</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建价值主张
          </el-button>
        </div>
      </template>
      
      <!-- 搜索和筛选 -->
      <div class="search-bar">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索价值主张名称"
          style="width: 300px; margin-right: 16px;"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="searchForm.category"
          placeholder="选择类别"
          style="width: 150px; margin-right: 16px;"
          clearable
        >
          <el-option label="品牌" value="brand" />
          <el-option label="产品" value="product" />
          <el-option label="服务" value="service" />
          <el-option label="交付" value="delivery" />
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
        :data="vptList" 
        style="margin-top: 20px;"
        v-loading="loading"
        stripe
        border
      >
        <el-table-column prop="vpt_id" label="ID" width="120" />
        <el-table-column prop="vpt_name" label="名称" min-width="200" />
        <el-table-column prop="category" label="类别" width="100">
          <template #default="scope">
            <el-tag :type="getCategoryType(scope.row.category)">
              {{ getCategoryLabel(scope.row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="owner" label="负责人" width="120" />
        <el-table-column prop="definition" label="定义" min-width="300" show-overflow-tooltip />
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
        <el-form-item label="价值主张ID" prop="vpt_id" v-if="!isEdit">
          <el-input v-model="form.vpt_id" placeholder="请输入价值主张ID" />
        </el-form-item>
        
        <el-form-item label="名称" prop="vpt_name">
          <el-input v-model="form.vpt_name" placeholder="请输入价值主张名称" />
        </el-form-item>
        
        <el-form-item label="类别" prop="category">
          <el-select v-model="form.category" placeholder="请选择类别" style="width: 100%;">
            <el-option label="品牌" value="brand" />
            <el-option label="产品" value="product" />
            <el-option label="服务" value="service" />
            <el-option label="交付" value="delivery" />
            <el-option label="价格" value="price" />
            <el-option label="质量" value="quality" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="负责人" prop="owner">
          <el-input v-model="form.owner" placeholder="请输入负责人" />
        </el-form-item>
        
        <el-form-item label="定义" prop="definition">
          <el-input 
            type="textarea" 
            v-model="form.definition" 
            placeholder="请输入价值主张定义"
            :rows="4"
          />
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
  getVPTList, 
  createVPT, 
  updateVPT, 
  deleteVPT 
} from '@/api/bmos/dimensions'

// 响应式数据
const vptList = ref([])
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()

// 搜索表单
const searchForm = reactive({
  keyword: '',
  category: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 表单数据
const form = reactive({
  vpt_id: '',
  vpt_name: '',
  category: '',
  owner: '',
  definition: ''
})

// 表单验证规则
const rules = {
  vpt_id: [
    { required: true, message: '请输入价值主张ID', trigger: 'blur' }
  ],
  vpt_name: [
    { required: true, message: '请输入价值主张名称', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择类别', trigger: 'change' }
  ]
}

// 计算属性
const dialogTitle = computed(() => isEdit.value ? '编辑价值主张' : '新建价值主张')

// 方法
const loadData = async () => {
  try {
    loading.value = true
    
    const params = {
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size,
      ...(searchForm.category && { category: searchForm.category })
    }
    
    const response = await getVPTList(params)
    vptList.value = response.data || []
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
  searchForm.category = ''
  pagination.page = 1
  loadData()
}

const handleCreate = () => {
  isEdit.value = false
  Object.assign(form, {
    vpt_id: '',
    vpt_name: '',
    category: '',
    owner: '',
    definition: ''
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(form, {
    vpt_id: row.vpt_id,
    vpt_name: row.vpt_name,
    category: row.category,
    owner: row.owner,
    definition: row.definition
  })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (isEdit.value) {
      await updateVPT(form.vpt_id, form)
      ElMessage.success('更新成功')
    } else {
      await createVPT(form)
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
      `确定要删除价值主张"${row.vpt_name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteVPT(row.vpt_id)
    ElMessage.success('删除成功')
    await loadData()
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(error)
    }
  }
}

const getCategoryType = (category) => {
  const types = {
    'brand': 'primary',
    'product': 'success',
    'service': 'warning',
    'delivery': 'info',
    'price': 'danger',
    'quality': 'success'
  }
  return types[category] || 'info'
}

const getCategoryLabel = (category) => {
  const labels = {
    'brand': '品牌',
    'product': '产品',
    'service': '服务',
    'delivery': '交付',
    'price': '价格',
    'quality': '质量'
  }
  return labels[category] || category
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
.vpt-management {
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


