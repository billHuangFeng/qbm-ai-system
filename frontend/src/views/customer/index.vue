<template>
  <div class="customer-management">
    <div class="page-header">
      <h1>客户管理</h1>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新增客户
      </el-button>
    </div>
    
    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="搜索">
          <el-input
            v-model="searchForm.keyword"
            placeholder="请输入客户名称、编码或联系人"
            clearable
            @keyup.enter="handleSearch"
            style="width: 300px"
          >
            <template #append>
              <el-button @click="handleSearch">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="行业">
          <el-select v-model="searchForm.industry" placeholder="选择行业" clearable>
            <el-option label="信息技术" value="信息技术" />
            <el-option label="制造业" value="制造业" />
            <el-option label="互联网" value="互联网" />
            <el-option label="金融" value="金融" />
            <el-option label="教育" value="教育" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="客户类型">
          <el-select v-model="searchForm.customer_type" placeholder="选择类型" clearable>
            <el-option label="企业客户" value="企业客户" />
            <el-option label="个人客户" value="个人客户" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="VIP客户">
          <el-select v-model="searchForm.is_vip" placeholder="选择VIP状态" clearable>
            <el-option label="是" :value="true" />
            <el-option label="否" :value="false" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 客户列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="customerList"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="customer_code" label="客户编码" width="120" />
        
        <el-table-column prop="customer_name" label="客户名称" min-width="200">
          <template #default="{ row }">
            <div class="customer-name">
              <span class="name">{{ row.customer_name }}</span>
              <el-tag v-if="row.is_vip" type="warning" size="small">VIP</el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="customer_type" label="客户类型" width="100" />
        
        <el-table-column prop="industry" label="行业" width="120" />
        
        <el-table-column prop="contact_person" label="联系人" width="120" />
        
        <el-table-column prop="phone" label="联系电话" width="140" />
        
        <el-table-column prop="customer_value_score" label="价值评分" width="100">
          <template #default="{ row }">
            <el-rate
              v-model="row.customer_value_score"
              disabled
              show-score
              text-color="#ff9900"
              score-template="{value}"
            />
          </template>
        </el-table-column>
        
        <el-table-column prop="customer_lifetime_value" label="生命周期价值" width="140">
          <template #default="{ row }">
            <span v-if="row.customer_lifetime_value">
              ¥{{ formatNumber(row.customer_lifetime_value) }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '活跃' : '非活跃' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button type="warning" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 批量操作 -->
    <div v-if="selectedCustomers.length > 0" class="batch-actions">
      <el-card>
        <div class="batch-content">
          <span>已选择 {{ selectedCustomers.length }} 个客户</span>
          <div class="batch-buttons">
            <el-button type="primary" @click="handleBatchExport">导出</el-button>
            <el-button type="warning" @click="handleBatchSetVip">设为VIP</el-button>
            <el-button type="danger" @click="handleBatchDelete">批量删除</el-button>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { getCustomers, deleteCustomer } from '@/api/customer'

const router = useRouter()

// 加载状态
const loading = ref(false)

// 搜索表单
const searchForm = reactive({
  keyword: '',
  industry: '',
  customer_type: '',
  is_vip: null
})

// 分页信息
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 客户列表
const customerList = ref([])

// 选中的客户
const selectedCustomers = ref([])

// 格式化数字
const formatNumber = (num) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toLocaleString()
}

// 获取客户列表
const fetchCustomers = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...searchForm
    }
    
    // 移除空值
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null) {
        delete params[key]
      }
    })
    
    const response = await getCustomers(params)
    customerList.value = response.data.items || []
    pagination.total = response.data.total || 0
  } catch (error) {
    console.error('获取客户列表失败:', error)
    ElMessage.error('获取客户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchCustomers()
}

// 重置搜索
const handleReset = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key] = key === 'is_vip' ? null : ''
  })
  pagination.page = 1
  fetchCustomers()
}

// 分页大小改变
const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  fetchCustomers()
}

// 当前页改变
const handleCurrentChange = (page) => {
  pagination.page = page
  fetchCustomers()
}

// 选择改变
const handleSelectionChange = (selection) => {
  selectedCustomers.value = selection
}

// 新增客户
const handleCreate = () => {
  router.push('/customers/create')
}

// 查看客户
const handleView = (row) => {
  router.push(`/customers/${row.id}`)
}

// 编辑客户
const handleEdit = (row) => {
  router.push(`/customers/${row.id}/edit`)
}

// 删除客户
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除客户"${row.customer_name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteCustomer(row.id)
    ElMessage.success('删除成功')
    fetchCustomers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除客户失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 批量导出
const handleBatchExport = () => {
  ElMessage.info('批量导出功能开发中...')
}

// 批量设为VIP
const handleBatchSetVip = () => {
  ElMessage.info('批量设置VIP功能开发中...')
}

// 批量删除
const handleBatchDelete = () => {
  ElMessage.info('批量删除功能开发中...')
}

// 组件挂载时获取数据
onMounted(() => {
  fetchCustomers()
})
</script>

<style scoped>
.customer-management {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  color: #2c3e50;
  font-size: 24px;
  margin: 0;
}

.search-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.customer-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.customer-name .name {
  font-weight: 500;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.batch-actions {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
}

.batch-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.batch-buttons {
  display: flex;
  gap: 10px;
}
</style>
