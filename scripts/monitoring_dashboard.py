"""
BMOS系统 - 监控大屏配置
Grafana仪表盘配置
"""

GRAFANA_DASHBOARD_CONFIG = {
    "dashboard": {
        "title": "BMOS系统监控大屏",
        "tags": ["bmos", "monitoring"],
        "timezone": "browser",
        "refresh": "5s",
        "panels": [
            {
                "title": "系统健康状态",
                "type": "stat",
                "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0},
                "targets": [
                    {
                        "expr": "bmos_health_status",
                        "legendFormat": "健康状态"
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "color": {"mode": "thresholds"},
                        "mappings": [
                            {"options": {"0": {"text": "不健康"}}, "type": "value"},
                            {"options": {"1": {"text": "健康"}}, "type": "value"}
                        ],
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"value": 0, "color": "red"},
                                {"value": 1, "color": "green"}
                            ]
                        }
                    }
                }
            },
            {
                "title": "API请求速率",
                "type": "graph",
                "gridPos": {"h": 8, "w": 12, "x": 6, "y": 0},
                "targets": [
                    {
                        "expr": "rate(bmos_http_requests_total[5m])",
                        "legendFormat": "{{method}} {{endpoint}}",
                        "refId": "A"
                    }
                ],
                "yAxes": [
                    {
                        "format": "reqps",
                        "label": "请求/秒"
                    }
                ]
            },
            {
                "title": "API响应时间分布",
                "type": "heatmap",
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
                "targets": [
                    {
                        "expr": "histogram_quantile(0.95, rate(bmos_http_request_duration_seconds_bucket[5m]))",
                        "legendFormat": "P95响应时间",
                        "refId": "A"
                    }
                ],
                "xAxis": {
                    "show": True,
                    "mode": "time"
                },
                "yAxis": {
                    "show": True,
                    "format": "ms"
                }
            },
            {
                "title": "错误率",
                "type": "stat",
                "gridPos": {"h": 4, "w": 6, "x": 12, "y": 0},
                "targets": [
                    {
                        "expr": "rate(bmos_http_requests_total{status=~\"5..\"}[5m]) / rate(bmos_http_requests_total[5m]) * 100",
                        "legendFormat": "错误率"
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "color": {"mode": "thresholds"},
                        "unit": "percent",
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"value": 0, "color": "green"},
                                {"value": 1, "color": "yellow"},
                                {"value": 5, "color": "red"}
                            ]
                        }
                    }
                }
            },
            {
                "title": "数据质量评分",
                "type": "gauge",
                "gridPos": {"h": 8, "w": 6, "x": 18, "y": 0},
                "targets": [
                    {
                        "expr": "avg(bmos_data_quality_score)",
                        "legendFormat": "平均质量评分"
                    }
                ],
                "fieldConfig": {
                    "defaults": {
                        "min": 0,
                        "max": 100,
                        "thresholds": {
                            "mode": "absolute",
                            "steps": [
                                {"value": 0, "color": "red"},
                                {"value": 70, "color": "yellow"},
                                {"value": 85, "color": "green"}
                            ]
                        },
                        "unit": "percent"
                    }
                }
            },
            {
                "title": "活跃任务数",
                "type": "graph",
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
                "targets": [
                    {
                        "expr": "bmos_scheduler_active_tasks",
                        "legendFormat": "活跃任务",
                        "refId": "A"
                    },
                    {
                        "expr": "bmos_scheduler_completed_tasks",
                        "legendFormat": "已完成任务",
                        "refId": "B"
                    },
                    {
                        "expr": "bmos_scheduler_failed_tasks",
                        "legendFormat": "失败任务",
                        "refId": "C"
                    }
                ]
            },
            {
                "title": "数据库连接池状态",
                "type": "graph",
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 16},
                "targets": [
                    {
                        "expr": "bmos_database_pool_size",
                        "legendFormat": "连接池大小",
                        "refId": "A"
                    },
                    {
                        "expr": "bmos_database_pool_active",
                        "legendFormat": "活跃连接",
                        "refId": "B"
                    },
                    {
                        "expr": "bmos_database_pool_idle",
                        "legendFormat": "空闲连接",
                        "refId": "C"
                    }
                ]
            },
            {
                "title": "Redis缓存命中率",
                "type": "graph",
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 16},
                "targets": [
                    {
                        "expr": "rate(bmos_redis_hits_total[5m]) / (rate(bmos_redis_hits_total[5m]) + rate(bmos_redis_misses_total[5m])) * 100",
                        "legendFormat": "缓存命中率",
                        "refId": "A"
                    }
                ],
                "yAxes": [
                    {
                        "format": "percent",
                        "min": 0,
                        "max": 100
                    }
                ]
            },
            {
                "title": "模型训练状态",
                "type": "table",
                "gridPos": {"h": 8, "w": 24, "x": 0, "y": 24},
                "targets": [
                    {
                        "expr": "bmos_model_training_status",
                        "format": "table",
                        "refId": "A"
                    }
                ],
                "columns": [
                    {"text": "模型ID"},
                    {"text": "模型类型"},
                    {"text": "训练状态"},
                    {"text": "准确度"},
                    {"text": "训练时长"}
                ]
            },
            {
                "title": "AI Copilot调用统计",
                "type": "piechart",
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 32},
                "targets": [
                    {
                        "expr": "sum by (tool_id) (bmos_ai_copilot_tool_calls_total)",
                        "legendFormat": "{{tool_id}}",
                        "refId": "A"
                    }
                ]
            },
            {
                "title": "数据导入统计",
                "type": "graph",
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 32},
                "targets": [
                    {
                        "expr": "rate(bmos_data_import_total[5m])",
                        "legendFormat": "导入速率",
                        "refId": "A"
                    },
                    {
                        "expr": "rate(bmos_data_import_errors_total[5m])",
                        "legendFormat": "错误速率",
                        "refId": "B"
                    }
                ]
            },
            {
                "title": "告警事件",
                "type": "alertlist",
                "gridPos": {"h": 8, "w": 24, "x": 0, "y": 40},
                "options": {
                    "onlyAlertsOnDashboard": False,
                    "rowsPerPage": 5,
                    "sortOrder": 1
                }
            }
        ]
    }
}

# 将配置保存为JSON文件
import json

def save_dashboard_config(filename: str = "bmos_dashboard.json"):
    """保存仪表盘配置到文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(GRAFANA_DASHBOARD_CONFIG, f, indent=2, ensure_ascii=False)
    print(f"仪表盘配置已保存到 {filename}")

if __name__ == "__main__":
    save_dashboard_config("bmos_dashboard.json")

