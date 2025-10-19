<template>
  <div class="facts-page">
    <el-card>
      <template #header>
        <div class="page-header">
          <h2>事实表管理</h2>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            添加事实表
          </el-button>
        </div>
      </template>

      <el-table :data="facts" v-loading="loading" border>
        <el-table-column prop="table_name" label="表名" width="200" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="row_count" label="数据量" width="120">
          <template #default="{ row }">
            <el-tag type="info">{{ row.row_count }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_updated" label="最后更新" width="180">
          <template #default="{ row }">
            {{ formatTime(row.last_updated) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="viewTable(row)">查看</el-button>
            <el-button size="small" type="primary" @click="editTable(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteTable(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const loading = ref(false)
const facts = ref([])

const mockFacts = [
  {
    table_name: 'fact_order',
    description: '订单事实表',
    row_count: 0,
    last_updated: new Date()
  },
  {
    table_name: 'fact_voice',
    description: '客户声音事实表',
    row_count: 0,
    last_updated: new Date()
  }
]

const loadFacts = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    facts.value = mockFacts
  } catch (error) {
    ElMessage.error('加载事实表失败')
  } finally {
    loading.value = false
  }
}

const showAddDialog = () => {
  ElMessage.info('添加事实表功能开发中')
}

const editTable = (row) => {
  ElMessage.info('编辑事实表功能开发中')
}

const viewTable = (row) => {
  ElMessage.info('查看事实表功能开发中')
}

const deleteTable = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这个事实表吗？', '确认删除', {
      type: 'warning'
    })
    ElMessage.success('删除成功')
    loadFacts()
  } catch {
    // 用户取消删除
  }
}

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

onMounted(() => {
  loadFacts()
})
</script>

<style scoped>
.facts-page {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}
</style>

