# 核心资源与核心能力标签设计

## 🎯 设计理念

核心资源和核心能力是企业的重要资产，是企业竞争优势的基础。在BMOS系统中，需要将这些概念设计为标签，并在决策记录中体现对它们的控制和建设意图。

---

## 🏷️ 标签体系设计

### 1. 核心资源标签 (Core Resources Tags - CRT)

#### 1.1 标签分类
```typescript
interface CoreResourceTag {
  crt_id: string;
  crt_name: string;
  crt_category: 'physical' | 'intellectual' | 'human' | 'financial' | 'relational';
  crt_type: 'tangible' | 'intangible';
  crt_description: string;
  crt_value: number; // 资源价值评估
  crt_rarity: 'common' | 'rare' | 'unique'; // 稀缺性
  crt_control_level: number; // 控制程度 (0-1)
  crt_competitiveness: number; // 竞争力 (0-1)
  created_at: Date;
  updated_at: Date;
}
```

#### 1.2 核心资源标签类型

##### 物理资源 (Physical Resources)
```typescript
const physicalResources = {
  'crt_manufacturing_facility': {
    name: '制造设施',
    description: '生产制造的基础设施和设备',
    value: 1000000,
    rarity: 'rare',
    control_level: 0.9,
    competitiveness: 0.8
  },
  'crt_technology_equipment': {
    name: '技术设备',
    description: '先进的生产技术和设备',
    value: 500000,
    rarity: 'rare',
    control_level: 0.85,
    competitiveness: 0.9
  },
  'crt_warehouse_logistics': {
    name: '仓储物流',
    description: '仓储和物流配送网络',
    value: 300000,
    rarity: 'common',
    control_level: 0.8,
    competitiveness: 0.7
  },
  'crt_raw_materials': {
    name: '原材料',
    description: '生产所需的原材料和零部件',
    value: 200000,
    rarity: 'common',
    control_level: 0.6,
    competitiveness: 0.5
  }
};
```

##### 知识产权资源 (Intellectual Resources)
```typescript
const intellectualResources = {
  'crt_patents': {
    name: '专利技术',
    description: '核心技术和发明专利',
    value: 2000000,
    rarity: 'unique',
    control_level: 1.0,
    competitiveness: 0.95
  },
  'crt_trademarks': {
    name: '商标品牌',
    description: '品牌商标和知识产权',
    value: 1500000,
    rarity: 'unique',
    control_level: 1.0,
    competitiveness: 0.9
  },
  'crt_trade_secrets': {
    name: '商业秘密',
    description: '核心工艺和商业机密',
    value: 1000000,
    rarity: 'unique',
    control_level: 0.95,
    competitiveness: 0.85
  },
  'crt_software_systems': {
    name: '软件系统',
    description: '核心业务软件和系统',
    value: 800000,
    rarity: 'rare',
    control_level: 0.9,
    competitiveness: 0.8
  }
};
```

##### 人力资源 (Human Resources)
```typescript
const humanResources = {
  'crt_key_talents': {
    name: '关键人才',
    description: '核心技术和管理的关键人员',
    value: 500000,
    rarity: 'unique',
    control_level: 0.7,
    competitiveness: 0.9
  },
  'crt_management_team': {
    name: '管理团队',
    description: '高级管理团队和决策层',
    value: 300000,
    rarity: 'rare',
    control_level: 0.8,
    competitiveness: 0.85
  },
  'crt_technical_experts': {
    name: '技术专家',
    description: '专业技术领域的专家团队',
    value: 400000,
    rarity: 'rare',
    control_level: 0.75,
    competitiveness: 0.8
  },
  'crt_sales_team': {
    name: '销售团队',
    description: '销售和市场推广团队',
    value: 200000,
    rarity: 'common',
    control_level: 0.8,
    competitiveness: 0.7
  }
};
```

##### 财务资源 (Financial Resources)
```typescript
const financialResources = {
  'crt_cash_reserves': {
    name: '现金储备',
    description: '企业现金和流动资金',
    value: 1000000,
    rarity: 'common',
    control_level: 1.0,
    competitiveness: 0.6
  },
  'crt_credit_facilities': {
    name: '信贷额度',
    description: '银行信贷和融资能力',
    value: 500000,
    rarity: 'common',
    control_level: 0.8,
    competitiveness: 0.5
  },
  'crt_investment_portfolio': {
    name: '投资组合',
    description: '投资和资产组合',
    value: 800000,
    rarity: 'rare',
    control_level: 0.9,
    competitiveness: 0.7
  }
};
```

##### 关系资源 (Relational Resources)
```typescript
const relationalResources = {
  'crt_supplier_network': {
    name: '供应商网络',
    description: '核心供应商和合作伙伴关系',
    value: 300000,
    rarity: 'rare',
    control_level: 0.6,
    competitiveness: 0.8
  },
  'crt_customer_relationships': {
    name: '客户关系',
    description: '核心客户和长期合作关系',
    value: 400000,
    rarity: 'rare',
    control_level: 0.7,
    competitiveness: 0.85
  },
  'crt_distribution_channels': {
    name: '分销渠道',
    description: '销售和分销网络',
    value: 250000,
    rarity: 'common',
    control_level: 0.8,
    competitiveness: 0.7
  },
  'crt_government_relations': {
    name: '政府关系',
    description: '政府监管和政策关系',
    value: 150000,
    rarity: 'rare',
    control_level: 0.5,
    competitiveness: 0.6
  }
};
```

### 2. 核心能力标签 (Core Capabilities Tags - CCT)

#### 2.1 标签分类
```typescript
interface CoreCapabilityTag {
  cct_id: string;
  cct_name: string;
  cct_category: 'technical' | 'operational' | 'strategic' | 'innovative' | 'organizational';
  cct_type: 'hard' | 'soft';
  cct_description: string;
  cct_maturity_level: number; // 成熟度 (0-1)
  cct_development_cost: number; // 建设成本
  cct_competitive_advantage: number; // 竞争优势 (0-1)
  cct_transferability: number; // 可转移性 (0-1)
  created_at: Date;
  updated_at: Date;
}
```

#### 2.2 核心能力标签类型

##### 技术能力 (Technical Capabilities)
```typescript
const technicalCapabilities = {
  'cct_rd_innovation': {
    name: '研发创新能力',
    description: '产品研发和技术创新能力',
    maturity_level: 0.8,
    development_cost: 2000000,
    competitive_advantage: 0.9,
    transferability: 0.3
  },
  'cct_production_technology': {
    name: '生产技术能力',
    description: '先进生产技术和工艺能力',
    maturity_level: 0.85,
    development_cost: 1500000,
    competitive_advantage: 0.8,
    transferability: 0.4
  },
  'cct_quality_control': {
    name: '质量控制能力',
    description: '产品质量管理和控制能力',
    maturity_level: 0.9,
    development_cost: 500000,
    competitive_advantage: 0.7,
    transferability: 0.6
  },
  'cct_digital_transformation': {
    name: '数字化转型能力',
    description: '数字化技术和系统应用能力',
    maturity_level: 0.6,
    development_cost: 1000000,
    competitive_advantage: 0.85,
    transferability: 0.5
  }
};
```

##### 运营能力 (Operational Capabilities)
```typescript
const operationalCapabilities = {
  'cct_supply_chain_management': {
    name: '供应链管理能力',
    description: '供应链优化和管理能力',
    maturity_level: 0.8,
    development_cost: 800000,
    competitive_advantage: 0.75,
    transferability: 0.7
  },
  'cct_logistics_distribution': {
    name: '物流配送能力',
    description: '物流网络和配送管理能力',
    maturity_level: 0.85,
    development_cost: 600000,
    competitive_advantage: 0.7,
    transferability: 0.8
  },
  'cct_inventory_management': {
    name: '库存管理能力',
    description: '库存优化和管理能力',
    maturity_level: 0.9,
    development_cost: 300000,
    competitive_advantage: 0.6,
    transferability: 0.9
  },
  'cct_cost_optimization': {
    name: '成本优化能力',
    description: '成本控制和优化能力',
    maturity_level: 0.85,
    development_cost: 400000,
    competitive_advantage: 0.8,
    transferability: 0.8
  }
};
```

##### 战略能力 (Strategic Capabilities)
```typescript
const strategicCapabilities = {
  'cct_market_analysis': {
    name: '市场分析能力',
    description: '市场趋势分析和预测能力',
    maturity_level: 0.7,
    development_cost: 500000,
    competitive_advantage: 0.8,
    transferability: 0.6
  },
  'cct_strategic_planning': {
    name: '战略规划能力',
    description: '长期战略规划和执行能力',
    maturity_level: 0.75,
    development_cost: 600000,
    competitive_advantage: 0.85,
    transferability: 0.4
  },
  'cct_risk_management': {
    name: '风险管理能力',
    description: '风险识别和控制能力',
    maturity_level: 0.8,
    development_cost: 400000,
    competitive_advantage: 0.7,
    transferability: 0.7
  },
  'cct_competitive_intelligence': {
    name: '竞争情报能力',
    description: '竞争对手分析和情报收集能力',
    maturity_level: 0.65,
    development_cost: 300000,
    competitive_advantage: 0.75,
    transferability: 0.5
  }
};
```

##### 创新能力 (Innovative Capabilities)
```typescript
const innovativeCapabilities = {
  'cct_product_innovation': {
    name: '产品创新能力',
    description: '新产品开发和创新设计能力',
    maturity_level: 0.8,
    development_cost: 1500000,
    competitive_advantage: 0.9,
    transferability: 0.3
  },
  'cct_business_model_innovation': {
    name: '商业模式创新能力',
    description: '商业模式创新和优化能力',
    maturity_level: 0.6,
    development_cost: 800000,
    competitive_advantage: 0.85,
    transferability: 0.2
  },
  'cct_process_innovation': {
    name: '流程创新能力',
    description: '业务流程创新和优化能力',
    maturity_level: 0.75,
    development_cost: 600000,
    competitive_advantage: 0.8,
    transferability: 0.4
  },
  'cct_technology_adoption': {
    name: '技术采用能力',
    description: '新技术采用和应用能力',
    maturity_level: 0.7,
    development_cost: 700000,
    competitive_advantage: 0.75,
    transferability: 0.6
  }
};
```

##### 组织能力 (Organizational Capabilities)
```typescript
const organizationalCapabilities = {
  'cct_leadership_management': {
    name: '领导管理能力',
    description: '领导力和管理能力',
    maturity_level: 0.8,
    development_cost: 500000,
    competitive_advantage: 0.8,
    transferability: 0.3
  },
  'cct_team_collaboration': {
    name: '团队协作能力',
    description: '团队合作和协作能力',
    maturity_level: 0.85,
    development_cost: 300000,
    competitive_advantage: 0.7,
    transferability: 0.6
  },
  'cct_knowledge_management': {
    name: '知识管理能力',
    description: '知识积累和分享能力',
    maturity_level: 0.7,
    development_cost: 400000,
    competitive_advantage: 0.75,
    transferability: 0.5
  },
  'cct_change_management': {
    name: '变革管理能力',
    description: '组织变革和适应能力',
    maturity_level: 0.65,
    development_cost: 600000,
    competitive_advantage: 0.8,
    transferability: 0.4
  }
};
```

---

## 🗄️ 数据库表设计

### 1. 核心资源标签表
```sql
CREATE TABLE dim_core_resource_tags (
    crt_id VARCHAR(50) PRIMARY KEY,
    crt_name VARCHAR(100) NOT NULL,
    crt_category VARCHAR(50) NOT NULL,
    crt_type VARCHAR(20) NOT NULL,
    crt_description TEXT,
    crt_value DECIMAL(15,2),
    crt_rarity VARCHAR(20),
    crt_control_level DECIMAL(3,2),
    crt_competitiveness DECIMAL(3,2),
    crt_status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_crt_category ON dim_core_resource_tags(crt_category);
CREATE INDEX idx_crt_type ON dim_core_resource_tags(crt_type);
CREATE INDEX idx_crt_rarity ON dim_core_resource_tags(crt_rarity);
```

### 2. 核心能力标签表
```sql
CREATE TABLE dim_core_capability_tags (
    cct_id VARCHAR(50) PRIMARY KEY,
    cct_name VARCHAR(100) NOT NULL,
    cct_category VARCHAR(50) NOT NULL,
    cct_type VARCHAR(20) NOT NULL,
    cct_description TEXT,
    cct_maturity_level DECIMAL(3,2),
    cct_development_cost DECIMAL(15,2),
    cct_competitive_advantage DECIMAL(3,2),
    cct_transferability DECIMAL(3,2),
    cct_status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_cct_category ON dim_core_capability_tags(cct_category);
CREATE INDEX idx_cct_type ON dim_core_capability_tags(cct_type);
CREATE INDEX idx_cct_maturity ON dim_core_capability_tags(cct_maturity_level);
```

### 3. 决策-核心资源关联表
```sql
CREATE TABLE bridge_decision_core_resources (
    bridge_id VARCHAR(50) PRIMARY KEY,
    decision_id VARCHAR(50) NOT NULL,
    crt_id VARCHAR(50) NOT NULL,
    resource_intent VARCHAR(100), -- 资源控制意图
    control_target DECIMAL(3,2), -- 控制目标
    current_control_level DECIMAL(3,2), -- 当前控制水平
    investment_amount DECIMAL(15,2), -- 投资金额
    expected_roi DECIMAL(5,4), -- 预期投资回报率
    priority_level VARCHAR(20), -- 优先级
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (decision_id) REFERENCES hierarchical_decisions(decision_id),
    FOREIGN KEY (crt_id) REFERENCES dim_core_resource_tags(crt_id)
);
```

### 4. 决策-核心能力关联表
```sql
CREATE TABLE bridge_decision_core_capabilities (
    bridge_id VARCHAR(50) PRIMARY KEY,
    decision_id VARCHAR(50) NOT NULL,
    cct_id VARCHAR(50) NOT NULL,
    capability_intent VARCHAR(100), -- 能力建设意图
    development_target DECIMAL(3,2), -- 发展目标
    current_maturity_level DECIMAL(3,2), -- 当前成熟度
    development_investment DECIMAL(15,2), -- 建设投资
    expected_advantage DECIMAL(3,2), -- 预期竞争优势
    priority_level VARCHAR(20), -- 优先级
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (decision_id) REFERENCES hierarchical_decisions(decision_id),
    FOREIGN KEY (cct_id) REFERENCES dim_core_capability_tags(cct_id)
);
```

---

## 🎯 决策记录中的核心资源与能力

### 1. 决策意图扩展
```typescript
interface DecisionIntent {
  decision_id: string;
  primary_intent: string; // 主要意图
  resource_intents: Array<{
    crt_id: string;
    intent: string; // 如："控制核心制造技术"
    target_control_level: number;
    investment_plan: number;
  }>;
  capability_intents: Array<{
    cct_id: string;
    intent: string; // 如："建设研发创新能力"
    target_maturity_level: number;
    development_plan: number;
  }>;
  quantitative_targets: {
    resource_control_targets: Record<string, number>;
    capability_development_targets: Record<string, number>;
  };
}
```

### 2. 决策示例

#### 示例1: 技术升级决策
```typescript
const techUpgradeDecision = {
  decision_id: "STR-TECH-20250119-001",
  decision_level: "strategic",
  primary_intent: "提升企业技术竞争力",
  resource_intents: [
    {
      crt_id: "crt_technology_equipment",
      intent: "控制先进生产技术设备",
      target_control_level: 0.95,
      investment_plan: 2000000
    },
    {
      crt_id: "crt_patents",
      intent: "获取核心技术专利",
      target_control_level: 1.0,
      investment_plan: 5000000
    }
  ],
  capability_intents: [
    {
      cct_id: "cct_rd_innovation",
      intent: "建设世界级研发创新能力",
      target_maturity_level: 0.95,
      development_plan: 3000000
    },
    {
      cct_id: "cct_production_technology",
      intent: "提升先进生产技术能力",
      target_maturity_level: 0.9,
      development_plan: 1500000
    }
  ],
  quantitative_targets: {
    resource_control_targets: {
      "crt_technology_equipment": 0.95,
      "crt_patents": 1.0
    },
    capability_development_targets: {
      "cct_rd_innovation": 0.95,
      "cct_production_technology": 0.9
    }
  }
};
```

#### 示例2: 供应链优化决策
```typescript
const supplyChainDecision = {
  decision_id: "TAC-SUPPLY-20250119-001",
  decision_level: "tactical",
  primary_intent: "优化供应链管理效率",
  resource_intents: [
    {
      crt_id: "crt_supplier_network",
      intent: "强化核心供应商关系",
      target_control_level: 0.8,
      investment_plan: 500000
    },
    {
      crt_id: "crt_warehouse_logistics",
      intent: "扩展仓储物流网络",
      target_control_level: 0.85,
      investment_plan: 800000
    }
  ],
  capability_intents: [
    {
      cct_id: "cct_supply_chain_management",
      intent: "建设智能供应链管理能力",
      target_maturity_level: 0.9,
      development_plan: 1000000
    },
    {
      cct_id: "cct_logistics_distribution",
      intent: "提升物流配送效率",
      target_maturity_level: 0.85,
      development_plan: 600000
    }
  ]
};
```

---

## 🔄 价值链中的核心资源与能力

### 1. 价值链环节映射
```typescript
const valueChainMapping = {
  "核心资源+能力": {
    core_resources: [
      "crt_manufacturing_facility",
      "crt_technology_equipment",
      "crt_key_talents",
      "crt_patents"
    ],
    core_capabilities: [
      "cct_production_technology",
      "cct_rd_innovation",
      "cct_quality_control"
    ],
    key_metrics: [
      "资源控制率",
      "能力成熟度",
      "资源价值",
      "能力竞争优势"
    ]
  },
  "产品特性": {
    core_resources: [
      "crt_patents",
      "crt_trade_secrets",
      "crt_software_systems"
    ],
    core_capabilities: [
      "cct_product_innovation",
      "cct_rd_innovation",
      "cct_quality_control"
    ],
    key_metrics: [
      "专利覆盖率",
      "创新能力指数",
      "质量能力水平"
    ]
  },
  "价值主张": {
    core_resources: [
      "crt_trademarks",
      "crt_customer_relationships",
      "crt_brand_value"
    ],
    core_capabilities: [
      "cct_market_analysis",
      "cct_customer_relationship_management",
      "cct_brand_management"
    ],
    key_metrics: [
      "品牌价值",
      "客户关系强度",
      "市场分析能力"
    ]
  }
};
```

### 2. 资源能力评估算法
```typescript
class ResourceCapabilityEvaluator {
  // 评估资源控制效果
  evaluateResourceControl(decisionId: string, crtId: string): {
    currentLevel: number;
    targetLevel: number;
    progress: number;
    effectiveness: number;
  } {
    // 实现资源控制效果评估逻辑
  }
  
  // 评估能力建设效果
  evaluateCapabilityDevelopment(decisionId: string, cctId: string): {
    currentMaturity: number;
    targetMaturity: number;
    progress: number;
    effectiveness: number;
  } {
    // 实现能力建设效果评估逻辑
  }
  
  // 计算资源能力综合价值
  calculateResourceCapabilityValue(decisionId: string): {
    totalResourceValue: number;
    totalCapabilityValue: number;
    combinedValue: number;
    roi: number;
  } {
    // 实现综合价值计算逻辑
  }
}
```

---

## 📊 业务洞察生成

### 1. 资源能力分析洞察
```typescript
interface ResourceCapabilityInsight {
  insight_type: 'resource_gap' | 'capability_gap' | 'investment_opportunity' | 'risk_warning';
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  affected_resources: string[];
  affected_capabilities: string[];
  recommendations: string[];
  expected_impact: {
    resource_improvement: number;
    capability_improvement: number;
    competitive_advantage: number;
    roi: number;
  };
}
```

### 2. 洞察生成示例
```typescript
const resourceCapabilityInsights = [
  {
    insight_type: 'resource_gap',
    priority: 'high',
    title: '核心技术专利控制不足',
    description: '当前核心专利控制率仅为60%，低于行业平均75%',
    affected_resources: ['crt_patents', 'crt_trade_secrets'],
    affected_capabilities: ['cct_rd_innovation'],
    recommendations: [
      '加大专利申请投入',
      '收购相关技术专利',
      '建立专利保护机制'
    ],
    expected_impact: {
      resource_improvement: 0.2,
      capability_improvement: 0.15,
      competitive_advantage: 0.25,
      roi: 2.5
    }
  },
  {
    insight_type: 'capability_gap',
    priority: 'medium',
    title: '数字化转型能力待提升',
    description: '数字化能力成熟度仅为60%，影响运营效率',
    affected_resources: ['crt_software_systems', 'crt_technology_equipment'],
    affected_capabilities: ['cct_digital_transformation'],
    recommendations: [
      '投资数字化基础设施',
      '培训数字化人才',
      '引入先进数字化工具'
    ],
    expected_impact: {
      resource_improvement: 0.15,
      capability_improvement: 0.3,
      competitive_advantage: 0.2,
      roi: 1.8
    }
  }
];
```

---

## 🎯 实施建议

### 1. 标签体系建设
1. **第一阶段**: 创建核心资源和能力标签表
2. **第二阶段**: 建立决策关联机制
3. **第三阶段**: 开发评估和分析算法
4. **第四阶段**: 集成到价值链分析中

### 2. 决策记录扩展
1. **扩展决策意图字段**: 包含资源控制和能力建设意图
2. **增加量化目标**: 资源控制目标和能力发展目标
3. **建立关联关系**: 决策与资源能力的关联
4. **开发评估机制**: 资源能力建设效果评估

### 3. 价值链分析增强
1. **资源能力映射**: 将资源能力映射到价值链各环节
2. **效果评估**: 评估资源能力对价值链效率的影响
3. **优化建议**: 基于资源能力分析生成优化建议
4. **投资决策**: 支持资源能力投资决策

---

**这个设计将核心资源和核心能力作为企业的重要资产纳入BMOS系统，确保决策记录能够体现对它们的控制和建设意图，为企业的战略发展提供更全面的支持！** 🎉



