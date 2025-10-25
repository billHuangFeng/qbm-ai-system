# 边际影响分析系统 - 安全架构设计文档

## 文档元数据
- **版本**: v1.0.0
- **创建日期**: 2025-01-23
- **负责人**: Cursor (安全架构设计)
- **实施方**: Lovable (安全实现)
- **状态**: ⏳ 待Lovable实施

---

## 1. 安全架构概述

### 1.1 安全目标
- **数据保护**: 敏感业务数据加密存储和传输
- **访问控制**: 基于角色的细粒度权限管理
- **审计追踪**: 完整的操作日志和审计记录
- **合规性**: 符合数据保护法规要求
- **可用性**: 确保系统高可用性和业务连续性

### 1.2 安全威胁模型
```
外部威胁 → 网络层 → 应用层 → 数据层 → 内部威胁
    ↓         ↓        ↓        ↓         ↓
  黑客攻击    DDoS    注入攻击   数据泄露   内部滥用
  恶意软件    中间人   权限提升   数据篡改   权限滥用
  社会工程   嗅探     会话劫持   数据丢失   数据泄露
```

---

## 2. 身份认证与授权

### 2.1 多因素认证 (MFA)

#### 2.1.1 认证流程设计
```typescript
interface AuthenticationFlow {
  // 第一步：用户名密码认证
  step1: {
    username: string;
    password: string;
    captcha?: string;
  };
  
  // 第二步：多因素认证
  step2: {
    method: 'sms' | 'email' | 'totp' | 'hardware_key';
    code: string;
    device_id?: string;
  };
  
  // 第三步：设备信任
  step3: {
    device_fingerprint: string;
    location_verification: boolean;
    risk_assessment: number;
  };
}
```

#### 2.1.2 认证实现
```typescript
class MultiFactorAuth {
  async authenticate(credentials: AuthenticationFlow): Promise<AuthResult> {
    // 1. 基础认证
    const basicAuth = await this.verifyCredentials(credentials.step1);
    if (!basicAuth.success) {
      return { success: false, error: 'Invalid credentials' };
    }

    // 2. 多因素认证
    const mfaResult = await this.verifyMFA(credentials.step2);
    if (!mfaResult.success) {
      return { success: false, error: 'MFA verification failed' };
    }

    // 3. 风险评估
    const riskScore = await this.assessRisk(credentials.step3);
    if (riskScore > 0.7) {
      return { success: false, error: 'High risk detected' };
    }

    // 4. 生成JWT令牌
    const token = await this.generateJWT(basicAuth.user);
    
    return { success: true, token, user: basicAuth.user };
  }
}
```

### 2.2 基于角色的访问控制 (RBAC)

#### 2.2.1 角色权限设计
```typescript
enum Role {
  SUPER_ADMIN = 'super_admin',
  SYSTEM_ADMIN = 'system_admin',
  BUSINESS_MANAGER = 'business_manager',
  DATA_ANALYST = 'data_analyst',
  VIEWER = 'viewer'
}

interface Permission {
  resource: string;
  action: string;
  conditions?: Record<string, any>;
}

const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  [Role.SUPER_ADMIN]: [
    { resource: '*', action: '*' }
  ],
  [Role.SYSTEM_ADMIN]: [
    { resource: 'system', action: 'manage' },
    { resource: 'users', action: 'manage' },
    { resource: 'data', action: 'import' },
    { resource: 'analysis', action: 'execute' }
  ],
  [Role.BUSINESS_MANAGER]: [
    { resource: 'analysis', action: 'view' },
    { resource: 'analysis', action: 'execute' },
    { resource: 'reports', action: 'generate' },
    { resource: 'decisions', action: 'approve' }
  ],
  [Role.DATA_ANALYST]: [
    { resource: 'data', action: 'import' },
    { resource: 'data', action: 'clean' },
    { resource: 'analysis', action: 'execute' },
    { resource: 'analysis', action: 'view' }
  ],
  [Role.VIEWER]: [
    { resource: 'analysis', action: 'view' },
    { resource: 'reports', action: 'view' }
  ]
};
```

#### 2.2.2 权限检查中间件
```typescript
class PermissionMiddleware {
  async checkPermission(
    user: User, 
    resource: string, 
    action: string
  ): Promise<boolean> {
    const userRole = user.role;
    const permissions = ROLE_PERMISSIONS[userRole];
    
    // 检查是否有权限
    const hasPermission = permissions.some(permission => 
      (permission.resource === '*' || permission.resource === resource) &&
      (permission.action === '*' || permission.action === action)
    );
    
    if (!hasPermission) {
      return false;
    }
    
    // 检查条件权限
    const conditionalPermissions = permissions.filter(p => p.conditions);
    for (const permission of conditionalPermissions) {
      if (!await this.checkConditions(permission.conditions, user, resource)) {
        return false;
      }
    }
    
    return true;
  }
}
```

---

## 3. 数据安全保护

### 3.1 数据加密策略

#### 3.1.1 传输加密
```typescript
class TransportSecurity {
  // HTTPS配置
  private httpsOptions = {
    minVersion: 'TLSv1.2',
    ciphers: [
      'ECDHE-RSA-AES256-GCM-SHA384',
      'ECDHE-RSA-AES128-GCM-SHA256',
      'ECDHE-RSA-AES256-SHA384',
      'ECDHE-RSA-AES128-SHA256'
    ].join(':'),
    honorCipherOrder: true
  };

  // API响应加密
  async encryptResponse(data: any): Promise<string> {
    const key = await this.getEncryptionKey();
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipher('aes-256-gcm', key);
    
    let encrypted = cipher.update(JSON.stringify(data), 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    const authTag = cipher.getAuthTag();
    
    return JSON.stringify({
      data: encrypted,
      iv: iv.toString('hex'),
      authTag: authTag.toString('hex')
    });
  }
}
```

#### 3.1.2 存储加密
```typescript
class DataEncryption {
  // 敏感字段加密
  async encryptSensitiveField(value: string, fieldType: string): Promise<string> {
    const key = await this.getFieldEncryptionKey(fieldType);
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipher('aes-256-gcm', key);
    
    let encrypted = cipher.update(value, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    const authTag = cipher.getAuthTag();
    
    return JSON.stringify({
      encrypted,
      iv: iv.toString('hex'),
      authTag: authTag.toString('hex'),
      algorithm: 'aes-256-gcm'
    });
  }

  // 数据库字段加密
  async encryptDatabaseField(value: any, columnName: string): Promise<string> {
    if (this.isSensitiveColumn(columnName)) {
      return await this.encryptSensitiveField(JSON.stringify(value), columnName);
    }
    return value;
  }
}
```

### 3.2 数据脱敏策略

#### 3.2.1 脱敏规则定义
```typescript
interface MaskingRule {
  field: string;
  type: 'email' | 'phone' | 'id_card' | 'bank_account' | 'name';
  method: 'partial' | 'full' | 'hash' | 'replace';
  replacement?: string;
}

const MASKING_RULES: MaskingRule[] = [
  {
    field: 'customer_email',
    type: 'email',
    method: 'partial',
    replacement: '***@***.com'
  },
  {
    field: 'customer_phone',
    type: 'phone',
    method: 'partial',
    replacement: '138****5678'
  },
  {
    field: 'customer_id_card',
    type: 'id_card',
    method: 'partial',
    replacement: '320***********1234'
  },
  {
    field: 'bank_account',
    type: 'bank_account',
    method: 'full',
    replacement: '****'
  }
];
```

#### 3.2.2 脱敏实现
```typescript
class DataMasking {
  maskSensitiveData(data: any, userRole: Role): any {
    const maskedData = { ...data };
    
    // 根据用户角色决定脱敏级别
    const maskingLevel = this.getMaskingLevel(userRole);
    
    for (const rule of MASKING_RULES) {
      if (maskedData[rule.field]) {
        maskedData[rule.field] = this.applyMaskingRule(
          maskedData[rule.field], 
          rule, 
          maskingLevel
        );
      }
    }
    
    return maskedData;
  }

  private applyMaskingRule(value: string, rule: MaskingRule, level: number): string {
    switch (rule.method) {
      case 'partial':
        return this.partialMask(value, rule.type, level);
      case 'full':
        return rule.replacement || '****';
      case 'hash':
        return this.hashValue(value);
      case 'replace':
        return rule.replacement || '****';
      default:
        return value;
    }
  }
}
```

---

## 4. 网络安全

### 4.1 API安全防护

#### 4.1.1 请求限流
```typescript
class RateLimiter {
  private requests = new Map<string, number[]>();
  
  async checkRateLimit(
    clientId: string, 
    endpoint: string, 
    limit: number = 100
  ): Promise<boolean> {
    const key = `${clientId}:${endpoint}`;
    const now = Date.now();
    const windowMs = 60 * 1000; // 1分钟窗口
    
    // 清理过期请求
    this.cleanExpiredRequests(key, now, windowMs);
    
    // 检查请求频率
    const requests = this.requests.get(key) || [];
    if (requests.length >= limit) {
      return false;
    }
    
    // 记录新请求
    requests.push(now);
    this.requests.set(key, requests);
    
    return true;
  }
}
```

#### 4.1.2 输入验证
```typescript
class InputValidator {
  validateRequest(req: Request): ValidationResult {
    const errors: string[] = [];
    
    // SQL注入检查
    if (this.containsSQLInjection(req.body)) {
      errors.push('Potential SQL injection detected');
    }
    
    // XSS检查
    if (this.containsXSS(req.body)) {
      errors.push('Potential XSS attack detected');
    }
    
    // 文件上传检查
    if (req.files) {
      for (const file of req.files) {
        if (!this.isValidFileType(file)) {
          errors.push(`Invalid file type: ${file.mimetype}`);
        }
        if (file.size > this.maxFileSize) {
          errors.push(`File too large: ${file.size} bytes`);
        }
      }
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  }
}
```

### 4.2 安全头配置

#### 4.2.1 HTTP安全头
```typescript
const securityHeaders = {
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'X-XSS-Protection': '1; mode=block',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Content-Security-Policy': `
    default-src 'self';
    script-src 'self' 'unsafe-inline' 'unsafe-eval';
    style-src 'self' 'unsafe-inline';
    img-src 'self' data: https:;
    font-src 'self' https://fonts.gstatic.com;
    connect-src 'self' https://api.qbm-system.com;
  `.replace(/\s+/g, ' ').trim()
};
```

---

## 5. 审计与监控

### 5.1 安全审计日志

#### 5.1.1 审计事件定义
```typescript
interface AuditEvent {
  id: string;
  timestamp: Date;
  userId: string;
  action: string;
  resource: string;
  result: 'success' | 'failure';
  details: Record<string, any>;
  ipAddress: string;
  userAgent: string;
  sessionId: string;
}

enum AuditAction {
  LOGIN = 'login',
  LOGOUT = 'logout',
  DATA_IMPORT = 'data_import',
  DATA_EXPORT = 'data_export',
  ANALYSIS_EXECUTE = 'analysis_execute',
  PERMISSION_CHANGE = 'permission_change',
  DATA_ACCESS = 'data_access',
  SYSTEM_CONFIG = 'system_config'
}
```

#### 5.1.2 审计日志记录
```typescript
class AuditLogger {
  async logEvent(event: AuditEvent): Promise<void> {
    // 记录到数据库
    await this.database.audit_logs.create({
      id: event.id,
      timestamp: event.timestamp,
      user_id: event.userId,
      action: event.action,
      resource: event.resource,
      result: event.result,
      details: JSON.stringify(event.details),
      ip_address: event.ipAddress,
      user_agent: event.userAgent,
      session_id: event.sessionId
    });
    
    // 记录到安全日志文件
    await this.writeSecurityLog(event);
    
    // 发送到安全监控系统
    await this.sendToSecurityMonitoring(event);
  }
}
```

### 5.2 安全监控

#### 5.2.1 异常检测
```typescript
class SecurityMonitor {
  async detectAnomalies(userId: string, action: string): Promise<SecurityAlert[]> {
    const alerts: SecurityAlert[] = [];
    
    // 检测异常登录
    const loginAnomalies = await this.detectLoginAnomalies(userId);
    alerts.push(...loginAnomalies);
    
    // 检测权限滥用
    const permissionAbuse = await this.detectPermissionAbuse(userId, action);
    alerts.push(...permissionAbuse);
    
    // 检测数据异常访问
    const dataAccessAnomalies = await this.detectDataAccessAnomalies(userId);
    alerts.push(...dataAccessAnomalies);
    
    return alerts;
  }
}
```

---

## 6. 合规性要求

### 6.1 数据保护法规

#### 6.1.1 GDPR合规
```typescript
class GDPRCompliance {
  // 数据主体权利
  async handleDataSubjectRequest(
    requestType: 'access' | 'rectification' | 'erasure' | 'portability',
    userId: string
  ): Promise<ComplianceResult> {
    switch (requestType) {
      case 'access':
        return await this.provideDataAccess(userId);
      case 'rectification':
        return await this.rectifyData(userId);
      case 'erasure':
        return await this.eraseData(userId);
      case 'portability':
        return await this.exportData(userId);
    }
  }
  
  // 数据最小化原则
  async minimizeDataCollection(data: any): Promise<any> {
    return this.removeUnnecessaryFields(data);
  }
}
```

#### 6.1.2 数据保留策略
```typescript
class DataRetentionPolicy {
  private retentionRules = {
    audit_logs: 7 * 365 * 24 * 60 * 60 * 1000, // 7年
    user_sessions: 30 * 24 * 60 * 60 * 1000,    // 30天
    temporary_files: 24 * 60 * 60 * 1000,       // 1天
    analysis_results: 365 * 24 * 60 * 60 * 1000 // 1年
  };
  
  async cleanupExpiredData(): Promise<void> {
    for (const [table, retentionPeriod] of Object.entries(this.retentionRules)) {
      const cutoffDate = new Date(Date.now() - retentionPeriod);
      await this.database[table].deleteMany({
        created_at: { $lt: cutoffDate }
      });
    }
  }
}
```

---

## 7. 安全配置管理

### 7.1 环境安全配置

#### 7.1.1 生产环境配置
```yaml
# security-config.yml
production:
  authentication:
    jwt_secret: ${JWT_SECRET}
    jwt_expiry: 3600
    mfa_required: true
    password_policy:
      min_length: 12
      require_uppercase: true
      require_lowercase: true
      require_numbers: true
      require_symbols: true
  
  encryption:
    algorithm: aes-256-gcm
    key_rotation_days: 90
    field_encryption: true
  
  network:
    https_only: true
    cors_origins: ["https://app.qbm-system.com"]
    rate_limiting:
      requests_per_minute: 100
      burst_limit: 200
  
  monitoring:
    security_logging: true
    anomaly_detection: true
    alert_threshold: 0.8
```

### 7.2 安全密钥管理

#### 7.2.1 密钥轮换
```typescript
class KeyRotation {
  async rotateEncryptionKeys(): Promise<void> {
    // 生成新密钥
    const newKey = await this.generateNewKey();
    
    // 重新加密现有数据
    await this.reEncryptExistingData(newKey);
    
    // 更新密钥配置
    await this.updateKeyConfiguration(newKey);
    
    // 清理旧密钥
    await this.cleanupOldKey();
  }
}
```

---

## 8. 安全测试

### 8.1 安全测试用例

#### 8.1.1 认证测试
```typescript
describe('Authentication Security', () => {
  it('应该防止暴力破解攻击', async () => {
    const credentials = { username: 'test', password: 'wrong' };
    
    // 尝试多次登录
    for (let i = 0; i < 10; i++) {
      const response = await login(credentials);
      if (i < 5) {
        expect(response.success).toBe(false);
      } else {
        // 第6次开始应该被锁定
        expect(response.error).toContain('account_locked');
      }
    }
  });
  
  it('应该验证JWT令牌有效性', async () => {
    const invalidToken = 'invalid.jwt.token';
    const response = await makeAuthenticatedRequest('/api/data', invalidToken);
    
    expect(response.status).toBe(401);
    expect(response.error).toContain('invalid_token');
  });
});
```

#### 8.1.2 数据安全测试
```typescript
describe('Data Security', () => {
  it('应该加密敏感数据', async () => {
    const sensitiveData = { customer_email: 'test@example.com' };
    const response = await createRecord(sensitiveData);
    
    // 检查数据库中数据是否加密
    const storedData = await getStoredData(response.id);
    expect(storedData.customer_email).not.toBe('test@example.com');
    expect(storedData.customer_email).toMatch(/^[A-F0-9]+$/); // 加密后的十六进制
  });
  
  it('应该正确脱敏数据', async () => {
    const data = { customer_phone: '13812345678' };
    const response = await getData(data.id, Role.VIEWER);
    
    expect(response.customer_phone).toBe('138****5678');
  });
});
```

---

## 9. 总结

本安全架构设计文档提供了全面的安全保护策略，包括：

1. **身份认证**: 多因素认证、基于角色的访问控制
2. **数据保护**: 传输加密、存储加密、数据脱敏
3. **网络安全**: API安全防护、请求限流、输入验证
4. **审计监控**: 安全审计日志、异常检测、安全监控
5. **合规性**: GDPR合规、数据保留策略
6. **配置管理**: 环境安全配置、密钥管理
7. **安全测试**: 认证测试、数据安全测试

所有安全措施都具备具体的实现指导，能够确保系统的安全性和合规性。

---

**文档状态**: ✅ 已完成，等待Lovable实施

**预计实施时间**: 3-4周

**联系方式**:
- Cursor技术支持: cursor-team@example.com
- Lovable实施团队: lovable-team@example.com
