<template>
  <div class="contract-management">
    <div class="page-header">
      <h1>合同管理</h1>
      <el-button type="primary">
        <el-icon><Plus /></el-icon>
        新增合同
      </el-button>
    </div>
    
    <el-card>
      <div class="coming-soon">
        <el-icon size="64"><Document /></el-icon>
        <h2>合同管理功能开发中...</h2>
        <p>该功能正在开发中，敬请期待</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { Plus, Document } from '@element-plus/icons-vue'
</script>

<style scoped>
.contract-management {
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

.coming-soon {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.coming-soon h2 {
  margin: 20px 0 10px 0;
  color: #2c3e50;
}

.coming-soon p {
  margin: 0;
  font-size: 16px;
}
</style>
