<template>
  <div class="help-container">
    <div class="page-header">
      <h1>帮助中心</h1>
      <p>QBM AI System 使用指南和常见问题解答</p>
    </div>
    
    <el-row :gutter="20">
      <!-- 快速开始 -->
      <el-col :span="8">
        <el-card class="help-card">
          <template #header>
            <div class="card-header">
              <el-icon><Guide /></el-icon>
              <span>快速开始</span>
            </div>
          </template>
          <div class="help-content">
            <h4>新用户指南</h4>
            <ul>
              <li><router-link to="/help/getting-started">系统介绍</router-link></li>
              <li><router-link to="/help/first-login">首次登录</router-link></li>
              <li><router-link to="/help/data-import">数据导入</router-link></li>
              <li><router-link to="/help/basic-analysis">基础分析</router-link></li>
            </ul>
          </div>
        </el-card>
      </el-col>
      
      <!-- 功能指南 -->
      <el-col :span="8">
        <el-card class="help-card">
          <template #header>
            <div class="card-header">
              <el-icon><Document /></el-icon>
              <span>功能指南</span>
            </div>
          </template>
          <div class="help-content">
            <h4>详细功能说明</h4>
            <ul>
              <li><router-link to="/help/customer-analysis">客户分析</router-link></li>
              <li><router-link to="/help/product-analysis">产品分析</router-link></li>
              <li><router-link to="/help/financial-analysis">财务分析</router-link></li>
              <li><router-link to="/help/market-analysis">市场分析</router-link></li>
            </ul>
          </div>
        </el-card>
      </el-col>
      
      <!-- 常见问题 -->
      <el-col :span="8">
        <el-card class="help-card">
          <template #header>
            <div class="card-header">
              <el-icon><QuestionFilled /></el-icon>
              <span>常见问题</span>
            </div>
          </template>
          <div class="help-content">
            <h4>FAQ</h4>
            <ul>
              <li><router-link to="/help/faq-login">登录问题</router-link></li>
              <li><router-link to="/help/faq-data">数据问题</router-link></li>
              <li><router-link to="/help/faq-analysis">分析问题</router-link></li>
              <li><router-link to="/help/faq-system">系统问题</router-link></li>
            </ul>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 搜索功能 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <el-icon><Search /></el-icon>
          <span>搜索帮助</span>
        </div>
      </template>
      <div class="search-section">
        <el-input
          v-model="searchQuery"
          placeholder="输入关键词搜索帮助内容..."
          @keyup.enter="searchHelp"
        >
          <template #append>
            <el-button @click="searchHelp">
              <el-icon><Search /></el-icon>
            </el-button>
          </template>
        </el-input>
        
        <div v-if="searchResults.length > 0" class="search-results">
          <h4>搜索结果</h4>
          <div v-for="result in searchResults" :key="result.id" class="search-result-item">
            <h5>{{ result.title }}</h5>
            <p>{{ result.content }}</p>
            <el-button type="text" @click="viewResult(result)">查看详情</el-button>
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 联系支持 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <el-icon><Service /></el-icon>
          <span>联系支持</span>
        </div>
      </template>
      <div class="support-section">
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="support-item">
              <el-icon class="support-icon"><Message /></el-icon>
              <h4>在线客服</h4>
              <p>工作时间：9:00-18:00</p>
              <el-button type="primary" @click="openChat">开始对话</el-button>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="support-item">
              <el-icon class="support-icon"><Phone /></el-icon>
              <h4>电话支持</h4>
              <p>400-123-4567</p>
              <el-button @click="makeCall">拨打电话</el-button>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="support-item">
              <el-icon class="support-icon"><Message /></el-icon>
              <h4>邮件支持</h4>
              <p>support@qbm-ai.com</p>
              <el-button @click="sendEmail">发送邮件</el-button>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>
    
    <!-- 系统信息 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <el-icon><InfoFilled /></el-icon>
          <span>系统信息</span>
        </div>
      </template>
      <div class="system-info">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="系统版本">v1.0.0</el-descriptions-item>
          <el-descriptions-item label="构建时间">2024-01-15</el-descriptions-item>
          <el-descriptions-item label="数据库版本">MySQL 8.0</el-descriptions-item>
          <el-descriptions-item label="缓存版本">Redis 7.0</el-descriptions-item>
          <el-descriptions-item label="前端框架">Vue.js 3.3.8</el-descriptions-item>
          <el-descriptions-item label="后端框架">FastAPI 0.104.1</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Guide, Document, QuestionFilled, Search, Service, 
  Message, Phone, InfoFilled 
} from '@element-plus/icons-vue'

const searchQuery = ref('')
const searchResults = ref([])

// 模拟搜索数据
const helpData = [
  {
    id: 1,
    title: '如何导入客户数据',
    content: '客户数据导入功能位于数据导入页面，支持CSV、Excel、JSON格式...',
    category: 'data-import'
  },
  {
    id: 2,
    title: '客户分析功能说明',
    content: '客户分析模块提供客户细分、流失预测、生命周期价值分析...',
    category: 'customer-analysis'
  },
  {
    id: 3,
    title: '登录失败问题解决',
    content: '如果遇到登录失败问题，请检查用户名密码是否正确...',
    category: 'faq-login'
  }
]

// 搜索帮助内容
const searchHelp = () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }
  
  const query = searchQuery.value.toLowerCase()
  searchResults.value = helpData.filter(item => 
    item.title.toLowerCase().includes(query) || 
    item.content.toLowerCase().includes(query)
  )
  
  if (searchResults.value.length === 0) {
    ElMessage.info('未找到相关帮助内容')
  }
}

// 查看搜索结果详情
const viewResult = (result) => {
  ElMessage.info(`查看: ${result.title}`)
  // 这里可以跳转到具体的帮助页面
}

// 打开在线客服
const openChat = () => {
  ElMessage.info('在线客服功能开发中...')
}

// 拨打电话
const makeCall = () => {
  ElMessage.info('电话支持: 400-123-4567')
}

// 发送邮件
const sendEmail = () => {
  ElMessage.info('邮件支持: support@qbm-ai.com')
}
</script>

<style scoped>
.help-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  color: #2c3e50;
  font-size: 28px;
  margin: 0 0 10px 0;
}

.page-header p {
  color: #666;
  font-size: 16px;
  margin: 0;
}

.help-card {
  height: 300px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.card-header .el-icon {
  font-size: 18px;
  color: #409eff;
}

.help-content h4 {
  color: #2c3e50;
  margin: 0 0 15px 0;
  font-size: 16px;
}

.help-content ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.help-content li {
  margin-bottom: 8px;
}

.help-content a {
  color: #409eff;
  text-decoration: none;
  font-size: 14px;
}

.help-content a:hover {
  text-decoration: underline;
}

.search-section {
  padding: 20px 0;
}

.search-results {
  margin-top: 20px;
}

.search-results h4 {
  color: #2c3e50;
  margin: 0 0 15px 0;
}

.search-result-item {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  margin-bottom: 10px;
}

.search-result-item h5 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 16px;
}

.search-result-item p {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.support-section {
  padding: 20px 0;
}

.support-item {
  text-align: center;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
  height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.support-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 15px;
}

.support-item h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 18px;
}

.support-item p {
  margin: 0 0 15px 0;
  color: #666;
  font-size: 14px;
}

.system-info {
  padding: 20px 0;
}
</style>


