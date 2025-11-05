from fastapi import APIRouter

router = APIRouter(prefix="/marginal", tags=["边际分析（Mock）"])


@router.get("/assets")
async def list_assets_mock():
    return {
        "items": [
            {
                "asset_id": "a-001",
                "asset_code": "A001",
                "asset_name": "生产设备A",
                "asset_type": "tangible",
                "acquisition_cost": 1200000.0,
                "discount_rate": 0.1,
                "cash_flow_years": 5,
                "annual_cash_flow": [320000, 300000, 280000, 260000, 240000],
                "calculated_npv": 1123456.0,
            }
        ],
        "mock": True,
    }


@router.get("/capabilities")
async def list_capabilities_mock():
    return {
        "items": [
            {
                "capability_id": "c-001",
                "capability_code": "C001",
                "capability_name": "生产能力",
                "capability_type": "operational",
                "proficiency_score": 0.86,
                "utilization_rate": 0.73,
                "contribution_percentage": 0.42,
                "monthly_value": 85000.0,
            }
        ],
        "mock": True,
    }


@router.get("/value-items")
async def list_value_items_mock():
    return {
        "items": [
            {
                "value_item_id": "v-001",
                "value_item_code": "V_FUNC_QUALITY",
                "value_item_name": "功能-质量",
                "value_type": "functional",
                "value_category": "quality",
                "baseline_value": 0.8,
                "target_value": 0.9,
                "weight_factor": 0.25,
                "importance_score": 0.9,
            }
        ],
        "mock": True,
    }


@router.get("/delta-metrics")
async def list_delta_metrics_mock():
    return {
        "items": [
            {
                "metric_code": "profit_delta",
                "reporting_month": "2025-10-01",
                "delta_value": 120000.0,
                "trend_strength": 0.62,
            },
            {
                "metric_code": "first_order_revenue",
                "reporting_month": "2025-10-01",
                "delta_value": 48000.0,
                "trend_strength": 0.55,
            },
        ],
        "mock": True,
    }


@router.get("/feedback-config")
async def list_feedback_config_mock():
    return {
        "items": [
            {
                "config_name": "profit_reinvest_rule",
                "trigger_conditions": {"profit_delta_gt": 100000},
                "feedback_actions": {
                    "reinvest_to": ["assets:production", "capability:rd"],
                    "ratio": 0.2,
                },
            }
        ],
        "mock": True,
    }


@router.get("/model-parameters")
async def list_model_parameters_mock():
    return {
        "items": [
            {
                "model_type": "VAR_baseline",
                "parameters": {"lags": 2, "aic": 1234.5},
                "accuracy_score": 0.78,
            },
            {
                "model_type": "DynamicWeight",
                "parameters": {"context_dims": 8},
                "accuracy_score": 0.81,
            },
        ],
        "mock": True,
    }
