<template>
  <div class="dimensions-page">
    <el-card>
      <template #header>
        <div class="page-header">
          <h2>维度表管理</h2>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            添加维度
          </el-button>
        </div>
      </template>

      <!-- 维度表列表 -->
      <el-table :data="dimensions" v-loading="loading" border>
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

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑维度表' : '添加维度表'"
      width="600px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="表名" prop="table_name">
          <el-input v-model="form.table_name" placeholder="请输入表名" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="字段配置">
          <div class="field-config">
            <el-button type="primary" size="small" @click="addField">添加字段</el-button>
            <el-table :data="form.fields" style="margin-top: 10px;">
              <el-table-column prop="name" label="字段名" width="150">
                <template #default="{ row, $index }">
                  <el-input v-model="row.name" size="small" />
                </template>
              </el-table-column>
              <el-table-column prop="type" label="类型" width="120">
                <template #default="{ row, $index }">
                  <el-select v-model="row.type" size="small">
                    <el-option label="String" value="String" />
                    <el-option label="Int32" value="Int32" />
                    <el-option label="Float32" value="Float32" />
                    <el-option label="DateTime" value="DateTime" />
                    <el-option label="Date" value="Date" />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column prop="comment" label="注释">
                <template #default="{ row, $index }">
                  <el-input v-model="row.comment" size="small" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80">
                <template #default="{ row, $index }">
                  <el-button size="small" type="danger" @click="removeField($index)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>

    <!-- 表详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="表详情"
      width="800px"
    >
      <div v-if="selectedTable">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="表名">{{ selectedTable.table_name }}</el-descriptions-item>
          <el-descriptions-item label="描述">{{ selectedTable.description }}</el-descriptions-item>
          <el-descriptions-item label="数据量">{{ selectedTable.row_count }}</el-descriptions-item>
          <el-descriptions-item label="最后更新">{{ formatTime(selectedTable.last_updated) }}</el-descriptions-item>
        </el-descriptions>

        <h4 style="margin-top: 20px;">表结构</h4>
        <el-table :data="selectedTable.structure" border>
          <el-table-column prop="name" label="字段名" />
          <el-table-column prop="type" label="类型" />
          <el-table-column prop="comment" label="注释" />
        </el-table>

        <h4 style="margin-top: 20px;">示例数据</h4>
        <el-table :data="selectedTable.sample_data" border>
          <el-table-column
            v-for="field in selectedTable.structure"
            :key="field.name"
            :prop="field.name"
            :label="field.name"
          />
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

// 响应式数据
const loading = ref(false)
const dimensions = ref([])
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const isEdit = ref(false)
const selectedTable = ref(null)
const formRef = ref()

// 表单数据
const form = reactive({
  table_name: '',
  description: '',
  fields: []
})

// 表单验证规则
const rules = {
  table_name: [
    { required: true, message: '请输入表名', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入描述', trigger: 'blur' }
  ]
}

// 模拟维度表数据
const mockDimensions = [
  {
    table_name: 'dim_vpt',
    description: '价值主张维度表',
    row_count: 5,
    last_updated: new Date(),
    structure: [
      { name: 'vpt_id', type: 'String', comment: '价值主张ID' },
      { name: 'vpt_name', type: 'String', comment: '价值主张名称' },
      { name: 'vpt_category', type: 'String', comment: '价值主张类别' },
      { name: 'create_time', type: 'DateTime', comment: '创建时间' }
    ],
    sample_data: [
      { vpt_id: 'vpt001', vpt_name: '高质量产品', vpt_category: 'quality', create_time: '2024-01-01 10:00:00' },
      { vpt_id: 'vpt002', vpt_name: '快速交付', vpt_category: 'speed', create_time: '2024-01-01 10:00:00' }
    ]
  },
  {
    table_name: 'dim_customer',
    description: '客户维度表',
    row_count: 5,
    last_updated: new Date(),
    structure: [
      { name: 'customer_id', type: 'String', comment: '客户ID' },
      { name: 'first_media_id', type: 'String', comment: '首次接触媒体ID' },
      { name: 'reg_date', type: 'Date', comment: '注册日期' }
    ],
    sample_data: [
      { customer_id: 'cust001', first_media_id: 'douyin', reg_date: '2024-01-01' },
      { customer_id: 'cust002', first_media_id: 'xiaohongshu', reg_date: '2024-01-02' }
    ]
  }
]

// 方法
const loadDimensions = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    dimensions.value = mockDimensions
  } catch (error) {
    ElMessage.error('加载维度表失败')
  } finally {
    loading.value = false
  }
}

const showAddDialog = () => {
  isEdit.value = false
  form.table_name = ''
  form.description = ''
  form.fields = []
  dialogVisible.value = true
}

const editTable = (row) => {
  isEdit.value = true
  form.table_name = row.table_name
  form.description = row.description
  form.fields = [...row.structure]
  dialogVisible.value = true
}

const viewTable = (row) => {
  selectedTable.value = row
  detailDialogVisible.value = true
}

const deleteTable = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这个维度表吗？', '确认删除', {
      type: 'warning'
    })
    ElMessage.success('删除成功')
    loadDimensions()
  } catch {
    // 用户取消删除
  }
}

const addField = () => {
  form.fields.push({
    name: '',
    type: 'String',
    comment: ''
  })
}

const removeField = (index) => {
  form.fields.splice(index, 1)
}

const submitForm = async () => {
  try {
    await formRef.value.validate()
    // 模拟提交
    ElMessage.success(isEdit.value ? '更新成功' : '添加成功')
    dialogVisible.value = false
    loadDimensions()
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

onMounted(() => {
  loadDimensions()
})
</script>

<style scoped>
.dimensions-page {
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

.field-config {
  width: 100%;
}
</style>

