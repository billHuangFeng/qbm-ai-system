# 复杂单据导入分工策略

**创建时间**: 2025-01-23  
**版本**: 1.0  
**状态**: ✅ **已确定**

---

## 📋 核心原则

复杂单据导入功能应采用 **"算法在后端，交互在前端"** 的混合模式：

- **Cursor (FastAPI)**: 实现核心算法和数据处理逻辑
- **Lovable (Edge Functions + Frontend)**: 实现用户交互界面和轻量级业务逻辑

---

## 🎯 分工建议

### ✅ Cursor 负责（FastAPI后端）

#### 1. 核心算法实现

**格式识别算法**
- ✅ 文档格式自动检测（6种格式识别）
- ✅ 字段类型和结构分析
- ✅ 模式匹配和特征提取
- ✅ 格式得分计算

**字段映射算法**
- ✅ 智能字段映射推荐
- ✅ 字段相似度计算（Levenshtein距离、语义相似度）
- ✅ 字段映射规则学习
- ✅ 位置映射（无表头文件）

**主数据匹配算法**
- ✅ 主数据ID自动匹配（7种主数据类型）
- ✅ 单字段和组合字段匹配
- ✅ 模糊匹配和精确匹配
- ✅ 置信度计算
- ✅ 匹配结果排序和推荐

**单据头ID匹配算法**
- ✅ 通过单据号匹配系统中已存在的单据头记录ID
- ✅ 匹配结果验证
- ✅ 匹配建议生成

**数据处理算法**
- ✅ 前向填充（格式2）
- ✅ 数据合并和关联
- ✅ 虚拟记录生成
- ✅ 数据清洗和转换

#### 2. 数据验证逻辑

- ✅ 必填字段验证（严格必填 vs 可补充必填）
- ✅ 数据质量评估
- ✅ 金额字段一致性验证（价税合计 = 不含税金额 + 税额）
- ✅ 业务规则验证

#### 3. API端点

**核心处理端点**
- `POST /api/v1/data-import/analyze` - 分析文件结构，推荐字段映射
- `POST /api/v1/data-import/process` - 处理复杂单据格式
- `POST /api/v1/data-import/validate` - 深度数据验证

**匹配和决策端点**
- `POST /api/v1/data-import/match-master-data` - 主数据匹配（批量）
- `POST /api/v1/data-import/match-document-header` - 单据头ID匹配（格式5补充明细时）
- `POST /api/v1/data-import/match-status` - 获取匹配状态和待决策项

**用户决策端点**
- `POST /api/v1/data-import/confirm-match` - 确认匹配决策（选择、创建新、废弃）

---

### ✅ Lovable 负责（Edge Functions + Frontend）

#### 1. 用户交互界面

**字段映射界面**
- ✅ 展示源字段和目标字段映射关系
- ✅ 用户手动调整映射
- ✅ 确认映射结果

**格式识别展示**
- ✅ 显示检测到的格式类型
- ✅ 格式置信度展示
- ✅ 用户确认或手动选择格式

**匹配决策界面**
- ✅ 主数据匹配结果展示（多个候选）
- ✅ 单据头匹配结果展示
- ✅ 用户选择操作：
  - 选择某个匹配项
  - 创建新的主数据/单据头
  - 废弃该条记录
- ✅ 批量决策支持

**进度和状态展示**
- ✅ 导入进度条
- ✅ 处理状态（分析中、待决策、处理中、完成）
- ✅ 错误和警告信息展示

#### 2. 轻量级业务逻辑（Edge Functions）

**简单验证**
- ✅ 文件格式基础验证
- ✅ 文件大小检查
- ✅ 必填参数验证

**状态管理**
- ✅ 导入批次创建
- ✅ 导入状态更新
- ✅ 用户决策记录

**数据写入（简单场景）**
- ✅ 简单CSV/JSON直接写入
- ✅ 经过用户决策后的数据写入

---

## 🔄 协作流程

### 典型导入流程

```
1. 用户上传文件
   ↓ (Lovable Frontend)
2. 前端发送文件到 FastAPI
   ↓ (Cursor FastAPI)
3. FastAPI 分析文件结构
   - 格式识别
   - 字段映射推荐
   ↓ (返回分析结果)
4. Lovable Frontend 展示映射界面
   - 用户确认或调整映射
   ↓ (用户确认)
5. Lovable Frontend 发送映射配置到 FastAPI
   ↓ (Cursor FastAPI)
6. FastAPI 执行格式处理和字段映射
   - 识别格式类型
   - 应用字段映射
   - 处理格式（前向填充、合并等）
   ↓ (发现需要匹配)
7. FastAPI 执行主数据匹配和单据头匹配
   - 生成匹配结果和待决策项
   ↓ (返回匹配结果)
8. Lovable Frontend 展示匹配决策界面
   - 主数据匹配候选列表
   - 单据头匹配结果
   - 用户进行决策
   ↓ (用户决策完成)
9. Lovable Frontend 发送决策结果到 FastAPI
   ↓ (Cursor FastAPI)
10. FastAPI 应用用户决策，完成数据处理
    ↓ (返回处理结果)
11. Lovable Frontend 展示导入结果
    - 成功/失败统计
    - 错误和警告
    - 导入报告
```

---

## 📊 技术考虑

### 为什么算法在FastAPI？

1. **计算复杂度**
   - 格式识别需要模式匹配和特征分析
   - 字段映射需要相似度计算算法
   - 主数据匹配需要数据库查询和模糊匹配
   - 这些算法复杂度 > O(n)

2. **依赖库**
   - pandas, numpy（数据处理）
   - python-Levenshtein（字符串相似度）
   - 可能需要的ML库（语义相似度）
   - PostgreSQL客户端（主数据查询）

3. **执行时间**
   - 大文件格式分析可能需要 > 10秒
   - 批量主数据匹配可能需要 > 10秒

4. **数据库访问**
   - 主数据查询需要连接PostgreSQL
   - 单据头记录查询需要连接数据库
   - Edge Functions不适合频繁的复杂数据库查询

### 为什么交互在Lovable？

1. **用户体验**
   - 前端界面响应速度快
   - 实时展示处理进度
   - 交互式决策界面

2. **轻量级逻辑**
   - Edge Functions处理简单验证和状态更新
   - 快速响应，无需复杂计算

3. **状态管理**
   - 前端管理用户交互状态
   - Edge Functions管理导入批次状态

---

## 📝 API接口设计

### 1. 文件分析接口

```http
POST /api/v1/data-import/analyze
Content-Type: multipart/form-data

{
  "file": <file>,
  "source_type": "purchase_order|sales_order|..."
}
```

**响应**:
```json
{
  "document_format": "excel",
  "detected_format_type": "repeated_header|first_row_header|...",
  "format_confidence": 0.95,
  "field_mappings": [
    {
      "source_field": "采购单号",
      "target_field": "单据号",
      "confidence": 0.98,
      "match_type": "exact|fuzzy|semantic"
    }
  ],
  "suggested_mappings": [...],
  "warnings": [...]
}
```

### 2. 格式处理接口

```http
POST /api/v1/data-import/process
Content-Type: application/json

{
  "file_id": "uuid",
  "field_mappings": {
    "源字段1": "目标字段1",
    ...
  },
  "format_type": "repeated_header|auto",
  "metadata": {...}
}
```

**响应**:
```json
{
  "processing_id": "uuid",
  "status": "processing|requires_decision|completed",
  "processed_records": 100,
  "requires_decisions": {
    "master_data_matches": [...],
    "document_header_matches": [...]
  }
}
```

### 3. 主数据匹配接口

```http
POST /api/v1/data-import/match-master-data
Content-Type: application/json

{
  "records": [
    {
      "row_index": 0,
      "master_data_type": "business_entity|product|...",
      "source_values": {
        "经营主体名称": "XXX公司",
        "统一社会信用代码": "91110000..."
      }
    }
  ]
}
```

**响应**:
```json
{
  "matches": [
    {
      "row_index": 0,
      "master_data_type": "business_entity",
      "candidates": [
        {
          "id": 123,
          "name": "XXX公司",
          "confidence": 0.98,
          "match_fields": ["entity_name", "credit_code"]
        },
        {
          "id": 456,
          "name": "XXX公司（相似）",
          "confidence": 0.75,
          "match_fields": ["entity_name"]
        }
      ],
      "no_match": false,
      "multiple_matches": true
    }
  ]
}
```

### 4. 单据头ID匹配接口（格式5补充明细）

```http
POST /api/v1/data-import/match-document-header
Content-Type: application/json

{
  "document_numbers": ["DOC001", "DOC002", ...],
  "document_type": "purchase_order|sales_order|..."
}
```

**响应**:
```json
{
  "matches": [
    {
      "document_number": "DOC001",
      "header_id": 789,
      "header_info": {
        "id": 789,
        "document_number": "DOC001",
        "document_date": "2024-01-01",
        "customer_name": "客户A"
      },
      "confidence": 1.0,
      "found": true
    },
    {
      "document_number": "DOC999",
      "header_id": null,
      "header_info": null,
      "confidence": 0.0,
      "found": false,
      "message": "系统中未找到单据号DOC999的单据头记录"
    }
  ],
  "unmatched_count": 1
}
```

### 5. 用户决策确认接口

```http
POST /api/v1/data-import/confirm-match
Content-Type: application/json

{
  "processing_id": "uuid",
  "decisions": [
    {
      "type": "master_data|document_header",
      "row_index": 0,
      "decision": "select|create_new|skip",
      "selected_id": 123,  // 选择某个匹配项时
      "new_data": {...},   // 创建新记录时
      "reason": "用户选择"
    }
  ]
}
```

**响应**:
```json
{
  "success": true,
  "applied_decisions": 5,
  "updated_records": 100,
  "status": "processing|completed"
}
```

---

## ✅ 总结

**核心分工**:
- **Cursor**: 算法实现、数据处理、匹配逻辑 → FastAPI
- **Lovable**: 用户界面、交互逻辑、状态管理 → Frontend + Edge Functions

**优势**:
- ✅ 算法集中管理，易于维护和优化
- ✅ 前端响应快，用户体验好
- ✅ 职责清晰，易于协作
- ✅ 支持复杂算法和大数据处理

---

**文档版本**: 1.0  
**最后更新**: 2025-01-23


