"""
观测性服务 - 指标采集、追踪系统、告警系统
"""
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class ExecutionMetrics:
    """执行指标"""
    task_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # 基础指标
    latency_ms: float = 0.0
    token_count: int = 0
    token_cost_usd: float = 0.0
    
    # 质量指标
    hallucination_rate: float = 0.0
    error_rate: float = 0.0
    retry_count: int = 0
    
    # 上下文指标
    memory_used: int = 0
    context_window_utilization: float = 0.0
    
    # 元数据
    model: str = ""
    task_type: str = ""


class ObservabilityService:
    """
    观测性服务
    记录和分析系统运行指标
    """

    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path
        self.realtime_metrics: List[ExecutionMetrics] = []
        self._metrics_buffer: Dict[str, List] = defaultdict(list)
        
        # 性能统计
        self.stats = {
            "total_requests": 0,
            "total_errors": 0,
            "total_tokens": 0,
            "avg_latency_ms": 0.0,
            "start_time": datetime.now(timezone.utc).isoformat()
        }

    def record_execution(self, metrics: ExecutionMetrics):
        """记录执行指标"""
        self.realtime_metrics.append(metrics)
        
        # 更新统计
        self.stats["total_requests"] += 1
        self.stats["total_tokens"] += metrics.token_count
        self.stats["total_errors"] += 1 if metrics.error_rate > 0 else 0
        
        # 实时计算平均延迟
        if self.stats["total_requests"] > 0:
            latencies = [m.latency_ms for m in self.realtime_metrics[-100:]]
            self.stats["avg_latency_ms"] = sum(latencies) / len(latencies)
        
        # 保持最近1000条
        if len(self.realtime_metrics) > 1000:
            self.realtime_metrics = self.realtime_metrics[-1000:]

    def get_dashboard_data(self) -> Dict:
        """获取仪表盘数据"""
        if not self.realtime_metrics:
            return self.stats
        
        recent = self.realtime_metrics[-100:]
        
        # 计算百分位数
        latencies = sorted([m.latency_ms for m in recent])
        
        def percentile(data: List, p: int) -> float:
            if not data:
                return 0.0
            idx = int(len(data) * p / 100)
            return data[min(idx, len(data) - 1)]
        
        return {
            **self.stats,
            "latency": {
                "avg": sum(latencies) / len(latencies) if latencies else 0,
                "p50": percentile(latencies, 50),
                "p95": percentile(latencies, 95),
                "p99": percentile(latencies, 99)
            },
            "tokens": {
                "total": sum(m.token_count for m in recent),
                "avg": sum(m.token_count for m in recent) / len(recent)
            },
            "quality": {
                "hallucination_rate": sum(m.hallucination_rate for m in recent) / len(recent),
                "error_rate": sum(m.error_rate for m in recent) / len(recent)
            },
            "retry_rate": sum(m.retry_count for m in recent) / len(recent),
            "uptime_seconds": (
                datetime.now(timezone.utc) - 
                datetime.fromisoformat(self.stats["start_time"])
            ).total_seconds()
        }

    def detect_drift(self, metric_name: str, threshold: float = 0.2) -> List[Dict]:
        """检测指标漂移"""
        if len(self.realtime_metrics) < 20:
            return []
        
        values = [getattr(m, metric_name) for m in self.realtime_metrics]
        
        # 简单漂移检测
        recent_10 = values[-10:]
        historical = values[:-10]
        
        if not historical:
            return []
        
        historical_mean = sum(historical) / len(historical)
        recent_mean = sum(recent_10) / len(recent_10)
        
        if historical_mean == 0:
            return []
        
        change_rate = abs(recent_mean - historical_mean) / historical_mean
        
        if change_rate > threshold:
            return [{
                "metric": metric_name,
                "change_rate": round(change_rate, 3),
                "threshold": threshold,
                "historical_mean": round(historical_mean, 3),
                "recent_mean": round(recent_mean, 3),
                "recommendation": "检查模型输出分布是否发生变化"
            }]
        
        return []

    def get_metrics_summary(self) -> Dict:
        """获取指标摘要"""
        return {
            "total_requests": self.stats["total_requests"],
            "total_errors": self.stats["total_errors"],
            "error_rate": self.stats["total_errors"] / max(1, self.stats["total_requests"]),
            "avg_latency_ms": round(self.stats["avg_latency_ms"], 2),
            "total_tokens": self.stats["total_tokens"]
        }


class AlertService:
    """
    告警服务
    支持分级告警：P0紧急 / P1重要 / P2一般 / P3通知
    """

    def __init__(self, observability: ObservabilityService = None):
        self.observability = observability
        self.alerts: List[Dict] = []
        self.alert_handlers: Dict[str, List] = defaultdict(list)
        
        # 告警规则
        self.rules = {
            "high_error_rate": {"threshold": 0.2, "level": "P0", "enabled": True},
            "high_latency": {"threshold_ms": 5000, "level": "P1", "enabled": True},
            "drift_detected": {"threshold": 0.3, "level": "P2", "enabled": True},
        }

    def check_and_alert(self, metrics: ExecutionMetrics) -> List[Dict]:
        """检查指标并触发告警"""
        new_alerts = []
        
        # 检查错误率
        if metrics.error_rate > self.rules["high_error_rate"]["threshold"]:
            alert = self._create_alert(
                "high_error_rate",
                "P0",
                f"错误率过高: {metrics.error_rate:.1%}",
                {"task_id": metrics.task_id, "error_rate": metrics.error_rate}
            )
            new_alerts.append(alert)
        
        # 检查延迟
        if metrics.latency_ms > self.rules["high_latency"]["threshold_ms"]:
            alert = self._create_alert(
                "high_latency",
                "P1",
                f"响应延迟过高: {metrics.latency_ms:.0f}ms",
                {"task_id": metrics.task_id, "latency_ms": metrics.latency_ms}
            )
            new_alerts.append(alert)
        
        # 记录告警
        for alert in new_alerts:
            self.alerts.append(alert)
            self._dispatch_alert(alert)
        
        return new_alerts

    def _create_alert(self, alert_type: str, level: str, message: str, data: Dict) -> Dict:
        """创建告警"""
        return {
            "id": f"alert_{int(time.time() * 1000)}",
            "type": alert_type,
            "level": level,
            "message": message,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "acknowledged": False
        }

    def _dispatch_alert(self, alert: Dict):
        """分发告警到处理器"""
        handlers = self.alert_handlers.get(alert["level"], [])
        for handler in handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler error: {e}")

    def register_handler(self, level: str, handler: callable):
        """注册告警处理器"""
        self.alert_handlers[level].append(handler)

    def get_active_alerts(self, level: Optional[str] = None) -> List[Dict]:
        """获取活跃告警"""
        alerts = [a for a in self.alerts if not a.get("acknowledged", False)]
        if level:
            alerts = [a for a in alerts if a["level"] == level]
        return alerts

    def acknowledge_alert(self, alert_id: str) -> bool:
        """确认告警"""
        for alert in self.alerts:
            if alert["id"] == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_at"] = datetime.now(timezone.utc).isoformat()
                return True
        return False


class MetricsCollector:
    """
    指标收集器 - 简化版
    用于收集thinking、memory、workflow等模块的指标
    """

    def __init__(self):
        self.collectors: Dict[str, Dict] = defaultdict(dict)

    def record(self, module: str, metric: str, value: Any):
        """记录指标"""
        if module not in self.collectors:
            self.collectors[module] = {"_ts": datetime.now(timezone.utc).isoformat()}
        self.collectors[module][metric] = value
        self.collectors[module]["_ts"] = datetime.now(timezone.utc).isoformat()

    def get_module_metrics(self, module: str) -> Dict:
        """获取模块指标"""
        return self.collectors.get(module, {})

    def get_all_metrics(self) -> Dict:
        """获取所有指标"""
        return dict(self.collectors)

    def clear(self, module: Optional[str] = None):
        """清除指标"""
        if module:
            self.collectors.pop(module, None)
        else:
            self.collectors.clear()
