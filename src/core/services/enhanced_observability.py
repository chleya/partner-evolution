"""
增强观测性服务 - Week 6
Prometheus指标、追踪、性能监控
"""
import time
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """指标类型"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def inc_counter(self, name: str, value: float = 1, labels: Dict = None):
        """增加计数器"""
        with self._lock:
            key = self._make_key(name, labels)
            self.counters[key] += value
    
    def set_gauge(self, name: str, value: float, labels: Dict = None):
        """设置仪表值"""
        with self._lock:
            key = self._make_key(name, labels)
            self.gauges[key] = value
    
    def observe_histogram(self, name: str, value: float, labels: Dict = None):
        """观察直方图"""
        with self._lock:
            key = self._make_key(name, labels)
            self.histograms[key].append(value)
    
    def _make_key(self, name: str, labels: Dict = None) -> str:
        """生成键"""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def get_metrics(self) -> Dict:
        """获取所有指标"""
        with self._lock:
            return {
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "histograms": {
                    k: {
                        "count": len(v),
                        "sum": sum(v),
                        "avg": sum(v) / len(v) if v else 0,
                        "min": min(v) if v else 0,
                        "max": max(v) if v else 0
                    }
                    for k, v in self.histograms.items()
                }
            }
    
    def export_prometheus(self) -> str:
        """导出Prometheus格式"""
        lines = []
        
        # Counters
        for name, value in self.counters.items():
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name} {value}")
        
        # Gauges
        for name, value in self.gauges.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {value}")
        
        # Histograms
        for name, values in self.histograms.items():
            if values:
                lines.append(f"# TYPE {name} histogram")
                lines.append(f"{name}_count {len(values)}")
                lines.append(f"{name}_sum {sum(values)}")
        
        return "\n".join(lines)


class EnhancedObservabilityService:
    """
    增强观测性服务
    
    特性：
    - Prometheus指标导出
    - 追踪(Trace)记录
    - 性能监控
    - 错误率统计
    - Token消耗统计
    """
    
    METRIC_TOTAL_REQUESTS = "partner_evolution_requests_total"
    METRIC_LATENCY = "partner_evolution_latency_seconds"
    METRIC_ERRORS = "partner_evolution_errors_total"
    METRIC_TOKENS = "partner_evolution_tokens_total"
    METRIC_THINKS = "partner_evolution_thinks_total"
    METRIC_WORKFLOWS = "partner_evolution_workflows_total"
    METRIC_HALLUCINATIONS = "partner_evolution_hallucinations_total"
    
    def __init__(self):
        self.metrics = MetricsCollector()
        self.traces: List[Dict] = []
        self.max_traces = 1000
        self.error_tracker: Dict[str, int] = defaultdict(int)
        self._start_time = time.time()
    
    def record_request(self, endpoint: str, latency_ms: float, success: bool = True):
        """记录请求"""
        self.metrics.inc_counter(
            self.METRIC_TOTAL_REQUESTS,
            labels={"endpoint": endpoint, "status": "success" if success else "error"}
        )
        self.metrics.observe_histogram(
            self.METRIC_LATENCY,
            latency_ms / 1000,
            labels={"endpoint": endpoint}
        )
    
    def record_error(self, error_type: str, endpoint: str = "unknown"):
        """记录错误"""
        self.metrics.inc_counter(
            self.METRIC_ERRORS,
            labels={"type": error_type, "endpoint": endpoint}
        )
        self.error_tracker[error_type] += 1
    
    def record_tokens(self, prompt_tokens: int, completion_tokens: int):
        """记录Token消耗"""
        self.metrics.inc_counter(self.METRIC_TOKENS, prompt_tokens, labels={"type": "prompt"})
        self.metrics.inc_counter(self.METRIC_TOKENS, completion_tokens, labels={"type": "completion"})
    
    def record_think(self, mode: str, confidence: float):
        """记录思考"""
        self.metrics.inc_counter(self.METRIC_THINKS, labels={"mode": mode})
        self.metrics.set_gauge(f"{self.METRIC_THINKS}_confidence", confidence, labels={"mode": mode})
    
    def record_workflow(self, workflow_name: str, status: str):
        """记录工作流"""
        self.metrics.inc_counter(self.METRIC_WORKFLOWS, labels={"workflow": workflow_name, "status": status})
    
    def record_hallucination_check(self, is_hallucination: bool):
        """记录幻觉检测"""
        self.metrics.inc_counter(
            self.METRIC_HALLUCINATIONS,
            labels={"result": "hallucination" if is_hallucination else "real"}
        )
    
    def start_trace(self, trace_id: str, operation: str, metadata: Dict = None) -> str:
        """开始追踪"""
        trace = {
            "trace_id": trace_id,
            "operation": operation,
            "metadata": metadata or {},
            "start_time": time.time(),
            "start_timestamp": datetime.now(timezone.utc).isoformat(),
            "spans": []
        }
        self.traces.append(trace)
        if len(self.traces) > self.max_traces:
            self.traces = self.traces[-self.max_traces:]
        return trace_id
    
    def end_trace(self, trace_id: str, status: str = "ok", error: str = None):
        """结束追踪"""
        for trace in reversed(self.traces):
            if trace["trace_id"] == trace_id:
                trace["end_time"] = time.time()
                trace["duration_ms"] = (trace["end_time"] - trace["start_time"]) * 1000
                trace["status"] = status
                if error:
                    trace["error"] = error
                break
    
    def add_span(self, trace_id: str, span_name: str, duration_ms: float, metadata: Dict = None):
        """添加跨度"""
        for trace in reversed(self.traces):
            if trace["trace_id"] == trace_id:
                trace["spans"].append({
                    "name": span_name,
                    "duration_ms": duration_ms,
                    "metadata": metadata or {}
                })
                break
    
    def get_metrics(self) -> Dict:
        """获取指标"""
        metrics_data = self.metrics.get_metrics()
        
        total_requests = sum(
            v for k, v in metrics_data["counters"].items() 
            if self.METRIC_TOTAL_REQUESTS in k
        )
        total_errors = sum(
            v for k, v in metrics_data["counters"].items() 
            if self.METRIC_ERRORS in k
        )
        
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        latencies = metrics_data["histograms"]
        avg_latency = sum(v["avg"] for v in latencies.values()) / len(latencies) if latencies else 0
        
        uptime_seconds = time.time() - self._start_time
        
        return {
            "metrics": metrics_data,
            "summary": {
                "total_requests": total_requests,
                "total_errors": total_errors,
                "error_rate_percent": round(error_rate, 2),
                "avg_latency_ms": round(avg_latency * 1000, 2),
                "uptime_seconds": round(uptime_seconds, 2),
                "traces_count": len(self.traces),
                "error_types": dict(self.error_tracker)
            }
        }
    
    def get_prometheus_metrics(self) -> str:
        """获取Prometheus格式指标"""
        return self.metrics.export_prometheus()
    
    def get_traces(self, limit: int = 100) -> List[Dict]:
        """获取追踪记录"""
        return self.traces[-limit:]
    
    def get_status(self) -> Dict:
        """获取状态"""
        metrics = self.get_metrics()
        
        return {
            "status": "healthy" if metrics["summary"]["error_rate_percent"] < 1 else "degraded",
            "uptime_seconds": metrics["summary"]["uptime_seconds"],
            "total_requests": metrics["summary"]["total_requests"],
            "error_rate_percent": metrics["summary"]["error_rate_percent"],
            "avg_latency_ms": metrics["summary"]["avg_latency_ms"],
            "error_types": metrics["summary"]["error_types"]
        }


# 全局实例
_observability_service = None

def get_observability_service() -> EnhancedObservabilityService:
    """获取观测性服务实例"""
    global _observability_service
    if _observability_service is None:
        _observability_service = EnhancedObservabilityService()
    return _observability_service
