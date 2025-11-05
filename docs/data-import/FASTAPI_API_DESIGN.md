# FastAPI API接口设计文档

**创建时间**: 2025-01-22  
**版本**: 1.0  
**状态**: ✅ **P1 - 重要文档**

**文档目的**: 提供FastAPI API接口的完整设计，供Lovable在Edge Functions中调用

---

## 📋 目录

1. [API端点定义](#1-api端点定义)
2. [认证和授权](#2-认证和授权)
3. [错误处理](#3-错误处理)
4. [请求响应模型](#4-请求响应模型)

---

## 1. API端点定义

### 1.1 文档格式识别

**端点**: `POST /api/v1/document/recognize-format`

**功能**: 识别文档格式和类型

**请求**:
```python
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Optional

class FormatRecognitionRequest(BaseModel):
    """格式识别请求（文件内容通过multipart/form-data传递）"""
    source_system: Optional[str] = None
    document_type: Optional[str] = None  # SO/SH/SI/PO/RC/PI
    tenant_id: str

# 实际请求使用multipart/form-data
# file: UploadFile
# source_system: str (可选)
# document_type: str (可选)
# tenant_id: str
```

**响应**:
```python
class FormatRecognitionResponse(BaseModel):
    """格式识别响应"""
    document_type: str  # SO/SH/SI/PO/RC/PI
    confidence: float  # 0-1
    detected_patterns: Dict[str, Any]
    recommendations: List[str]
    
    # 格式识别详情
    format_type: str  # repeated_header|first_row_header|header_only|line_only|mixed|grouped
    format_confidence: float
    header_fields: List[str]
    line_fields: List[str]
    statistics: Dict[str, Any]
```

**实现代码**:
```python
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import pandas as pd
from typing import Optional

app = FastAPI()

@app.post("/api/v1/document/recognize-format")
async def recognize_format(
    file: UploadFile = File(...),
    source_system: Optional[str] = None,
    document_type: Optional[str] = None,
    tenant_id: str = None,
    authorization: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> FormatRecognitionResponse:
    """
    识别文档格式和类型
    
    算法步骤:
    1. 解析文件（Excel/CSV/JSON）
    2. 分析列结构（Header字段 vs Line字段）
    3. 检测数据模式（重复率、空值率、分组特征）
    4. 计算格式得分（6种格式）
    5. 返回最高置信度的格式类型
    """
    try:
        # 1. 验证JWT token
        token_data = verify_token(authorization.credentials)
        tenant_id = token_data.get("tenant_id") or tenant_id
        
        if not tenant_id:
            raise HTTPException(status_code=400, detail="缺少tenant_id")
        
        # 2. 解析文件
        file_content = await file.read()
        df = await parse_file(file_content, file.filename)
        
        # 3. 初始化格式识别器
        from src.services.data_enhancement.document_format_detector import DocumentFormatDetector
        detector = DocumentFormatDetector()
        
        # 4. 识别格式
        result = await detector.detect_format(df, {
            "source_system": source_system,
            "document_type": document_type,
            "tenant_id": tenant_id
        })
        
        # 5. 返回结果
        return FormatRecognitionResponse(
            document_type=result.document_type or document_type,
            confidence=result.confidence,
            detected_patterns=result.detected_patterns,
            recommendations=result.recommendations,
            format_type=result.format_type,
            format_confidence=result.format_confidence,
            header_fields=result.header_fields,
            line_fields=result.line_fields,
            statistics=result.statistics
        )
        
    except Exception as e:
        logger.error(f"格式识别失败: {e}")
        raise HTTPException(status_code=500, detail=f"格式识别失败: {str(e)}")
```

---

### 1.2 头行识别

**端点**: `POST /api/v1/document/identify-headers`

**功能**: 识别头行结构

**请求**:
```python
class HeaderLineIdentificationRequest(BaseModel):
    """头行识别请求"""
    data: List[Dict[str, Any]]  # 解析后的数据
    document_type: str  # SO/SH/SI/PO/RC/PI
    format_type: Optional[str] = None  # 格式类型（如果已识别）
    field_mappings: Optional[Dict[str, str]] = None  # 字段映射
    tenant_id: str
```

**响应**:
```python
class HeaderLineIdentificationResponse(BaseModel):
    """头行识别响应"""
    headers: List[Dict[str, Any]]  # Header记录列表
    lines: List[Dict[str, Any]]  # Line记录列表
    associations: List[Dict[str, Any]]  # header_id → line_ids映射
    
    # 识别详情
    format_type: str
    confidence: float
    statistics: Dict[str, Any]
```

**实现代码**:
```python
@app.post("/api/v1/document/identify-headers")
async def identify_headers(
    request: HeaderLineIdentificationRequest,
    authorization: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> HeaderLineIdentificationResponse:
    """
    识别头行结构
    
    算法步骤:
    1. 应用字段映射（如果提供）
    2. 检测格式类型（如果未提供）
    3. 识别Header行（单据号、客户/供应商、日期等）
    4. 识别Line行（SKU、数量、单价等）
    5. 建立关联关系（格式1：单据号匹配，格式2：前向填充）
    """
    try:
        # 1. 验证JWT token
        token_data = verify_token(authorization.credentials)
        tenant_id = token_data.get("tenant_id") or request.tenant_id
        
        # 2. 转换为DataFrame
        df = pd.DataFrame(request.data)
        
        # 3. 应用字段映射
        if request.field_mappings:
            df = apply_field_mappings(df, request.field_mappings)
        
        # 4. 初始化头行识别器
        from src.services.data_enhancement.document_header_matcher import HeaderLineIdentifier
        identifier = HeaderLineIdentifier(request.document_type)
        
        # 5. 识别头行结构
        result = identifier.identify(df, request.field_mappings)
        
        # 6. 返回结果
        return HeaderLineIdentificationResponse(
            headers=result["headers"],
            lines=result["lines"],
            associations=result["associations"],
            format_type=result["format_type"],
            confidence=result["confidence"],
            statistics=result["statistics"]
        )
        
    except Exception as e:
        logger.error(f"头行识别失败: {e}")
        raise HTTPException(status_code=500, detail=f"头行识别失败: {str(e)}")
```

---

### 1.3 主数据匹配

**端点**: `POST /api/v1/document/match-master-data`

**功能**: 主数据模糊匹配

**请求**:
```python
class MasterDataMatchRequest(BaseModel):
    """主数据匹配请求"""
    entity_type: str  # customer/sku/supplier/channel
    input_values: List[Dict[str, Any]]  # [{"name": "...", "code": "..."}]
    tenant_id: str
    threshold: float = 0.8  # 匹配阈值
    return_top: int = 3  # 返回top N候选
```

**响应**:
```python
class MasterDataMatchResponse(BaseModel):
    """主数据匹配响应"""
    matches: List[Dict[str, Any]]  # 匹配结果列表
    
    # 每个匹配结果包含:
    # {
    #   "input": {"name": "...", "code": "..."},
    #   "matched": {"id": "...", "name": "...", "code": "..."},
    #   "confidence": 0.95,
    #   "match_type": "exact|fuzzy|combined",
    #   "candidates": [...]  # top N候选
    # }
    
    unmatched: List[Dict[str, Any]]  # 未匹配的输入
    statistics: Dict[str, Any]  # 匹配统计
```

**实现代码**:
```python
@app.post("/api/v1/document/match-master-data")
async def match_master_data(
    request: MasterDataMatchRequest,
    authorization: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> MasterDataMatchResponse:
    """
    主数据模糊匹配
    
    算法步骤:
    1. 验证JWT token，提取tenant_id
    2. 查询主数据表（根据entity_type）
    3. 对每个输入值执行匹配：
       a. 精确匹配（编码）
       b. 模糊匹配（名称，使用rapidfuzz）
       c. 组合匹配（编码+名称）
    4. 返回匹配结果和候选列表
    """
    try:
        # 1. 验证JWT token
        token_data = verify_token(authorization.credentials)
        tenant_id = token_data.get("tenant_id") or request.tenant_id
        
        # 2. 初始化主数据匹配器
        from src.services.data_enhancement.master_data_matcher import MasterDataMatcher
        from src.security.database import SecureDatabaseService
        
        db_service = get_db_service()
        matcher = MasterDataMatcher(db_service)
        
        # 3. 执行批量匹配
        matches = []
        unmatched = []
        
        for input_value in request.input_values:
            match_result = await matcher.match_master_data(
                entity_type=request.entity_type,
                input_name=input_value.get("name"),
                input_code=input_value.get("code"),
                tenant_id=tenant_id,
                threshold=request.threshold,
                return_top=request.return_top
            )
            
            if match_result:
                matches.append({
                    "input": input_value,
                    "matched": match_result["matched"],
                    "confidence": match_result["confidence"],
                    "match_type": match_result["match_type"],
                    "candidates": match_result["candidates"]
                })
            else:
                unmatched.append(input_value)
        
        # 4. 计算统计
        statistics = {
            "total": len(request.input_values),
            "matched": len(matches),
            "unmatched": len(unmatched),
            "match_rate": len(matches) / len(request.input_values) if request.input_values else 0
        }
        
        # 5. 返回结果
        return MasterDataMatchResponse(
            matches=matches,
            unmatched=unmatched,
            statistics=statistics
        )
        
    except Exception as e:
        logger.error(f"主数据匹配失败: {e}")
        raise HTTPException(status_code=500, detail=f"主数据匹配失败: {str(e)}")
```

---

### 1.4 单据头ID匹配

**端点**: `POST /api/v1/document/match-document-header`

**功能**: 通过单据号匹配系统中已存在的单据头记录ID（格式5补充明细时使用）

**请求**:
```python
class DocumentHeaderMatchRequest(BaseModel):
    """单据头匹配请求"""
    document_numbers: List[str]  # 单据号列表
    document_type: str  # SO/SH/SI/PO/RC/PI
    tenant_id: str
```

**响应**:
```python
class DocumentHeaderMatchResponse(BaseModel):
    """单据头匹配响应"""
    matches: List[Dict[str, Any]]  # 匹配结果列表
    
    # 每个匹配结果包含:
    # {
    #   "document_number": "SO001",
    #   "header_id": "uuid",
    #   "header_info": {...},
    #   "confidence": 1.0,
    #   "found": true
    # }
    
    unmatched_count: int
```

**实现代码**:
```python
@app.post("/api/v1/document/match-document-header")
async def match_document_header(
    request: DocumentHeaderMatchRequest,
    authorization: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> DocumentHeaderMatchResponse:
    """
    单据头ID匹配
    
    算法步骤:
    1. 验证JWT token
    2. 根据document_type确定目标表
    3. 查询数据库，通过单据号精确匹配
    4. 返回匹配结果
    """
    try:
        # 1. 验证JWT token
        token_data = verify_token(authorization.credentials)
        tenant_id = token_data.get("tenant_id") or request.tenant_id
        
        # 2. 确定目标表
        table_map = {
            "SO": "sales_order_header",
            "SH": "shipment_header",
            "SI": "sales_invoice_header",
            "PO": "purchase_order_header",
            "RC": "receipt_header",
            "PI": "purchase_invoice_header"
        }
        
        table_name = table_map.get(request.document_type)
        if not table_name:
            raise HTTPException(status_code=400, detail=f"不支持的单据类型: {request.document_type}")
        
        # 3. 查询数据库
        from src.security.database import SecureDatabaseService
        db_service = get_db_service()
        
        matches = []
        unmatched = []
        
        async with db_service.get_connection() as conn:
            for doc_number in request.document_numbers:
                # 查询单据头
                query = f"""
                SELECT id, {get_document_number_field(request.document_type)} as document_number,
                       document_date, customer_id, supplier_id, total_amount
                FROM {table_name}
                WHERE tenant_id = $1
                AND {get_document_number_field(request.document_type)} = $2
                LIMIT 1
                """
                
                row = await conn.fetchrow(query, tenant_id, doc_number)
                
                if row:
                    matches.append({
                        "document_number": doc_number,
                        "header_id": str(row["id"]),
                        "header_info": dict(row),
                        "confidence": 1.0,
                        "found": True
                    })
                else:
                    unmatched.append(doc_number)
        
        # 4. 返回结果
        return DocumentHeaderMatchResponse(
            matches=matches,
            unmatched_count=len(unmatched)
        )
        
    except Exception as e:
        logger.error(f"单据头匹配失败: {e}")
        raise HTTPException(status_code=500, detail=f"单据头匹配失败: {str(e)}")

def get_document_number_field(doc_type: str) -> str:
    """获取单据号字段名"""
    field_map = {
        "SO": "order_number",
        "SH": "shipment_number",
        "SI": "invoice_number",
        "PO": "po_number",
        "RC": "receipt_number",
        "PI": "invoice_number"
    }
    return field_map.get(doc_type, "document_number")
```

---

## 2. 认证和授权

### 2.1 JWT Token验证

**实现**:
```python
from fastapi import Header, HTTPException
from fastapi.security import HTTPBearer
import jwt
from typing import Dict, Optional

security = HTTPBearer()

async def verify_token(
    authorization: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    验证JWT token
    
    如何验证Supabase生成的JWT token:
    1. 从Header中提取Authorization token
    2. 使用Supabase JWT secret验证token签名
    3. 检查token是否过期
    4. 提取tenant_id和user_id
    
    Returns:
        {
            "user_id": "...",
            "tenant_id": "...",
            "email": "...",
            ...
        }
    """
    token = authorization.credentials
    
    try:
        # 1. 验证token签名（使用Supabase JWT secret）
        import os
        supabase_jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        
        if not supabase_jwt_secret:
            raise HTTPException(status_code=500, detail="JWT secret未配置")
        
        # 2. 解码token
        payload = jwt.decode(
            token,
            supabase_jwt_secret,
            algorithms=["HS256"]
        )
        
        # 3. 检查token是否过期（jwt库会自动检查）
        # 4. 提取用户信息
        user_id = payload.get("sub")  # Supabase使用"sub"作为user_id
        tenant_id = payload.get("tenant_id")  # 如果token中包含tenant_id
        email = payload.get("email")
        
        return {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "email": email,
            "raw_payload": payload
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token已过期，请重新登录"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail=f"无效的Token: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Token验证失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Token验证失败: {str(e)}"
        )
```

### 2.2 使用示例

```python
@app.post("/api/v1/document/recognize-format")
async def recognize_format(
    file: UploadFile = File(...),
    token_data: Dict[str, Any] = Depends(verify_token)
):
    # 使用token_data中的tenant_id和user_id
    tenant_id = token_data["tenant_id"]
    user_id = token_data["user_id"]
    
    # 继续处理...
    pass
```

---

## 3. 错误处理

### 3.1 标准错误响应格式

```python
class ErrorResponse(BaseModel):
    """标准错误响应"""
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None
```

### 3.2 错误代码列表

```python
ERROR_CODES = {
    # 文件相关错误
    "INVALID_FILE_FORMAT": "文件格式不支持",
    "FILE_TOO_LARGE": "文件大小超过限制",
    "FILE_PARSE_FAILED": "文件解析失败",
    
    # 格式识别错误
    "RECOGNITION_FAILED": "格式识别失败",
    "INSUFFICIENT_DATA": "数据不足，无法识别格式",
    "AMBIGUOUS_FORMAT": "格式不明确，存在多个候选",
    
    # 匹配错误
    "MATCHING_FAILED": "主数据匹配失败",
    "NO_MASTER_DATA": "主数据表不存在或为空",
    "MATCHING_TIMEOUT": "匹配超时",
    
    # 验证错误
    "VALIDATION_FAILED": "数据验证失败",
    "INVALID_DATA_TYPE": "数据类型错误",
    "MISSING_REQUIRED_FIELD": "必填字段缺失",
    
    # 认证错误
    "INVALID_TOKEN": "无效的Token",
    "TOKEN_EXPIRED": "Token已过期",
    "MISSING_TENANT_ID": "缺少tenant_id",
    
    # 服务器错误
    "SERVER_ERROR": "服务器内部错误",
    "DATABASE_ERROR": "数据库错误",
    "SERVICE_UNAVAILABLE": "服务不可用"
}
```

### 3.3 错误处理示例

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """处理ValueError"""
    return JSONResponse(
        status_code=400,
        content={
            "error_code": "INVALID_INPUT",
            "error_message": str(exc),
            "details": {}
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """处理一般异常"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "SERVER_ERROR",
            "error_message": "服务器内部错误",
            "details": {"error": str(exc)}
        }
    )
```

---

## 4. 请求响应模型

### 4.1 通用响应模型

```python
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = True
    message: str = "操作成功"
    timestamp: str = None  # 自动填充
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.timestamp is None:
            from datetime import datetime
            self.timestamp = datetime.utcnow().isoformat()

class ErrorResponse(BaseResponse):
    """错误响应模型"""
    success: bool = False
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None
```

### 4.2 API端点列表

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/v1/document/recognize-format` | POST | 格式识别 | ✅ |
| `/api/v1/document/identify-headers` | POST | 头行识别 | ✅ |
| `/api/v1/document/match-master-data` | POST | 主数据匹配 | ✅ |
| `/api/v1/document/match-document-header` | POST | 单据头匹配 | ✅ |
| `/api/v1/document/validate` | POST | 数据验证 | ⏳ |
| `/api/v1/document/health` | GET | 健康检查 | ✅ |

---

## 5. 环境变量配置

### 5.1 必需的环境变量

```python
# .env文件
SUPABASE_JWT_SECRET=your-jwt-secret-key
FASTAPI_URL=http://localhost:8000
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379
```

### 5.2 配置加载

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置"""
    supabase_jwt_secret: str
    fastapi_url: str = "http://localhost:8000"
    database_url: str
    redis_url: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 6. API使用示例

### 6.1 Edge Functions调用示例

```typescript
// Edge Function中调用FastAPI
async function callFastAPI(
  endpoint: string,
  payload: any,
  authHeader: string
): Promise<any> {
  const fastApiUrl = Deno.env.get('FASTAPI_URL');
  
  const response = await fetch(`${fastApiUrl}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authHeader}`,
    },
    body: JSON.stringify(payload),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(`FastAPI error: ${error.error_message}`);
  }
  
  return await response.json();
}

// 使用示例：格式识别
const result = await callFastAPI(
  '/api/v1/document/recognize-format',
  {
    file_content: base64FileContent,
    file_name: 'example.xlsx',
    document_type: 'SO',
    tenant_id: 'tenant-123'
  },
  supabaseJwtToken
);
```

---

**文档版本**: 1.0  
**最后更新**: 2025-01-22  
**维护者**: Cursor (算法设计与技术架构)

