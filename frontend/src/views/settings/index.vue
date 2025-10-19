<template>
  <div class="settings-container">
    <div class="page-header">
      <h1>系统设置</h1>
    </div>
    
    <el-tabs v-model="activeTab" type="border-card">
      <!-- 基本设置 -->
      <el-tab-pane label="基本设置" name="basic">
        <el-card>
          <template #header>
            <span>基本配置</span>
          </template>
          
          <el-form :model="basicSettings" label-width="120px">
            <el-form-item label="系统名称">
              <el-input v-model="basicSettings.systemName" placeholder="请输入系统名称"></el-input>
            </el-form-item>
            
            <el-form-item label="系统描述">
              <el-input 
                type="textarea" 
                v-model="basicSettings.systemDescription" 
                placeholder="请输入系统描述"
                :rows="3"
              ></el-input>
            </el-form-item>
            
            <el-form-item label="时区设置">
              <el-select v-model="basicSettings.timezone" placeholder="请选择时区">
                <el-option label="北京时间 (UTC+8)" value="Asia/Shanghai"></el-option>
                <el-option label="东京时间 (UTC+9)" value="Asia/Tokyo"></el-option>
                <el-option label="纽约时间 (UTC-5)" value="America/New_York"></el-option>
                <el-option label="伦敦时间 (UTC+0)" value="Europe/London"></el-option>
              </el-select>
            </el-form-item>
            
            <el-form-item label="语言设置">
              <el-select v-model="basicSettings.language" placeholder="请选择语言">
                <el-option label="简体中文" value="zh-CN"></el-option>
                <el-option label="English" value="en-US"></el-option>
                <el-option label="日本語" value="ja-JP"></el-option>
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveBasicSettings">保存设置</el-button>
              <el-button @click="resetBasicSettings">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
      
      <!-- 安全设置 -->
      <el-tab-pane label="安全设置" name="security">
        <el-card>
          <template #header>
            <span>安全配置</span>
          </template>
          
          <el-form :model="securitySettings" label-width="120px">
            <el-form-item label="密码策略">
              <el-checkbox-group v-model="securitySettings.passwordPolicy">
                <el-checkbox label="requireUppercase">必须包含大写字母</el-checkbox>
                <el-checkbox label="requireLowercase">必须包含小写字母</el-checkbox>
                <el-checkbox label="requireNumbers">必须包含数字</el-checkbox>
                <el-checkbox label="requireSpecialChars">必须包含特殊字符</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <el-form-item label="最小密码长度">
              <el-input-number v-model="securitySettings.minPasswordLength" :min="6" :max="20"></el-input-number>
            </el-form-item>
            
            <el-form-item label="会话超时时间">
              <el-input-number v-model="securitySettings.sessionTimeout" :min="5" :max="480"></el-input-number>
              <span style="margin-left: 10px;">分钟</span>
            </el-form-item>
            
            <el-form-item label="登录失败锁定">
              <el-switch v-model="securitySettings.enableLockout"></el-switch>
            </el-form-item>
            
            <el-form-item label="最大失败次数" v-if="securitySettings.enableLockout">
              <el-input-number v-model="securitySettings.maxFailedAttempts" :min="3" :max="10"></el-input-number>
            </el-form-item>
            
            <el-form-item label="锁定时间" v-if="securitySettings.enableLockout">
              <el-input-number v-model="securitySettings.lockoutDuration" :min="5" :max="60"></el-input-number>
              <span style="margin-left: 10px;">分钟</span>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveSecuritySettings">保存设置</el-button>
              <el-button @click="resetSecuritySettings">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
      
      <!-- 通知设置 -->
      <el-tab-pane label="通知设置" name="notification">
        <el-card>
          <template #header>
            <span>通知配置</span>
          </template>
          
          <el-form :model="notificationSettings" label-width="120px">
            <el-form-item label="邮件通知">
              <el-switch v-model="notificationSettings.emailEnabled"></el-switch>
            </el-form-item>
            
            <el-form-item label="SMTP服务器" v-if="notificationSettings.emailEnabled">
              <el-input v-model="notificationSettings.smtpServer" placeholder="请输入SMTP服务器地址"></el-input>
            </el-form-item>
            
            <el-form-item label="SMTP端口" v-if="notificationSettings.emailEnabled">
              <el-input-number v-model="notificationSettings.smtpPort" :min="1" :max="65535"></el-input-number>
            </el-form-item>
            
            <el-form-item label="发送邮箱" v-if="notificationSettings.emailEnabled">
              <el-input v-model="notificationSettings.senderEmail" placeholder="请输入发送邮箱"></el-input>
            </el-form-item>
            
            <el-form-item label="邮箱密码" v-if="notificationSettings.emailEnabled">
              <el-input type="password" v-model="notificationSettings.emailPassword" placeholder="请输入邮箱密码"></el-input>
            </el-form-item>
            
            <el-form-item label="系统通知">
              <el-checkbox-group v-model="notificationSettings.systemNotifications">
                <el-checkbox label="systemError">系统错误</el-checkbox>
                <el-checkbox label="userLogin">用户登录</el-checkbox>
                <el-checkbox label="dataImport">数据导入</el-checkbox>
                <el-checkbox label="analysisComplete">分析完成</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveNotificationSettings">保存设置</el-button>
              <el-button @click="resetNotificationSettings">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
      
      <!-- 系统监控 -->
      <el-tab-pane label="系统监控" name="monitor">
        <SystemMonitorChart />
      </el-tab-pane>
      
      <!-- 数据管理 -->
      <el-tab-pane label="数据管理" name="data">
        <el-card>
          <template #header>
            <span>数据管理</span>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="data-section">
                <h4>数据备份</h4>
                <p>定期备份系统数据，确保数据安全</p>
                <el-button type="primary" @click="backupData">立即备份</el-button>
                <el-button @click="scheduleBackup">设置自动备份</el-button>
              </div>
            </el-col>
            
            <el-col :span="12">
              <div class="data-section">
                <h4>数据清理</h4>
                <p>清理过期数据，释放存储空间</p>
                <el-button type="warning" @click="cleanExpiredData">清理过期数据</el-button>
                <el-button @click="cleanLogs">清理日志文件</el-button>
              </div>
            </el-col>
          </el-row>
          
          <el-divider />
          
          <div class="data-section">
            <h4>数据统计</h4>
            <el-row :gutter="20">
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-value">{{ dataStats.totalUsers }}</div>
                  <div class="stat-label">用户总数</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-value">{{ dataStats.totalCustomers }}</div>
                  <div class="stat-label">客户总数</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-value">{{ dataStats.totalProducts }}</div>
                  <div class="stat-label">产品总数</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-value">{{ dataStats.totalOrders }}</div>
                  <div class="stat-label">订单总数</div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import SystemMonitorChart from '@/components/charts/SystemMonitorChart.vue'

const activeTab = ref('basic')

// 基本设置
const basicSettings = reactive({
  systemName: 'QBM AI System',
  systemDescription: '基于AI的商业模式量化分析系统',
  timezone: 'Asia/Shanghai',
  language: 'zh-CN'
})

// 安全设置
const securitySettings = reactive({
  passwordPolicy: ['requireUppercase', 'requireLowercase', 'requireNumbers'],
  minPasswordLength: 8,
  sessionTimeout: 30,
  enableLockout: true,
  maxFailedAttempts: 5,
  lockoutDuration: 15
})

// 通知设置
const notificationSettings = reactive({
  emailEnabled: false,
  smtpServer: '',
  smtpPort: 587,
  senderEmail: '',
  emailPassword: '',
  systemNotifications: ['systemError', 'analysisComplete']
})

// 数据统计
const dataStats = reactive({
  totalUsers: 25,
  totalCustomers: 1250,
  totalProducts: 85,
  totalOrders: 3420
})

// 保存基本设置
const saveBasicSettings = () => {
  // 这里应该调用API保存设置
  ElMessage.success('基本设置保存成功')
}

// 重置基本设置
const resetBasicSettings = () => {
  Object.assign(basicSettings, {
    systemName: 'QBM AI System',
    systemDescription: '基于AI的商业模式量化分析系统',
    timezone: 'Asia/Shanghai',
    language: 'zh-CN'
  })
  ElMessage.info('基本设置已重置')
}

// 保存安全设置
const saveSecuritySettings = () => {
  // 这里应该调用API保存设置
  ElMessage.success('安全设置保存成功')
}

// 重置安全设置
const resetSecuritySettings = () => {
  Object.assign(securitySettings, {
    passwordPolicy: ['requireUppercase', 'requireLowercase', 'requireNumbers'],
    minPasswordLength: 8,
    sessionTimeout: 30,
    enableLockout: true,
    maxFailedAttempts: 5,
    lockoutDuration: 15
  })
  ElMessage.info('安全设置已重置')
}

// 保存通知设置
const saveNotificationSettings = () => {
  // 这里应该调用API保存设置
  ElMessage.success('通知设置保存成功')
}

// 重置通知设置
const resetNotificationSettings = () => {
  Object.assign(notificationSettings, {
    emailEnabled: false,
    smtpServer: '',
    smtpPort: 587,
    senderEmail: '',
    emailPassword: '',
    systemNotifications: ['systemError', 'analysisComplete']
  })
  ElMessage.info('通知设置已重置')
}

// 数据备份
const backupData = () => {
  ElMessage.info('开始数据备份...')
  // 这里应该调用备份API
  setTimeout(() => {
    ElMessage.success('数据备份完成')
  }, 3000)
}

// 设置自动备份
const scheduleBackup = () => {
  ElMessage.info('自动备份设置功能开发中...')
}

// 清理过期数据
const cleanExpiredData = () => {
  ElMessage.warning('确定要清理过期数据吗？')
  // 这里应该调用清理API
}

// 清理日志文件
const cleanLogs = () => {
  ElMessage.warning('确定要清理日志文件吗？')
  // 这里应该调用清理API
}

// 组件挂载时加载设置
onMounted(() => {
  // 这里应该从API加载当前设置
  console.log('加载系统设置')
})
</script>

<style scoped>
.settings-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  color: #2c3e50;
  font-size: 24px;
  margin: 0;
}

.data-section {
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
  margin-bottom: 20px;
}

.data-section h4 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.data-section p {
  margin: 0 0 15px 0;
  color: #666;
  font-size: 14px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}
</style>


