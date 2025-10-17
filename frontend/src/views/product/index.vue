<template>
  <div class="product-management">
    <div class="page-header">
      <h1>产品管理</h1>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新增产品
      </el-button>
    </div>
    
    <!-- 产品列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="productList"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="product_code" label="产品编码" width="120" />
        <el-table-column prop="product_name" label="产品名称" min-width="200" />
        <el-table-column prop="product_category" label="产品类别" width="120" />
        <el-table-column prop="base_price" label="基础价格" width="120">
          <template #default="{ row }">
            <span v-if="row.base_price">¥{{ formatNumber(row.base_price) }}</span>
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
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getProducts } from '@/api/product'

const router = useRouter()
const loading = ref(false)
const productList = ref([])

const formatNumber = (num) => {
  return num.toLocaleString()
}

const fetchProducts = async () => {
  loading.value = true
  try {
    const response = await getProducts({ page: 1, size: 20 })
    productList.value = response.data.items || []
  } catch (error) {
    ElMessage.error('获取产品列表失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  router.push('/products/create')
}

const handleView = (row) => {
  ElMessage.info('查看产品功能开发中...')
}

const handleEdit = (row) => {
  router.push(`/products/${row.id}/edit`)
}

const handleDelete = (row) => {
  ElMessage.info('删除产品功能开发中...')
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.product-management {
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

.table-card {
  margin-bottom: 20px;
}
</style>
