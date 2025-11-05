"""
性能监控和告警系统
提供性能指标收集、监控、告警等功能
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from collections import deque
import psutil
import redis

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """指标类型枚举"""

    COUNTER = "counter"  # 计数器
    GAUGE = "gauge"  # 仪表盘
    HISTOGRAM = "histogram"  # 直方图
    TIMER = "timer"  # 计时器


class AlertSeverity(Enum):
    """告警严重程度枚举"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """告警状态枚举"""

    ACTIVE = "active"  # 活跃
    ACKNOWLEDGED = "acknowledged"  # 已确认
    RESOLVED = "resolved"  # 已解决
    SUPPRESSED = "suppressed"  # 已抑制


@dataclass
class Metric:
    """指标模型"""

    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str]
    metric_type: MetricType


@dataclass
class AlertRule:
    """告警规则模型"""

    id: str
    name: str
    metric_name: str
    condition: str  # 'gt', 'lt', 'eq', 'neq'
    threshold: float
    severity: AlertSeverity
    enabled: bool
    notification_channels: List[str]


@dataclass
class Alert:
    """告警模型"""

    id: str
    rule_id: str
    metric_name: str
    current_value: float
    threshold: float
    severity: AlertSeverity
    status: AlertStatus
    triggered_at: datetime
    resolved_at: Optional[datetime]
    message: str
    notification_sent: bool


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self, db_service, cache_service):
        self.db_service = db_service
        self.cache_service = cache_service

        # 指标缓存
        self.metrics_cache = {}

        # 告警规则
        self.alert_rules = []

        # 活跃告警
        self.active_alerts = {}

        # 指标历史（最近1小时）
        self.metrics_history = deque(maxlen=3600)

        # 系统指标收集
        self.system_metrics_enabled = True

    async def collect_metric(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
        metric_type: MetricType = MetricType.GAUGE,
    ):
        """收集指标"""
        try:
            metric = Metric(
                name=name,
                value=value,
                timestamp=datetime.now(),
                tags=tags or {},
                metric_type=metric_type,
            )

            # 添加到历史
            self.metrics_history.append(metric)

            # 更新缓存
            self.metrics_cache[name] = metric

            # 检查告警规则
            await self._check_alert_rules(metric)

            # 定期保存到数据库
            if len(self.metrics_history) % 100 == 0:
                await self._save_metrics_to_db(self.metrics_history)

        except Exception as e:
            logger.error(f"Failed to collect metric: {str(e)}")

    async def get_metric(self, name: str) -> Optional[Metric]:
        """获取指标"""
        try:
            return self.metrics_cache.get(name)

        except Exception as e:
            logger.error(f"Failed to get metric: {str(e)}")
            return None

    async def get_metrics_history(
        self,
        name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[Metric]:
        """获取指标历史"""
        try:
            if start_time and end_time:
                history = [
                    m
                    for m in self.metrics_history
                    if m.name == name and start_time <= m.timestamp <= end_time
                ]
            else:
                history = [m for m in self.metrics_history if m.name == name]

            # 排序并限制数量
            history.sort(key=lambda x: x.timestamp, reverse=True)
            return history[:limit]

        except Exception as e:
            logger.error(f"Failed to get metrics history: {str(e)}")
            return []

    async def create_alert_rule(
        self,
        name: str,
        metric_name: str,
        condition: str,
        threshold: float,
        severity: AlertSeverity,
        notification_channels: List[str],
    ) -> str:
        """创建告警规则"""
        try:
            rule_id = f"alert_rule_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            rule = AlertRule(
                id=rule_id,
                name=name,
                metric_name=metric_name,
                condition=condition,
                threshold=threshold,
                severity=severity,
                enabled=True,
                notification_channels=notification_channels,
            )

            self.alert_rules.append(rule)

            logger.info(f"Created alert rule: {rule_id}")
            return rule_id

        except Exception as e:
            logger.error(f"Failed to create alert rule: {str(e)}")
            raise

    async def get_active_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        metric_name: Optional[str] = None,
    ) -> List[Alert]:
        """获取活跃告警"""
        try:
            alerts = list(self.active_alerts.values())

            if severity:
                alerts = [a for a in alerts if a.severity == severity]

            if metric_name:
                alerts = [a for a in alerts if a.metric_name == metric_name]

            return alerts

        except Exception as e:
            logger.error(f"Failed to get active alerts: {str(e)}")
            return []

    async def acknowledge_alert(self, alert_id: str) -> bool:
        """确认告警"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = AlertStatus.ACKNOWLEDGED
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {str(e)}")
            return False

    async def resolve_alert(self, alert_id: str) -> bool:
        """解决告警"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.now()

                # 从活跃告警中移除
                del self.active_alerts[alert_id]

                return True

            return False

        except Exception as e:
            logger.error(f"Failed to resolve alert: {str(e)}")
            return False

    async def get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        try:
            if not self.system_metrics_enabled:
                return {}

            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)

            # 内存使用情况
            memory = psutil.virtual_memory()

            # 磁盘使用情况
            disk = psutil.disk_usage("/")

            # 网络IO
            network = psutil.net_io_counters()

            metrics = {
                "cpu": {"percent": cpu_percent, "cores": psutil.cpu_count()},
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent,
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                },
                "timestamp": datetime.now().isoformat(),
            }

            return metrics

        except Exception as e:
            logger.error(f"Failed to get system metrics: {str(e)}")
            return {}

    # ==================== 私有方法 ====================

    async def _check_alert_rules(self, metric: Metric):
        """检查告警规则"""
        try:
            # 查找相关的告警规则
            for rule in self.alert_rules:
                if not rule.enabled:
                    continue

                if rule.metric_name != metric.name:
                    continue

                # 检查条件
                if self._evaluate_condition(
                    metric.value, rule.condition, rule.threshold
                ):
                    # 触发告警
                    await self._trigger_alert(rule, metric)

        except Exception as e:
            logger.error(f"Failed to check alert rules: {str(e)}")

    def _evaluate_condition(
        self, value: float, condition: str, threshold: float
    ) -> bool:
        """评估条件"""
        try:
            if condition == "gt":
                return value > threshold
            elif condition == "lt":
                return value < threshold
            elif condition == "eq":
                return value == threshold
            elif condition == "neq":
                return value != threshold
            elif condition == "gte":
                return value >= threshold
            elif condition == "lte":
                return value <= threshold
            else:
                return False

        except Exception as e:
            logger.error(f"Failed to evaluate condition: {str(e)}")
            return False

    async def _trigger_alert(self, rule: AlertRule, metric: Metric):
        """触发告警"""
        try:
            # 检查是否已经存在相同的告警
            existing_alert = None
            for alert in self.active_alerts.values():
                if alert.rule_id == rule.id and alert.status == AlertStatus.ACTIVE:
                    existing_alert = alert
                    break

            if existing_alert:
                # 更新现有告警
                existing_alert.current_value = metric.value
                existing_alert.triggered_at = datetime.now()
            else:
                # 创建新告警
                alert_id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                alert = Alert(
                    id=alert_id,
                    rule_id=rule.id,
                    metric_name=rule.metric_name,
                    current_value=metric.value,
                    threshold=rule.threshold,
                    severity=rule.severity,
                    status=AlertStatus.ACTIVE,
                    triggered_at=datetime.now(),
                    resolved_at=None,
                    message=f"{rule.name}: {metric.name} = {metric.value} {rule.condition} {rule.threshold}",
                    notification_sent=False,
                )

                self.active_alerts[alert_id] = alert

                # 发送通知
                await self._send_notification(alert, rule.notification_channels)

                logger.warning(f"Alert triggered: {alert.message}")

        except Exception as e:
            logger.error(f"Failed to trigger alert: {str(e)}")

    async def _send_notification(self, alert: Alert, channels: List[str]):
        """发送通知"""
        try:
            notification_message = {
                "alert_id": alert.id,
                "severity": alert.severity.value,
                "metric_name": alert.metric_name,
                "current_value": alert.current_value,
                "threshold": alert.threshold,
                "message": alert.message,
                "triggered_at": alert.triggered_at.isoformat(),
            }

            # 这里可以实现发送通知的逻辑
            # 例如：发送邮件、短信、Slack消息等

            logger.info(f"Notification sent to {channels}: {notification_message}")
            alert.notification_sent = True

        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")

    async def _save_metrics_to_db(self, metrics: deque):
        """保存指标到数据库"""
        try:
            # 这里可以实现保存到数据库的逻辑
            # 暂时跳过
            pass

        except Exception as e:
            logger.error(f"Failed to save metrics to database: {str(e)}")


class AlertManager:
    """告警管理器"""

    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor

    async def create_alert_rule(
        self,
        name: str,
        metric_name: str,
        condition: str,
        threshold: float,
        severity: AlertSeverity,
        notification_channels: List[str],
    ) -> str:
        """创建告警规则"""
        return await self.monitor.create_alert_rule(
            name, metric_name, condition, threshold, severity, notification_channels
        )

    async def get_active_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        metric_name: Optional[str] = None,
    ) -> List[Alert]:
        """获取活跃告警"""
        return await self.monitor.get_active_alerts(severity, metric_name)

    async def acknowledge_alert(self, alert_id: str) -> bool:
        """确认告警"""
        return await self.monitor.acknowledge_alert(alert_id)

    async def resolve_alert(self, alert_id: str) -> bool:
        """解决告警"""
        return await self.monitor.resolve_alert(alert_id)

    async def get_alert_stats(self) -> Dict[str, Any]:
        """获取告警统计"""
        try:
            all_alerts = list(self.monitor.active_alerts.values())

            stats = {
                "total_alerts": len(all_alerts),
                "by_severity": {
                    severity.value: len(
                        [a for a in all_alerts if a.severity == severity]
                    )
                    for severity in AlertSeverity
                },
                "by_status": {
                    status.value: len([a for a in all_alerts if a.status == status])
                    for status in AlertStatus
                },
            }

            return stats

        except Exception as e:
            logger.error(f"Failed to get alert stats: {str(e)}")
            return {}
