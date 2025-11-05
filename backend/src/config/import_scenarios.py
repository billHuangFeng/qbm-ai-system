"""
BMOS系统 - 导入场景配置
作用: 定义各种数据导入场景的配置，包括目标表、主数据匹配、验证规则等
状态: ✅ 实施中
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class TargetTableConfig(BaseModel):
    """目标表配置"""

    table_name: str
    display_name: str
    has_lines: bool = False
    line_table: Optional[str] = None
    header_ref_field: Optional[str] = None  # Line表引用Header的字段名（如header_id）


class MasterDataMatchingConfig(BaseModel):
    """主数据匹配配置"""

    enabled: bool = True
    field_name: str
    master_data_type: str  # customer/supplier/sku/channel
    matching_strategy: str = "fuzzy"  # exact/fuzzy/combined


class ValidationRuleConfig(BaseModel):
    """验证规则配置"""

    rule_type: str  # required/type/range/pattern/custom
    field: str
    level: str = "error"  # error/warning/info
    message: str
    validator_config: Optional[Dict[str, Any]] = None


class ImportScenarioConfig(BaseModel):
    """导入场景配置"""

    scenario_id: str
    scenario_name: str
    target_tables: Dict[str, TargetTableConfig]  # header/lines配置
    document_type: str  # header_detail/header_only/line_only/master_data
    master_data_matching: Optional[Dict[str, MasterDataMatchingConfig]] = None
    validation_rules: List[ValidationRuleConfig] = []
    import_strategy: Dict[str, Any] = {}


# ============================================
# 销售订单导入场景
# ============================================

SALES_ORDER_SCENARIO = ImportScenarioConfig(
    scenario_id="sales_order",
    scenario_name="销售订单导入",
    target_tables={
        "header": TargetTableConfig(
            table_name="sales_order_header",
            display_name="销售订单头表",
            has_lines=True,
            line_table="sales_order_line",
            header_ref_field="header_id",
        ),
        "lines": TargetTableConfig(
            table_name="sales_order_line",
            display_name="销售订单明细表",
            has_lines=False,
        ),
    },
    document_type="header_detail",
    master_data_matching={
        "customer": MasterDataMatchingConfig(
            enabled=True,
            field_name="customer_code",
            master_data_type="customer",
            matching_strategy="combined",
        ),
        "sku": MasterDataMatchingConfig(
            enabled=True,
            field_name="sku_code",
            master_data_type="sku",
            matching_strategy="combined",
        ),
        "channel": MasterDataMatchingConfig(
            enabled=False,
            field_name="channel_code",
            master_data_type="channel",
            matching_strategy="fuzzy",
        ),
    },
    validation_rules=[
        ValidationRuleConfig(
            rule_type="required",
            field="order_date",
            level="error",
            message="订单日期不能为空",
        ),
        ValidationRuleConfig(
            rule_type="required",
            field="customer_id",
            level="error",
            message="客户ID不能为空，请先匹配客户主数据",
        ),
        ValidationRuleConfig(
            rule_type="consistency",
            field="total_amount",
            level="error",
            message="Header总额必须等于Line金额之和",
        ),
    ],
    import_strategy={
        "format_type": "repeated_header",  # 支持的格式类型
        "batch_size": 1000,  # 批量导入大小
        "enable_auto_match": True,  # 是否启用自动匹配
        "require_confirmation": True,  # 是否需要用户确认
    },
)


# ============================================
# 发货单导入场景
# ============================================

SHIPMENT_SCENARIO = ImportScenarioConfig(
    scenario_id="shipment",
    scenario_name="发货单导入",
    target_tables={
        "header": TargetTableConfig(
            table_name="shipment_header",
            display_name="发货单头表",
            has_lines=True,
            line_table="shipment_line",
            header_ref_field="header_id",
        ),
        "lines": TargetTableConfig(
            table_name="shipment_line", display_name="发货单明细表", has_lines=False
        ),
    },
    document_type="header_detail",
    master_data_matching={
        "customer": MasterDataMatchingConfig(
            enabled=True,
            field_name="customer_code",
            master_data_type="customer",
            matching_strategy="combined",
        ),
        "sku": MasterDataMatchingConfig(
            enabled=True,
            field_name="sku_code",
            master_data_type="sku",
            matching_strategy="combined",
        ),
    },
    validation_rules=[
        ValidationRuleConfig(
            rule_type="required",
            field="shipment_date",
            level="error",
            message="发货日期不能为空",
        )
    ],
    import_strategy={
        "format_type": "repeated_header",
        "batch_size": 1000,
        "enable_auto_match": True,
        "require_confirmation": True,
    },
)


# ============================================
# 销售发票导入场景
# ============================================

SALES_INVOICE_SCENARIO = ImportScenarioConfig(
    scenario_id="sales_invoice",
    scenario_name="销售发票导入",
    target_tables={
        "header": TargetTableConfig(
            table_name="sales_invoice_header",
            display_name="销售发票头表",
            has_lines=True,
            line_table="sales_invoice_line",
            header_ref_field="header_id",
        ),
        "lines": TargetTableConfig(
            table_name="sales_invoice_line",
            display_name="销售发票明细表",
            has_lines=False,
        ),
    },
    document_type="header_detail",
    master_data_matching={
        "customer": MasterDataMatchingConfig(
            enabled=True,
            field_name="customer_code",
            master_data_type="customer",
            matching_strategy="combined",
        ),
        "sku": MasterDataMatchingConfig(
            enabled=True,
            field_name="sku_code",
            master_data_type="sku",
            matching_strategy="combined",
        ),
    },
    validation_rules=[
        ValidationRuleConfig(
            rule_type="required",
            field="invoice_date",
            level="error",
            message="发票日期不能为空",
        )
    ],
    import_strategy={
        "format_type": "repeated_header",
        "batch_size": 1000,
        "enable_auto_match": True,
        "require_confirmation": True,
    },
)


# ============================================
# 采购订单导入场景
# ============================================

PURCHASE_ORDER_SCENARIO = ImportScenarioConfig(
    scenario_id="purchase_order",
    scenario_name="采购订单导入",
    target_tables={
        "header": TargetTableConfig(
            table_name="purchase_order_header",
            display_name="采购订单头表",
            has_lines=True,
            line_table="purchase_order_line",
            header_ref_field="header_id",
        ),
        "lines": TargetTableConfig(
            table_name="purchase_order_line",
            display_name="采购订单明细表",
            has_lines=False,
        ),
    },
    document_type="header_detail",
    master_data_matching={
        "supplier": MasterDataMatchingConfig(
            enabled=True,
            field_name="supplier_code",
            master_data_type="supplier",
            matching_strategy="combined",
        ),
        "sku": MasterDataMatchingConfig(
            enabled=True,
            field_name="sku_code",
            master_data_type="sku",
            matching_strategy="combined",
        ),
    },
    validation_rules=[
        ValidationRuleConfig(
            rule_type="required",
            field="po_date",
            level="error",
            message="采购订单日期不能为空",
        ),
        ValidationRuleConfig(
            rule_type="required",
            field="supplier_id",
            level="error",
            message="供应商ID不能为空，请先匹配供应商主数据",
        ),
    ],
    import_strategy={
        "format_type": "repeated_header",
        "batch_size": 1000,
        "enable_auto_match": True,
        "require_confirmation": True,
    },
)


# ============================================
# 收货单导入场景
# ============================================

RECEIPT_SCENARIO = ImportScenarioConfig(
    scenario_id="receipt",
    scenario_name="收货单导入",
    target_tables={
        "header": TargetTableConfig(
            table_name="receipt_header",
            display_name="收货单头表",
            has_lines=True,
            line_table="receipt_line",
            header_ref_field="header_id",
        ),
        "lines": TargetTableConfig(
            table_name="receipt_line", display_name="收货单明细表", has_lines=False
        ),
    },
    document_type="header_detail",
    master_data_matching={
        "supplier": MasterDataMatchingConfig(
            enabled=True,
            field_name="supplier_code",
            master_data_type="supplier",
            matching_strategy="combined",
        ),
        "sku": MasterDataMatchingConfig(
            enabled=True,
            field_name="sku_code",
            master_data_type="sku",
            matching_strategy="combined",
        ),
    },
    validation_rules=[
        ValidationRuleConfig(
            rule_type="required",
            field="receipt_date",
            level="error",
            message="收货日期不能为空",
        )
    ],
    import_strategy={
        "format_type": "repeated_header",
        "batch_size": 1000,
        "enable_auto_match": True,
        "require_confirmation": True,
    },
)


# ============================================
# 采购发票导入场景
# ============================================

PURCHASE_INVOICE_SCENARIO = ImportScenarioConfig(
    scenario_id="purchase_invoice",
    scenario_name="采购发票导入",
    target_tables={
        "header": TargetTableConfig(
            table_name="purchase_invoice_header",
            display_name="采购发票头表",
            has_lines=True,
            line_table="purchase_invoice_line",
            header_ref_field="header_id",
        ),
        "lines": TargetTableConfig(
            table_name="purchase_invoice_line",
            display_name="采购发票明细表",
            has_lines=False,
        ),
    },
    document_type="header_detail",
    master_data_matching={
        "supplier": MasterDataMatchingConfig(
            enabled=True,
            field_name="supplier_code",
            master_data_type="supplier",
            matching_strategy="combined",
        ),
        "sku": MasterDataMatchingConfig(
            enabled=True,
            field_name="sku_code",
            master_data_type="sku",
            matching_strategy="combined",
        ),
    },
    validation_rules=[
        ValidationRuleConfig(
            rule_type="required",
            field="invoice_date",
            level="error",
            message="发票日期不能为空",
        )
    ],
    import_strategy={
        "format_type": "repeated_header",
        "batch_size": 1000,
        "enable_auto_match": True,
        "require_confirmation": True,
    },
)


# ============================================
# 客户主数据导入场景
# ============================================

CUSTOMER_MASTER_SCENARIO = ImportScenarioConfig(
    scenario_id="customer_master",
    scenario_name="客户主数据导入",
    target_tables={
        "master": TargetTableConfig(
            table_name="dim_customer", display_name="客户主数据表", has_lines=False
        )
    },
    document_type="master_data",
    master_data_matching=None,  # 主数据导入不需要匹配
    validation_rules=[
        ValidationRuleConfig(
            rule_type="required",
            field="customer_name",
            level="error",
            message="客户名称不能为空",
        ),
        ValidationRuleConfig(
            rule_type="unique",
            field="customer_code",
            level="error",
            message="客户代码必须唯一",
        ),
    ],
    import_strategy={
        "format_type": "first_row_header",
        "batch_size": 5000,
        "enable_auto_match": False,
        "require_confirmation": False,
    },
)


# ============================================
# 供应商主数据导入场景
# ============================================

SUPPLIER_MASTER_SCENARIO = ImportScenarioConfig(
    scenario_id="supplier_master",
    scenario_name="供应商主数据导入",
    target_tables={
        "master": TargetTableConfig(
            table_name="dim_supplier", display_name="供应商主数据表", has_lines=False
        )
    },
    document_type="master_data",
    master_data_matching=None,
    validation_rules=[
        ValidationRuleConfig(
            rule_type="required",
            field="supplier_name",
            level="error",
            message="供应商名称不能为空",
        )
    ],
    import_strategy={
        "format_type": "first_row_header",
        "batch_size": 5000,
        "enable_auto_match": False,
        "require_confirmation": False,
    },
)


# ============================================
# SKU主数据导入场景
# ============================================

SKU_MASTER_SCENARIO = ImportScenarioConfig(
    scenario_id="sku_master",
    scenario_name="SKU主数据导入",
    target_tables={
        "master": TargetTableConfig(
            table_name="dim_sku", display_name="SKU主数据表", has_lines=False
        )
    },
    document_type="master_data",
    master_data_matching=None,
    validation_rules=[
        ValidationRuleConfig(
            rule_type="required",
            field="sku_name",
            level="error",
            message="SKU名称不能为空",
        )
    ],
    import_strategy={
        "format_type": "first_row_header",
        "batch_size": 5000,
        "enable_auto_match": False,
        "require_confirmation": False,
    },
)


# ============================================
# 场景注册表
# ============================================

IMPORT_SCENARIOS: Dict[str, ImportScenarioConfig] = {
    "sales_order": SALES_ORDER_SCENARIO,
    "shipment": SHIPMENT_SCENARIO,
    "sales_invoice": SALES_INVOICE_SCENARIO,
    "purchase_order": PURCHASE_ORDER_SCENARIO,
    "receipt": RECEIPT_SCENARIO,
    "purchase_invoice": PURCHASE_INVOICE_SCENARIO,
    "customer_master": CUSTOMER_MASTER_SCENARIO,
    "supplier_master": SUPPLIER_MASTER_SCENARIO,
    "sku_master": SKU_MASTER_SCENARIO,
}


# ============================================
# 辅助函数
# ============================================


def get_scenario(scenario_id: str) -> Optional[ImportScenarioConfig]:
    """根据场景ID获取场景配置"""
    return IMPORT_SCENARIOS.get(scenario_id)


def get_scenario_by_document_type(document_type: str) -> Optional[ImportScenarioConfig]:
    """根据单据类型获取场景配置"""
    # 单据类型到场景ID的映射
    doc_type_to_scenario = {
        "SO": "sales_order",
        "SH": "shipment",
        "SI": "sales_invoice",
        "PO": "purchase_order",
        "RC": "receipt",
        "PI": "purchase_invoice",
    }

    scenario_id = doc_type_to_scenario.get(document_type)
    if scenario_id:
        return IMPORT_SCENARIOS.get(scenario_id)

    return None


def get_all_scenarios() -> Dict[str, ImportScenarioConfig]:
    """获取所有场景配置"""
    return IMPORT_SCENARIOS


def get_scenarios_by_category(category: str) -> List[ImportScenarioConfig]:
    """根据类别获取场景配置"""
    # 类别定义
    categories = {
        "销售流程": ["sales_order", "shipment", "sales_invoice"],
        "采购流程": ["purchase_order", "receipt", "purchase_invoice"],
        "主数据": ["customer_master", "supplier_master", "sku_master"],
    }

    scenario_ids = categories.get(category, [])
    return [IMPORT_SCENARIOS[sid] for sid in scenario_ids if sid in IMPORT_SCENARIOS]
